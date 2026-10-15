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

  // The attributes tip.js turns into a card, for one related-work entry.
  function tip(w) {
    return {
      "data-tip": w.oneLine,
      "data-tip-title": w.label,
      ...(w.year ? { "data-tip-chip": String(w.year) } : {}),
      ...(w.ours ? { "data-tip-tone": "ours" } : {}),
    };
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
      box.dataset.motion = "fill";
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

  // The map as a list for the feed: one block per row of the map, each work with its column.
  function buildMapList(box, rel, x, y) {
    const flat = (t) => String(t).replace(/\n/g, " ");
    const list = html("div", { class: "map-list", role: "group", "aria-label": `Related work by ${flat(x.label).toLowerCase()} and ${flat(y.label).toLowerCase()}` }, box);
    y.levels.forEach((lv) => {
      const mine = rel.works.filter((w) => w.y === lv);
      if (!mine.length) return;
      html("h3", {}, list, `${flat(y.label)} ${flat(lv)}`);
      const ul = html("ul", {}, list);
      for (const w of mine) {
        const li = html("li", { class: w.ours ? "ours" : "", tabindex: "0", ...tip(w) }, ul);
        html("b", { "data-tip-anchor": "" }, li, w.label);
        li.append(` · ${flat(w.x)}`);
      }
    });
  }

  function buildMap(box) {
    const rel = lookup(box.dataset.source);
    if (!usable(rel, box.dataset.source)) return;
    if (!rel.axes || !rel.axes.x || !rel.axes.y) {
      console.error(`deck: ${box.dataset.source} has no axes for the map`);
      return;
    }
    const { x, y } = rel.axes;
    if (phone) {
      buildMapList(box, rel, x, y);
      return;
    }
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
        "data-motion": w.ours ? "pop" : "arrive",
        "data-step": 110,
        "data-i": r * 3 + n,
        tabindex: "0",
        role: "img",
        "aria-label": w.label,
        ...tip(w),
      }, fig);
      svg("circle", { cx, cy, r: w.ours ? 12 : 9, "data-tip-anchor": "" }, g);
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
  // ours drawn last. Dots pop in by year when the slide opens (motion.js).
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
        class: w.ours ? "work ours" : "work",
        "data-motion": "pop",
        "data-step": 140,
        "data-i": i,
        tabindex: "0",
        role: "img",
        "aria-label": `${w.year}, ${w.label}`,
        ...tip(w),
      }, fig);
      svg("circle", { cx: px(w.year), cy, r: w.ours ? 12 : 9, "data-tip-anchor": "" }, g);
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

  // <div class="flow" data-source="readings.funnel.openstack">: how a corpus is filtered, from
  // what was fetched to what was kept. Stages may count different units (comments, pairs,
  // lessons), so no width is shared between stages; inside a stage its reasons share one unit
  // and are drawn to scale. Each stage is a fragment, so the room sees one kind of loss at a time.
  // Data: { changes, stages: [{ label, unit, count, reasons: [{ label, count }] }], kept }.
  function buildFlow(box) {
    const f = lookup(box.dataset.source);
    if (!f || !Array.isArray(f.stages) || !f.stages.length) {
      console.error(`deck: ${box.dataset.source} has no stages to draw`);
      return;
    }
    const n = (v) => Number(v).toLocaleString("en-US");
    const tall = phone;
    // Desktop: fetched, the stages and kept side by side, stages top-aligned so their counts read
    // as one row. Phone: the same, one under another, each reason on one line over a thin bar.
    const L = tall
      ? { W: 440, endW: 400, endH: 72, colW: 400, gap: 16, head: 50, row: 35, bar: 6, big: "flow-big" }
      : { W: 0, endW: 170, endH: 150, colW: 236, gap: 50, head: 112, row: 66, bar: 22, big: "flow-big" };
    if (!tall) L.W = 2 * L.endW + f.stages.length * L.colW + (f.stages.length + 1) * L.gap;
    const stageH = (st) => L.head + st.reasons.length * L.row;
    const H = tall
      ? 2 * (L.endH + L.gap) + f.stages.reduce((h, st) => h + stageH(st) + L.gap, 0)
      : Math.max(L.endH, ...f.stages.map(stageH)) + 10;
    const fig = svg("svg", {
      viewBox: `0 0 ${L.W} ${H}`,
      role: "img",
      "aria-label": `From ${n(f.changes)} merged changes to ${n(f.kept)} lessons kept: ${f.stages
        .map((st) => `${n(st.count)} ${st.label}`)
        .join(", ")}`,
    });
    let x = 0, y = 0;
    const arrow = (g) => {
      if (tall) svg("path", { d: `M208,${y - L.gap + 6} h24 l-12,12 z`, class: "flow-arrow" }, g);
      else svg("path", { d: `M${x - L.gap + 9},${L.endH / 2 - 13} l20,13 l-20,13 z`, class: "flow-arrow" }, g);
    };
    const endBox = (label, value, cls, attrs, withArrow) => {
      const g = svg("g", attrs || {}, fig);
      if (withArrow) arrow(g);
      const bx = tall ? 20 : x, by = tall ? y : 0;
      svg("rect", { x: bx, y: by, width: L.endW, height: L.endH, rx: 14, class: `flow-end ${cls}` }, g);
      if (tall) {
        svg("text", { x: bx + 22, y: by + 51, class: `flow-big ${cls}` }, g, n(value));
        svg("text", { x: bx + L.endW - 22, y: by + 49, class: "flow-unit", "text-anchor": "end" }, g, label.replace("\n", " "));
        y += L.endH + L.gap;
      } else {
        svg("text", { x: bx + L.endW / 2, y: by + 64, class: `flow-big ${cls}`, "text-anchor": "middle" }, g, n(value));
        lines(svg("text", { class: "flow-unit", "text-anchor": "middle" }, g), label, bx + L.endW / 2, by + 108, 26);
        x += L.endW + L.gap;
      }
    };
    endBox("merged\nchanges", f.changes, "start");
    for (const st of f.stages) {
      const g = svg("g", { class: "fragment flow-stage" }, fig);
      arrow(g);
      const sx = tall ? 20 : x, sy = tall ? y : 0;
      svg("text", { x: sx, y: sy + (tall ? 28 : 36), class: "flow-count" }, g, n(st.count));
      svg("text", { x: tall ? sx + L.colW : sx, y: sy + (tall ? 28 : 70), class: "flow-unit", "text-anchor": tall ? "end" : "start" }, g, st.label);
      // A rule under the stage's header, so its reasons read as what it is made of.
      svg("line", { x1: sx, x2: sx + L.colW, y1: sy + (tall ? 38 : 88), y2: sy + (tall ? 38 : 88), class: "flow-rule" }, g);
      const most = Math.max(...st.reasons.map((r) => r.count));
      st.reasons.forEach((r, i) => {
        const ry = sy + L.head + i * L.row;
        if (tall) {
          svg("text", { x: sx, y: ry + 8, class: "flow-reason" }, g, r.label);
          svg("text", { x: sx + L.colW, y: ry + 8, class: "flow-reason", "text-anchor": "end" }, g, n(r.count));
          svg("rect", { x: sx, y: ry + 16, width: Math.max(3, (r.count / most) * L.colW), height: L.bar, rx: 3, class: "flow-bar", "data-motion": "growx", "data-i": i }, g);
        } else {
          const w = Math.max(3, (r.count / most) * (L.colW - 86));
          svg("text", { x: sx, y: ry + 10, class: "flow-reason" }, g, r.label);
          svg("rect", { x: sx, y: ry + 20, width: w, height: L.bar, rx: 3, class: "flow-bar", "data-motion": "growx", "data-i": i }, g);
          svg("text", { x: sx + w + 8, y: ry + 38, class: "flow-reason" }, g, n(r.count));
        }
      });
      if (tall) y += stageH(st) + L.gap;
      else x += L.colW + L.gap;
    }
    endBox("lessons\nkept", f.kept, "kept", { class: "fragment" }, true);
    box.appendChild(fig);
  }

  // <div class="forest" data-source="readings.split">: a contrast and its parts, each a point
  // with its interval against a "no gain" line, on one scale for every community. The parts of a
  // split add up to the whole; each split is a fragment, and the part the claim is about is the
  // accent mark. Data: { org: { name, whole: { estimate, low, high }, <split>: [part, part] } },
  // the splits named in data-splits, each split's accented part's index in data-accent.
  function buildForest(box) {
    const data = lookup(box.dataset.source);
    const splits = (box.dataset.splits || "").split(",").filter(Boolean);
    if (!data || !splits.length) {
      console.error(`deck: ${box.dataset.source} has no splits to draw`);
      return;
    }
    const accent = (box.dataset.accent || "").split(",").map(Number);
    const orgs = Object.values(data);
    const cells = orgs.flatMap((o) => [o.whole, ...splits.flatMap((k) => o[k])]);
    const lo = Math.min(0, ...cells.map((c) => c.low)), hi = Math.max(...cells.map((c) => c.high));
    const pad = (hi - lo) * 0.06;
    const tall = phone;
    // On a phone each row's label sits above its line, so the plot keeps the screen's width.
    const labelW = tall ? 0 : 236, plotW = tall ? 380 : 300, panelW = labelW + plotW + 20;
    const rowH = tall ? 50 : 44, groupGap = tall ? 8 : 18;
    const rowsPer = 1 + splits.reduce((r, k) => r + data[Object.keys(data)[0]][k].length, 0);
    const panelH = 54 + rowsPer * rowH + splits.length * groupGap + 40;
    const W = tall ? 440 : panelW * orgs.length + 20 * (orgs.length - 1);
    const H = tall ? panelH * orgs.length : panelH;
    const fig = svg("svg", {
      viewBox: `0 0 ${W} ${H}`,
      role: "img",
      "aria-label": orgs
        .map((o) => `${o.name}: the whole gain, then ${splits.map((k) => o[k].map((p) => p.label).join(" against ")).join("; ")}`)
        .join(". "),
    });
    const groups = [svg("g", {}, fig), ...splits.map(() => svg("g", { class: "fragment" }, fig))];
    orgs.forEach((o, oi) => {
      const px = tall ? 10 : oi * (panelW + 20), py = tall ? oi * panelH : 0;
      const sx = (v) => px + labelW + ((v - lo + pad) / (hi - lo + 2 * pad)) * plotW;
      svg("text", { x: px, y: py + 30, class: "forest-org" }, groups[0], o.name);
      // The "no gain" line runs the panel's height; on a phone, where labels sit above their
      // lines, it is a short tick on each row so it never crosses a label.
      if (!tall) svg("line", { x1: sx(0), x2: sx(0), y1: py + 46, y2: py + panelH - 34, class: "forest-zero" }, groups[0]);
      svg("text", { x: sx(0), y: py + panelH - 10, class: "forest-axis", "text-anchor": "middle" }, groups[0], "no gain");
      svg("text", { x: px + labelW + plotW, y: py + panelH - 10, class: "forest-axis", "text-anchor": "end" }, groups[0], "more gain \u2192");
      let ry = py + 54 + rowH / 2;
      const point = (g, c, label, cls) => {
        if (tall) svg("text", { x: px + 20, y: ry - 18, class: "forest-label" }, g, label);
        else svg("text", { x: px + labelW - 14, y: ry + 7, class: "forest-label", "text-anchor": "end" }, g, label);
        if (tall) svg("line", { x1: sx(0), x2: sx(0), y1: ry - 12, y2: ry + 12, class: "forest-zero" }, g);
        svg("line", { x1: sx(c.low), x2: sx(c.high), y1: ry, y2: ry, class: `forest-ci ${cls}`, "data-motion": "growx" }, g);
        svg("circle", { cx: sx(c.estimate), cy: ry, r: 9, class: `forest-pt ${cls}`, "data-motion": "pop" }, g);
        ry += rowH;
      };
      point(groups[0], o.whole, "whole gain", "whole");
      splits.forEach((k, si) => {
        ry += groupGap;
        o[k].forEach((p, pi) => point(groups[si + 1], p, p.label, accent[si] === pi ? "ours" : "part"));
      });
    });
    box.appendChild(fig);
  }

  // <svg data-only="phone"> / data-only="desktop": a figure drawn twice, wide for a slide and
  // tall for the feed. Only the one for this screen stays, so nothing counts or reads it twice.
  for (const node of document.querySelectorAll("[data-only]")) {
    if (node.dataset.only !== (phone ? "phone" : "desktop")) node.remove();
  }
  branch();
  bindValues();
  buildDots();
  document.querySelectorAll(".relmap[data-source]").forEach(buildMap);
  document.querySelectorAll(".timeline[data-source]").forEach(buildTimeline);
  document.querySelectorAll(".flow[data-source]").forEach(buildFlow);
  document.querySelectorAll(".forest[data-source]").forEach(buildForest);
  const chs = chapters();
  buildAgenda(chs);
  if (phone) {
    document.documentElement.classList.add("phone");
    // A feed has no stepping: a fragment would hide its content and stretch the page by a screen.
    for (const f of document.querySelectorAll(".reveal .fragment")) f.classList.remove("fragment");
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
