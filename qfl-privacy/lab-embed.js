// The live lab on the lab slides: the lab page (lab/index.html) in a frame, at the slide's tab.
// From a file, on a phone and in print (deck.css), the slide shows the paper's figure and a link.
// A frame loads the first time its slide is shown; the speaker view's previews show the still.
// The page reports its height, so the frame fits it, and hands back the keys a presenter's
// clicker sends, so the next press turns the slide even after a click inside the lab.
(function () {
  "use strict";

  const receiver = /receiver/i.test(location.search);
  const frames = [...document.querySelectorAll("iframe.lab-frame[data-lab-src]")];
  if (!frames.length || !window.Reveal) return;
  // Opened from a file (the exported PDF and slides), or on a phone, where the scaled slide would
  // draw the panel's small text under 10px: the paper's figure and a link to the lab page, which
  // has its own phone layout. The phone and sideways tests are deck.js's own.
  const phone = matchMedia("(max-width: 600px)").matches && !receiver;
  const short = matchMedia("(max-height: 500px) and (pointer: coarse) and (orientation: landscape)");
  const sideways = short.matches && !phone && !receiver && innerWidth / innerHeight > 1.9;
  if (location.protocol === "file:" || receiver || phone || sideways) {
    document.documentElement.classList.add("lab-still");
    return;
  }

  const load = () => {
    const slide = Reveal.getCurrentSlide();
    for (const f of frames) if (!f.src && slide && slide.contains(f)) f.src = f.dataset.labSrc;
  };
  Reveal.on("ready", load);
  Reveal.on("slidechanged", load);

  // The same moves Reveal's own keyboard makes: in a deck without vertical stacks every arrow
  // steps through the slides in order, and Shift jumps to an end.
  const linear = () =>
    Reveal.getConfig().navigationMode === "linear" || !Reveal.hasHorizontalSlides() || !Reveal.hasVerticalSlides();
  const last = () => Reveal.getHorizontalSlides().length - 1;
  const KEYS = {
    PageDown: () => Reveal.next(), n: () => Reveal.next(), PageUp: () => Reveal.prev(), p: () => Reveal.prev(),
    " ": (shift) => (shift ? Reveal.prev() : Reveal.next()),
    ArrowRight: (shift) => (shift ? Reveal.slide(last()) : linear() ? Reveal.next() : Reveal.right()),
    ArrowLeft: (shift) => (shift ? Reveal.slide(0) : linear() ? Reveal.prev() : Reveal.left()),
    ArrowDown: (shift) => (shift ? Reveal.slide(undefined, Number.MAX_VALUE) : linear() ? Reveal.next() : Reveal.down()),
    ArrowUp: (shift) => (shift ? Reveal.slide(undefined, 0) : linear() ? Reveal.prev() : Reveal.up()),
    b: () => Reveal.togglePause(), ".": () => Reveal.togglePause(),
  };
  window.addEventListener("message", (e) => {
    // Only this deck's own lab frames, from its own origin, may steer it.
    if (e.origin !== location.origin) return;
    const f = frames.find((x) => x.contentWindow === e.source);
    const d = e.data;
    if (!f || !d || d.source !== "qfl-lab") return;
    if (typeof d.height === "number" && d.height > 0 && d.height < 4000) f.style.height = `${Math.ceil(d.height)}px`;
    if (d.focus || d.key) {
      if (document.activeElement === f) f.blur();
    }
    if (typeof d.key === "string" && Object.hasOwn(KEYS, d.key)) KEYS[d.key](d.shift === true);
  });
})();
