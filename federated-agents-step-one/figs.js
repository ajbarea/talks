// Draws the split-example figure from data/readings.js before Reveal starts: one split's first
// reading with its interval, then five splits, each its mean of two seeds, on one axis.
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
  const LEFT = 168;
  const RIGHT = 700;
  const AXIS_MIN = -3;
  const AXIS_MAX = 6;
  const x = (v) => LEFT + ((v - AXIS_MIN) / (AXIS_MAX - AXIS_MIN)) * (RIGHT - LEFT);
  const ROW = 56;
  const ROWS_TOP = 158;
  const H = ROWS_TOP + ROW * names.length + 66;
  const svg = document.createElementNS(SVG, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `Exact-match points on OpenStack's development data. One split read ${data.split_first}, its interval from ${drawn.split_first_low} to ${drawn.split_first_high}, clearing zero. Five splits of two seeds each ranged from ${data.split_low} to ${data.split_high}, averaging ${data.split_mean}.`);

  const el = (tag, attrs, text) => {
    const n = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    svg.appendChild(n);
    return n;
  };

  el("line", { x1: x(0), x2: x(0), y1: 16, y2: H - 42, class: "zero" });
  el("text", { x: x(0), y: H - 18, class: "tick", "text-anchor": "middle" }, "0");
  for (const t of [-2, 2, 4]) {
    el("line", { x1: x(t), x2: x(t), y1: 16, y2: H - 42, class: "grid" });
    el("text", { x: x(t), y: H - 18, class: "tick", "text-anchor": "middle" }, t > 0 ? `+${t}` : `${t}`);
  }

  el("text", { x: 4, y: 62, class: "row-label strong" }, "First reading");
  el("text", { x: 4, y: 92, class: "row-sub" }, "one split, five seeds");
  el("line", { x1: x(low), x2: x(high), y1: 76, y2: 76, class: "interval" });
  for (const end of [low, high]) el("line", { x1: x(end), x2: x(end), y1: 62, y2: 90, class: "cap" });
  el("circle", { cx: x(first), cy: 76, r: 15, class: "point ours" });
  el("text", { x: x(first), y: 50, class: "value strong", "text-anchor": "middle" }, data.split_first);

  el("text", { x: 4, y: ROWS_TOP - 6, class: "row-label" }, "Five splits");
  names.forEach((name, i) => {
    const y = ROWS_TOP + ROW * i + 26;
    const v = means[name];
    el("text", { x: 30, y: y + 8, class: "row-sub" }, `split ${i + 1}`);
    el("circle", { cx: x(v), cy: y, r: 14, class: name === "registered" ? "point ours" : "point" });
    el("text", { x: x(v) + 24, y: y + 9, class: "value" }, v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2));
  });

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
