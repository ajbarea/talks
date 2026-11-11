// The talks as a cover flow: a carousel in the WAI-ARIA APG pattern over a native scroll-snap strip.
// The strip's own scrolling (touch, trackpad, keys) moves the covers and CSS view timelines turn them; this
// script only names the centered talk once a glide settles, adds keys, mouse drag, the wheel and a click on a
// side cover, and plays the centered talk's preview loop.
(() => {
  const root = document.getElementById("talks");
  const strip = root && root.querySelector(".covers");
  const slides = strip ? [...strip.children] : [];
  if (!slides.length) return document.documentElement.classList.remove("flow");
  const n = slides.length;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const timelines = CSS.supports("animation-timeline: view()");
  const scrollend = "onscrollend" in window;
  const live = root.querySelector("[aria-live]");
  const prev = root.querySelector(".prev");
  const next = root.querySelector(".next");
  const dots = root.querySelector(".dots");
  const title = (s) => s.querySelector("h2").textContent.trim();

  root.setAttribute("aria-roledescription", "carousel");
  slides.forEach((s, i) => {
    s.setAttribute("role", "group");
    s.setAttribute("aria-roledescription", "slide");
    s.setAttribute("aria-label", `${title(s)}, ${i + 1} of ${n}`);
    const dot = document.createElement("button");
    dot.type = "button";
    dot.tabIndex = -1;
    dot.addEventListener("click", () => go(i));
    dots.append(dot);
  });
  if (n > 1) prev.hidden = next.hidden = dots.hidden = false;
  // A pointer press on a cover or a dot never takes focus: both sit in hidden content, and focus already in
  // the carousel is carried to the new centered talk when it settles.
  for (const el of [strip, dots]) {
    el.addEventListener("mousedown", (e) => e.target.closest(".cover, button") && e.preventDefault());
  }

  // Geometry, read once and again only when the strip changes size: the strip scrolls one slot per talk.
  let slot = slides[0].offsetWidth;
  const left = (i) => slides[i].offsetLeft + slot / 2 - strip.clientWidth / 2;
  const nearest = () => (slot > 0 ? Math.max(0, Math.min(n - 1, Math.round((strip.scrollLeft - left(0)) / slot))) : 0);

  let current = -1;
  let target = null; // where keys and the wheel are taking the strip, so presses add up mid-glide
  const go = (i, smooth = !reduce.matches) => {
    target = Math.max(0, Math.min(n - 1, i));
    strip.scrollTo({ left: left(target), behavior: smooth ? "smooth" : "instant" });
  };
  const step = (d) => go((target ?? current) + d);

  // The preview loop plays only on the centered talk, once it has decoded, so the cover never blanks.
  let loading = null;
  const play = (s) => {
    const img = s.querySelector("img[data-loop]");
    if (!img || reduce.matches) return;
    const loop = new Image();
    loading = loop;
    loop.src = img.dataset.loop;
    loop.decode().then(() => {
      if (loading === loop && slides[current] === s && !reduce.matches) img.src = loop.src;
    }, () => {});
  };
  const still = (s) => {
    const img = s && s.querySelector("img[data-loop]");
    if (img && img.src.endsWith("thumb-loop.webp")) img.src = img.src.replace(/thumb-loop\.webp$/, "thumb.webp");
  };

  // A resize or zoom moves the snap points: the centered talk stays centered, so nothing else changes.
  let width = strip.clientWidth;
  const keep = () => {
    const w = strip.clientWidth;
    const s = slides[0].offsetWidth; // the slot follows the window's height too
    if (current < 0 || (w === width && s === slot)) return;
    width = w;
    slot = s;
    strip.scrollTo({ left: left(current), behavior: "instant" });
  };

  // A talk is centered once the strip comes to rest: only then do the hidden talks change and the change is read out.
  const settle = (announce) => {
    target = null;
    const i = nearest();
    if (i === current) return;
    const old = slides[current];
    const focused = old && old.contains(document.activeElement) ? document.activeElement : null;
    current = i;
    slides.forEach((s, k) => {
      const here = k === i;
      if (here) s.removeAttribute("aria-hidden");
      else s.setAttribute("aria-hidden", "true");
      s.querySelector(".about").inert = !here;
      dots.children[k].setAttribute("aria-current", here ? "true" : "false");
    });
    dots.style.setProperty("--at", i);
    still(old);
    prev.setAttribute("aria-disabled", i === 0 ? "true" : "false");
    next.setAttribute("aria-disabled", i === n - 1 ? "true" : "false");
    mark(i);
    if (document.readyState === "complete") play(slides[i]);
    if (focused) {
      // Keep focus on the same control of the new centered talk instead of losing it to the page; moving
      // focus into the new slide already reads its name, so the live region stays quiet.
      slides[i].querySelector(focused.closest("h2") ? "h2 a" : ".open").focus({ preventScroll: true });
    } else if (announce) {
      live.textContent = `${title(slides[i])}, ${i + 1} of ${n}`;
    }
    if (announce) history.replaceState(history.state, "", `#${slides[i].dataset.name}`);
  };

  // Without view timelines the covers turn by class, set whenever the nearest talk changes mid-glide.
  let marked = -1;
  const mark = (c) => {
    if (timelines || c === marked) return;
    marked = c;
    slides.forEach((s, k) => {
      s.classList.toggle("here", k === c);
      s.classList.toggle("left", k < c);
      s.style.setProperty("--far", Math.abs(k - c));
    });
  };

  // Settling waits for scrollend; a per-frame scroll listener runs only where scrollend or view timelines lack.
  let dragging = false;
  if (!timelines || !scrollend) {
    let rest = 0;
    let queued = false;
    strip.addEventListener("scroll", () => {
      if (!timelines && !queued) {
        queued = true;
        requestAnimationFrame(() => { queued = false; mark(nearest()); });
      }
      if (scrollend) return;
      clearTimeout(rest);
      rest = setTimeout(() => !dragging && settle(true), 120);
    }, { passive: true });
  }
  strip.addEventListener("scrollend", () => !dragging && settle(true));

  prev.addEventListener("click", () => prev.getAttribute("aria-disabled") !== "true" && step(-1));
  next.addEventListener("click", () => next.getAttribute("aria-disabled") !== "true" && step(1));

  // Arrow keys glide from inside the carousel, or from the page while the stage is in view; Home and End inside.
  let inView = true;
  const seen = new IntersectionObserver(([e]) => { inView = e.isIntersecting; }, { threshold: 0.15 });
  seen.observe(root.querySelector(".stage"));
  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const t = e.target;
    const inside = root.contains(t);
    if (!inside && !(inView && (t === document.body || t === document.documentElement))) return;
    if (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
    const d = { ArrowLeft: -1, ArrowRight: 1 }[e.key];
    if (d) step(d);
    else if (inside && e.key === "Home") go(0);
    else if (inside && e.key === "End") go(n - 1);
    else return;
    e.preventDefault();
  });

  // A click on a side cover brings it to the center; a click on the centered cover opens the deck.
  let dragged = false;
  strip.addEventListener("click", (e) => {
    const s = e.target.closest(".talk");
    const cover = e.target.closest(".cover");
    if (dragged) { e.preventDefault(); dragged = false; return; }
    if (!s || !cover) return;
    const i = slides.indexOf(s);
    if (i !== nearest()) { e.preventDefault(); go(i); }
  });

  // A mouse drags the strip like a finger: it follows the pointer, then glides on by the release speed.
  let x0 = 0, s0 = 0, trail = [];
  strip.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse" || e.button !== 0 || e.target.closest(".about")) return;
    x0 = e.clientX; s0 = strip.scrollLeft; trail = [[e.timeStamp, e.clientX]]; dragged = false;
    const move = (m) => {
      if (!dragging && Math.abs(m.clientX - x0) < 5) return;
      if (!dragging) { dragging = true; strip.classList.add("dragging"); strip.setPointerCapture(e.pointerId); }
      strip.scrollLeft = s0 - (m.clientX - x0);
      trail.push([m.timeStamp, m.clientX]);
      if (trail.length > 6) trail.shift();
    };
    const up = (u) => {
      strip.removeEventListener("pointermove", move);
      strip.removeEventListener("pointerup", up);
      strip.removeEventListener("pointercancel", up);
      if (!dragging) return;
      dragged = u.type === "pointerup";
      const [t1, x1] = trail[0];
      const v = (u.clientX - x1) / Math.max(1, u.timeStamp - t1); // px per ms, positive to the right
      const at = (strip.scrollLeft - left(0)) / slot;
      const fling = Math.max(-2, Math.min(2, (-v * 180) / slot));
      dragging = false;
      go(Math.round(at + fling));
      // Snapping comes back once the glide has landed on its talk, so it never jumps mid-glide.
      // A release that lands exactly on a talk scrolls nowhere, so no scrollend comes: settle here too.
      const land = () => { clearTimeout(late); strip.classList.remove("dragging"); settle(true); };
      const late = setTimeout(land, 900);
      strip.addEventListener("scrollend", land, { once: true });
    };
    strip.addEventListener("pointermove", move);
    strip.addEventListener("pointerup", up);
    strip.addEventListener("pointercancel", up);
  });

  // A vertical wheel over the covers steps one talk per notch or per trackpad gesture; at either end, and
  // anywhere off the covers, the page scrolls on. Sideways trackpad swipes scroll the strip natively.
  let lastWheel = 0, lastStep = 0, lastAbs = 0;
  strip.addEventListener("wheel", (e) => {
    if (e.ctrlKey || Math.abs(e.deltaX) >= Math.abs(e.deltaY) || e.target.closest(".about")) return;
    const row = slides[Math.max(0, current)].querySelector(".cover").getBoundingClientRect();
    if (e.clientY < row.top || e.clientY > row.bottom) return;
    const d = Math.sign(e.deltaY);
    const to = (target ?? current) + d;
    if (to < 0 || to >= n) return;
    e.preventDefault();
    const abs = Math.abs(e.deltaY);
    const notch = e.deltaMode !== 0 || abs % 100 === 0 || abs % 120 === 0;
    const fresh = e.timeStamp - lastWheel > 160 || abs > lastAbs * 1.5;
    if ((notch && e.timeStamp - lastStep > 90) || (fresh && e.timeStamp - lastStep > 260)) {
      step(d);
      lastStep = e.timeStamp;
    }
    lastWheel = e.timeStamp;
    lastAbs = abs;
  }, { passive: false });

  new ResizeObserver(keep).observe(strip);
  addEventListener("resize", keep);
  reduce.addEventListener("change", () => (reduce.matches ? still(slides[current]) : play(slides[current])));
  // A link to another talk on this page, followed or typed, glides to it.
  addEventListener("hashchange", () => {
    const i = slides.findIndex((s) => `#${s.dataset.name}` === location.hash);
    if (i >= 0 && i !== current) go(i);
  });

  // Open on the talk named in the address, else the middle one, with nothing read out; its loop waits for load.
  const named = slides.findIndex((s) => `#${s.dataset.name}` === location.hash);
  strip.scrollLeft = left(named >= 0 ? named : Math.floor((n - 1) / 2));
  settle(false);
  if (document.readyState === "complete") play(slides[current]);
  else addEventListener("load", () => play(slides[current]), { once: true });

  // The talk opens out of the cover that was clicked.
  addEventListener("pageswap", (e) => {
    if (!e.viewTransition || !e.activation || !e.activation.entry) return;
    const path = new URL(e.activation.entry.url).pathname;
    for (const cover of strip.querySelectorAll(".cover")) {
      if (new URL(cover.href).pathname === path) cover.style.viewTransitionName = "talk-shot";
    }
  });
})();
