// Runs qfl-privacy/lab-embed.js under stub browser globals and sends it messages: only its own
// frame, from its own origin, with its tag and a known key, may steer the deck.
"use strict";

const calls = []; let onMessage = null;
const frame = {
  dataset: { labSrc: "lab/index.html#tab=reps" },
  src: "",
  style: {},
  contentWindow: { name: "lab" },
  blur() {},
};
globalThis.location = { protocol: "https:", search: "", origin: "https://deck.test" };
globalThis.matchMedia = () => ({ matches: false });
globalThis.innerWidth = 1920; globalThis.innerHeight = 1080;
globalThis.document = {
  querySelectorAll: () => [frame],
  documentElement: { classList: { add() {} } },
  activeElement: null,
};
globalThis.Reveal = {
  on() {},
  getCurrentSlide: () => null,
  next: () => calls.push("next"),
  prev: () => calls.push("prev"),
};
globalThis.window = {
  Reveal: globalThis.Reveal,
  addEventListener: (t, h) => {
    if (t === "message") onMessage = h;
  },
};
require(process.argv[2]);
const send = (origin, source, data) => onMessage({ origin, source, data });
const own = frame.contentWindow, deck = "https://deck.test";
send("https://evil.test", own, { source: "qfl-lab", key: "PageDown" });
send(deck, { name: "stranger" }, { source: "qfl-lab", key: "PageDown" });
send(deck, own, { source: "other", key: "PageDown" });
send(deck, own, { source: "qfl-lab", key: "constructor" });
send(deck, own, { source: "qfl-lab", height: 1e9 });
const tooTall = frame.style.height || "";
send(deck, own, { source: "qfl-lab", key: "PageDown", height: 512.2 });
console.log(JSON.stringify({ calls, tooTall, height: frame.style.height }));
