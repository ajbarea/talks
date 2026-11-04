// Runs shared/deck.js against a stub DOM and checks what a speaker-view preview (?receiver) registers.
// A preview is never a phone: it must not reload when the window crosses 600px, and must not build the rail.
// Run with: node tests/deck_receiver.js
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const SOURCE = fs.readFileSync(path.join(__dirname, "..", "shared", "deck.js"), "utf8");

function element() {
  const node = {
    dataset: {},
    children: [],
    style: { setProperty() {} },
    classList: { add() {}, remove() {} },
    setAttribute() {},
    addEventListener() {},
    appendChild(child) {
      this.children.push(child);
      return child;
    },
    querySelector: () => null,
    querySelectorAll: () => [],
    getClientRects: () => [{}],
    getBoundingClientRect: () => ({ top: 0, bottom: 0 }),
  };
  return node;
}

// Loads deck.js with the given query string and reports what it registered.
function load(search) {
  const mediaListeners = [];
  const revealEvents = [];
  const section = element();
  section.dataset.chapter = "Intro";
  const reveal = {
    initialize: () => ({ then: (fn) => fn() }),
    on: (name) => revealEvents.push(name),
    getIndices: () => ({ h: 0, v: 0 }),
    getCurrentSlide: () => null,
    getScale: () => 1,
  };
  const context = {
    window: { DECK_DATA: {} },
    location: { search },
    console,
    Reveal: reveal,
    RevealNotes: {},
    matchMedia: () => ({
      matches: false,
      addEventListener: (type, fn) => mediaListeners.push(type),
    }),
    document: {
      documentElement: element(),
      querySelectorAll: (sel) => (sel.includes("section[data-chapter]") ? [section] : []),
      querySelector: () => element(),
      createElement: () => element(),
      createElementNS: () => element(),
    },
  };
  vm.runInNewContext(SOURCE, context);
  return { mediaListeners, revealEvents };
}

const preview = load("?receiver");
const audience = load("");

const failures = [];
const check = (ok, message) => {
  if (!ok) failures.push(message);
};

check(preview.mediaListeners.length === 0, `speaker-view preview registered ${preview.mediaListeners.length} viewport reload listener(s), expected 0`);
check(!preview.revealEvents.includes("resize"), "speaker-view preview built the chapter rail (Reveal resize hook registered), expected none");
check(audience.mediaListeners.length === 1, `audience deck registered ${audience.mediaListeners.length} viewport listener(s), expected 1`);
check(audience.revealEvents.includes("resize"), "audience deck did not build the chapter rail, expected it");

if (failures.length) {
  for (const message of failures) console.error(`FAIL: ${message}`);
  process.exit(1);
}
console.log("OK: speaker-view previews neither reload nor show the rail; audience deck unchanged");
