// Draws the split-example figure from data/readings.js before Reveal starts, in three build steps:
// one split's first reading with its interval, then five splits (each the mean of two seeds), then
// the five splits' average.
(function () {
  "use strict";
  const SVG = "http://www.w3.org/2000/svg";
  const box = document.querySelector("#split-fig");
  if (!box) return;
  const data = window.DECK_DATA.readings;
  const drawn = window.DECK_FIGURE;
  const means = drawn.split_means;
  const names = Object.keys(means);
  if (names.length !== drawn.split_count) throw new Error("split figure: means disagree with split_count");

  const first = Number(data.split_first);
  const low = Number(drawn.split_first_low);
  const high = Number(drawn.split_first_high);
  const W = 720;
  const LEFT = 270;
  const RIGHT = 700;
  const AXIS_MIN = -3;
  const AXIS_MAX = 6;
  const x = (v) => LEFT + ((v - AXIS_MIN) / (AXIS_MAX - AXIS_MIN)) * (RIGHT - LEFT);
  const ROW = 46;
  const ROWS_TOP = 176;
  // Below the rows: the axis ticks, then the average's label under them.
  const GRID_END = ROWS_TOP + ROW * names.length + 24;
  const TICK_Y = GRID_END + 24;
  const MEAN_Y = TICK_Y + 34;
  const H = MEAN_Y + 6;
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `Exact-match points on OpenStack's development data. One split read ${data.split_first}, its interval from ${drawn.split_first_low} to ${drawn.split_first_high}, clearing zero. Five splits of two seeds each ranged from ${data.split_low} to ${data.split_high}, averaging ${data.split_mean}.`);

  // Each build step is an SVG group; reveal.js shows a group with class "fragment" on a click.
  const step = (index) => {
    const g = document.createElementNS(SVG, "g");
    if (index) {
      g.setAttribute("class", "fragment");
      g.setAttribute("data-fragment-index", index);
    }
    svg.appendChild(g);
    return g;
  };
  let into = step(0);
  const el = (tag, attrs, text) => {
    const n = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    into.appendChild(n);
    return n;
  };

  el("line", { x1: x(0), x2: x(0), y1: 16, y2: GRID_END, class: "zero" });
  el("text", { x: x(0), y: TICK_Y, class: "tick", "text-anchor": "middle" }, "0");
  for (const t of [-2, 2, 4]) {
    el("line", { x1: x(t), x2: x(t), y1: 16, y2: GRID_END, class: "grid" });
    el("text", { x: x(t), y: TICK_Y, class: "tick", "text-anchor": "middle" }, t > 0 ? `+${t}` : `${t}`);
  }

  el("text", { x: 4, y: 62, class: "row-label first" }, "First reading");
  el("text", { x: 4, y: 92, class: "row-sub" }, "1 split, 5 seeds");
  el("line", { x1: x(low), x2: x(high), y1: 76, y2: 76, class: "interval" });
  for (const end of [low, high]) el("line", { x1: x(end), x2: x(end), y1: 62, y2: 90, class: "cap" });
  el("circle", { cx: x(first), cy: 76, r: 15, class: "point first" });
  el("text", { x: x(first), y: 50, class: "value first", "text-anchor": "middle" }, data.split_first);

  into = step(1);
  el("text", { x: 4, y: ROWS_TOP - 32, class: "row-label" }, "5 splits");
  el("text", { x: 4, y: ROWS_TOP - 6, class: "row-sub" }, "2 seeds each");
  names.forEach((name, i) => {
    const y = ROWS_TOP + ROW * i + 26;
    const v = means[name];
    // The first reading's split, re-read on two of its seeds, is named as that split.
    el("text", { x: 30, y: y + 8, class: "row-sub" }, name === "registered" ? "that split" : `split ${i + 1}`);
    el("circle", { cx: x(v), cy: y, r: 14, class: "point" });
    // A negative value's label sits left of its dot, clear of the zero line.
    const side = v < 0 ? { x: x(v) - 24, "text-anchor": "end" } : { x: x(v) + 24 };
    el("text", { ...side, y: y + 9, class: "value" }, v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2));
  });

  into = step(2);
  const mean = Number(data.split_mean);
  el("line", { x1: x(mean), x2: x(mean), y1: ROWS_TOP + 4, y2: MEAN_Y - 28, class: "mean" });
  el("text", { x: x(mean), y: MEAN_Y, class: "value strong", "text-anchor": "middle" }, `average ${data.split_mean}`);

  box.appendChild(svg);
})();

// The data-window band is drawn to the calendar: each window's share of the months comes from its
// own label in data/readings.js, so a changed window redraws the band.
(function () {
  "use strict";
  const band = document.querySelector(".windows");
  if (!band) return;
  const data = window.DECK_DATA.readings;
  const months = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };
  const parse = (m) => months[m[0]] + 12 * Number(m[1]);
  const span = (label) => {
    const found = [...label.matchAll(/([A-Z][a-z]{2}) (\d{4})/g)].map((m) => parse([m[1], m[2]]));
    if (found.length < 1 || found.length > 2) throw new Error(`data window: cannot read "${label}"`);
    return [found[0], found[found.length - 1]];
  };
  const wins = [...band.querySelectorAll(".win")];
  const spans = wins.map((win) => span(data[win.querySelector("[data-value]").dataset.value.split(".")[1]]));
  const start = spans[0][0];
  const end = spans[spans.length - 1][1] + 1;
  wins.forEach((win, i) => {
    const [from, to] = spans[i];
    win.style.setProperty("--l", ((from - start) / (end - start)) * 100);
    win.style.setProperty("--w", ((to + 1 - from) / (end - start)) * 100);
  });
})();

// The "what Sphragis builds" slide: the example's code with the developer's change marked, and the
// examples-per-organization bars, each as its share of the largest, and the audit's valid shares.
(function () {
  "use strict";
  const drawn = window.DECK_FIGURE.example;
  for (const node of document.querySelectorAll("[data-example]")) {
    const runs = drawn && drawn[node.dataset.example];
    if (!runs) throw new Error(`example figure: no "${node.dataset.example}" side`);
    for (const [text, changed] of runs) {
      node.appendChild(changed ? Object.assign(document.createElement("mark"), { textContent: text }) : document.createTextNode(text));
    }
  }
  const data = window.DECK_DATA.readings;
  const read = (path) => {
    const n = Number(String(data[path.split(".")[1]]).replace(/,/g, ""));
    if (!Number.isFinite(n)) throw new Error(`bar figure: cannot read ${path}`);
    return n;
  };
  // A bar with data-of is a share of that count; the others in a figure share its largest bar.
  for (const fig of document.querySelectorAll("figure:has([data-bar])")) {
    const bars = [...fig.querySelectorAll("[data-bar]")];
    const counts = bars.map((bar) => read(bar.dataset.bar));
    const most = Math.max(...counts);
    bars.forEach((bar, i) => {
      const of = bar.dataset.of ? read(bar.dataset.of) : most;
      bar.style.setProperty("--share", (counts[i] / of) * 100);
    });
  }
})();
