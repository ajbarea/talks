// The gradient inversion lab: the talk's live toy as a page of its own. The state lives in the
// URL hash (#tab=attack&input=3&reps=2&shots=0&restarts=10), so any view can be shared exactly.
// The toy runs here (../lab-sim.js); the paper's runs come frozen from figures.py (data/runs.js)
// and are only drawn and counted, never rescored.
(function () {
  "use strict";

  const Q = window.QLab;
  const RUNS = window.PAPER_RUNS;
  const SVG = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const TH = { recovered: RUNS.thresholds.recovered, close: RUNS.thresholds.close };
  const BLOCKS = Q.TOY.blocks;
  const REPS = Q.TOY.steps.reps.reps;
  const SHOTS = [10, 100, 1000, 10000, 100000, 1000000, 0];
  const NS = [20, 100, 200];
  const TABS = [
    ["intro", "Federated learning"],
    ["attack", "One attack"],
    ["reps", "Repetitions"],
    ["restarts", "Restarts"],
    ["shots", "Shots"],
    ["runs", "The paper's runs"],
  ];
  const DEF = { tab: "intro", input: 1, reps: 2, shots: 0, restarts: 10, n: 200, exp: "all", embed: 0 };
  // A search's pace: each restart rolls for ROLL ms, released one after another so the last lands
  // at TOTAL ms; a trail fades for FADE ms after landing. A whole search that starts by itself
  // ends inside five seconds (WCAG 2.2.2), and the transport can pause, step and slow it.
  const PACE = { total: 4500, roll: 1800, fade: 400, trail: 8 };
  const WORD = { recovered: "recovered", close: "close", ambiguous: "another input fits", stuck: "stuck" };
  const embed = new URLSearchParams(location.hash.slice(1)).get("embed") === "1";

  const el = (tag, attrs, parent, text) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) if (v !== undefined && v !== null) n.setAttribute(k, v);
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
  const rad = (v) => (v < 0.001 ? "< 0.001" : v.toFixed(3));
  const circuit = (r) => `${r} × ${BLOCKS / r}`;
  const shotsWord = (s) => (s ? `${s.toLocaleString("en-US")} shots` : "exact gradient");
  const announce = (text) => {
    const s = document.getElementById("status");
    s.textContent = "";
    requestAnimationFrame(() => (s.textContent = text));
  };

  // ---- state in the URL ------------------------------------------------------------------------

  const state = { ...DEF };
  function readHash() {
    const q = new URLSearchParams(location.hash.slice(1));
    const int = (k, lo, hi) => {
      const v = Number.parseInt(q.get(k), 10);
      return Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : DEF[k];
    };
    const tab = q.get("tab");
    state.tab = TABS.some(([t]) => t === tab) ? tab : DEF.tab;
    state.input = int("input", 1, 9999);
    state.reps = REPS.includes(int("reps", 1, 8)) ? int("reps", 1, 8) : DEF.reps;
    const shots = Number.parseInt(q.get("shots"), 10);
    state.shots = SHOTS.includes(shots) ? shots : DEF.shots;
    state.restarts = int("restarts", 1, 20);
    state.n = NS.includes(int("n", 1, 200)) ? int("n", 1, 200) : DEF.n;
    const exp = q.get("exp");
    state.exp = exp === "all" || RUNS.experiments.some((e) => e.id === exp) ? exp : DEF.exp;
    state.embed = embed ? 1 : 0;
  }
  function hashOf(s) {
    const q = new URLSearchParams();
    q.set("tab", s.tab);
    const keys = { attack: ["input", "reps", "shots", "restarts"], reps: ["input", "n", "reps"], restarts: ["input", "restarts", "n"], shots: ["input", "shots", "n"], runs: ["exp"] }[s.tab] || [];
    for (const k of keys) if (s[k] !== DEF[k]) q.set(k, s[k]);
    if (s.embed) q.set("embed", "1");
    return `#${q.toString()}`;
  }
  // Controls replace the history entry; a new tab adds one, so Back returns to the last tab.
  function commit(push) {
    const h = hashOf(state);
    // "Open the full lab" carries the panel's current state.
    for (const a of document.querySelectorAll("a.open-full")) a.href = `index.html${hashOf({ ...state, embed: 0 })}`;
    if (h === location.hash) return;
    if (push) history.pushState(null, "", h);
    else history.replaceState(null, "", h);
  }

  // ---- the Bloch sphere ----------------------------------------------------------------------

  // A single qubit after encoding x is (cos x/2)|0> + (sin x/2)|1> up to the trainable rotations;
  // drawn as the angle round a great circle, so the hidden input, the best guess and every
  // restart's end point sit apart.
  const AZ = -0.38;
  const EL = 0.24;
  const R = 78;
  const BINS = 52;
  function project([x, y, z]) {
    const across = x * Math.cos(AZ) + y * Math.sin(AZ);
    const depth = -x * Math.sin(AZ) + y * Math.cos(AZ);
    const up = z * Math.cos(EL) - depth * Math.sin(EL);
    return [120 + R * across, 120 - R * up];
  }
  const onCircle = (a, k = 1) => project([k * Math.sin(a), 0, k * Math.cos(a)]);
  function ringPath(f) {
    const pts = [];
    for (let i = 0; i <= 64; i++) pts.push(f((Q.TAU * i) / 64));
    return `M${pts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join("L")}`;
  }
  function buildBloch(box) {
    const blurb = "Bloch sphere: the hidden input (ring), the attacker's best guess (dot) and where each restart ended (small dots outside)";
    const s = sv("svg", { viewBox: "0 0 240 240", class: "bloch", role: "img", "aria-label": blurb }, box);
    sv("circle", { cx: 120, cy: 120, r: R, class: "sphere" }, s);
    sv("path", { d: ringPath((t) => project([Math.cos(t), Math.sin(t), 0])), class: "equator" }, s);
    sv("path", { d: ringPath((t) => onCircle(t)), class: "meridian" }, s);
    const [tx, ty] = onCircle(0);
    const [bx, by] = onCircle(Math.PI);
    sv("text", { x: tx - 12, y: ty - 4, class: "pole", "text-anchor": "end" }, s, "|0⟩");
    sv("text", { x: bx - 12, y: by + 20, class: "pole", "text-anchor": "end" }, s, "|1⟩");
    const ends = sv("g", {}, s);
    const truthSpoke = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "truth" }, s);
    const guessSpoke = sv("line", { x1: 120, y1: 120, x2: 120, y2: 120, class: "guess unset" }, s);
    const truth = sv("circle", { r: 10, cx: 120, cy: 120, class: "truth-ring" }, s);
    const guess = sv("circle", { r: 5.5, cx: 120, cy: 120, class: "guess-dot unset" }, s);
    sv("circle", { cx: 120, cy: 120, r: 3.5, class: "hub" }, s);
    return {
      s,
      truth(x) {
        const [px, py] = onCircle(x);
        set(truthSpoke, { x2: px, y2: py });
        set(truth, { cx: px, cy: py });
      },
      // Each landed restart's end, just outside the sphere; several within a few degrees stack
      // outward, so a crowd of landings reads as a taller stack.
      ends(list) {
        ends.textContent = "";
        const stacks = new Map();
        for (const [angle, outcome] of list) {
          const a = ((angle % Q.TAU) + Q.TAU) % Q.TAU;
          const bin = Math.round((a / Q.TAU) * BINS) % BINS;
          const k = stacks.get(bin) || 0;
          stacks.set(bin, k + 1);
          const [ex, ey] = onCircle(a, 1.16 + 0.1 * Math.min(k, 3));
          sv("circle", { cx: ex.toFixed(1), cy: ey.toFixed(1), r: 4, class: `end ${outcome}` }, ends);
        }
      },
      guess(g) {
        const on = g !== null;
        guessSpoke.classList.toggle("unset", !on);
        guess.classList.toggle("unset", !on);
        if (!on) return;
        const [gx, gy] = onCircle(g);
        set(guessSpoke, { x2: gx, y2: gy });
        set(guess, { cx: gx, cy: gy });
      },
      label(text) {
        s.setAttribute("aria-label", `${blurb}. ${text}`);
      },
    };
  }

  // ---- the loss plot -------------------------------------------------------------------------

  const PW = 560;
  const PAD = { l: 14, r: 14, t: 14, b: 40 };
  const SPAN = PW - PAD.l - PAD.r;
  function buildPlot(box, ph) {
    const blurb = "Matching loss across every guess, lowest where a guess's gradient matches the client's";
    const s = sv("svg", { viewBox: `0 0 ${PW} ${ph}`, class: "trace", role: "img", "aria-label": blurb }, box);
    const grid = sv("g", { class: "grid" }, s);
    for (let i = 0; i <= 8; i++) {
      const x = PAD.l + (SPAN * i) / 8;
      sv("line", { x1: x, x2: x, y1: PAD.t, y2: ph - PAD.b }, grid);
    }
    for (let i = 0; i <= 4; i++) {
      const y = PAD.t + ((ph - PAD.t - PAD.b) * i) / 4;
      sv("line", { x1: PAD.l, x2: PW - PAD.r, y1: y, y2: y }, grid);
    }
    [["0", 0], ["π", 0.5], ["2π", 1]].forEach(([t, f]) => {
      sv("text", { x: PAD.l + SPAN * f, y: ph - 14, class: "tick", "text-anchor": f === 0 ? "start" : f === 1 ? "end" : "middle" }, s, t);
    });
    sv("text", { x: PAD.l + SPAN * 0.25, y: ph - 14, class: "axis", "text-anchor": "middle" }, s, "guess →");
    const truth = sv("line", { class: "truth-mark", y1: PAD.t, y2: ph - PAD.b }, s);
    const ghost = sv("path", { class: "curve", "stroke-opacity": 0.25, "stroke-dasharray": "6 5" }, s);
    const curve = sv("path", { class: "curve" }, s);
    const paths = sv("g", { class: "paths" }, s);
    const trails = sv("g", { class: "trails" }, s);
    const balls = sv("g", {}, s);
    const axisPlate = sv("rect", { x: PAD.l + 2, y: PAD.t + 1, width: 170, height: 30, rx: 4, class: "plate" }, s);
    const axis = sv("text", { x: PAD.l + 8, y: PAD.t + 23, class: "axis" }, s, "↑ matching loss");
    const tagPlate = sv("rect", { y: ph - PAD.b - 33, width: 132, height: 30, rx: 4, class: "plate" }, s);
    const tag = sv("text", { y: ph - PAD.b - 11, class: "axis tag" }, s, "hidden input");
    return { s, ph, truth, ghost, curve, paths, trails, balls, tag, tagPlate, axis, axisPlate, blurb };
  }

  // ---- one attack, drawn at any moment of its search -------------------------------------------

  function timing(n) {
    const gap = n > 1 ? Math.min(600, (PACE.total - PACE.roll) / (n - 1)) : 0;
    return { gap, T: (n - 1) * gap + PACE.roll };
  }
  // Attacks already run, kept to the most recent 48, so stepping through inputs stays bounded.
  const cache = new Map();
  function attackOf(input, reps, shots, restarts) {
    const key = `${input}/${reps}/${shots}`;
    let hit = cache.get(key);
    if (hit) cache.delete(key);
    else {
      const c = Q.client(input, reps, BLOCKS / reps, shots);
      hit = { c, runs: [], curve: Q.landscape(c, 240), ghost: shots ? Q.landscape(Q.client(input, reps, BLOCKS / reps, 0), 240) : null };
      if (cache.size >= 48) cache.delete(cache.keys().next().value);
    }
    while (hit.runs.length < restarts) Q.addRestart(hit.c, hit.runs, undefined, TH);
    cache.set(key, hit);
    const runs = hit.runs.slice(0, restarts);
    return { ...hit, runs, best: Q.pickBest(runs, runs.length) };
  }

  // A scope: sphere, loss plot, readouts and (outside embeds) a table of every restart. set()
  // loads an attack; seek(t) draws it at time t of its search, so play, pause, step and scrub
  // all draw through one function and any moment can be revisited.
  function makeScope(box, opts) {
    const panel = el("div", { class: `panel${opts.split ? " split" : ""}` }, box);
    const head = el("div", { class: "panel-head" }, panel);
    const title = el("h3", {}, head);
    // In a slide, beside the paper's figure, the panel says it is the toy.
    if (embed) el("span", { class: "toy-tag" }, title, "Toy");
    title.append(opts.title || "");
    const sub = el("span", { class: "sub" }, head);
    const body = el("div", { class: "p-body" }, panel);
    // One grid: the plot beside the sphere, the readouts under them; a narrow screen puts the
    // plot on its own row and the sphere beside the readouts.
    const scope = el("div", { class: "scope" }, body);
    const bloch = buildBloch(el("div", { class: "s-bloch" }, scope));
    const plot = buildPlot(el("div", { class: "s-plot" }, scope), opts.ph || 190);
    const read = el("div", { class: "readouts" }, scope);
    const main = el("p", { class: "meter main" }, read);
    const mainLabel = el("span", {}, main, "Restarts that found the input");
    const mainValue = el("b", {}, main, "–");
    const minor = el("p", { class: "meter minor" }, read);
    el("span", {}, minor, "Best guess");
    const minorValue = el("b", {}, minor, "–");
    let tbody = null;
    if (!opts.noTable) {
      const det = el("details", { class: "table" }, body);
      if (!opts.closedTable) det.open = true;
      el("summary", {}, det, "Each restart, as a table");
      const t = el("table", { class: "runs" }, el("div", { class: "table-wrap" }, det));
      const hr = el("tr", {}, el("thead", {}, t));
      for (const [h, c] of [["#", ""], ["start", ""], ["end", ""], ["loss", ""], ["from the input", ""], ["outcome", "o"]]) el("th", { scope: "col", class: c || null }, hr, h);
      tbody = el("tbody", {}, t);
    }
    if (opts.extra) opts.extra(panel);

    let A = null;
    let tm = null;
    let pts = [];
    let shape = null;
    let lastLanded = null;
    const half = SPAN / 2;
    const X = (v) => PAD.l + ((((v % Q.TAU) + Q.TAU) % Q.TAU) / Q.TAU) * SPAN;
    const wrapped = (a, b) => Math.abs(a[0] - b[0]) > half;
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

    function load(a, label) {
      A = a;
      sub.textContent = label || "";
      const ph = plot.ph;
      const top = Math.max(...a.curve, ...(a.ghost || [])) || 1;
      const Y = (L) => ph - PAD.b - (Math.min(L, top) / top) * (ph - PAD.t - PAD.b);
      const line = (arr) => `M${Array.from(arr, (L, i) => `${(PAD.l + (i / arr.length) * SPAN).toFixed(1)} ${Y(L).toFixed(1)}`).join("L")}`;
      plot.curve.setAttribute("d", line(a.curve));
      plot.ghost.setAttribute("d", a.ghost ? line(a.ghost) : "");
      const tx = X(a.c.x);
      set(plot.truth, { x1: tx, x2: tx });
      const right = tx < PW / 2;
      set(plot.tag, { x: right ? tx + 8 : tx - 8, "text-anchor": right ? "start" : "end" });
      // Plates fit their labels at whatever size the screen's CSS draws them.
      const tw = plot.tag.getComputedTextLength() + 10;
      set(plot.tagPlate, { x: right ? tx + 3 : tx - 3 - tw, width: tw });
      plot.axisPlate.setAttribute("width", plot.axis.getComputedTextLength() + 12);
      bloch.truth(a.c.x);
      tm = timing(a.runs.length);
      pts = a.runs.map((r) => r.path.map((v, j) => [X(v), Y(r.losses[j])]));
      plot.paths.textContent = "";
      plot.trails.textContent = "";
      plot.balls.textContent = "";
      shape = {
        full: a.runs.map(() => sv("path", { d: "" }, plot.paths)),
        segs: a.runs.map(() => Array.from({ length: PACE.trail }, () => sv("line", { "stroke-opacity": 0 }, plot.trails))),
        balls: a.runs.map(() => sv("circle", { r: 0, class: "ball rolling" }, plot.balls)),
        // Each restart's whole path, drawn once it lands; what each restart showed last frame
        // (-1 not drawn yet, 0 not started, 1 on screen), and whether its trail has faded out.
        d: pts.map(fullPath),
        seen: a.runs.map(() => -1),
        pathOn: a.runs.map(() => null),
        faded: a.runs.map(() => false),
      };
      if (tbody) {
        tbody.textContent = "";
        shape.rows = a.runs.map((r, i) => {
          const tr = el("tr", { class: "wait" }, tbody);
          el("td", {}, tr, String(i + 1));
          el("td", {}, tr, r.start.toFixed(3));
          return { tr, cells: [el("td", {}, tr, "–"), el("td", {}, tr, "–"), el("td", {}, tr, "–"), el("td", { class: "o" }, tr, "waiting")] };
        });
      }
      lastLanded = null;
    }

    // Landing time of restart i, for the transport's tick marks and its step-to-landing keys.
    const landAt = (i) => i * tm.gap + PACE.roll;

    function seek(t) {
      if (!A) return;
      const n = A.runs.length;
      let landed = 0;
      let started = 0;
      let hits = 0;
      const done = t >= tm.T;
      for (let i = 0; i < n; i++) {
        const local = (t - i * tm.gap) / PACE.roll;
        const tr = pts[i];
        const ball = shape.balls[i];
        const r = A.runs[i];
        if (local < 0) {
          if (shape.seen[i] !== 0) {
            shape.seen[i] = 0;
            shape.pathOn[i] = null;
            shape.faded[i] = false;
            ball.setAttribute("r", 0);
            shape.full[i].setAttribute("d", "");
            shape.segs[i].forEach((s) => s.setAttribute("stroke-opacity", 0));
          }
          continue;
        }
        shape.seen[i] = 1;
        started += 1;
        const f = Math.min(1, local) * (tr.length - 1);
        const p = at(tr, f);
        const isLanded = local >= 1;
        if (isLanded) {
          landed += 1;
          if (r.outcome === "recovered") hits += 1;
        }
        set(ball, { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: done && i === A.best ? 9 : 6, class: `ball ${isLanded ? r.outcome : "rolling"}${done && i === A.best ? " best" : ""}` });
        if (shape.pathOn[i] !== isLanded) {
          shape.pathOn[i] = isLanded;
          shape.full[i].setAttribute("d", isLanded ? shape.d[i] : "");
        }
        const fade = reduce ? 0 : local < 1 ? 1 : Math.max(0, 1 - ((local - 1) * PACE.roll) / PACE.fade);
        // A trail that has faded out stays out until the restart is drawn again from earlier on.
        if (fade === 0 && shape.faded[i]) continue;
        shape.faded[i] = fade === 0;
        shape.segs[i].forEach((s, k) => {
          const a = at(tr, Math.max(0, f - k - 1));
          const z = at(tr, Math.max(0, f - k));
          const gone = fade === 0 || wrapped(a, z) || f - k <= 0;
          set(s, { x1: a[0].toFixed(1), y1: a[1].toFixed(1), x2: z[0].toFixed(1), y2: z[1].toFixed(1), "stroke-opacity": gone ? 0 : ((0.75 * (PACE.trail - k)) / PACE.trail) * fade });
        });
      }
      // The parts that change only when a restart lands are redrawn only then.
      const key = done ? -1 : landed * (n + 1) + started;
      if (key === lastLanded) return;
      lastLanded = key;
      const list = A.runs.slice(0, landed).map((r) => [r.end, r.outcome]);
      bloch.ends(list);
      mainLabel.textContent = done ? "Restarts that found the input" : "Restarts that found the input, so far";
      mainValue.textContent = `${hits} of ${done ? n : landed}`;
      if (shape.rows) {
        shape.rows.forEach((row, i) => {
          const r = A.runs[i];
          const local = (t - i * tm.gap) / PACE.roll;
          const isLanded = local >= 1;
          row.tr.className = isLanded ? (done && i === A.best ? "best" : "") : "wait";
          row.cells[0].textContent = isLanded ? r.end.toFixed(3) : "–";
          row.cells[1].textContent = isLanded ? r.loss.toExponential(2) : "–";
          row.cells[2].textContent = isLanded ? `${rad(r.error)} rad` : "–";
          row.cells[3].textContent = "";
          if (isLanded) {
            el("i", { class: `end ${r.outcome}`, style: `background: var(--${r.outcome === "recovered" ? "leak" : r.outcome === "close" ? "leak-tint" : r.outcome === "ambiguous" ? "held-tint" : "open"}); box-shadow: inset 0 0 0 1.5px var(--${r.outcome === "ambiguous" ? "held" : r.outcome === "stuck" ? "muted" : "leak"})` }, row.cells[3]);
            row.cells[3].append(WORD[r.outcome] + (done && i === A.best ? ", best fit" : ""));
          } else row.cells[3].textContent = local >= 0 ? "rolling" : "waiting";
        });
      }
      if (done) {
        const b = A.runs[A.best];
        bloch.guess(b.end);
        minorValue.textContent = `${WORD[b.outcome]}, ${rad(b.error)} rad`;
        const words = `${hits} of ${n} restarts found the hidden input; the best fit is ${rad(b.error)} radians from it (${WORD[b.outcome]}).`;
        bloch.label(words);
        plot.s.setAttribute("aria-label", `${plot.blurb}. ${words}`);
        if (opts.onDone) opts.onDone(words);
      } else {
        bloch.guess(null);
        minorValue.textContent = "–";
      }
    }

    return {
      title,
      load,
      seek,
      get T() {
        return tm ? tm.T : 0;
      },
      landings() {
        return A ? A.runs.map((r, i) => [landAt(i), r.outcome === "recovered"]) : [];
      },
    };
  }

  // ---- the transport: play, pause, step, scrub, speed -----------------------------------------

  // One transport drives one or more scopes on one clock. A step is one drawn point of a path
  // (three of the attack's 150 optimiser steps); Shift steps to the next or previous landing.
  const STEP = PACE.roll / 50;
  // The shown view's transport takes the keys; one listener, so rebuilt views leave none behind.
  let activeKeys = null;
  document.addEventListener("keydown", (e) => activeKeys && activeKeys(e));
  function makeTransport(box, scopes, opts = {}) {
    const wrap = el("div", { class: "transport" }, box);
    const keys = el("div", { class: "keys" }, wrap);
    const play = el("button", { class: "btn", type: "button", "aria-label": "Play" }, keys, "▶ Play");
    const back = el("button", { class: "btn icon", type: "button", "aria-label": "Step back" }, keys, "◀");
    const fwd = el("button", { class: "btn icon", type: "button", "aria-label": "Step forward" }, keys, "▶");
    const scrubBox = el("div", { class: "scrub" }, wrap);
    const marks = el("div", { class: "landings", "aria-hidden": "true" }, scrubBox);
    const scrub = el("input", { type: "range", min: 0, max: 100, step: 1, value: 0, "aria-label": "Time in the search" }, scrubBox);
    const clock = el("div", { class: "clock" }, wrap);
    const where = el("span", {}, clock);
    const right = el("span", {}, clock);
    const speedBox = el("span", { class: "seg", role: "group", "aria-label": "Speed" }, right);
    const speeds = [0.25, 0.5, 1].map((v) => {
      const b = el("button", { type: "button", "aria-pressed": String(v === 1) }, speedBox, v === 1 ? "1×" : v === 0.5 ? "½×" : "¼×");
      b.addEventListener("click", () => {
        speed = v;
        speeds.forEach(([x, bb]) => bb.setAttribute("aria-pressed", String(x === v)));
      });
      return [v, b];
    });
    let t = 0;
    let T = 0;
    let speed = 1;
    let playing = false;
    let raf = 0;
    let last = 0;
    let stepTimer = 0;
    const ticks = () => Math.max(1, Math.round(T / STEP));
    let lastWhere = "";
    const secs = (v) => (v / 1000).toFixed(1);
    const valueText = () => `${secs(t)} of ${secs(T)} seconds; ${where.textContent}`;
    function draw() {
      scopes.forEach((s) => s.seek(t));
      scrub.value = String(Math.round(t / STEP));
      const land = scopes[0].landings();
      const landed = land.filter(([at]) => at <= t).length;
      const rolling = land.findIndex(([at]) => at > t && at - PACE.roll <= t);
      let bold = `${landed} of ${land.length} landed`;
      let rest = "";
      if (t >= T) bold = "Search finished";
      else if (rolling >= 0) {
        const k = Math.round(((t - (land[rolling][0] - PACE.roll)) / PACE.roll) * 150);
        bold = `Restart ${rolling + 1} of ${land.length} rolling`;
        rest = `, optimiser step ${Math.min(150, Math.max(0, k))} of 150; ${landed} landed`;
      }
      if (bold + rest !== lastWhere) {
        lastWhere = bold + rest;
        where.textContent = "";
        el("b", {}, where, bold);
        if (rest) where.append(rest);
      }
      // While it plays, the scrubber is not re-announced every frame.
      if (!playing) scrub.setAttribute("aria-valuetext", valueText());
      const clockText = `${secs(t)} s of ${secs(T)} s `;
      if (right.firstChild?.nodeType === 3) right.firstChild.textContent = clockText;
      else right.prepend(clockText);
    }
    function setPlaying(on) {
      playing = on;
      play.textContent = on ? "❚❚ Pause" : t >= T ? "↺ Replay" : "▶ Play";
      play.setAttribute("aria-label", on ? "Pause" : t >= T ? "Replay" : "Play");
      cancelAnimationFrame(raf);
      clearTimeout(stepTimer);
      if (!on) {
        scrub.setAttribute("aria-valuetext", valueText());
        return;
      }
      if (t >= T) t = 0;
      if (reduce) {
        // No motion: each press of play shows the search one landing at a time.
        const land = scopes[0].landings().map(([at]) => at);
        const tick = () => {
          const nextAt = land.find((at) => at > t + 1e-6);
          t = nextAt === undefined ? T : nextAt;
          draw();
          if (t >= T) setPlaying(false);
          else stepTimer = setTimeout(tick, 900 / speed);
        };
        tick();
        return;
      }
      last = performance.now();
      const frame = (now) => {
        t = Math.min(T, t + Math.max(0, now - last) * speed);
        last = now;
        draw();
        if (t >= T) setPlaying(false);
        else raf = requestAnimationFrame(frame);
      };
      raf = requestAnimationFrame(frame);
    }
    function goto(v) {
      setPlaying(false);
      t = Math.max(0, Math.min(T, v));
      draw();
      setPlaying(false);
    }
    function stepLanding(dir) {
      const land = scopes[0].landings().map(([at]) => at);
      const target = dir > 0 ? land.find((at) => at > t + 1e-6) : [...land].reverse().find((at) => at < t - 1e-6);
      goto(target === undefined ? (dir > 0 ? T : 0) : target);
    }
    play.addEventListener("click", () => setPlaying(!playing));
    back.addEventListener("click", (e) => (e.shiftKey ? stepLanding(-1) : goto(t - STEP)));
    fwd.addEventListener("click", (e) => (e.shiftKey ? stepLanding(1) : goto(t + STEP)));
    scrub.addEventListener("input", () => goto(Number(scrub.value) * STEP));
    // Keys anywhere in the view, or with nothing focused: Space plays and pauses, arrows step,
    // Shift+arrows jump to the next landing, Home and End go to the ends. Keys typed into a
    // control, and Space on a button, link or disclosure, keep their own meaning.
    const view = opts.keyScope || box;
    function onKey(e) {
      if (e.defaultPrevented || !(e.target === document.body || view.contains(e.target))) return;
      const tag = e.target.tagName;
      if (e.target !== scrub && (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA")) return;
      if (e.key === " " && (tag === "SUMMARY" || tag === "A")) return;
      if (e.key === " " && tag !== "BUTTON") {
        e.preventDefault();
        setPlaying(!playing);
      } else if ((e.key === "ArrowLeft" || e.key === "ArrowRight") && (e.target === scrub || tag !== "BUTTON" || e.target.closest(".keys"))) {
        e.preventDefault();
        const dir = e.key === "ArrowRight" ? 1 : -1;
        if (e.shiftKey) stepLanding(dir);
        else goto(t + dir * STEP);
      } else if (e.key === "Home" || e.key === "End") {
        if (e.target === scrub || tag !== "INPUT") {
          e.preventDefault();
          goto(e.key === "Home" ? 0 : T);
        }
      }
    }
    return {
      // Load new attacks into the scopes and start from the beginning: motion starts by itself
      // only when asked (autoplay) and never under reduced motion, which shows the end.
      restart(autoplay) {
        T = Math.max(...scopes.map((s) => s.T));
        scrub.max = String(ticks());
        marks.textContent = "";
        for (const [at, hit] of scopes[0].landings()) {
          const i = el("i", { class: hit ? "hit" : "" }, marks);
          i.style.left = `${(100 * at) / T}%`;
        }
        t = autoplay && !reduce ? 0 : T;
        activeKeys = onKey;
        draw();
        setPlaying(Boolean(autoplay && !reduce));
      },
      stop() {
        setPlaying(false);
        if (activeKeys === onKey) activeKeys = null;
      },
      get playing() {
        return playing;
      },
    };
  }

  // ---- many hidden inputs: the toy's own trend ------------------------------------------------

  // Runs a step's tally over hidden inputs 1 to n in a Worker, or on this thread a frame's
  // budget at a time where a Worker cannot start (a page opened from a file).
  let worker = null;
  let workerOk = location.protocol !== "file:";
  let jobId = 0;
  // One job runs at a time, for whichever view started it last; starting another cancels it.
  let cancelCurrent = null;
  // If the Worker fails mid-job, the job carries on here from the next hidden input.
  let onWorkerError = null;
  function startWorker() {
    if (!workerOk || worker) return worker;
    try {
      worker = new Worker("worker.js");
      worker.addEventListener("error", (e) => {
        e.preventDefault();
        workerOk = false;
        worker.terminate();
        worker = null;
        const resume = onWorkerError;
        onWorkerError = null;
        if (resume) resume();
      });
    } catch {
      workerOk = false;
      worker = null;
    }
    return worker;
  }
  // Returns the job's cancel function; isCurrent(cancel) says whether that job is still running.
  function tallyRun(step, n, onScore, onDone) {
    if (cancelCurrent) cancelCurrent();
    const id = ++jobId;
    let seed = 1;
    let raf = 0;
    let handler = null;
    const w = startWorker();
    const cancel = () => {
      cancelAnimationFrame(raf);
      // The Worker stops this job too, rather than finishing it for nobody.
      if (handler && w) {
        w.removeEventListener("message", handler);
        w.postMessage({ cancel: id });
      }
      handler = null;
      if (onWorkerError === onThread) onWorkerError = null;
      if (cancelCurrent === cancel) cancelCurrent = null;
    };
    const finish = () => {
      cancel();
      onDone();
    };
    function onThread() {
      if (handler && w) w.removeEventListener("message", handler);
      handler = null;
      let jobs = seed <= n ? Q.tallyJobs(step, seed) : [];
      const tick = () => {
        if (id !== jobId) return;
        const until = performance.now() + 8;
        while (seed <= n && performance.now() < until) {
          const j = jobs.find((x) => x.runs.length < x.n);
          if (j) {
            Q.addRestart(j.c, j.runs, undefined, TH);
            continue;
          }
          onScore(seed, Q.tallyScore(step, jobs, TH));
          seed += 1;
          if (seed <= n) jobs = Q.tallyJobs(step, seed);
        }
        if (seed > n) finish();
        else raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }
    cancelCurrent = cancel;
    if (w) {
      handler = (e) => {
        if (e.data.id !== id) return;
        if (e.data.done) finish();
        else {
          onScore(e.data.seed, e.data.scores);
          seed = e.data.seed + 1;
        }
      };
      w.addEventListener("message", handler);
      onWorkerError = onThread;
      w.postMessage({ id, step, from: 1, to: n, th: TH });
    } else onThread();
    return cancel;
  }
  const isCurrent = (cancel) => cancel !== null && cancelCurrent === cancel;

  // The rows: one per value of the step's control, one mark per hidden input, a count on the
  // right, laid out like the paper's figure beside them.
  const TOY_R = Q.TOY.steps.reps.restarts;
  const SHOT_STEP = Q.TOY.steps.shots;
  const ROWSPEC = {
    reps: { head: ["r × ℓ", `restarts of ${TOY_R} that found it, a pie per input`], values: Q.TOY.steps.reps.reps, label: (r) => `${r}×${BLOCKS / r}`, of: (n) => n * TOY_R },
    restarts: { head: ["restarts", "inputs recovered by the best restart"], values: Q.TOY.steps.restarts.restarts, label: String, of: (n) => n },
    shots: { head: ["shots", `inputs guessed within ${TH.close} rad`], values: Q.TOY.steps.shots.shots, label: (v) => (v ? v.toLocaleString("en-US") : "exact"), of: (n) => n },
  };
  function makeDraws(box, step, opts) {
    const spec = ROWSPEC[step];
    const fig = el("figure", { class: "strip-fig toy" }, box);
    const cap = el("figcaption", {}, fig);
    el("b", {}, cap, "The toy, many draws");
    const capText = el("span", {}, cap);
    const grid = el("div", { class: "strips", role: "img" }, fig);
    const progress = el("p", { class: "progress", "aria-live": "off" }, fig);
    let stop = null;
    let rows = [];
    let csv = [];
    let n = 0;
    let lastHere = [null, 0];
    let complete = false;
    function build(count) {
      n = count;
      complete = false;
      capText.textContent = ` 1 qubit, hidden inputs 1 to ${n}, not picked. ${opts.fixed}.`;
      grid.textContent = "";
      el("span", { class: "hd" }, grid, spec.head[0]);
      el("span", { class: "hd" }, grid, spec.head[1]);
      el("span", { class: "hd cnt" }, grid, `of ${spec.of(n)}`);
      rows = spec.values.map((v) => {
        const lab = el("span", { class: "lab" }, grid, spec.label(v));
        const dots = el("span", { class: `dots${n > 20 ? " many" : ""}` }, grid);
        const marks = Array.from({ length: n }, () => el("i", { class: "pending" }, dots));
        const cnt = el("span", { class: "cnt" }, grid, "–");
        return { v, lab, marks, cnt, total: 0, done: 0 };
      });
      csv = [];
      here(...lastHere);
    }
    function run(count) {
      if (stop) stop();
      build(count);
      progress.textContent = `Running hidden inputs 1 to ${n}…`;
      const t0 = performance.now();
      stop = tallyRun(
        step,
        n,
        (seed, scores) => {
          scores.forEach((s, i) => {
            const row = rows[i];
            const m = row.marks[seed - 1];
            m.classList.remove("pending");
            if (step === "reps") {
              m.dataset.f = "1";
              m.style.setProperty("--f", String(s / TOY_R));
            } else m.classList.toggle("hit", Boolean(s));
            row.total += Number(s);
            row.done += 1;
            row.cnt.textContent = String(row.total);
          });
          csv.push([seed, ...scores.map(Number)]);
          progress.textContent = `Hidden inputs run: ${seed} of ${n}`;
        },
        () => {
          const secs = ((performance.now() - t0) / 1000).toFixed(1);
          const words = rows.map((r) => `${spec.label(r.v)}: ${r.total}`).join("; ");
          grid.setAttribute("aria-label", `The toy over hidden inputs 1 to ${n}, ${spec.head[1]}, of ${spec.of(n)}: ${words}`);
          progress.textContent = `${n} hidden inputs in ${secs} s${worker ? ", in a background thread" : ""}.`;
          stop = null;
          complete = true;
        },
      );
    }
    function here(value, input) {
      lastHere = [value, input];
      rows.forEach((r) => {
        const on = r.v === value;
        r.lab.classList.toggle("on", on);
        r.marks.forEach((m, d) => m.classList.toggle("here", on && d === input - 1));
      });
    }
    return {
      run,
      here,
      // Finished, or still running: another view's job cancels this one, and showing it again reruns it.
      settled: () => complete || isCurrent(stop),
      count: () => n,
      csv() {
        const header = ["input", ...spec.values.map((v) => `${spec.head[0]} ${spec.label(v)}`)].join(",");
        return [header, ...csv.sort((a, b) => a[0] - b[0]).map((r) => r.join(","))].join("\n");
      },
      stop() {
        if (stop) stop();
        stop = null;
      },
    };
  }

  // ---- the paper's runs: drawn from the frozen bundle -------------------------------------------

  const COL = Object.fromEntries(RUNS.columns.map((c, i) => [c, i]));
  const row = (r) => Object.fromEntries(RUNS.columns.map((c, i) => [c, r[i]]));
  const ALL = RUNS.rows.map(row);

  // A strip of the paper's seeds: one mark per seed, filled by its outcome, as in its figures.
  function paperStrips(box, title, sub, groups, opts = {}) {
    const fig = el("figure", { class: "strip-fig paper" }, box);
    const cap = el("figcaption", {}, fig);
    el("b", {}, cap, title);
    cap.append(sub);
    const grid = el("div", { class: "strips" }, fig);
    el("span", { class: "hd" }, grid, opts.keyHead || "circuit");
    el("span", { class: "hd" }, grid, opts.dotHead || "seeds, best of the restarts");
    el("span", { class: "hd cnt" }, grid, opts.countHead || "recovered");
    for (const g of groups) {
      el("span", { class: "lab" }, grid, g.label);
      const dots = el("span", { class: "dots", role: "img", "aria-label": `${g.label}: ${g.words}` }, grid);
      for (const r of g.rows) el("i", { class: opts.cls ? opts.cls(r) : r.best, title: `seed ${r.seed}: ${WORD[r.best]}, ${rad(r.error)} rad` }, dots);
      el("span", { class: "cnt" }, grid, g.count);
    }
    const key = el("p", { class: "key" }, fig);
    for (const [c, w] of opts.key || [["recovered", "recovered"], ["close", "close"], ["ambiguous", "another input fits"], ["", "stuck"]]) {
      const s = el("span", {}, key);
      el("i", { class: c }, s);
      s.append(w);
    }
    return fig;
  }
  const bySetting = (rows, keyf) => {
    const m = new Map();
    for (const r of rows) {
      const k = keyf(r);
      if (!m.has(k)) m.set(k, []);
      m.get(k).push(r);
    }
    for (const v of m.values()) v.sort((a, b) => a.seed - b.seed);
    return m;
  };
  const count = (rows, f) => rows.filter(f).length;
  const lettersHit = (r) => [...r.outcomes].filter((c) => c === "r").length;

  // ---- downloads ----------------------------------------------------------------------------

  function download(name, text, type) {
    const a = el("a", { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 0);
  }
  const csvCell = (v) => (v === null || v === undefined ? "" : /[",\r\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  const paperCsv = () => [RUNS.columns.join(","), ...RUNS.rows.map((r) => r.map(csvCell).join(","))].join("\n");

  // ---- controls --------------------------------------------------------------------------------

  function inputPicker(box, onChange) {
    const k = el("div", { class: "knob" }, box);
    const id = `in-${Math.random().toString(36).slice(2, 8)}`;
    el("label", { for: id }, k, "Hidden input (seed)");
    const row = el("div", { class: "stepper" }, k);
    const prev = el("button", { class: "btn icon", type: "button", "aria-label": "Previous hidden input" }, row, "−");
    const num = el("input", { id, type: "number", min: 1, max: 9999, step: 1, value: state.input, inputmode: "numeric" }, row);
    const next = el("button", { class: "btn icon", type: "button", "aria-label": "Next hidden input" }, row, "+");
    const rnd = el("button", { class: "btn rand", type: "button" }, row, "Random");
    const go = (v) => {
      state.input = Math.min(9999, Math.max(1, v | 0 || 1));
      num.value = state.input;
      onChange();
    };
    prev.addEventListener("click", () => go(state.input - 1));
    next.addEventListener("click", () => go(state.input + 1));
    rnd.addEventListener("click", () => go(1 + Math.floor(Math.random() * 9999)));
    num.addEventListener("change", () => go(Number(num.value)));
    return { sync: () => (num.value = state.input) };
  }
  function selectKnob(box, label, values, value, text, onChange, cls) {
    const k = el("div", { class: `knob${cls ? ` ${cls}` : ""}` }, box);
    const id = `sel-${Math.random().toString(36).slice(2, 8)}`;
    el("label", { for: id }, k, label);
    const s = el("select", { id }, k);
    for (const v of values) el("option", { value: v }, s, text(v));
    s.value = String(value);
    s.addEventListener("change", () => {
      onChange(Number(s.value));
      // In a slide, the clicker's arrows go back to the deck once a value is picked.
      if (embed) s.blur();
    });
    // Tabs share the state, so a view shown again first shows the current value.
    s.sync = (v) => (s.value = String(v));
    return s;
  }
  function rangeKnob(box, label, min, max, value, text, onChange) {
    const k = el("div", { class: "knob range" }, box);
    const id = `rng-${Math.random().toString(36).slice(2, 8)}`;
    const top = el("div", { class: "row" }, k);
    el("label", { for: id }, top, label);
    const out = el("output", { for: id }, top, text(value));
    const r = el("input", { id, type: "range", min, max, step: 1, value }, k);
    r.setAttribute("aria-valuetext", text(value));
    r.addEventListener("input", () => {
      out.textContent = text(Number(r.value));
      r.setAttribute("aria-valuetext", out.textContent);
      onChange(Number(r.value));
    });
    r.sync = (v) => {
      r.value = String(v);
      out.textContent = text(v);
      r.setAttribute("aria-valuetext", out.textContent);
    };
    return r;
  }
  function segKnob(box, label, values, value, text, onChange) {
    const k = el("div", { class: "knob" }, box);
    el("span", {}, k, label);
    const g = el("span", { class: "seg", role: "group", "aria-label": label }, k);
    const bs = values.map((v) => {
      const b = el("button", { type: "button", "aria-pressed": String(v === value) }, g, text(v));
      b.addEventListener("click", () => {
        bs.forEach(([x, bb]) => bb.setAttribute("aria-pressed", String(x === v)));
        onChange(v);
      });
      return [v, b];
    });
    return { sync: (v) => bs.forEach(([x, bb]) => bb.setAttribute("aria-pressed", String(x === v))) };
  }

  // ---- views -----------------------------------------------------------------------------------

  const views = {};
  // Coalesce bursts of control events (a slider drag) into one recompute per frame.
  const debounced = (f) => {
    let q = 0;
    return () => {
      if (!q) q = requestAnimationFrame(() => ((q = 0), f()));
    };
  };
  const intro = (box, text) => el("p", { class: "lede" }, box, text);
  const openFull = (box) => {
    if (!embed) return;
    const s = { ...state, embed: 0 };
    el("a", { class: "open-full", href: `index.html${hashOf(s)}`, target: "_blank", rel: "noopener" }, box, "Open the full lab ↗");
  };

  views.attack = (box) => {
    el("h2", {}, box, "One attack, step by step");
    intro(box, "Pick a hidden input and a circuit. The attacker starts restarts from different guesses and lets each roll downhill on the matching loss. Pause on a wrong dip, step it forward, then add restarts until one reaches the input.");
    const knobs = el("div", { class: "knobs" }, box);
    const picker = inputPicker(knobs, () => update(true));
    const repsK = selectKnob(knobs, "Circuit, r × ℓ", REPS, state.reps, (r) => `${circuit(r)}${r === 1 ? " (1 repetition)" : ` (${r} repetitions)`}`, (v) => ((state.reps = v), update(true)));
    const shotsK = selectKnob(knobs, "Shots per expectation value", SHOTS, state.shots, shotsWord, (v) => ((state.shots = v), update(true)));
    const restartsK = rangeKnob(knobs, "Restarts", 1, 20, state.restarts, (v) => `${v} restart${v === 1 ? "" : "s"}`, (v) => ((state.restarts = v), later()));
    const bench = el("div", { class: "bench" }, box);
    const scope = makeScope(bench, { title: "The toy circuit", onDone: announce, split: true });
    const tp = makeTransport(box, [scope], { keyScope: box });
    const later = debounced(() => update(false));
    function update(autoplay) {
      picker.sync();
      repsK.sync(state.reps);
      shotsK.sync(state.shots);
      restartsK.sync(state.restarts);
      commit(false);
      scope.load(attackOf(state.input, state.reps, state.shots, state.restarts), `hidden input ${state.input}; ${circuit(state.reps)}; ${shotsWord(state.shots)}`);
      tp.restart(autoplay);
    }
    return { show: () => update(true), hide: () => tp.stop() };
  };

  views.reps = (box) => {
    el("h2", {}, box, "More encoding repetitions, same parameter count");
    intro(box, `Both circuits have ${BLOCKS} trainable blocks: one repetition of ${BLOCKS}, or ${BLOCKS} repetitions of one. More repetitions put more frequencies in the loss, so it has more dips for a restart to get stuck in (Kumar et al., 2023). The same hidden input runs on both, on one clock.`);
    const knobs = el("div", { class: "knobs" }, box);
    const picker = inputPicker(knobs, () => update(true));
    if (embed) return repsEmbed(box, knobs, picker);
    const bench = el("div", { class: "bench" }, box);
    const lo = makeScope(bench, { title: `1 repetition × ${BLOCKS} blocks`, closedTable: true });
    const hi = makeScope(bench, { title: `${BLOCKS} repetitions × 1 block`, closedTable: true, onDone: (w) => announce(`${circuit(BLOCKS)}: ${w}`) });
    const tp = makeTransport(box, [lo, hi], { keyScope: box });
    const draws = drawsSection(box, "reps", `${TOY_R} restarts, exact gradients`, paperReps);
    function update(autoplay) {
      picker.sync();
      commit(false);
      lo.load(attackOf(state.input, 1, 0, TOY_R), `hidden input ${state.input}`);
      hi.load(attackOf(state.input, BLOCKS, 0, TOY_R), `hidden input ${state.input}`);
      tp.restart(autoplay);
      draws.here(null, state.input);
    }
    return { show: () => (update(true), draws.ensure()), hide: () => tp.stop() };
  };

  // Inside a slide there is room for one panel: the repetitions are its free control.
  function repsEmbed(box, knobs, picker) {
    const repsK = segKnob(knobs, "Circuit, r × ℓ", REPS, state.reps, circuit, (v) => ((state.reps = v), update(true)));
    const bench = el("div", { class: "bench" }, box);
    const scope = makeScope(bench, { title: `1 qubit, ${TOY_R} restarts, exact gradients`, onDone: announce, noTable: true });
    const tp = makeTransport(box, [scope], { keyScope: box });
    const draws = drawsSection(box, "reps", `${TOY_R} restarts, exact gradients`, paperReps);
    function update(autoplay) {
      picker.sync();
      repsK.sync(state.reps);
      commit(false);
      scope.load(attackOf(state.input, state.reps, 0, TOY_R), `hidden input ${state.input}; ${circuit(state.reps)}`);
      tp.restart(autoplay);
      draws.here(state.reps, state.input);
    }
    return { show: () => (update(true), draws.ensure()), hide: () => tp.stop() };
  }

  views.restarts = (box) => {
    el("h2", {}, box, "Stuck is not private: add restarts");
    intro(box, "The attacker never sees the hidden input, but it can tell which restart fits best: the one with the lowest matching loss. So a stuck restart only costs time. Add restarts until one reaches the input.");
    const knobs = el("div", { class: "knobs" }, box);
    const picker = inputPicker(knobs, () => update(true));
    const restartsK = rangeKnob(knobs, "Restarts", 1, 20, state.restarts, (v) => `${v} restart${v === 1 ? "" : "s"}`, (v) => ((state.restarts = v), later()));
    const bench = el("div", { class: "bench" }, box);
    const R = Q.TOY.steps.restarts.reps;
    const scope = makeScope(bench, { title: `${R} repetitions × ${BLOCKS / R} block${BLOCKS / R === 1 ? "" : "s"}, exact gradients`, onDone: announce, split: !embed, noTable: embed });
    const tp = makeTransport(box, [scope], { keyScope: box });
    const draws = drawsSection(box, "restarts", `${circuit(R)}, exact gradients`, paperBudget);
    const later = debounced(() => update(false));
    function update(autoplay) {
      picker.sync();
      restartsK.sync(state.restarts);
      commit(false);
      scope.load(attackOf(state.input, R, 0, state.restarts), `hidden input ${state.input}; ${state.restarts} restart${state.restarts === 1 ? "" : "s"}`);
      tp.restart(autoplay);
      draws.here(Q.TOY.steps.restarts.restarts.includes(state.restarts) ? state.restarts : null, state.input);
    }
    return { show: () => (update(true), draws.ensure()), hide: () => tp.stop() };
  };

  views.shots = (box) => {
    el("h2", {}, box, "Shot noise: gradients from measurements");
    intro(box, "On a device each expectation value is estimated from shots, so the client's gradient is noisy. The dashed curve is the loss with the exact gradient; the solid one is what the attacker matches against. Fewer shots lift and shift the dip.");
    const knobs = el("div", { class: "knobs" }, box);
    const picker = inputPicker(knobs, () => update(true));
    const shotsK = selectKnob(knobs, "Shots per expectation value", SHOTS, state.shots, shotsWord, (v) => ((state.shots = v), update(true)));
    const bench = el("div", { class: "bench" }, box);
    const scope = makeScope(bench, { title: `${SHOT_STEP.reps} repetitions × ${BLOCKS / SHOT_STEP.reps} blocks, ${SHOT_STEP.restarts} restarts`, onDone: announce, split: !embed, noTable: embed });
    const tp = makeTransport(box, [scope], { keyScope: box });
    const draws = drawsSection(box, "shots", `${circuit(SHOT_STEP.reps)}, ${SHOT_STEP.restarts} restarts`, paperShots);
    function update(autoplay) {
      picker.sync();
      shotsK.sync(state.shots);
      commit(false);
      scope.load(attackOf(state.input, SHOT_STEP.reps, state.shots, SHOT_STEP.restarts), `hidden input ${state.input}; ${shotsWord(state.shots)}`);
      tp.restart(autoplay);
      draws.here(Q.TOY.steps.shots.shots.includes(state.shots) ? state.shots : null, state.input);
    }
    return { show: () => (update(true), draws.ensure()), hide: () => tp.stop() };
  };

  // The many-draw rows and, beside them, the paper's rows for the same question.
  function drawsSection(box, step, fixed, paperFig) {
    const sec = el("section", { class: "draws", "aria-label": "Many hidden inputs" }, box);
    const head = el("div", { class: "draws-head" }, sec);
    el("h3", {}, head, "One input is a noisy sample; many show the trend");
    const tools = el("div", { class: "knobs" }, head);
    let nK = null;
    if (!embed) {
      nK = segKnob(tools, "Hidden inputs", NS, state.n, String, (v) => {
        state.n = v;
        commit(false);
        d.run(v);
      });
      const b = el("button", { class: "btn", type: "button" }, tools, "Download rows (CSV)");
      b.addEventListener("click", () => download(`qfl-toy-${step}-inputs-1-${state.n}.csv`, d.csv(), "text/csv"));
    } else openFull(head);
    const pair = el("div", { class: "pair" }, sec);
    const d = makeDraws(pair, step, { fixed });
    if (!embed) paperFig(pair);
    return {
      // Shown again: the rows match the shared count (another tab may have changed it), and a
      // job another view cancelled runs again.
      ensure() {
        const want = embed ? Q.TOY.draws : state.n;
        if (nK) nK.sync(state.n);
        if (!d.settled() || d.count() !== want) d.run(want);
      },
      here: (v, input) => d.here(v, input),
    };
  }

  // The paper's settings and lines, read from the bundle and picked as figures.py picks them.
  const PS = RUNS.settings;
  const plain = (r) => r.shots === 0 && r.batch === 1;
  const most = (rows, f) => Math.max(...rows.map(f));
  function paperReps(box) {
    // The figure's line: the most qubits and the most trainable blocks, so the parameter count is
    // fixed while the repetitions vary.
    const rq1 = ALL.filter((r) => r.exp === "rq1" && plain(r));
    const n = most(rq1, (r) => r.qubits);
    const top = most(rq1, (r) => r.reps * r.layers);
    const rows = rq1.filter((r) => r.qubits === n && r.reps * r.layers === top);
    const groups = [...bySetting(rows, (r) => `${r.reps}×${r.layers}`)].map(([k, rs]) => ({
      label: k,
      rows: rs,
      count: `${count(rs, (r) => r.best === "recovered")}, hits ${rs.reduce((a, r) => a + lettersHit(r), 0)}`,
      words: `${count(rs, (r) => r.best === "recovered")} of ${rs.length} seeds recovered`,
    }));
    const tries = PS.seeds * PS.restarts;
    paperStrips(box, "The paper", ` ${n} qubits, the same parameter count on each line, ${PS.seeds} seeds, ${PS.restarts} restarts each. Hits: restarts of ${tries} that found the input.`, groups, { countHead: "recovered, hits" });
  }
  function paperBudget(box) {
    const rows = ALL.filter((r) => r.exp === "budget" && plain(r));
    const n = most(rows, (r) => r.qubits);
    const [few, many] = [PS.restarts, PS.budgetRestarts];
    const cls = (r) => (r.bestSmall === "recovered" ? "recovered" : r.best === "recovered" ? "close" : "");
    const groups = [...bySetting(rows, (r) => `${r.reps}×${r.layers}`)].map(([k, rs]) => ({
      label: k,
      rows: rs,
      count: `${count(rs, (r) => r.bestSmall === "recovered")}→${count(rs, (r) => r.best === "recovered")}`,
      words: `${count(rs, (r) => r.bestSmall === "recovered")} recovered with ${few} restarts, ${count(rs, (r) => r.best === "recovered")} with ${many}`,
    }));
    paperStrips(box, "The paper", ` the hardest ${n}-qubit circuits, ${PS.seeds} seeds, rerun with ${many} restarts.`, groups, {
      cls,
      countHead: `${few}→${many}`,
      key: [["recovered", `with ${few} restarts`], ["close", `only with ${many}`], ["", "neither"]],
    });
  }
  function paperShots(box) {
    const fig = el("div", {}, box);
    const shotsList = [...new Set(ALL.filter((r) => r.exp === "rq2").map((r) => r.shots))].sort((a, b) => a - b);
    let s = shotsList[0];
    const draw = () => {
      fig.textContent = "";
      const tools = el("div", { class: "knobs" }, fig);
      segKnob(tools, "The paper's shots", shotsList, s, (v) => v.toLocaleString("en-US"), (v) => ((s = v), draw()));
      const rows = ALL.filter((r) => r.exp === "rq2" && r.shots === s);
      const within = (r) => r.best === "recovered" || r.best === "close";
      const groups = [...bySetting(rows, (r) => `${r.qubits}q ${r.reps}×${r.layers}`)].map(([k, rs]) => ({ label: k, rows: rs, count: String(count(rs, within)), words: `${count(rs, within)} of ${rs.length} seeds within ${TH.close} rad` }));
      paperStrips(fig, "The paper", ` ${s.toLocaleString("en-US")} shots per expectation value, ${PS.seeds} seeds.`, groups, {
        cls: (r) => (within(r) ? "recovered" : ""),
        countHead: `within ${TH.close} rad`,
        key: [["recovered", `guessed within ${TH.close} rad`], ["", "not"]],
      });
    };
    draw();
  }

  views.runs = (box) => {
    el("h2", {}, box, "Every run the paper made");
    intro(box, `${RUNS.rows.length.toLocaleString("en-US")} attacks from the paper's results, each a dot: one seed (its own hidden input and angles), filled by its best restart's outcome. Every seed of every setting is here, as figures.py scored it from the paper's results. Pick a dot to read its restarts.`);
    const tools = el("div", { class: "knobs" }, box);
    const chips = el("div", { class: "filters", role: "group", "aria-label": "Experiments" }, tools);
    const dl = el("div", { class: "stepper" }, tools);
    el("button", { class: "btn", type: "button" }, dl, "Download all (CSV)").addEventListener("click", () => download("qfl-privacy-runs.csv", paperCsv(), "text/csv"));
    el("button", { class: "btn", type: "button" }, dl, "Download all (JSON)").addEventListener("click", () => download("qfl-privacy-runs.json", JSON.stringify(RUNS, null, 1), "application/json"));
    const list = el("div", { class: "exp-list" }, box);
    const opts = [{ id: "all", title: "All" }, ...RUNS.experiments];
    const chipBtns = opts.map((o) => {
      const b = el("button", { class: "btn", type: "button", "aria-pressed": String(state.exp === o.id) }, chips, o.title);
      b.addEventListener("click", () => {
        state.exp = o.id;
        chipBtns.forEach((x, i) => x.setAttribute("aria-pressed", String(opts[i].id === o.id)));
        commit(false);
        draw();
      });
      return b;
    });
    const keyOf = {
      rq1: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`],
      budget: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`, `${r.restarts} restarts`],
      rq2: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`, `${r.shots.toLocaleString("en-US")} shots`],
      rq3: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`, `batch ${r.batch}`],
      rq4: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`, `batch ${r.batch}`, `label ${r.label}`],
      rq5: (r) => [`${r.qubits}q`, `${r.reps}×${r.layers}`, r.task, `step ${r.step}`],
    };
    let drawn = false;
    function draw() {
      drawn = true;
      list.textContent = "";
      for (const e of RUNS.experiments) {
        if (state.exp !== "all" && state.exp !== e.id) continue;
        const sec = el("section", { class: "exp", "aria-label": e.title }, list);
        el("h3", {}, sec, e.title);
        const rows = ALL.filter((r) => r.exp === e.id);
        el("p", { class: "sub" }, sec, `${e.varies}; ${rows.length} attacks, ${rows[0].restarts} restarts each.`);
        const grid = el("div", { class: "strips" }, sec);
        el("span", { class: "hd" }, grid, "setting");
        el("span", { class: "hd" }, grid, "seeds");
        el("span", { class: "hd cnt" }, grid, "recovered");
        const detail = el("p", { class: "detail", "aria-live": "polite" }, sec, "Pick a dot to read that attack.");
        // One Tab stop per experiment; the arrow keys move between its dots (a roving tabindex).
        const lines = [];
        grid.addEventListener("keydown", (ev) => {
          const at = lines.flatMap((l, y) => l.map((b, x) => [b, x, y])).find(([b]) => b === ev.target);
          if (!at) return;
          let [, x, y] = at;
          if (ev.key === "ArrowRight") x += 1;
          else if (ev.key === "ArrowLeft") x -= 1;
          else if (ev.key === "ArrowDown") y += 1;
          else if (ev.key === "ArrowUp") y -= 1;
          else if (ev.key === "Home") x = 0;
          else if (ev.key === "End") x = lines[y].length - 1;
          else return;
          ev.preventDefault();
          y = Math.max(0, Math.min(lines.length - 1, y));
          x = Math.max(0, Math.min(lines[y].length - 1, x));
          ev.target.tabIndex = -1;
          lines[y][x].tabIndex = 0;
          lines[y][x].focus();
        });
        for (const [k, rs] of bySetting(rows, (r) => keyOf[e.id](r).join(" · "))) {
          el("span", { class: "lab" }, grid, k);
          const dots = el("span", { class: "dots" }, grid);
          const line = [];
          lines.push(line);
          for (const r of rs) {
            const b = el("button", { type: "button", class: r.best, tabindex: lines.length === 1 && !line.length ? "0" : "-1", "aria-pressed": "false", "aria-label": `${k}, seed ${r.seed}: ${WORD[r.best]}` }, dots);
            line.push(b);
            b.addEventListener("click", () => {
              sec.querySelectorAll('.dots button[aria-pressed="true"]').forEach((x) => x.setAttribute("aria-pressed", "false"));
              b.setAttribute("aria-pressed", "true");
              for (const l of lines) for (const x of l) x.tabIndex = x === b ? 0 : -1;
              detail.textContent = "";
              el("b", {}, detail, `${k}, seed ${r.seed}: `);
              detail.append(`best restart ${WORD[r.best]}, ${rad(r.error)} rad from the input; ${lettersHit(r)} of ${r.outcomes.length} restarts recovered it. Each restart in order: `);
              el("span", { class: "letters" }, detail, r.outcomes);
              detail.append(" (r recovered, c close, a another input fits, s stuck).");
            });
          }
          el("span", { class: "cnt" }, grid, `${count(rs, (r) => r.best === "recovered")} of ${rs.length}`);
        }
        const key = el("p", { class: "key" }, sec);
        for (const [c, w] of [["recovered", "recovered"], ["close", "close"], ["ambiguous", "another input fits"], ["", "stuck"]]) {
          const s = el("span", {}, key);
          el("i", { class: c }, s);
          s.append(w);
        }
      }
    }
    return { show: () => (drawn ? null : draw()), hide: () => {} };
  };

  views.intro = (box) => {
    const svg = box.querySelector("svg.fl");
    const again = box.querySelector("#fl-again");
    const run = () => {
      svg.classList.remove("run");
      void svg.getBoundingClientRect();
      svg.classList.add("run");
    };
    if (reduce) again.hidden = true;
    again.addEventListener("click", run);
    return { show: run, hide: () => svg.classList.remove("run") };
  };

  // ---- tabs and routing ----------------------------------------------------------------------

  const built = {};
  const tablist = document.querySelector(".tabs");
  const tabBtns = TABS.map(([id, name]) => {
    const b = el("button", { role: "tab", id: `tab-${id}`, "aria-controls": `view-${id}`, type: "button" }, tablist, name);
    document.getElementById(`view-${id}`).setAttribute("aria-labelledby", `tab-${id}`);
    b.addEventListener("click", () => go(id, true));
    return b;
  });
  // Arrow keys move between tabs (WAI-ARIA tabs pattern, automatic activation).
  tablist.addEventListener("keydown", (e) => {
    const i = TABS.findIndex(([t]) => t === state.tab);
    let j = null;
    if (e.key === "ArrowRight") j = (i + 1) % TABS.length;
    else if (e.key === "ArrowLeft") j = (i - 1 + TABS.length) % TABS.length;
    else if (e.key === "Home") j = 0;
    else if (e.key === "End") j = TABS.length - 1;
    if (j === null) return;
    e.preventDefault();
    go(TABS[j][0], true);
    tabBtns[j].focus();
  });
  let current = null;
  function go(tab, push) {
    if (current && current !== tab) built[current]?.hide();
    state.tab = tab;
    TABS.forEach(([id], i) => {
      const on = id === tab;
      tabBtns[i].setAttribute("aria-selected", String(on));
      tabBtns[i].tabIndex = on ? 0 : -1;
      document.getElementById(`view-${id}`).hidden = !on;
    });
    if (!built[tab]) built[tab] = views[tab](document.getElementById(`view-${tab}`));
    current = tab;
    commit(push);
    built[tab].show();
  }
  // A URL edited by hand, or Back: rebuild the views, so every control shows the new state.
  function reroute() {
    readHash();
    if (current) built[current]?.hide();
    if (cancelCurrent) cancelCurrent();
    for (const [id] of TABS) {
      if (id === "intro" || !built[id]) continue;
      built[id].hide();
      // A fresh, empty section: the old one's listeners go with it.
      const old = document.getElementById(`view-${id}`);
      old.replaceWith(old.cloneNode(false));
      delete built[id];
    }
    current = null;
    go(state.tab, false);
  }
  // Back and Forward between entries that differ only in the hash fire hashchange too.
  window.addEventListener("hashchange", reroute);

  // ---- inside a slide ------------------------------------------------------------------------

  if (embed) {
    document.body.classList.add("embed");
    // The deck sizes the frame to the page's height.
    // The deck and the page share an origin; nothing is sent to any other.
    const post = (msg) => window.parent !== window && window.parent.postMessage({ source: "qfl-lab", ...msg }, location.origin);
    // The page's own height (main's), so the frame can shrink as well as grow.
    const main = document.querySelector("main");
    new ResizeObserver(() => post({ height: Math.ceil(main.getBoundingClientRect().height) + 4 })).observe(main);
    // A presenter's clicker sends page or arrow keys. Keys a control does not use go to the deck,
    // and a click hands the keyboard back, so the next press turns the slide.
    const DECK = new Set(["PageDown", "PageUp", "ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp", " ", "n", "p", "b", "."]);
    document.addEventListener("keydown", (e) => {
      const tag = e.target.tagName;
      const arrow = e.key === "ArrowLeft" || e.key === "ArrowRight";
      const own =
        tag === "INPUT" || tag === "SELECT" || (tag === "BUTTON" && (e.key === " " || e.key === "Enter")) || (arrow && e.target.closest?.(".keys"));
      if (e.key === "PageDown" || e.key === "PageUp" || (!own && DECK.has(e.key))) {
        // The deck acts on it, so the page does not too (Space would also play the search).
        e.preventDefault();
        e.stopPropagation();
        post({ key: e.key, shift: e.shiftKey });
      }
    }, true);
    // After a click on a button or the scrubber, the keyboard goes back to the deck. A number
    // box or a list keeps it, so it can be typed into.
    document.addEventListener("pointerup", (e) => {
      const c = e.target.closest?.('button, input[type="range"]');
      if (!c) return;
      setTimeout(() => {
        c.blur();
        post({ focus: true });
      }, 0);
    });
  }

  readHash();
  go(state.tab, false);
})();
