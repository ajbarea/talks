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
  // Speaker view previews slides in narrow iframes (?receiver); they keep the slide layout.
  const receiver = /receiver/i.test(location.search);
  const phone = narrow.matches && !receiver;
  if (!receiver) narrow.addEventListener("change", () => location.reload());
  // A phone on its side, on a screen wider than 16:9, keeps the slide's layout fitted to the
  // screen's width rather than its height, and scrolls: fitted to the height, a 16:9 slide's small
  // text drew at 10px. On a 16:9 phone the two fits are the same, so it keeps the paged slides.
  const short = matchMedia("(max-height: 500px) and (pointer: coarse) and (orientation: landscape)");
  const sideways = short.matches && !phone && !receiver && innerWidth / innerHeight > 1.9;
  if (!receiver) short.addEventListener("change", () => location.reload());

  const FOCUSABLE = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
  const focusableInside = (sel) =>
    [...document.querySelectorAll(`${sel} :is(${FOCUSABLE})`)].some((n) => n.getClientRects().length);

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
        li.append(`, ${flat(w.x)}`);
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

  // "3 · My checker" is shown as the number and the name, "3 My checker", on the kickers, the
  // agenda and the rail. The source keeps the plain form, which the gates and exports read.
  function chapterInto(node, text) {
    const m = /^(\d+)\s*·\s*(.+)$/.exec(text.trim());
    if (!m) return;
    node.textContent = "";
    html("span", { class: "num" }, node, m[1]);
    node.append(` ${m[2]}`);
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
      for (const name of chs.keys()) chapterInto(html("li", {}, ol, name), name);
    }
  }

  function buildRail(chs) {
    if (!chs.size) return;
    const rail = html("nav", { class: "rail", "aria-label": "Chapters" }, document.querySelector(".reveal"));
    for (const [name, slide] of chs) {
      const b = html("button", { type: "button", "data-chapter": name }, rail, name);
      chapterInto(b, name);
      b.addEventListener("click", () => {
        const i = Reveal.getIndices(slide);
        Reveal.slide(i.h, i.v);
      });
    }
    const sync = () => {
      const current = Reveal.getCurrentSlide();
      const c = current && current.dataset.chapter;
      rail.hidden = !c;
      for (const b of rail.children) b.setAttribute("aria-current", b.dataset.chapter === c ? "step" : "false");
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

  // <div class="forest" data-source="readings.split" data-unit="...">: a contrast and its parts,
  // each a point with its interval, on one numeric scale for every community, ticked at even steps
  // with a zero line and the unit under the ticks. The parts of a split add up to the whole; each
  // split is a fragment, and the part the claim is about is the accent mark.
  // Data: { org: { name, whole: { estimate, low, high }, <split>: [part, part] } }, the splits
  // named in data-splits, each split's accented part's index in data-accent.
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
    const lo = Math.min(0, ...cells.map((c) => c.low)), hi = Math.max(0, ...cells.map((c) => c.high));
    const pad = (hi - lo) * 0.04, d0 = lo - pad, d1 = hi + pad;
    // Ticks inside the data's range at an even step (1, 2 or 5 times a power of ten), at most
    // four of them, so their labels never touch at the plot's width.
    const mag = 10 ** Math.floor(Math.log10(hi - lo));
    const inside = (st) => Math.floor(hi / st + 1e-9) - Math.ceil(lo / st - 1e-9) + 1;
    const step = [0.1, 0.2, 0.5, 1, 2, 5, 10].map((m) => m * mag).find((st) => inside(st) <= 4);
    const ticks = [];
    for (let k = Math.ceil(lo / step - 1e-9); k <= Math.floor(hi / step + 1e-9); k++) ticks.push(k * step);
    const digits = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
    const tickText = (t) => (Math.abs(t) < step / 2 ? "0" : `${t > 0 ? "+" : "\u2212"}${Math.abs(t).toFixed(digits)}`);
    const tall = phone;
    // On a phone each row's label sits above its line, so the plot keeps the screen's width.
    const labelW = tall ? 0 : 236, plotW = tall ? 380 : 300, panelW = labelW + plotW + 20;
    const rowH = tall ? 42 : 44, groupGap = tall ? 8 : 18;
    const rowsPer = 1 + splits.reduce((r, k) => r + data[Object.keys(data)[0]][k].length, 0);
    const unit = box.dataset.unit || "";
    const foot = unit ? (tall ? 58 : 66) : 40;
    const panelH = 54 + rowsPer * rowH + splits.length * groupGap + foot;
    const W = tall ? 440 : panelW * orgs.length + 20 * (orgs.length - 1);
    const H = tall ? panelH * orgs.length : panelH;
    const fig = svg("svg", {
      viewBox: `0 0 ${W} ${H}`,
      role: "img",
      "aria-label": orgs
        .map((o) => `${o.name}: the whole gain ${tickText(o.whole.estimate)}, then ${splits.map((k) => o[k].map((p) => p.label).join(" against ")).join("; ")}`)
        .join(". ") + (unit ? `. Gains in ${unit}.` : ""),
    });
    const groups = [svg("g", {}, fig), ...splits.map(() => svg("g", { class: "fragment" }, fig))];
    orgs.forEach((o, oi) => {
      const px = tall ? 10 : oi * (panelW + 20), py = tall ? oi * panelH : 0;
      const sx = (v) => px + labelW + ((v - d0) / (d1 - d0)) * plotW;
      svg("text", { x: px, y: py + 30, class: "forest-org" }, groups[0], o.name);
      const top = py + 46, bottom = py + panelH - foot + 6;
      // A light rule at each tick and a dashed one at zero, the whole panel's height; on a phone,
      // where labels sit above their lines, the rules stop short of each label.
      for (const t of ticks) {
        if (!tall) svg("line", { x1: sx(t), x2: sx(t), y1: top, y2: bottom, class: t === 0 ? "forest-zero" : "forest-grid" }, groups[0]);
        svg("text", { x: sx(t), y: bottom + 24, class: "forest-axis", "text-anchor": "middle" }, groups[0], tickText(t));
      }
      if (unit) svg("text", { x: px + labelW + plotW, y: bottom + (tall ? 48 : 52), class: "forest-unit", "text-anchor": "end" }, groups[0], unit);
      let ry = py + 54 + rowH / 2;
      const point = (g, c, label, cls) => {
        // On a phone the label sits just above its line, clear of the dot in the row above.
        if (tall) svg("text", { x: px + 20, y: ry - 12, class: "forest-label" }, g, label);
        else svg("text", { x: px + labelW - 14, y: ry + 7, class: "forest-label", "text-anchor": "end" }, g, label);
        if (tall) for (const t of ticks) svg("line", { x1: sx(t), x2: sx(t), y1: ry - 8, y2: ry + 8, class: t === 0 ? "forest-zero" : "forest-grid" }, g);
        svg("line", { x1: sx(c.low), x2: sx(c.high), y1: ry, y2: ry, class: `forest-ci ${cls}`, "data-motion": "growx" }, g);
        svg("circle", { cx: sx(c.estimate), cy: ry, r: tall ? 7 : 9, class: `forest-pt ${cls}`, "data-motion": "pop" }, g);
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
  for (const k of document.querySelectorAll(".reveal .slides .kicker")) chapterInto(k, k.textContent);
  if (phone) document.documentElement.classList.add("phone");
  if (sideways) document.documentElement.classList.add("sideways");
  if (phone || sideways) {
    // A feed has no stepping: a fragment would hide its content and stretch the page by a screen.
    for (const f of document.querySelectorAll(".reveal .fragment")) f.classList.remove("fragment");
  }

  const scrollView = phone || sideways;

  // reveal.js 6's scroll view opens a deep link part of a page short, and scroll snap then settles
  // past the deck's middle on the slide before. Go to the slide's page directly.
  function scrollToSlide(slide) {
    const page = slide && slide.closest(".scroll-page");
    const view = document.querySelector(".reveal-viewport");
    if (page && view) view.scrollTop = page.offsetTop;
  }

  // A slide as a still thumbnail: every step shown, motion at its finished state, nothing focusable.
  function thumbnail(slide, deckW, deckH) {
    const stage = html("span", { class: "reveal", style: `--deck-w:${deckW}px;--deck-h:${deckH}px` });
    stage.inert = true;
    const copy = slide.cloneNode(true);
    copy.classList.remove("past", "future");
    copy.classList.add("present");
    copy.style.display = "block";
    copy.removeAttribute("hidden");
    copy.removeAttribute("aria-hidden");
    for (const n of copy.querySelectorAll(".fragment")) n.classList.add("visible");
    for (const n of copy.querySelectorAll(".m-go")) n.classList.remove("m-go", "m-still");
    for (const n of [copy, ...copy.querySelectorAll("[id]")]) n.removeAttribute("id");
    html("span", { class: "slides" }, stage).appendChild(copy);
    return stage;
  }

  // Every slide at once. Reveal's own overview is one long row and is off in scroll view.
  let grid = null;
  function buildGrid() {
    const { width, height } = Reveal.getConfig();
    const dialog = html("dialog", { class: "slide-grid", "aria-label": "All slides" }, document.body);
    const head = html("div", { class: "slide-grid-head" }, dialog);
    html("h2", {}, head, "All slides");
    html("button", { type: "button" }, head, "Close").addEventListener("click", () => dialog.close());
    const list = html("ol", { class: "slide-grid-list" }, dialog);
    const links = new Map();
    Reveal.getSlides().forEach((slide, n) => {
      const title = slide.querySelector("h1, h2")?.textContent.trim();
      const label = title ? `Slide ${n + 1}: ${title}` : `Slide ${n + 1}`;
      const link = html("a", { href: `#/${slide.id || n}`, "aria-label": label }, html("li", {}, list));
      html("span", { class: "slide-grid-thumb" }, link).appendChild(thumbnail(slide, width, height));
      html("span", { class: "slide-grid-num" }, link, String(n + 1));
      link.addEventListener("click", (e) => {
        e.preventDefault();
        dialog.close();
        if (scrollView) {
          scrollToSlide(slide);
        } else {
          const i = Reveal.getIndices(slide);
          Reveal.slide(i.h, i.v);
        }
      });
      links.set(slide, link);
    });
    // Reveal listens on the document: stop here, or the arrows would turn the slides behind.
    dialog.addEventListener("keydown", (e) => {
      e.stopPropagation();
      if (e.key === "o" || e.key === "O") dialog.close();
    });
    const fit = () => {
      const cell = list.querySelector(".slide-grid-thumb");
      if (cell) dialog.style.setProperty("--grid-scale", String(cell.clientWidth / width));
    };
    new ResizeObserver(fit).observe(list);
    return { dialog, links, fit };
  }

  function openGrid() {
    grid = grid || buildGrid();
    for (const link of grid.links.values()) link.removeAttribute("aria-current");
    grid.dialog.showModal();
    grid.fit();
    const here = grid.links.get(Reveal.getCurrentSlide());
    if (here) {
      here.setAttribute("aria-current", "true");
      here.focus();
      here.scrollIntoView({ block: "center" });
    }
  }

  const slidePosition = () => `${Reveal.getSlides().indexOf(Reveal.getCurrentSlide()) + 1} of ${Reveal.getTotalSlides()}`;

  // Paged slides open the grid from reveal's number. Scroll view hides that number, so it gets a button.
  function wireGrid() {
    if (scrollView) {
      const open = html("button", { type: "button", class: "slide-grid-open", "aria-haspopup": "dialog" }, document.body);
      const sync = () => {
        open.textContent = slidePosition().replace(" of ", " / ");
        open.setAttribute("aria-label", `Slide ${slidePosition()}. Show all slides`);
      };
      open.addEventListener("click", openGrid);
      Reveal.on("slidechanged", sync);
      sync();
      return;
    }
    const number = document.querySelector(".reveal .slide-number");
    if (!number) return;
    number.addEventListener("click", (e) => {
      if (!e.target.closest("a")) return;
      e.preventDefault();
      openGrid();
    });
    // Reveal rewrites the number's link on every change.
    const label = () => number.querySelector("a")?.setAttribute("aria-label", `Slide ${slidePosition()}. Show all slides`);
    new MutationObserver(label).observe(number, { childList: true });
    label();
  }

  Reveal.initialize({
    hash: true,
    overview: false,
    ...(receiver ? {} : { keyboard: { 79: openGrid } }),
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
    // The tutorial bounces the next arrow until a key is pressed, past the five-second motion rule.
    controlsTutorial: false,
    // A phone gets a portrait canvas and scroll view, and deck.css stacks the columns, so text
    // stays readable instead of a 16:9 slide shrunk to a third of its size.
    ...(phone ? { view: "scroll" } : {}),
    ...(sideways
      ? (() => {
          const fit = (innerWidth * (1 - 0.04)) / 1280;
          return { view: "scroll", scrollLayout: "compact", minScale: fit, maxScale: fit };
        })()
      : {}),
    scrollActivationWidth: null,
    plugins: [RevealNotes],
  }).then(() => {
    // Reveal's arrow <aside> would be a landmark nested in its role=application wrapper.
    document.querySelector(".reveal .controls")?.setAttribute("role", "none");
    // Safari gives a scroller no keyboard stop; add one when nothing inside can take focus.
    if (phone && !focusableInside(".reveal .slides")) {
      document.querySelector(".reveal-viewport")?.setAttribute("tabindex", "0");
    }
    if (!phone && !sideways && !receiver) buildRail(chs);
    if (!receiver) wireGrid();
    // Scroll view leaves the hash alone, so a rotation's reload would reopen the feed at slide 1.
    // Write the slide being read (its id when it has one, as reveal.js does) once the feed settles,
    // so a fast scroll makes few replaceState calls (Safari limits them), and without adding
    // history entries. Once the
    // screen has turned, a reload is coming and the feed's relayout scrolls: not the reader's slide.
    if (phone || sideways) {
      const want = decodeURIComponent(location.hash.replace(/^#\/?/, "").split("/")[0]);
      if (want) scrollToSlide(/^\d+$/.test(want) ? Reveal.getSlides()[Number(want)] : document.getElementById(want));
      const turned = () => narrow.matches !== phone || short.matches !== sideways;
      let timer = 0;
      Reveal.on("slidechanged", (e) => {
        if (turned()) return;
        clearTimeout(timer);
        timer = setTimeout(() => {
          if (!turned()) history.replaceState(null, "", `#/${e.currentSlide.id || e.indexh}`);
        }, 300);
      });
    }
  });
})();
