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
  const W = 700;
  const LEFT = 130;
  const RIGHT = 672;
  const AXIS_MIN = -3;
  const AXIS_MAX = 6;
  const x = (v) => LEFT + ((v - AXIS_MIN) / (AXIS_MAX - AXIS_MIN)) * (RIGHT - LEFT);
  const ROW = 46;
  const ROWS_TOP = 138;
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

  el("text", { x: 4, y: 60, class: "row-label strong" }, "First reading");
  el("text", { x: 4, y: 82, class: "row-sub" }, "one split, five seeds");
  el("line", { x1: x(low), x2: x(high), y1: 66, y2: 66, class: "interval" });
  el("circle", { cx: x(first), cy: 66, r: 11, class: "point ours" });
  el("text", { x: x(first), y: 44, class: "value strong", "text-anchor": "middle" }, data.split_first);

  el("text", { x: 4, y: ROWS_TOP - 8, class: "row-label" }, "Five splits");
  names.forEach((name, i) => {
    const y = ROWS_TOP + ROW * i + 20;
    const v = means[name];
    el("text", { x: 22, y: y + 7, class: "row-sub" }, `split ${i + 1}`);
    el("circle", { cx: x(v), cy: y, r: 10, class: name === "registered" ? "point ours" : "point" });
    el("text", { x: x(v) + 18, y: y + 7, class: "value" }, v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2));
  });

  box.appendChild(svg);
})();
