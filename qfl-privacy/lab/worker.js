// Many hidden inputs at once, off the page's thread: the same simulator the page runs
// (../lab-sim.js), scored the same way. One message per hidden input, so the rows fill as they go.
/* global QLab */
importScripts("../lab-sim.js");

let current = 0;
self.onmessage = (e) => {
  const { id, step, from, to, th } = e.data;
  current = id;
  let seed = from;
  // A newer request (another step, or more inputs) supersedes this one between inputs.
  const next = () => {
    if (current !== id) return;
    const until = Date.now() + 40;
    while (seed <= to && Date.now() < until) {
      self.postMessage({ id, seed, scores: QLab.tally(step, seed, th) });
      seed += 1;
    }
    if (seed <= to) setTimeout(next, 0);
    else self.postMessage({ id, done: true });
  };
  next();
};
