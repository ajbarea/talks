// The live lab on the lab slides: the lab page (lab/index.html) in a frame, at the slide's tab.
// From a file, and in print (deck.css), the slide shows the paper's figure and the lab's address.
// A frame loads the first time its slide is shown, never in the speaker view's slide previews.
// The page reports its height, so the frame fits it, and hands back the keys a presenter's
// clicker sends, so the next press turns the slide even after a click inside the lab.
(function () {
  "use strict";

  const receiver = /receiver/i.test(location.search);
  const frames = [...document.querySelectorAll("iframe.lab-frame[data-src]")];
  if (!frames.length || !window.Reveal) return;
  // Opened from a file (the exported PDF and slides): the paper's figure alone, no frame.
  if (location.protocol === "file:") {
    document.documentElement.classList.add("lab-still");
    return;
  }

  const load = () => {
    const slide = Reveal.getCurrentSlide();
    for (const f of frames) if (!receiver && !f.src && slide && slide.contains(f)) f.src = f.dataset.src;
  };
  Reveal.on("ready", load);
  Reveal.on("slidechanged", load);

  const KEYS = {
    PageDown: () => Reveal.next(), " ": () => Reveal.next(), n: () => Reveal.next(), ArrowRight: () => Reveal.right(),
    ArrowDown: () => Reveal.down(), PageUp: () => Reveal.prev(), p: () => Reveal.prev(), ArrowLeft: () => Reveal.left(),
    ArrowUp: () => Reveal.up(), b: () => Reveal.togglePause(), ".": () => Reveal.togglePause(),
  };
  window.addEventListener("message", (e) => {
    // Only this deck's own lab frames may steer it.
    const f = frames.find((x) => x.contentWindow === e.source);
    const d = e.data;
    if (!f || !d || d.source !== "qfl-lab") return;
    if (typeof d.height === "number" && d.height > 0 && d.height < 4000) f.style.height = `${Math.ceil(d.height)}px`;
    if (d.focus || d.key) {
      if (document.activeElement === f) f.blur();
    }
    if (typeof d.key === "string" && Object.hasOwn(KEYS, d.key)) KEYS[d.key]();
  });
})();
