// Tips for any element with data-tip="summary" (plus data-tip-title, data-tip-chip, data-tip-tone).
// One card per trigger, in the top layer; the trigger gets aria-describedby, and its native title
// is removed. Hover opens after a short delay, keyboard focus opens at once, a tap toggles.
// Escape closes it, and the pointer can cross onto the tip. Nothing runs in a print export.
(function () {
  "use strict";

  if (/[?&]print-pdf/.test(location.search)) return;
  const triggers = [...document.querySelectorAll("[data-tip]")];
  if (!triggers.length) return;

  const OPEN_DELAY = 140, CLOSE_DELAY = 200, EDGE = 8, GAP = 12;
  const EASE = "cubic-bezier(0.22, 0.8, 0.3, 1)";
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  // window.__tipJs forces the hand placement, for tests of the fallback.
  const byCss = !window.__tipJs && CSS.supports("position-area: top") && CSS.supports("anchor-name: --a");
  const native = "showPopover" in HTMLElement.prototype;

  function make(name, cls, parent, text) {
    const n = document.createElement(name);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    if (parent) parent.appendChild(n);
    return n;
  }

  const anchor = make("i", "tip-anchor", document.body);
  anchor.setAttribute("aria-hidden", "true");
  const parts = new Map();
  let current = null, openTimer = 0, closeTimer = 0, lastType = "mouse", hovered = null;

  triggers.forEach((t, n) => {
    t.removeAttribute("title");
    for (const title of t.querySelectorAll(":scope > title")) title.remove();
    const tip = make("div", "tip", document.body);
    tip.id = `tip-${n}`;
    tip.setAttribute("role", "tooltip");
    if (native) tip.setAttribute("popover", "manual");
    if (t.dataset.tipTone) tip.dataset.tone = t.dataset.tipTone;
    if (!byCss) tip.classList.add("tip-js");
    const head = make("span", "tip-head", tip);
    if (t.dataset.tipTitle) make("b", "tip-name", head, t.dataset.tipTitle);
    if (t.dataset.tipChip) make("span", "tip-chip", head, t.dataset.tipChip);
    make("p", "tip-text", tip, t.dataset.tip);
    make("span", "tip-arrow", tip).setAttribute("aria-hidden", "true");
    t.setAttribute("aria-describedby", tip.id);
    parts.set(t, { tip, anim: null });

    t.addEventListener("pointerenter", (e) => {
      if (e.pointerType === "touch") return;
      hovered = t;
      clearTimeout(closeTimer);
      if (current === t) return;
      clearTimeout(openTimer);
      openTimer = setTimeout(() => show(t), current ? 0 : OPEN_DELAY);
    });
    t.addEventListener("pointerleave", (e) => {
      if (e.pointerType === "touch") return;
      if (hovered === t) hovered = null;
      clearTimeout(openTimer);
      later(t);
    });
    tip.addEventListener("pointerenter", () => clearTimeout(closeTimer));
    tip.addEventListener("pointerleave", () => later(t));
    t.addEventListener("focusin", () => {
      if (t.matches(":focus-visible")) show(t);
    });
    t.addEventListener("focusout", () => later(t));
    t.addEventListener("click", () => {
      if (lastType === "mouse") return;
      current === t ? close(t) : show(t);
    });
  });

  // A tip stays while the pointer is on the dot or the tip, or the dot has keyboard focus.
  function later(t) {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      if (t.matches(":focus-visible") || hovered === t || parts.get(t).tip.matches(":hover")) return;
      close(t);
    }, CLOSE_DELAY);
  }

  function open(tip) {
    if (!native) return tip.classList.add("tip-open");
    if (!tip.matches(":popover-open")) tip.showPopover();
  }

  function hide(tip) {
    if (!native) return tip.classList.remove("tip-open");
    if (tip.matches(":popover-open")) tip.hidePopover();
  }

  function show(t) {
    clearTimeout(closeTimer);
    if (current === t) return;
    if (current) close(current, true);
    const p = parts.get(t);
    current = t;
    if (p.anim) p.anim.cancel();
    open(p.tip);
    t.classList.add("tip-on");
    const side = place(t);
    if (still.matches) return;
    const dy = side === "top" ? 7 : -7;
    p.tip.style.transformOrigin = `var(--tip-ax) ${side === "top" ? "100%" : "0"}`;
    p.anim = p.tip.animate(
      [{ opacity: 0, transform: `translateY(${dy}px) scale(0.95)` }, { opacity: 1, transform: "none" }],
      { duration: 170, easing: EASE },
    );
  }

  function close(t, instant) {
    const p = parts.get(t);
    t.classList.remove("tip-on");
    if (current === t) current = null;
    if (p.anim) p.anim.cancel();
    if (instant || still.matches) return hide(p.tip);
    p.anim = p.tip.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 90, easing: "ease-in" });
    p.anim.onfinish = () => hide(p.tip);
  }

  // Points the anchor at the trigger's mark, then reads back where the tip landed (the browser
  // may have flipped it) so the arrow faces the dot. Returns the side the tip is on.
  function place(t) {
    const tip = parts.get(t).tip;
    const a = (t.querySelector("[data-tip-anchor]") || t).getBoundingClientRect();
    anchor.style.cssText = `left:${a.left}px;top:${a.top}px;width:${a.width}px;height:${a.height}px`;
    const cx = a.left + a.width / 2;
    if (!byCss) {
      const w = tip.offsetWidth, h = tip.offsetHeight;
      const above = a.top - GAP - h >= EDGE;
      const x = Math.min(Math.max(cx - w / 2, EDGE), innerWidth - w - EDGE);
      tip.style.setProperty("--tip-x", `${x}px`);
      tip.style.setProperty("--tip-y", `${above ? a.top - GAP - h : a.bottom + GAP}px`);
    }
    const r = tip.getBoundingClientRect();
    const side = r.bottom <= a.top + a.height / 2 ? "top" : "bottom";
    tip.dataset.side = side;
    tip.style.setProperty("--tip-ax", `${Math.min(Math.max(cx - r.left, 18), r.width - 18)}px`);
    return side;
  }

  addEventListener("pointerdown", (e) => {
    lastType = e.pointerType || "mouse";
    if (!current) return;
    if (current.contains(e.target) || parts.get(current).tip.contains(e.target)) return;
    close(current);
  }, true);

  // Capture phase, so reveal.js never sees the Escape that closes a tip, or the Space and Enter
  // that toggle one.
  addEventListener("keydown", (e) => {
    if (e.key === "Escape" && current) {
      e.preventDefault();
      e.stopPropagation();
      close(current);
    } else if ((e.key === "Enter" || e.key === " ") && parts.has(e.target)) {
      e.preventDefault();
      e.stopPropagation();
      current === e.target ? close(e.target) : show(e.target);
    }
  }, true);

  const follow = () => current && place(current);
  addEventListener("resize", follow);
  addEventListener("scroll", follow, { capture: true, passive: true });
  if (window.Reveal) {
    Reveal.on("slidechanged", () => current && close(current, true));
    Reveal.on("resize", follow);
  }
})();
