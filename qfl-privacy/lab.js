// The live lab: one instrument per lab slide, each with one control free and the others fixed, and
// beside the paper's figure a row of hidden inputs 1 to 20 per value of that control. It builds its
// markup when the page loads (so the slide gates measure it) and runs only when its slide is shown.
// Everything runs on the main thread: a deck opened from file:// cannot start a Web Worker.
(function () {
  "use strict";

  const Q = window.QLab;
  const DATA = window.DECK_DATA || {};
  const SVG = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const TOY = Q.TOY;
  const REPS = TOY.steps.reps.reps;
  const SHOTS = [10, 100, 1000, 10000, 100000, 1000000, 0];
  const MAX_RESTARTS = Math.max(...TOY.steps.restarts.restarts);
  // The paper's thresholds and the numbers the row notes compare with, from data/readings.js.
  const paper = DATA.paper || {};
  const TH = {
    recovered: Number(paper.recoveredRad) || Q.DEFAULTS.recovered,
    close: Number(paper.closeRad) || Q.DEFAULTS.close,
  };
  // Each step opens on hidden input 1 with its free control at the first value of its rows (shots
  // at exact), the others fixed at the toy's values.
  const STEPS = {};
  for (const [name, s] of Object.entries(TOY.steps)) {
    const first = (k) => (k === name ? (k === "shots" ? 0 : s[k][0]) : s[k]);
    STEPS[name] = { free: name, reps: first("reps"), restarts: first("restarts"), shots: first("shots"), draw: 1 };
  }
  // A search's pace: each restart rolls for ROLL ms, released one after another so the last lands
  // at TOTAL ms, and leaves a trail of TRAIL path points that fades for FADE ms once it lands. The
  // whole search ends inside the five seconds after which motion that starts by itself needs a pause
  // control (WCAG 2.2.2). Replay runs SLOW times slower, and only when asked for.
  const PACE = { total: 4500, roll: 1800, fade: 400, trail: 8, slow: 2.5 };
  const WORD = { recovered: "recovered", close: "close", ambiguous: "another input fits", stuck: "stuck" };

  const el = (tag, attrs, parent, text) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  };
  const sv = (tag, attrs, parent, text) => {
    const n = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  };
  const set = (n, attrs) => {
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  };
  const shotsWord = (s) => (s ? `${s.toLocaleString("en-US")} shots` : "exact gradient");
  const rad = (v) => (v < 0.001 ? "< 0.001" : v.toFixed(3));

  // Attacks already run, by client: the restarts slider only reads more of a stored run. Kept to
  // the most recent CLIENTS entries, so stepping through hidden inputs all talk long stays bounded.
  const CLIENTS = 24;
  const cache = new Map();
  function entry(seed, reps, shots) {
    const key = `${seed}/${reps}/${shots}`;
    let hit = cache.get(key);
    if (hit) {
      cache.delete(key);
    } else {
      const c = Q.client(seed, reps, TOY.blocks / reps, shots);
      hit = { c, runs: [], curve: Q.landscape(c, 240) };
      if (cache.size >= CLIENTS) cache.delete(cache.keys().next().value);
    }
    cache.set(key, hit);
    return hit;
  }
  // Main-thread work is done a frame's budget at a time, so a slide never freezes.
  const BUDGET_MS = 8;
  function extend(hit, n, until) {
    while (hit.runs.length < n && performance.now() < until) Q.addRestart(hit.c, hit.runs, undefined, TH);
    return hit.runs.length >= n;
  }

  // ---- the Bloch sphere ----------------------------------------------------------------------

  // Orthographic view: turned a little about its vertical axis, seen a little from above. An encoded
  // input x sits on the x-z great circle at angle x from |0>; points off the sphere at radius s.
  const AZ = -0.38;
  const EL = 0.24;
  const R = 78;
  function project([x, y, z]) {
    const across = x * Math.cos(AZ) + y * Math.sin(AZ);
    const depth = -x * Math.sin(AZ) + y * Math.cos(AZ);
    return [120 + R * across, 120 - R * (z * Math.cos(EL) + depth * Math.sin(EL))];
  }
  const onCircle = (angle, s = 1) => project([s * Math.sin(angle), 0, s * Math.cos(angle)]);
  function ringPath(point) {
    const pts = [];
    for (let i = 0; i <= 72; i++) pts.push(point((Math.PI * 2 * i) / 72).map((v) => v.toFixed(1)).join(" "));
    return `M${pts.join("L")}Z`;
  }

  function buildBloch(box) {
    const blurb = "Bloch sphere: the hidden input (ring), the attacker's best guess (dot) and where each restart ended (ticks outside)";
    const s = sv("svg", { viewBox: "0 0 240 240", class: "bloch", role: "img", "aria-label": blurb }, box);
    const title = sv("title", {}, s, blurb);
    sv("circle", { cx: 120, cy: 120, r: R, class: "sphere" }, s);
    sv("path", { d: ringPath((t) => project([Math.cos(t), Math.sin(t), 0])), class: "equator" }, s);
    sv("path", { d: ringPath((t) => onCircle(t)), class: "meridian" }, s);
    const [tx, ty] = onCircle(0);
    const [bx, by] = onCircle(Math.PI);
    sv("text", { x: tx - 12, y: ty - 4, class: "pole", "text-anchor": "end" }, s, "|0⟩");
    sv("text", { x: bx - 12, y: by + 20, class: "pole", "text-anchor": "end" }, s, "|1⟩");
    const ends = sv("g", { class: "ends" }, s);
    // Hidden until the first result, so the first frame shows no marker at the drawing's centre.
    const marks = sv("g", { class: "unset" }, s);
    const truthSpoke = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "truth" }, marks);
    const guessSpoke = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "guess unset" }, marks);
    const truth = sv("circle", { r: 10, cx: 120, cy: 120, class: "truth-ring" }, marks);
    const guess = sv("circle", { r: 5.5, cx: 120, cy: 120, class: "guess-dot unset" }, marks);
    sv("circle", { cx: 120, cy: 120, r: 3.5, class: "hub" }, s);
    const stacks = new Map();
    return {
      reset(x) {
        marks.removeAttribute("class");
        ends.textContent = "";
        stacks.clear();
        const [px, py] = onCircle(x);
        set(truthSpoke, { x2: px, y2: py });
        set(truth, { cx: px, cy: py });
        guessSpoke.classList.add("unset");
        guess.classList.add("unset");
      },
      // A restart's end point: a tick just outside the sphere, stacked outward when several end
      // within a few degrees of each other, so a crowd of landings reads as a taller stack.
      end(angle, outcome) {
        const a = ((angle % Q.TAU) + Q.TAU) % Q.TAU;
        const bin = Math.round(a / 0.12);
        const k = stacks.get(bin) || 0;
        stacks.set(bin, k + 1);
        const [ex, ey] = onCircle(a, 1.16 + 0.1 * Math.min(k, 3));
        sv("circle", { cx: ex.toFixed(1), cy: ey.toFixed(1), r: 4, class: `end ${outcome}` }, ends);
      },
      guess(g) {
        const [gx, gy] = onCircle(g);
        set(guessSpoke, { x2: gx, y2: gy });
        set(guess, { cx: gx, cy: gy });
        guessSpoke.classList.remove("unset");
        guess.classList.remove("unset");
      },
      label(text) {
        title.textContent = `${blurb}. ${text}`;
        s.setAttribute("aria-label", title.textContent);
      },
    };
  }

  // ---- the loss plot ---------------------------------------------------------------------------

  // The matching loss across one turn of guesses, with the hidden input marked and each restart's
  // search rolled down it.
  const PW = 560;
  const PH = 230;
  const PAD = { l: 14, r: 14, t: 14, b: 40 };
  const SPAN = PW - PAD.l - PAD.r;
  function buildPlot(box) {
    const blurb = "Matching loss across every guess, lowest where a guess's gradient matches the client's";
    const s = sv("svg", { viewBox: `0 0 ${PW} ${PH}`, class: "trace", role: "img", "aria-label": blurb }, box);
    const title = sv("title", {}, s, blurb);
    const grid = sv("g", { class: "grid" }, s);
    for (let i = 0; i <= 8; i++) {
      const x = PAD.l + (SPAN * i) / 8;
      sv("line", { x1: x, x2: x, y1: PAD.t, y2: PH - PAD.b }, grid);
    }
    for (let i = 0; i <= 4; i++) {
      const y = PAD.t + ((PH - PAD.t - PAD.b) * i) / 4;
      sv("line", { x1: PAD.l, x2: PW - PAD.r, y1: y, y2: y }, grid);
    }
    [["0", 0], ["π", 0.5], ["2π", 1]].forEach(([t, f]) => {
      sv("text", { x: PAD.l + SPAN * f, y: PH - 14, class: "tick", "text-anchor": f === 0 ? "start" : f === 1 ? "end" : "middle" }, s, t);
    });
    sv("text", { x: PAD.l + SPAN * 0.25, y: PH - 14, class: "axis", "text-anchor": "middle" }, s, "guess →");
    // Hidden until the first result, like the sphere's markers.
    const truth = sv("line", { class: "truth-mark unset", y1: PAD.t, y2: PH - PAD.b }, s);
    const curve = sv("path", { class: "curve" }, s);
    const paths = sv("g", { class: "paths" }, s);
    const trails = sv("g", { class: "trails" }, s);
    const balls = sv("g", { class: "balls" }, s);
    // Drawn last, on white plates, so neither the curve nor a ball crosses them.
    sv("rect", { x: PAD.l + 2, y: PAD.t + 1, width: 170, height: 28, rx: 4, class: "plate" }, s);
    sv("text", { x: PAD.l + 8, y: PAD.t + 22, class: "axis" }, s, "↑ matching loss");
    const tagPlate = sv("rect", { y: PH - PAD.b - 31, width: 132, height: 28, rx: 4, class: "plate unset" }, s);
    const tag = sv("text", { y: PH - PAD.b - 10, class: "axis tag unset" }, s, "hidden input");
    return { s, title, truth, curve, paths, trails, balls, tag, tagPlate };
  }

  // ---- the rows of hidden inputs beside the paper's figure -------------------------------------

  // Laid out like the paper's figures beside them: a label column, one mark per hidden input, a
  // count on the right.
  const ROW = {
    reps: { head: ["r × ℓ", "restarts of 10 that hit, per input", `of ${TOY.draws * TOY.steps.reps.restarts}`], label: (r) => `${r}×${TOY.blocks / r}`, pitch: 40 },
    restarts: { head: ["restarts", "hidden inputs recovered", `of ${TOY.draws}`], label: (n) => String(n), pitch: 32 },
    shots: { head: ["shots", `hidden inputs within ${TH.close} rad`, `of ${TOY.draws}`], label: (s) => (s ? s.toLocaleString("en-US") : "exact"), pitch: 34 },
  };
  const X0 = 102;
  const DX = 15.5;
  const CELLS = TOY.steps.reps.restarts;

  function buildRows(box, step) {
    const spec = ROW[step];
    const values = TOY.steps[step][step];
    const H = 34 + spec.pitch * values.length;
    const cap = el("figcaption", {}, box);
    el("b", {}, cap, "The toy, in this browser");
    cap.append(`1 qubit, hidden inputs 1 to ${TOY.draws}, not picked`);
    const s = sv("svg", { viewBox: `0 0 480 ${H}`, class: "toy-fig", role: "img", "aria-label": "Toy results per hidden input: computing" }, box);
    sv("text", { x: 0, y: 20, class: "h", "text-anchor": "start" }, s, spec.head[0]);
    sv("text", { x: 96, y: 20, class: "h", "text-anchor": "start" }, s, spec.head[1]);
    sv("text", { x: 480, y: 20, class: "h", "text-anchor": "end" }, s, spec.head[2]);
    const note = el("p", { class: "paper-note toy-note", "aria-live": "polite" }, box, "Running hidden inputs 1 to 20…");
    const rows = values.map((v, i) => {
      const y = 34 + spec.pitch * i;
      const band = sv("rect", { x: -4, y: y + 2, width: 488, height: spec.pitch - 4, rx: 4, class: "band" }, s);
      const label = sv("text", { x: 0, y: y + spec.pitch / 2 + 8, class: "l" }, s, spec.label(v));
      const marks = [];
      for (let d = 0; d < TOY.draws; d++) {
        const cx = X0 + DX * d;
        if (step === "reps") {
          // One column per hidden input: its 10 restarts, filled from the bottom when they hit.
          const g = sv("g", {}, s);
          const top = y + 4;
          const cells = [];
          for (let k = 0; k < CELLS; k++) {
            cells.push(sv("rect", { x: cx - 5.5, y: (top + (CELLS - 1 - k) * 3.2).toFixed(1), width: 11, height: 2.6, class: "cell" }, g));
          }
          const frame = sv("rect", { x: cx - 7.5, y: top - 2, width: 15, height: CELLS * 3.2 + 3, rx: 2, class: "here-mark" }, g);
          marks.push({ g, cells, frame });
        } else {
          const cy = y + spec.pitch / 2;
          const dot = sv("circle", { cx, cy, r: 6, class: "dot" }, s);
          const frame = sv("circle", { cx, cy, r: 9.5, class: "here-mark" }, s);
          marks.push({ dot, frame });
        }
      }
      const count = sv("text", { x: 480, y: y + spec.pitch / 2 + 8, class: "n", "text-anchor": "end" }, s, "");
      return { band, label, marks, count, total: 0, done: 0 };
    });
    const results = [];
    return {
      // One hidden input's scores, one per row.
      add(draw, scores) {
        results[draw - 1] = scores;
        scores.forEach((v, i) => {
          const row = rows[i];
          const m = row.marks[draw - 1];
          if (step === "reps") m.cells.forEach((c, k) => c.classList.toggle("hit", k < v));
          else m.dot.classList.toggle("hit", v);
          row.total += Number(v);
          row.done += 1;
          row.count.textContent = String(row.total);
        });
      },
      complete() {
        const t = rows.map((r) => r.total);
        const last = t.length - 1;
        const words = values.map((v, i) => `${spec.label(v)}: ${t[i]}`).join("; ");
        s.setAttribute("aria-label", `Toy results over hidden inputs 1 to ${TOY.draws}, ${spec.head[1]}, ${spec.head[2]}: ${words}`);
        const p = DATA.rq1 || {};
        const r2 = DATA.rq2 || {};
        if (step === "reps") {
          note.textContent = `Restarts that hit ${t[0] > t[last] ? "fell" : "did not fall"} from ${t[0]} to ${t[last]} of ${TOY.draws * CELLS} as repetitions grew; the paper's went from ${p.hits1} to ${p.hits8} of ${p.tries}. One qubit is the easy end.`;
        } else if (step === "restarts") {
          note.textContent = `Hidden inputs recovered ${t[last] > t[0] ? "rose" : "did not rise"} from ${t[0]} with 1 restart to ${t[last]} with ${values[last]}, as stuck seeds did in the paper.`;
        } else {
          note.textContent = `Within ${TH.close} rad here: ${t[0]} of ${TOY.draws} at 10 shots, ${t[1]} at 100. One qubit is the easy end; the paper's 8-qubit circuits lost at ${r2.lowShots || 100}.`;
        }
      },
      // Outline the row of the free control's value and the mark of the hidden input on show.
      here(value, draw) {
        rows.forEach((row, i) => {
          const on = values[i] === value;
          row.band.classList.toggle("on", on);
          row.label.classList.toggle("on", on);
          row.marks.forEach((m, d) => m.frame.classList.toggle("on", on && d === draw - 1));
        });
      },
    };
  }

  // Runs hidden inputs 1 to 20 for a step, a frame's budget at a time, and shows each as it is
  // scored, no faster than one every STEP_MS so the rows fill at a pace the room can follow.
  const STEP_MS = reduce ? 0 : 60;
  function fillRows(rows, step) {
    let draw = 1;
    let jobs = Q.tallyJobs(step, draw);
    let shownAt = 0;
    const ready = [];
    const tick = (now) => {
      const until = performance.now() + BUDGET_MS;
      while (draw <= TOY.draws && performance.now() < until) {
        const j = jobs.find((x) => x.runs.length < x.n);
        if (j) {
          Q.addRestart(j.c, j.runs, undefined, TH);
          continue;
        }
        ready.push([draw, Q.tallyScore(step, jobs, TH)]);
        draw += 1;
        if (draw <= TOY.draws) jobs = Q.tallyJobs(step, draw);
      }
      if (reduce) {
        if (draw > TOY.draws) ready.splice(0).forEach(([d, s]) => rows.add(d, s));
      } else if (ready.length && now - shownAt >= STEP_MS) {
        rows.add(...ready.shift());
        shownAt = now;
      }
      if (draw > TOY.draws && !ready.length) rows.complete();
      else requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // ---- one instrument ------------------------------------------------------------------------

  function control(form, step, name, label, max, value, free, text) {
    const id = `lab-${step}-${name}`;
    const row = el("div", { class: `ctl${free ? " free" : " fixed"}` }, form);
    el("label", { for: id }, row, free ? label : `${label}, fixed`);
    const input = el("input", { id, type: "range", min: name === "restarts" ? 1 : 0, max, step: 1, value }, row);
    const out = el("output", { for: id }, row);
    if (!free) input.disabled = true;
    return { input, out, text, free };
  }

  function instrument(box) {
    const name = box.dataset.lab;
    const step = STEPS[name];
    if (!step) {
      console.error(`lab: no step ${name}`);
      return;
    }
    const state = { ...step };
    box.textContent = "";
    // One grid: deck.css places these areas on a slide and stacks them on a phone.
    const head = el("p", { class: "lab-head" }, box);
    el("b", {}, head, "Toy circuit, live in this browser");
    const origin = el("span", { class: "lab-origin" }, head);
    const fixedNote = el("span", { class: "lab-fixed" }, head);
    const bloch = buildBloch(el("div", { class: "lab-bloch" }, box));
    const plot = buildPlot(el("div", { class: "lab-trace" }, box));
    const read = el("div", { class: "lab-read", "aria-live": "polite" }, box);
    const main = el("p", { class: "meter main" }, read);
    const mainLabel = el("span", {}, main, "Restarts that found the input");
    const mainValue = el("b", {}, main, "–");
    const minor = el("p", { class: "meter minor" }, read);
    el("span", {}, minor, "Best guess");
    const minorValue = el("b", {}, minor, "–");
    const form = el("div", { class: "lab-ctl", role: "group", "aria-label": "Lab controls" }, box);
    const ctl = {
      reps: control(form, name, "reps", "Repetitions", REPS.length - 1, REPS.indexOf(state.reps), step.free === "reps", (i) => `${REPS[i]} × ${TOY.blocks / REPS[i]}`),
      shots: control(form, name, "shots", "Shots", SHOTS.length - 1, SHOTS.indexOf(state.shots), step.free === "shots", (i) => shotsWord(SHOTS[i])),
      restarts: control(form, name, "restarts", "Restarts", MAX_RESTARTS, state.restarts, step.free === "restarts", (i) => `${i} restart${i === 1 ? "" : "s"}`),
    };
    const buttons = el("div", { class: "lab-buttons" }, box);
    const next = el("button", { type: "button" }, buttons, "Next hidden input");
    const reset = el("button", { type: "button" }, buttons, "Reset");
    const replay = el("button", { type: "button" }, buttons, "Replay slowly");
    // With reduced motion every search shows its end at once, so there is nothing to replay.
    if (reduce) replay.hidden = true;
    const side = box.closest(".lab-row")?.querySelector(`[data-rows="${name}"]`);
    const rows = side ? buildRows(side, name) : null;

    let frame = 0;
    let shown = false;

    function sync() {
      for (const [k, c] of Object.entries(ctl)) {
        const i = k === "reps" ? REPS.indexOf(state.reps) : k === "shots" ? SHOTS.indexOf(state.shots) : state.restarts;
        c.input.value = String(i);
        c.out.textContent = c.text(i);
        c.input.setAttribute("aria-valuetext", k === "reps" ? `${c.text(i)}: repetitions times trainable blocks` : c.text(i));
      }
      origin.textContent = `hidden input ${state.draw} of ${TOY.draws}`;
      // The fixed values, once more in the header: a phone hides the fixed controls.
      fixedNote.textContent = `fixed: ${Object.values(ctl)
        .filter((c) => !c.free)
        .map((c) => c.out.textContent)
        .join(", ")}`;
      rows?.here(state[name], state.draw);
    }

    // One redraw per animation frame however many input events a drag fires, and the restarts it
    // needs computed a frame's budget at a time.
    let queued = 0;
    let speed = 1;
    function request(slow) {
      speed = slow ? PACE.slow : 1;
      if (!queued) queued = requestAnimationFrame(draw);
    }

    function draw() {
      queued = 0;
      cancelAnimationFrame(frame);
      sync();
      const hit = entry(state.draw, state.reps, state.shots);
      const more = () => {
        if (extend(hit, state.restarts, performance.now() + BUDGET_MS)) render(hit);
        else frame = requestAnimationFrame(more);
      };
      if (!extend(hit, state.restarts, performance.now() + BUDGET_MS)) {
        busy();
        frame = requestAnimationFrame(more);
        return;
      }
      render(hit);
    }

    function busy() {
      box.classList.remove("done");
      read.setAttribute("aria-busy", "true");
    }

    function render(hit) {
      const { c, curve } = hit;
      const runs = hit.runs.slice(0, state.restarts);
      const n = runs.length;
      const best = Q.pickBest(runs, n);
      const b = runs[best];
      const top = Math.max(...curve) || 1;
      const X = (v) => PAD.l + ((((v % Q.TAU) + Q.TAU) % Q.TAU) / Q.TAU) * SPAN;
      const Y = (L) => PH - PAD.b - (Math.min(L, top) / top) * (PH - PAD.t - PAD.b);
      plot.curve.setAttribute("d", `M${Array.from(curve, (L, i) => `${(PAD.l + (i / curve.length) * SPAN).toFixed(1)} ${Y(L).toFixed(1)}`).join("L")}`);
      const tx = X(c.x);
      set(plot.truth, { x1: tx, x2: tx });
      // The label sits on the side of the mark with more room.
      const right = tx < PW / 2;
      set(plot.tag, { x: right ? tx + 8 : tx - 8, "text-anchor": right ? "start" : "end" });
      set(plot.tagPlate, { x: right ? tx + 3 : tx - 135 });
      for (const n2 of [plot.truth, plot.tag, plot.tagPlate]) n2.classList.remove("unset");
      plot.paths.textContent = "";
      plot.trails.textContent = "";
      plot.balls.textContent = "";
      bloch.reset(c.x);
      const half = SPAN / 2;
      const pts = runs.map((r) => r.path.map((v, j) => [X(v), Y(r.losses[j])]));
      const full = runs.map(() => sv("path", { d: "" }, plot.paths));
      const segs = runs.map(() => Array.from({ length: PACE.trail }, () => sv("line", { "stroke-opacity": 0 }, plot.trails)));
      const balls = runs.map(() => sv("circle", { r: 6, class: "ball rolling" }, plot.balls));
      const landed = new Array(n).fill(false);
      let hits = 0;
      let count = 0;
      const gap = n > 1 ? Math.min(600, (PACE.total - PACE.roll) / (n - 1)) : 0;
      const wrapped = (a, b2) => Math.abs(a[0] - b2[0]) > half;
      const at = (t, f) => {
        const i = Math.min(t.length - 1, Math.floor(f));
        const j = Math.min(t.length - 1, i + 1);
        const u = f - i;
        if (wrapped(t[i], t[j])) return t[u < 0.5 ? i : j];
        return [t[i][0] + (t[j][0] - t[i][0]) * u, t[i][1] + (t[j][1] - t[i][1]) * u];
      };
      const fullPath = (t) => {
        let d = "";
        let last = null;
        t.forEach((p, j) => {
          if (j % 2 && j !== t.length - 1) return;
          d += `${last === null || Math.abs(p[0] - last) > half ? "M" : "L"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`;
          last = p[0];
        });
        return d;
      };
      const meter = (final) => {
        mainLabel.textContent = final ? "Restarts that found the input" : "Restarts that found the input, so far";
        mainValue.textContent = `${hits} of ${final ? n : count}`;
      };
      const land = (i) => {
        landed[i] = true;
        count += 1;
        if (runs[i].outcome === "recovered") hits += 1;
        balls[i].setAttribute("class", `ball ${runs[i].outcome}`);
        bloch.end(runs[i].end, runs[i].outcome);
        meter(false);
      };
      const finish = () => {
        runs.forEach((r, i) => {
          if (!landed[i]) land(i);
          const end = pts[i][pts[i].length - 1];
          set(balls[i], { cx: end[0], cy: end[1], r: i === best ? 9 : 6 });
          segs[i].forEach((s) => s.setAttribute("stroke-opacity", 0));
          full[i].setAttribute("d", fullPath(pts[i]));
        });
        balls[best].classList.add("best");
        bloch.guess(b.end);
        meter(true);
        minorValue.textContent = `${WORD[b.outcome]}, ${rad(b.error)} rad`;
        box.classList.add("done");
        // Screen readers hear the result once, when it is complete.
        read.setAttribute("aria-busy", "false");
        const words = `${hits} of ${n} restarts found the hidden input; the best guess is ${rad(b.error)} radians from it (${WORD[b.outcome]}).`;
        bloch.label(words);
        plot.title.textContent = `Matching loss across every guess, lowest where a guess's gradient matches the client's. ${words}`;
        plot.s.setAttribute("aria-label", plot.title.textContent);
      };
      minorValue.textContent = "–";
      meter(false);
      if (reduce) {
        finish();
        return;
      }
      busy();
      const stretch = speed;
      const t0 = performance.now();
      const span = (n - 1) * gap + PACE.roll + PACE.fade;
      const tick = (now) => {
        // A frame's timestamp can precede t0 (it marks the frame's start), so clamp at zero.
        const t = Math.max(0, now - t0) / stretch;
        if (t >= span) {
          finish();
          return;
        }
        runs.forEach((r, i) => {
          const local = (t - i * gap) / PACE.roll;
          const tr = pts[i];
          if (local < 0) {
            balls[i].setAttribute("r", 0);
            return;
          }
          const f = Math.min(1, local) * (tr.length - 1);
          const p = at(tr, f);
          set(balls[i], { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 6 });
          if (local >= 1 && !landed[i]) land(i);
          const fade = local < 1 ? 1 : Math.max(0, 1 - ((local - 1) * PACE.roll) / PACE.fade);
          segs[i].forEach((s, k) => {
            const a = at(tr, Math.max(0, f - k - 1));
            const z = at(tr, Math.max(0, f - k));
            const gone = wrapped(a, z) || f - k <= 0;
            set(s, { x1: a[0].toFixed(1), y1: a[1].toFixed(1), x2: z[0].toFixed(1), y2: z[1].toFixed(1), "stroke-opacity": gone ? 0 : ((0.75 * (PACE.trail - k)) / PACE.trail) * fade });
          });
        });
        frame = requestAnimationFrame(tick);
      };
      frame = requestAnimationFrame(tick);
    }

    for (const [k, c] of Object.entries(ctl)) {
      c.input.addEventListener("input", () => {
        const i = Number(c.input.value);
        if (k === "reps") state.reps = REPS[i];
        else if (k === "shots") state.shots = SHOTS[i];
        else state.restarts = i;
        request();
      });
    }
    next.addEventListener("click", () => {
      state.draw = (state.draw % TOY.draws) + 1;
      request();
    });
    reset.addEventListener("click", () => {
      Object.assign(state, step);
      request();
    });
    replay.addEventListener("click", () => request(true));

    // Keys pressed in the panel stay in the panel: Space on a button would otherwise also turn
    // the slide. Escape hands the keyboard back to the slides.
    box.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        document.activeElement?.blur();
        return;
      }
      e.stopPropagation();
    });
    // After a drag or a click, give the keyboard back too, so a presenter's clicker (which sends
    // arrow or page keys) turns the slide instead of moving the control it last touched.
    box.addEventListener("pointerup", (e) => {
      setTimeout(() => e.target.closest("input, button")?.blur(), 0);
    });

    sync();
    return {
      show() {
        if (shown) return;
        shown = true;
        request();
        if (rows) fillRows(rows, name);
      },
    };
  }

  const labs = new Map();
  for (const box of document.querySelectorAll("[data-lab]")) {
    const lab = instrument(box);
    if (lab) labs.set(box.closest("section"), lab);
  }
  // Run a lab the first time its slide is shown (in the paged deck or the phone's scrolling feed).
  const showCurrent = () => labs.get(window.Reveal?.getCurrentSlide?.())?.show();
  if (window.Reveal && labs.size) {
    Reveal.on("ready", showCurrent);
    Reveal.on("slidechanged", showCurrent);
  }
})();
