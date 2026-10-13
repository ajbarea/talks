// Deck behaviour: values and figures bound from data/readings.js and data/related.js, the agenda and chapter rail
// built from each slide's data-chapter, then reveal.js started. Everything here runs before
// Reveal.initialize, so fragments it creates are counted like hand-written ones.
(function () {
  "use strict";

  const DATA = window.DECK_DATA || {};
  const SVG = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  // A narrow portrait screen gets a vertical feed; anything wider gets slides scaled to fit.
  // Crossing the line (a rotation, a resized window) reloads, and the hash keeps the slide.
  const narrow = matchMedia("(max-width: 600px)");
  const phone = narrow.matches;
  narrow.addEventListener("change", () => location.reload());

  function lookup(path) {
    const value = path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), DATA);
    if (value === undefined) console.error(`deck: no data at ${path}`);
    return value;
  }

  function svg(name, attrs, parent, text) {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (text !== undefined) node.textContent = text;
    if (parent) parent.appendChild(node);
    return node;
  }

  function html(name, attrs, parent, text) {
    const node = document.createElement(name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (text !== undefined) node.textContent = text;
    if (parent) parent.appendChild(node);
    return node;
  }

  // <span data-if="readings.planted_all">: kept only when the flag is true (data-unless: false).
  // Removed rather than hidden, so the speaker notes read only the branch that holds.
  function branch() {
    for (const node of document.querySelectorAll("[data-if], [data-unless]")) {
      const keep = node.dataset.if ? lookup(node.dataset.if) === true : lookup(node.dataset.unless) === false;
      if (!keep) node.remove();
    }
  }

  // <span data-value="results.failShare" data-format="pct"></span>
  function bindValues() {
    for (const node of document.querySelectorAll("[data-value]")) {
      const v = lookup(node.dataset.value);
      if (v === undefined) {
        node.textContent = `[missing ${node.dataset.value}]`;
      } else if (node.dataset.format === "pct") {
        node.textContent = `${Math.round(v * 100)}%`;
      } else if (typeof v === "number") {
        node.textContent = v.toLocaleString("en-US");
      } else {
        node.textContent = String(v);
      }
    }
  }

  // <div class="dots" data-dots="results.failShare" data-total="100">: one dot per unit,
  // the share filled. With data-of, data-dots is a count out of the total at data-of. A count
  // drawn as marks, so it traces to the data like a typed number.
  function buildDots() {
    for (const box of document.querySelectorAll("[data-dots]")) {
      const of = box.dataset.of ? lookup(box.dataset.of) : undefined;
      const total = typeof of === "number" ? of : Number(box.dataset.total || 100);
      const share = lookup(box.dataset.dots);
      if (typeof share !== "number") continue;
      const hit = typeof of === "number" ? share : Math.round(share * total);
      const cols = Number(box.dataset.cols || 20);
      const rows = Math.ceil(total / cols);
      const fig = svg("svg", {
        viewBox: `0 0 ${cols * 20} ${rows * 20}`,
        role: "img",
        "aria-label": `${hit} of ${total} filled`,
      });
      for (let i = 0; i < total; i++) {
        svg("circle", {
          cx: (i % cols) * 20 + 10,
          cy: Math.floor(i / cols) * 20 + 10,
          r: 7,
          class: i < hit ? "dot hit" : "dot",
          style: `--i:${i}`,
        }, fig);
      }
      box.appendChild(fig);
    }
  }

  // <div class="relmap" data-source="related">: rivals placed by the two axes in the data,
  // ours added as the slide's last fragment, and the "how ours differs" lines beside it.
  // A list still being filled in leaves its slide empty instead of stopping the deck.
  function usable(rel, source) {
    if (rel && Array.isArray(rel.works) && rel.works.length) return true;
    console.error(`deck: ${source} has no works to draw`);
    return false;
  }

  // A label with "\n" in it becomes one line per part, centred on y.
  function lines(node, text, x, y, step) {
    const parts = String(text).split("\n");
    parts.forEach((part, i) => {
      svg("tspan", { x, y: y + (i - (parts.length - 1) / 2) * step }, node, part);
    });
    return node;
  }

  function buildMap(box) {
    const rel = lookup(box.dataset.source);
    if (!usable(rel, box.dataset.source)) return;
    if (!rel.axes || !rel.axes.x || !rel.axes.y) {
      console.error(`deck: ${box.dataset.source} has no axes for the map`);
      return;
    }
    const { x, y } = rel.axes;
    const W = 1180, H = 430, left = 190, top = 10, bottom = 74;
    const cw = (W - left) / x.levels.length;
    const rh = (H - top - bottom) / y.levels.length;
    const fig = svg("svg", {
      viewBox: `0 0 ${W} ${H}`,
      role: "img",
      "aria-label": `Related work by ${x.label.toLowerCase()} and ${y.label.toLowerCase()}`,
    });
    y.levels.forEach((lv, r) => {
      const cy = top + r * rh;
      svg("rect", { x: left, y: cy, width: W - left, height: rh, class: r % 2 ? "band" : "band alt" }, fig);
      lines(svg("text", { class: "axis-level", "text-anchor": "end" }, fig), lv, left - 14, cy + rh / 2 + 7, 24);
    });
    x.levels.forEach((lv, c) => {
      if (c) svg("line", { x1: left + c * cw, x2: left + c * cw, y1: top, y2: H - bottom, class: "col" }, fig);
      lines(svg("text", { class: "axis-level", "text-anchor": "middle" }, fig), lv, left + c * cw + cw / 2, H - bottom + 34, 24);
    });
    svg("text", { x: 10, y: top + 4, class: "axis-label", "dominant-baseline": "hanging" }, fig, y.label);
    lines(svg("text", { class: "axis-label" }, fig), x.label, 10, H - bottom + 46, 24);

    const place = (w) => [x.levels.indexOf(w.x), y.levels.indexOf(w.y)];
    const count = new Map();
    for (const w of rel.works) count.set(place(w).join(), (count.get(place(w).join()) || 0) + 1);
    const seen = new Map();
    for (const w of rel.works) {
      const [c, r] = place(w);
      if (c < 0 || r < 0) {
        console.error(`deck: ${w.id} sits outside the map axes (${w.x}, ${w.y})`);
        continue;
      }
      const key = `${c},${r}`;
      const n = seen.get(key) || 0;
      seen.set(key, n + 1);
      const cx = left + c * cw + 24;
      const cy = top + r * rh + rh / 2 + (n - (count.get(key) - 1) / 2) * 30;
      const g = svg("g", {
        class: w.ours ? "work ours fragment" : "work",
        tabindex: "0",
        role: "img",
        "aria-label": `${w.label}: ${w.oneLine}`,
      }, fig);
      svg("title", {}, g, `${w.label} (${w.year}): ${w.oneLine}`);
      svg("circle", { cx, cy, r: w.ours ? 12 : 9 }, g);
      svg("text", { x: cx + 18, y: cy + 7 }, g, w.label);
    }
    html("div", { class: "map" }, box).appendChild(fig);

    const rivals = rel.works.filter((w) => w.differs);
    if (rivals.length && box.dataset.differs !== "off") {
      const list = html("ul", { class: "differs" }, box);
      for (const w of rivals) {
        const li = html("li", { class: "fragment" }, list);
        html("b", {}, li, w.label);
        li.append(` ${w.differs}`);
      }
    }
  }

  // <div class="timeline" data-source="related">: one lane per group, one dot per work,
  // ours drawn last. Dots pop in by year when the slide opens, unless motion is reduced.
  function buildTimeline(box) {
    const rel = lookup(box.dataset.source);
    if (!usable(rel, box.dataset.source)) return;
    const works = [...rel.works].sort((a, b) => a.year - b.year);
    const groups = [...new Set(works.map((w) => w.group))];
    const y0 = works[0].year, y1 = works[works.length - 1].year;
    const W = 1100, left = 200, right = 60, lane = 70, top = 30;
    const H = top + groups.length * lane + 50;
    const px = (year) => left + ((year - y0) / Math.max(1, y1 - y0)) * (W - left - right);
    const fig = svg("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `Related work from ${y0} to ${y1}` });
    groups.forEach((g, i) => {
      const cy = top + i * lane + lane / 2;
      svg("line", { x1: left, x2: W - right, y1: cy, y2: cy, class: "lane" }, fig);
      svg("text", { x: left - 16, y: cy + 6, class: "axis-level", "text-anchor": "end" }, fig, g);
    });
    for (let year = y0; year <= y1; year++) {
      svg("text", { x: px(year), y: H - 12, class: "axis-level", "text-anchor": "middle" }, fig, String(year));
    }
    works.forEach((w, i) => {
      const cy = top + groups.indexOf(w.group) * lane + lane / 2;
      const g = svg("g", {
        class: w.ours ? "work ours pop" : "work pop",
        style: `--i:${i}`,
        tabindex: "0",
        role: "img",
        "aria-label": `${w.year}, ${w.label}: ${w.oneLine}`,
      }, fig);
      svg("title", {}, g, `${w.label} (${w.year}): ${w.oneLine}`);
      svg("circle", { cx: px(w.year), cy, r: w.ours ? 12 : 9 }, g);
      svg("text", { x: px(w.year), y: cy - 18, "text-anchor": "middle" }, g, w.label);
    });
    box.appendChild(fig);
  }

  function chapters() {
    const seen = new Map();
    for (const s of document.querySelectorAll(".reveal .slides section[data-chapter]")) {
      if (!seen.has(s.dataset.chapter)) seen.set(s.dataset.chapter, s);
    }
    return seen;
  }

  // <ol class="agenda" data-auto>: the chapter names, so agenda and rail never disagree.
  function buildAgenda(chs) {
    for (const ol of document.querySelectorAll("ol.agenda[data-auto]")) {
      for (const name of chs.keys()) html("li", {}, ol, name);
    }
  }

  function buildRail(chs) {
    if (!chs.size) return;
    const rail = html("nav", { class: "rail", "aria-label": "Chapters" }, document.querySelector(".reveal"));
    for (const [name, slide] of chs) {
      const b = html("button", { type: "button" }, rail, name);
      b.addEventListener("click", () => {
        const i = Reveal.getIndices(slide);
        Reveal.slide(i.h, i.v);
      });
    }
    const sync = () => {
      const current = Reveal.getCurrentSlide();
      const c = current && current.dataset.chapter;
      rail.hidden = !c;
      for (const b of rail.children) b.setAttribute("aria-current", b.textContent === c ? "step" : "false");
      const on = rail.querySelector('[aria-current="step"]');
      if (on) rail.scrollLeft = on.offsetLeft - (rail.clientWidth - on.offsetWidth) / 2;
    };
    // The rail is fixed to the screen while slides scale, so on a small screen a slide's own top
    // padding can be shorter than the rail: --rail-clear is the padding that clears it.
    const clear = () => {
      const top = document.querySelector(".reveal .slides").getBoundingClientRect().top;
      const need = (rail.getBoundingClientRect().bottom + 6 - top) / Reveal.getScale();
      document.querySelector(".reveal").style.setProperty("--rail-clear", `${Math.max(0, Math.ceil(need))}px`);
    };
    Reveal.on("slidechanged", sync);
    Reveal.on("resize", clear);
    sync();
    clear();
  }

  branch();
  bindValues();
  buildDots();
  document.querySelectorAll(".relmap[data-source]").forEach(buildMap);
  document.querySelectorAll(".timeline[data-source]").forEach(buildTimeline);
  const chs = chapters();
  buildAgenda(chs);
  if (phone) {
    document.documentElement.classList.add("phone");
    // A feed has no stepping: a fragment would hide its content and stretch the page by a screen.
    for (const f of document.querySelectorAll(".reveal .fragment")) f.classList.remove("fragment");
    // A wide figure keeps a readable size and pans sideways instead of shrinking its labels.
    for (const fig of document.querySelectorAll(".reveal .slides svg[viewBox]")) {
      const w = fig.viewBox.baseVal.width;
      if (w > 480) {
        fig.style.minWidth = `${Math.round(w * 0.9)}px`;
        fig.parentElement.classList.add("pan");
      }
    }
  }

  Reveal.initialize({
    hash: true,
    width: phone ? 480 : 1280,
    height: phone ? 1120 : 720,
    margin: 0.04,
    center: false,
    slideNumber: "c/t",
    transition: reduce ? "none" : "fade",
    transitionSpeed: "fast",
    backgroundTransition: "none",
    autoAnimate: !reduce,
    pdfSeparateFragments: false,
    // A phone gets a portrait canvas and scroll view, and deck.css stacks the columns, so text
    // stays readable instead of a 16:9 slide shrunk to a third of its size.
    ...(phone ? { view: "scroll" } : {}),
    scrollActivationWidth: null,
    plugins: [RevealNotes],
  }).then(() => {
    if (!phone) buildRail(chs);
  });
})();
