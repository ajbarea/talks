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
  const live = root.querySelector("[aria-live]");
  const prev = root.querySelector(".prev");
  const next = root.querySelector(".next");
  const dots = root.querySelector(".dots");
  const title = (s) => s.querySelector("h2").textContent.trim();

  root.setAttribute("aria-roledescription", "carousel");
  slides.forEach((s, i) => {
    const pos = document.createElement("span");
    pos.className = "sr-only";
    pos.id = `pos-${s.dataset.name}`;
    pos.textContent = `, ${i + 1} of ${n}`;
    s.querySelector("h2").after(pos);
    s.setAttribute("role", "group");
    s.setAttribute("aria-roledescription", "slide");
    s.setAttribute("aria-labelledby", `title-${s.dataset.name} ${pos.id}`);
    const dot = document.createElement("button");
    dot.type = "button";
    dot.tabIndex = -1;
    dot.addEventListener("click", () => go(i));
    dots.append(dot);
  });
  prev.hidden = next.hidden = dots.hidden = false;

  // Geometry, read once and again only when the strip changes size: the strip scrolls one slot per talk.
  let slot = slides[0].offsetWidth;
  const left = (i) => slides[i].offsetLeft + slot / 2 - strip.clientWidth / 2;
  const nearest = () => Math.max(0, Math.min(n - 1, Math.round((strip.scrollLeft - left(0)) / slot)));

  let current = -1;
  let target = null; // where keys and the wheel are taking the strip, so presses add up mid-glide
  const go = (i, smooth = !reduce.matches) => {
    target = Math.max(0, Math.min(n - 1, i));
    strip.scrollTo({ left: left(target), behavior: smooth ? "smooth" : "instant" });
  };
  const step = (d) => go((target ?? current) + d);

  // The preview loop plays only on the centered talk, and only once it is loaded, so the cover never blanks.
  let loading = null;
  const play = (s) => {
    const img = s.querySelector("img[data-loop]");
    if (!img || reduce.matches) return;
    const loop = new Image();
    loading = loop;
    loop.src = img.dataset.loop;
    loop.decode().then(() => {
      if (loading === loop && slides[current] === s) img.src = loop.src;
    }, () => {});
  };
  const still = (s) => {
    const img = s.querySelector("img[data-loop]");
    if (img) img.src = img.getAttribute("src").replace(/thumb-loop\.webp$/, "thumb.webp");
  };

  // A talk is centered once the strip comes to rest: only then do the hidden talks change and the change is read out.
  const settle = (announce) => {
    const i = nearest();
    target = null;
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
      if (!here) still(s);
    });
    prev.setAttribute("aria-disabled", i === 0 ? "true" : "false");
    next.setAttribute("aria-disabled", i === n - 1 ? "true" : "false");
    mark(i);
    play(slides[i]);
    if (focused) {
      // Keep focus on the same control of the new centered talk instead of losing it to the page.
      const kind = focused.matches(".open") ? ".open" : focused.closest("h2") ? "h2 a" : ".open";
      slides[i].querySelector(kind).focus({ preventScroll: true });
    }
    if (announce) {
      live.textContent = `${title(slides[i])}, ${i + 1} of ${n}`;
      history.replaceState(history.state, "", `#${slides[i].dataset.name}`);
    }
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

  let rest = 0;
  let queued = false;
  strip.addEventListener("scroll", () => {
    if (!timelines && !queued) {
      queued = true;
      requestAnimationFrame(() => { queued = false; mark(nearest()); });
    }
    clearTimeout(rest);
    rest = setTimeout(() => !dragging && settle(true), "onscrollend" in window ? 600 : 120);
  }, { passive: true });
  strip.addEventListener("scrollend", () => {
    if (dragging) return;
    clearTimeout(rest);
    settle(true);
  });

  prev.addEventListener("click", () => prev.getAttribute("aria-disabled") !== "true" && step(-1));
  next.addEventListener("click", () => next.getAttribute("aria-disabled") !== "true" && step(1));

  // Arrow keys glide from anywhere on the page that is not a form field; Home and End inside the carousel.
  document.addEventListener("keydown", (e) => {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const t = e.target;
    const inside = root.contains(t);
    if (!inside && t !== document.body && t !== document.documentElement) return;
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
  let dragging = false;
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
      const land = () => { clearTimeout(late); strip.classList.remove("dragging"); };
      const late = setTimeout(land, 900);
      strip.addEventListener("scrollend", land, { once: true });
    };
    strip.addEventListener("pointermove", move);
    strip.addEventListener("pointerup", up);
    strip.addEventListener("pointercancel", up);
  });

  // A vertical wheel over the stage steps one talk per notch or per trackpad gesture; at either end the page
  // scrolls on. Sideways trackpad swipes scroll the strip natively.
  let lastWheel = 0, lastStep = 0, lastAbs = 0;
  strip.addEventListener("wheel", (e) => {
    if (e.ctrlKey || Math.abs(e.deltaX) >= Math.abs(e.deltaY) || e.target.closest(".about")) return;
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

  new ResizeObserver(() => {
    slot = slides[0].offsetWidth;
    if (current >= 0) strip.scrollTo({ left: left(current), behavior: "instant" });
  }).observe(strip);
  reduce.addEventListener("change", () => (reduce.matches ? slides.forEach(still) : play(slides[current])));

  // Open on the talk named in the address, else the middle one, with nothing read out.
  const named = slides.findIndex((s) => `#${s.dataset.name}` === location.hash);
  strip.scrollLeft = left(named >= 0 ? named : Math.floor((n - 1) / 2));
  settle(false);

  // The talk opens out of the cover that was clicked.
  addEventListener("pageswap", (e) => {
    if (!e.viewTransition || !e.activation || !e.activation.entry) return;
    const path = new URL(e.activation.entry.url).pathname;
    for (const cover of strip.querySelectorAll(".cover")) {
      if (new URL(cover.href).pathname === path) cover.style.viewTransitionName = "talk-shot";
    }
  });
})();
