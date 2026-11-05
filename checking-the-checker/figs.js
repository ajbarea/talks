// This talk's figures, drawn from data/deck-data.js before ../shared/deck.js binds values and starts
// reveal.js, so their data-value labels and fragments are bound and counted like hand-written ones.
// A count a slide title states in words is recounted from the data here; a mismatch is a console
// error, which the slide gates block.
(function () {
  "use strict";

  const DATA = window.DECK_DATA || {};
  const get = (path) => path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), DATA);
  const fail = (msg) => console.error(`figs: ${msg}`);

  function el(name, attrs, parent, text) {
    const node = document.createElement(name);
    for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
    if (text !== undefined) node.textContent = text;
    if (parent) parent.appendChild(node);
    return node;
  }

  // <div data-bars="cases">: one row per case, bar length to scale with the longest.
  function caseBars(box) {
    const cases = get(box.dataset.bars) || [];
    const most = Math.max(...cases.map((c) => c.days));
    cases.forEach((c, i) => {
      const row = el("div", { class: `bar-row g-${c.group}` }, box);
      el("span", { class: "case-n", "aria-hidden": "true" }, row, String(c.n));
      el("span", { class: "bar-label" }, row, c.what);
      const track = el("span", { class: "bar-track", "aria-hidden": "true" }, row);
      el("span", { class: "bar-fill", style: `width:${(c.days / most) * 100}%`, "data-motion": "growx", "data-i": i }, track);
      el("span", { class: "bar-value", "data-value": `${box.dataset.bars}.${i}.shown` }, row);
    });
  }

  // <div data-columns="rebreak.mutations" data-tests="rebreak.tests">: one column per mutation,
  // height to scale with the most tests failed, grouped by case; a mutation no test caught is an
  // empty dashed column.
  function rebreakColumns(box) {
    const muts = get(box.dataset.columns) || [];
    const most = Math.max(...muts.map((m) => m.failed));
    const caught = muts.filter((m) => m.failed > 0).length;
    if (caught !== get("rebreak.caught") || muts.length !== get("rebreak.total")) {
      fail(`rebreak: ${caught} of ${muts.length} caught in the mutations, not the counts the title states`);
    }
    const plot = el("div", { class: "cols", "aria-hidden": "true" }, box);
    let group;
    let last;
    muts.forEach((m, i) => {
      if (m.n !== last) {
        group = el("div", { class: `col-group g-${m.group}` }, plot);
        el("div", { class: "col-bars" }, group);
        const label = el("span", { class: "col-case" }, group);
        el("span", { class: "col-word" }, label, "Case ");
        label.append(String(m.n));
        last = m.n;
      }
      const bars = group.querySelector(".col-bars");
      const col = el("div", { class: m.failed ? "col" : "col miss" }, bars);
      el("span", { class: "col-num" }, col, m.failed ? String(m.failed) : "✕");
      el("span", {
        class: "col-fill",
        style: `height:${m.failed ? (m.failed / most) * 100 : 100}%`,
        ...(m.failed ? { "data-motion": "grow", "data-i": i } : {}),
      }, col);
    });
    const misses = el("ul", { class: "misses" }, box);
    muts.forEach((m, i) => {
      if (!m.failed) {
        const li = el("li", {}, misses);
        el("b", {}, li, `Case ${m.n} missed: `);
        el("span", { "data-value": `${box.dataset.columns}.${i}.miss` }, li);
      }
    });
  }

  // <table data-matrix="checkers.tools" data-clean=... data-all=... data-count=...>: one row per tool, one cell per fault. The marks repeat the
  // colour as a symbol, so the table reads the same without colour.
  const MARK = { bad: "✕", good: "✓", warn: "!", mixed: "~", none: "–" };
  function matrix(table) {
    const tools = get(table.dataset.matrix) || [];
    const clean = tools.filter((t) => t.cells.slice(0, 2).some((c) => c.clean)).length;
    const all = tools.filter((t) => t.cells[2].all).length;
    if (clean !== get(table.dataset.clean)) fail(`checkers: ${clean} clean after nothing, not the title's count`);
    if (all !== get(table.dataset.all)) fail(`checkers: ${all} reported all as not found, not the stated count`);
    if (tools.length !== get(table.dataset.count)) fail(`checkers: ${tools.length} tools, not the stated count`);
    const heads = [...table.querySelectorAll("thead th")].slice(1).map((th) => th.dataset.short || th.textContent);
    const body = el("tbody", {}, table);
    tools.forEach((t, i) => {
      // A tool that printed a clean result after checking nothing is the slide's point: its row is marked.
      const tr = el("tr", t.cells.slice(0, 2).some((c) => c.clean) ? { class: "clean-nothing" } : {}, body);
      el("th", { scope: "row", "data-value": `${table.dataset.matrix}.${i}.name` }, tr);
      t.cells.forEach((c, j) => {
        const td = el("td", { class: `k-${c.kind}${j === 2 ? " fragment" : ""}`, "data-label": heads[j] }, tr);
        if (j === 2) td.setAttribute("data-fragment-index", "1");
        el("span", { class: "mark", "aria-hidden": "true" }, td, MARK[c.kind]);
        el("span", { "data-value": `${table.dataset.matrix}.${i}.cells.${j}.text` }, td);
      });
    });
  }

  // <span data-bar="field.papersAfter" data-scale="2">: a bar as long as its value on that scale.
  // <span data-range="field.modelLow field.modelHigh" data-scale="100">: a bar from one value to the other.
  function sized() {
    for (const node of document.querySelectorAll("[data-bar]")) {
      node.style.width = `${(get(node.dataset.bar) / Number(node.dataset.scale)) * 100}%`;
    }
    for (const node of document.querySelectorAll("[data-range]")) {
      const [lo, hi] = node.dataset.range.split(" ").map(get);
      const s = Number(node.dataset.scale);
      node.style.left = `${(lo / s) * 100}%`;
      node.style.width = `${((hi - lo) / s) * 100}%`;
    }
  }

  // <div data-runs="case6.runs" data-of="case6.entries">: one bar per run, out of every entry.
  function runs(box) {
    const all = get(box.dataset.runs) || [];
    all.forEach((v, i) => {
      const row = el("div", { class: "bar-row g-report" }, box);
      el("span", { class: "bar-label" }, row, `Run ${i + 1}`);
      const track = el("span", { class: "bar-track", "aria-hidden": "true" }, row);
      el("span", { class: "bar-fill", style: `width:${(v / get(box.dataset.of)) * 100}%` }, track);
      el("span", { class: "bar-value", "data-value": `${box.dataset.runs}.${i}` }, row);
    });
  }

  document.querySelectorAll("[data-bars]").forEach(caseBars);
  document.querySelectorAll("[data-columns]").forEach(rebreakColumns);
  document.querySelectorAll("[data-matrix]").forEach(matrix);
  document.querySelectorAll("[data-runs]").forEach(runs);
  sized();
})();
