// Motion for the decks: plays the data-motion elements (see motion.css) when their slide opens or
// the fragment holding them appears. Loaded after deck.js. With reduced motion, on a phone, in a
// PDF export, or when a render freezes CSS animation, nothing here runs and every figure stays in
// its finished state.
(function () {
  "use strict";

  const root = document.documentElement;
  const slidesBox = document.querySelector(".reveal");

  // The deck opens out of the index preview that was clicked (browsers without view
  // transitions just navigate). The name is held only while the transition runs.
  addEventListener("pagereveal", (e) => {
    if (!e.viewTransition || !slidesBox) return;
    slidesBox.style.viewTransitionName = "talk-shot";
    e.viewTransition.finished.finally(() => (slidesBox.style.viewTransitionName = ""));
  });

  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const printing = /[?&]print-pdf/.test(location.search);
  if (reduce || printing || root.classList.contains("phone") || !window.Reveal) return;

  const probe = document.createElement("i");
  probe.className = "m-probe";
  probe.setAttribute("aria-hidden", "true");
  document.body.appendChild(probe);
  // A renderer that freezes animation (the slide checks and exports) turns this off.
  const animating = () => getComputedStyle(probe).animationName !== "none";

  // data-delay / dur / step are milliseconds; data-i is the stagger position.
  const PROPS = { delay: "--m-delay", dur: "--m-d", step: "--m-step", i: "--i", iter: "--m-iter", origin: "--m-origin", dir: "--m-dir" };

  for (const box of document.querySelectorAll('[data-motion="stagger"]')) {
    [...box.children].forEach((child, i) => {
      if (!child.dataset.motion) child.dataset.motion = box.dataset.child || "rise";
      if (child.dataset.i === undefined) child.style.setProperty("--i", i);
    });
  }
  const all = [...document.querySelectorAll("[data-motion]")];
  for (const el of all) {
    for (const [attr, prop] of Object.entries(PROPS)) {
      const v = el.dataset[attr];
      if (v === undefined) continue;
      el.style.setProperty(prop, /^[\d.]+$/.test(v) && !["i", "iter"].includes(attr) ? `${v}ms` : v);
    }
    if (el.dataset.motion === "draw") el.setAttribute("pathLength", "1");
    if (el.dataset.motion === "flow" && el.dataset.path) el.style.offsetPath = `path("${el.dataset.path}")`;
    if (el.dataset.motion === "count") el.dataset.final = el.textContent;
  }
  const inSlide = (slide) => all.filter((el) => slide.contains(el));
  const fragmentOf = (el) => el.closest(".fragment");

  // Counts up to the text the deck bound, then puts that exact text back.
  const counting = new Map();
  function stopCount(el) {
    cancelAnimationFrame(counting.get(el));
    counting.delete(el);
    el.textContent = el.dataset.final;
  }
  function startCount(el) {
    const final = el.dataset.final;
    const found = final.match(/\d[\d,]*(?:\.(\d+))?/);
    if (!found || !animating()) return;
    const target = parseFloat(found[0].replace(/,/g, ""));
    const places = found[1] ? found[1].length : 0;
    const grouped = found[0].includes(",");
    const fmt = (v) =>
      v.toLocaleString("en-US", { minimumFractionDigits: places, maximumFractionDigits: places, useGrouping: grouped });
    const dur = Number(el.dataset.dur) || 900;
    const delay = Number(el.dataset.delay) || 0;
    const t0 = performance.now() + delay;
    el.textContent = final.replace(found[0], fmt(0));
    const tick = (now) => {
      const p = Math.min(1, Math.max(0, (now - t0) / dur));
      if (p >= 1) return stopCount(el);
      el.textContent = final.replace(found[0], fmt(target * (1 - Math.pow(1 - p, 3))));
      counting.set(el, requestAnimationFrame(tick));
    };
    counting.set(el, requestAnimationFrame(tick));
  }

  function set(el, on, still) {
    if (on === el.classList.contains("m-go")) return;
    el.classList.toggle("m-go", on);
    el.classList.toggle("m-still", on && !!still);
    if (el.dataset.motion !== "count") return;
    if (on) { if (!still) startCount(el); }
    else if (counting.has(el)) stopCount(el);
  }

  // Elements outside any fragment play with the slide; the rest wait for their fragment.
  function sync(slide, still) {
    for (const el of inSlide(slide)) {
      const f = fragmentOf(el);
      set(el, !f || f.classList.contains("visible"), still);
    }
  }

  function clear(slide) {
    for (const el of inSlide(slide)) set(el, false);
  }

  root.classList.add("m-live");
  Reveal.on("ready", (e) => sync(e.currentSlide));
  if (Reveal.isReady()) sync(Reveal.getCurrentSlide());
  Reveal.on("fragmentshown", () => sync(Reveal.getCurrentSlide()));
  Reveal.on("fragmenthidden", () => sync(Reveal.getCurrentSlide()));
  Reveal.on("slidechanged", (e) => {
    const { previousSlide: prev, currentSlide: now } = e;
    if (prev) {
      // Reset after the fade, so a slide never un-builds in front of the room.
      setTimeout(() => {
        if (Reveal.getCurrentSlide() !== prev) clear(prev);
      }, 450);
    }
    const back = prev && Reveal.getIndices(now).h < Reveal.getIndices(prev).h;
    // Stepping back to a slide shows it as it was left: built, not replayed.
    sync(now, back);
  });
})();
