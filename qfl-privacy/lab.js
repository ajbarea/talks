// The live lab: one instrument per lab slide, each with one control free and the others fixed.
// It builds its markup when the page loads (so the slide gates measure it) and runs its attack
// only when its slide is shown. Everything runs on the main thread: a deck opened from file://
// cannot start a Web Worker, and one attack takes a fraction of a second.
(function () {
  "use strict";

  const Q = window.QLab;
  const DATA = window.DECK_DATA || {};
  const SVG = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  // The trainable blocks stay at this total while repetitions change, as on the paper's
  // fixed-parameter lines: r repetitions of 8 / r blocks each.
  const BLOCKS = 8;
  const REPS = [1, 2, 4, 8];
  const SHOTS = [10, 100, 1000, 10000, 100000, 1000000, 0];
  const MAX_RESTARTS = 20;
  // The paper's thresholds, from data/readings.js.
  const paper = DATA.paper || {};
  const TH = {
    recovered: Number(paper.recoveredRad) || Q.DEFAULTS.recovered,
    close: Number(paper.closeRad) || Q.DEFAULTS.close,
  };
  // Each step's known-good preset: a seed whose run shows the step's point (found by search,
  // tests/test_qfl_lab.py holds each one to it), and the values of the controls.
  const STEPS = {
    reps: { free: "reps", seed: 121, reps: 1, shots: 0, restarts: 10 },
    restarts: { free: "restarts", seed: 15, reps: 8, shots: 0, restarts: 1 },
    shots: { free: "shots", seed: 17, reps: 2, shots: 0, restarts: 10 },
  };
  const WORDS = { recovered: "Recovered", close: "Close", ambiguous: "Ambiguous", stuck: "Stuck" };
  const MEANING = {
    recovered: "found the input",
    close: "near the input",
    ambiguous: "another input fits",
    stuck: "worse fit, gave up",
  };

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
  const shotsWord = (s) => (s ? `${s.toLocaleString("en-US")} shots` : "exact gradient");
  const rad = (v) => (v < 0.001 ? "< 0.001" : v.toFixed(3));

  // Attacks already run, by client: the restarts slider only reads more of a stored run. Kept to
  // the most recent CLIENTS entries, so clicking "New hidden input" all talk long stays bounded.
  const CLIENTS = 24;
  const cache = new Map();
  function entry(seed, reps, shots) {
    const key = `${seed}/${reps}/${shots}`;
    let hit = cache.get(key);
    if (hit) {
      cache.delete(key);
    } else {
      const c = Q.client(seed, reps, BLOCKS / reps, shots);
      hit = { c, runs: [], curve: Q.landscape(c, 240) };
      if (cache.size >= CLIENTS) cache.delete(cache.keys().next().value);
    }
    cache.set(key, hit);
    return hit;
  }
  // Run restarts until `n` are stored or the frame's time budget is spent; true when done.
  const BUDGET_MS = 10;
  function extend(hit, n) {
    const until = performance.now() + BUDGET_MS;
    while (hit.runs.length < n && performance.now() < until) Q.addRestart(hit.c, hit.runs, undefined, TH);
    return hit.runs.length >= n;
  }

  // ---- drawing -------------------------------------------------------------------------------

  // The Bloch sphere in orthographic view: turned a little about its vertical axis, seen a little
  // from above. An encoded input x sits on the x-z great circle at angle x from |0>.
  const AZ = -0.38;
  const EL = 0.24;
  function project([x, y, z]) {
    const across = x * Math.cos(AZ) + y * Math.sin(AZ);
    const depth = -x * Math.sin(AZ) + y * Math.cos(AZ);
    return [120 + 92 * across, 120 - 92 * (z * Math.cos(EL) + depth * Math.sin(EL))];
  }
  function blochPoint(angle) {
    return project([Math.sin(angle), 0, Math.cos(angle)]);
  }
  function ringPath(point) {
    const pts = [];
    for (let i = 0; i <= 72; i++) pts.push(point((Math.PI * 2 * i) / 72).map((v) => v.toFixed(1)).join(" "));
    return `M${pts.join("L")}Z`;
  }

  function buildBloch(box) {
    const s = sv("svg", { viewBox: "0 0 240 240", class: "bloch", role: "img", "aria-label": "Bloch sphere: the hidden input and the attacker's best guess" }, box);
    const title = sv("title", {}, s, "Bloch sphere: the hidden input and the attacker's best guess");
    sv("circle", { cx: 120, cy: 120, r: 92, class: "sphere" }, s);
    sv("path", { d: ringPath((t) => project([Math.cos(t), Math.sin(t), 0])), class: "equator" }, s);
    sv("path", { d: ringPath(blochPoint), class: "meridian" }, s);
    const [tx, ty] = blochPoint(0);
    const [bx, by] = blochPoint(Math.PI);
    sv("text", { x: tx, y: ty - 10, class: "pole", "text-anchor": "middle" }, s, "|0⟩");
    sv("text", { x: bx, y: by + 24, class: "pole", "text-anchor": "middle" }, s, "|1⟩");
    // Hidden until the first result, so the first frame shows no arrow to the drawing's corner.
    const arrows = sv("g", { class: "unset" }, s);
    const arc = sv("path", { class: "gap" }, arrows);
    const truth = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "truth" }, arrows);
    const truthTip = sv("circle", { r: 7, cx: 120, cy: 120, class: "truth-tip" }, arrows);
    const guess = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "guess" }, arrows);
    const guessTip = sv("circle", { r: 7, cx: 120, cy: 120, class: "guess-tip" }, arrows);
    sv("circle", { cx: 120, cy: 120, r: 3.5, class: "hub" }, s);
    return {
      set(x, g) {
        arrows.removeAttribute("class");
        const [px, py] = blochPoint(x);
        truth.setAttribute("x2", px);
        truth.setAttribute("y2", py);
        truthTip.setAttribute("cx", px);
        truthTip.setAttribute("cy", py);
        const [gx, gy] = blochPoint(g);
        guess.setAttribute("x2", gx);
        guess.setAttribute("y2", gy);
        guessTip.setAttribute("cx", gx);
        guessTip.setAttribute("cy", gy);
        // the arc between them, the error the paper measures (modulo a full turn)
        let d = (((g - x) % Q.TAU) + Q.TAU) % Q.TAU;
        if (d > Math.PI) d -= Q.TAU;
        const pts = [];
        for (let i = 0; i <= 24; i++) pts.push(project([0.55 * Math.sin(x + (d * i) / 24), 0, 0.55 * Math.cos(x + (d * i) / 24)]));
        arc.setAttribute("d", `M${pts.map((p) => p.map((v) => v.toFixed(1)).join(" ")).join("L")}`);
      },
      label(text) {
        title.textContent = text;
        s.setAttribute("aria-label", text);
      },
    };
  }

  // The matching loss across one turn of guesses, with the hidden input marked and each
  // restart's search drawn on it.
  const PW = 560;
  const PH = 230;
  const PAD = { l: 14, r: 14, t: 14, b: 40 };
  function buildPlot(box) {
    const blurb = "Matching loss across every guess, lowest where a guess's gradient matches the client's";
    const s = sv("svg", { viewBox: `0 0 ${PW} ${PH}`, class: "trace", role: "img", "aria-label": blurb }, box);
    const title = sv("title", {}, s, blurb);
    const grid = sv("g", { class: "grid" }, s);
    for (let i = 0; i <= 8; i++) {
      const x = PAD.l + ((PW - PAD.l - PAD.r) * i) / 8;
      sv("line", { x1: x, x2: x, y1: PAD.t, y2: PH - PAD.b }, grid);
    }
    for (let i = 0; i <= 4; i++) {
      const y = PAD.t + ((PH - PAD.t - PAD.b) * i) / 4;
      sv("line", { x1: PAD.l, x2: PW - PAD.r, y1: y, y2: y }, grid);
    }
    [["0", 0], ["π", 0.5], ["2π", 1]].forEach(([t, f]) => {
      sv("text", { x: PAD.l + (PW - PAD.l - PAD.r) * f, y: PH - 14, class: "tick", "text-anchor": f === 0 ? "start" : f === 1 ? "end" : "middle" }, s, t);
    });
    sv("text", { x: PAD.l + (PW - PAD.l - PAD.r) * 0.25, y: PH - 14, class: "axis", "text-anchor": "middle" }, s, "guess \u2192");
    const truth = sv("line", { class: "truth-mark", y1: PAD.t, y2: PH - PAD.b }, s);
    const curve = sv("path", { class: "curve" }, s);
    const paths = sv("g", { class: "paths" }, s);
    const balls = sv("g", { class: "balls" }, s);
    // Drawn last, over the curve, with a white halo.
    sv("text", { x: PAD.l + 8, y: PAD.t + 20, class: "axis halo" }, s, "\u2191 matching loss");
    return { s, title, truth, curve, paths, balls };
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
    const step = STEPS[box.dataset.lab];
    if (!step) {
      console.error(`lab: no step ${box.dataset.lab}`);
      return;
    }
    const state = { ...step };
    box.textContent = "";
    // One grid: deck.css places these areas side by side on a slide and stacks them on a phone.
    const head = el("p", { class: "lab-head" }, box);
    el("b", {}, head, "Toy circuit, live in this browser");
    const origin = el("span", { class: "lab-origin" }, head);
    const fixedNote = el("span", { class: "lab-fixed" }, head);
    const bloch = buildBloch(el("div", { class: "lab-bloch" }, box));
    const plot = buildPlot(el("div", { class: "lab-trace" }, box));
    const read = el("div", { class: "lab-read", "aria-live": "polite" }, box);
    const form = el("div", { class: "lab-ctl", role: "group", "aria-label": "Lab controls" }, box);
    const name = box.dataset.lab;
    const ctl = {
      reps: control(form, name, "reps", "Repetitions", REPS.length - 1, REPS.indexOf(state.reps), step.free === "reps", (i) => `${REPS[i]} \u00d7 ${BLOCKS / REPS[i]}`),
      shots: control(form, name, "shots", "Shots", SHOTS.length - 1, SHOTS.indexOf(state.shots), step.free === "shots", (i) => shotsWord(SHOTS[i])),
      restarts: control(form, name, "restarts", "Restarts", MAX_RESTARTS, state.restarts, step.free === "restarts", (i) => `${i} restart${i === 1 ? "" : "s"}`),
    };
    const buttons = el("div", { class: "lab-buttons" }, box);
    const fresh = el("button", { type: "button" }, buttons, "New hidden input");
    const reset = el("button", { type: "button" }, buttons, "Reset to preset");

    let frame = 0;
    let shown = false;

    function sync() {
      for (const [name, c] of Object.entries(ctl)) {
        const i = name === "reps" ? REPS.indexOf(state.reps) : name === "shots" ? SHOTS.indexOf(state.shots) : state.restarts;
        c.input.value = String(i);
        c.out.textContent = c.text(i);
        c.input.setAttribute("aria-valuetext", name === "reps" ? `${c.text(i)}: repetitions times trainable blocks` : c.text(i));
      }
      origin.innerHTML = state.seed === step.seed ? '<span class="long">preset input, picked to show the effect</span><span class="short">picked input</span>' : "random input";
      // The fixed values, once more in the header: a phone hides the fixed controls.
      fixedNote.textContent = `fixed here: ${Object.values(ctl)
        .filter((c) => !c.free)
        .map((c) => c.out.textContent)
        .join(", ")}`;
    }

    // One redraw per animation frame however many input events a drag fires, and the restarts it
    // needs computed a frame's budget at a time, so the slide never freezes.
    let queued = 0;
    function request() {
      if (!queued) queued = requestAnimationFrame(draw);
    }

    function draw() {
      queued = 0;
      cancelAnimationFrame(frame);
      sync();
      const hit = entry(state.seed, state.reps, state.shots);
      if (!extend(hit, state.restarts)) {
        searching();
        const more = () => {
          if (extend(hit, state.restarts)) render(hit);
          else frame = requestAnimationFrame(more);
        };
        frame = requestAnimationFrame(more);
        return;
      }
      render(hit);
    }

    function searching() {
      box.classList.remove("done");
      read.setAttribute("aria-busy", "true");
      read.innerHTML = '<p class="verdict searching"><b>Searching</b><span>restarts rolling downhill</span></p>';
    }

    function render(hit) {
      const { c, curve } = hit;
      const runs = hit.runs.slice(0, state.restarts);
      const best = Q.pickBest(runs, runs.length);
      const top = Math.max(...curve) || 1;
      const X = (v) => PAD.l + ((((v % Q.TAU) + Q.TAU) % Q.TAU) / Q.TAU) * (PW - PAD.l - PAD.r);
      const Y = (L) => PH - PAD.b - (Math.min(L, top) / top) * (PH - PAD.t - PAD.b);
      plot.curve.setAttribute("d", `M${Array.from(curve, (L, i) => `${(PAD.l + (i / curve.length) * (PW - PAD.l - PAD.r)).toFixed(1)} ${Y(L).toFixed(1)}`).join("L")}`);
      plot.truth.setAttribute("x1", X(c.x));
      plot.truth.setAttribute("x2", X(c.x));
      plot.paths.textContent = "";
      plot.balls.textContent = "";
      // Each restart's search as a trail of points, its losses stored when it ran.
      const trails = runs.map((r) => r.path.map((v, j) => [X(v), Y(r.losses[j])]));
      const lines = trails.map(() => sv("path", { d: "" }, plot.paths));
      const dots = runs.map((r, i) => sv("circle", { r: i === best ? 9 : 6, class: `ball ${r.outcome}${i === best ? " best" : ""}` }, plot.balls));
      const hits = runs.filter((r) => r.outcome === "recovered").length;
      const b = runs[best];
      const n = trails[0].length;
      const DUR = 1400;
      const half = (PW - PAD.l - PAD.r) / 2;
      const paint = (k) => {
        trails.forEach((t, i) => {
          const upto = Math.min(t.length - 1, k);
          // Every second point is enough for the line. A search that crosses 0 or 2pi reappears
          // at the other edge, so the stroke starts again there.
          let d = "";
          let last = null;
          for (let j = 0; j <= upto; j++) {
            if (j % 2 && j !== upto) continue;
            const p = t[j];
            d += `${last === null || Math.abs(p[0] - last) > half ? "M" : "L"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`;
            last = p[0];
          }
          lines[i].setAttribute("d", d);
          dots[i].setAttribute("cx", t[upto][0]);
          dots[i].setAttribute("cy", t[upto][1]);
        });
        bloch.set(c.x, b.path[Math.min(b.path.length - 1, k)]);
      };
      const finish = () => {
        paint(n - 1);
        box.classList.add("done");
        const err = rad(b.error);
        read.innerHTML = "";
        const o = el("p", { class: `verdict ${b.outcome}` }, read);
        el("b", {}, o, WORDS[b.outcome]);
        el("span", {}, o, MEANING[b.outcome]);
        const e = el("p", { class: "meter" }, read);
        el("span", {}, e, "Error");
        el("b", {}, e, `${err} rad`);
        const h = el("p", { class: "meter" }, read);
        el("span", {}, h, "Restarts that hit");
        el("b", {}, h, `${hits} of ${runs.length}`);
        // Screen readers hear the result once, when it is complete.
        read.setAttribute("aria-busy", "false");
        const words = `${WORDS[b.outcome]}: the best guess is ${err} radians from the hidden input; ${hits} of ${runs.length} restarts found it.`;
        bloch.label(`Bloch sphere: the hidden input and the attacker's best guess. ${words}`);
        plot.title.textContent = `Matching loss across every guess, lowest where a guess's gradient matches the client's. ${words}`;
        plot.s.setAttribute("aria-label", plot.title.textContent);
      };
      if (reduce) {
        finish();
        return;
      }
      searching();
      const t0 = performance.now();
      const tick = (now) => {
        // A frame's timestamp can precede t0 (it marks the frame's start), so clamp at the first point.
        const k = Math.max(0, Math.floor(((now - t0) / DUR) * (n - 1)));
        if (k >= n - 1) {
          finish();
          return;
        }
        paint(k);
        frame = requestAnimationFrame(tick);
      };
      frame = requestAnimationFrame(tick);
    }

    for (const [name, c] of Object.entries(ctl)) {
      c.input.addEventListener("input", () => {
        const i = Number(c.input.value);
        if (name === "reps") state.reps = REPS[i];
        else if (name === "shots") state.shots = SHOTS[i];
        else state.restarts = i;
        request();
      });
    }
    fresh.addEventListener("click", () => {
      state.seed = 1000 + Math.floor(Math.random() * 1e6);
      request();
    });
    reset.addEventListener("click", () => {
      Object.assign(state, step);
      request();
    });

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
        if (!shown) {
          shown = true;
          request();
        }
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
