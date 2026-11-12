// The live lab's simulator: one qubit, a data re-uploading circuit, the client's gradient by the
// parameter-shift rule (exact or from sampled shots), and a gradient-matching attack run with Adam.
// Plain functions, no DOM, so node runs the same file in tests/test_qfl_lab.py.
(function (root, make) {
  if (typeof module === "object" && module.exports) module.exports = make();
  else root.QLab = make();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const TAU = 2 * Math.PI;
  // The paper's outcome thresholds (qflp: RECOVERED_RAD, CLOSE_RAD, EXPLAINS_SLACK). lab.js passes
  // the first two from data/readings.js, so a change in the paper reaches the panel; the slack is
  // fixed here.
  const DEFAULTS = { recovered: 0.05, close: 0.2, slack: 1e-6 };

  // mulberry32: a small seeded generator, so a preset replays the same run on every machine.
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // A standard normal draw (Box-Muller).
  function gauss(rand) {
    let u = 0;
    while (u === 0) u = rand();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * rand());
  }

  // The state a0|0> + a1|1> as [re0, im0, re1, im1].
  function ry(s, a) {
    const c = Math.cos(a / 2);
    const n = Math.sin(a / 2);
    return [c * s[0] - n * s[2], c * s[1] - n * s[3], n * s[0] + c * s[2], n * s[1] + c * s[3]];
  }

  function rz(s, a) {
    const c = Math.cos(a / 2);
    const n = Math.sin(a / 2);
    // e^{-ia/2} on |0>, e^{ia/2} on |1>
    return [c * s[0] + n * s[1], c * s[1] - n * s[0], c * s[2] - n * s[3], c * s[3] + n * s[2]];
  }

  // r repetitions of: encode RY(x), then l trainable blocks of RY(theta) RZ(theta).
  // theta holds 2*r*l angles in gate order.
  function state(x, theta, r, l) {
    let s = [1, 0, 0, 0];
    let k = 0;
    for (let rep = 0; rep < r; rep++) {
      s = ry(s, x);
      for (let b = 0; b < l; b++) {
        s = ry(s, theta[k++]);
        s = rz(s, theta[k++]);
      }
    }
    return s;
  }

  // <Z> = |a0|^2 - |a1|^2.
  function expZ(x, theta, r, l) {
    const s = state(x, theta, r, l);
    return s[0] * s[0] + s[1] * s[1] - s[2] * s[2] - s[3] * s[3];
  }

  // The Bloch vector of a state, for drawing.
  function bloch(s) {
    const re = s[0] * s[2] + s[1] * s[3];
    const im = s[0] * s[3] - s[1] * s[2];
    return [2 * re, 2 * im, s[0] * s[0] + s[1] * s[1] - s[2] * s[2] - s[3] * s[3]];
  }

  // An estimate of <Z> from `shots` measurements: k of them read 0, <Z> = 2k/shots - 1. Exact
  // binomial draws up to 1,000 shots; above that the normal approximation, or the Poisson one
  // when fewer than 10 outcomes are expected on the rarer side.
  function sampleZ(z, shots, rand) {
    if (!shots) return z;
    const p = Math.min(1, Math.max(0, (1 + z) / 2));
    let k;
    if (shots <= 1000) {
      k = 0;
      for (let i = 0; i < shots; i++) if (rand() < p) k++;
    } else {
      const q = Math.min(p, 1 - p);
      if (shots * q >= 10) {
        k = Math.round(shots * p + gauss(rand) * Math.sqrt(shots * p * (1 - p)));
      } else {
        // Knuth's Poisson draw on the rarer outcome.
        const limit = Math.exp(-shots * q);
        let n = 0;
        let prod = rand();
        while (prod > limit) {
          n++;
          prod *= rand();
        }
        k = p <= 0.5 ? n : shots - n;
      }
      k = Math.min(shots, Math.max(0, k));
    }
    return (2 * k) / shots - 1;
  }

  // The client's gradient of (f - y)^2 in every theta, each df/dtheta_j from the parameter-shift
  // rule (f(theta_j + pi/2) - f(theta_j - pi/2)) / 2, as a device computes it: with `shots`, each
  // of the 2P + 1 expectation values is estimated from that many measurements.
  function gradient(x, theta, r, l, y, shots, rand) {
    const f = sampleZ(expZ(x, theta, r, l), shots, rand);
    const g = new Float64Array(theta.length);
    const t = Float64Array.from(theta);
    for (let j = 0; j < t.length; j++) {
      const keep = t[j];
      t[j] = keep + Math.PI / 2;
      const plus = sampleZ(expZ(x, t, r, l), shots, rand);
      t[j] = keep - Math.PI / 2;
      const minus = sampleZ(expZ(x, t, r, l), shots, rand);
      t[j] = keep;
      g[j] = 2 * (f - y) * ((plus - minus) / 2);
    }
    return g;
  }

  function sqdist(a, b) {
    let d = 0;
    for (let j = 0; j < a.length; j++) d += (a[j] - b[j]) ** 2;
    return d;
  }

  // The attacker's matching loss: how far its own noiseless gradient at a guess is from the one
  // the client sent.
  function matchLoss(guess, target, theta, r, l, y) {
    return sqdist(gradient(guess, theta, r, l, y, 0), target);
  }

  // Distance between angles modulo 2*pi, as the paper measures it.
  function angleError(a, b) {
    const d = (((a - b) % TAU) + TAU) % TAU;
    return Math.min(d, TAU - d);
  }

  // Everything one client and one attack need: the hidden input, the circuit's angles, the
  // starting guesses, and the noise seed, all drawn from one seed.
  function client(seed, reps, layers, shots) {
    const rand = rng(seed);
    const x = Math.PI * rand();
    const theta = Array.from({ length: 2 * reps * layers }, () => TAU * rand());
    const starts = Array.from({ length: 64 }, () => Math.PI * rand());
    const target = gradient(x, theta, reps, layers, 1, shots, rng(seed ^ 0x9e3779b9));
    const c = { seed, x, theta, reps, layers, shots, y: 1, starts, target };
    // Fixed per client, so the outcome rule reads them instead of recomputing them per restart.
    c.truthLoss = matchLoss(x, target, theta, reps, layers, 1);
    c.norm2 = target.reduce((a, g) => a + g * g, 0);
    return c;
  }

  // One restart: Adam on the guess, its slope a central difference of the matching loss. Returns
  // the path and the loss at each of its points (for drawing), and the end point.
  function descend(c, start, opts) {
    const o = { steps: 150, lr: 0.05, b1: 0.9, b2: 0.999, eps: 1e-8, h: 1e-5, every: 3, ...opts };
    const L = (v) => matchLoss(v, c.target, c.theta, c.reps, c.layers, c.y);
    let v = start;
    let m = 0;
    let s = 0;
    const path = [v];
    const losses = [L(v)];
    for (let t = 1; t <= o.steps; t++) {
      const d = (L(v + o.h) - L(v - o.h)) / (2 * o.h);
      m = o.b1 * m + (1 - o.b1) * d;
      s = o.b2 * s + (1 - o.b2) * d * d;
      const mh = m / (1 - o.b1 ** t);
      const sh = s / (1 - o.b2 ** t);
      v -= (o.lr * mh) / (Math.sqrt(sh) + o.eps);
      if (t % o.every === 0) {
        path.push(v);
        losses.push(L(v));
      }
    }
    const loss = path[path.length - 1] === v ? losses[losses.length - 1] : L(v);
    return { start, end: v, loss, path, losses };
  }

  // The paper's four outcomes for one end point.
  function outcome(c, end, loss, th) {
    const t = { ...DEFAULTS, ...th };
    const err = angleError(end, c.x);
    if (err <= t.recovered) return "recovered";
    if (err <= t.close) return "close";
    if (loss <= c.truthLoss + t.slack * c.norm2) return "ambiguous";
    return "stuck";
  }

  // The next restart, from the client's next starting point, scored by the paper's rule. The
  // panel calls this one restart at a time, so a long attack can be spread across frames.
  function addRestart(c, runs, opts, th) {
    const run = descend(c, c.starts[runs.length], opts);
    run.outcome = outcome(c, run.end, run.loss, th);
    run.error = angleError(run.end, c.x);
    runs.push(run);
    return run;
  }

  // The attacker keeps the restart with the lowest loss among the first n, which needs no
  // knowledge of the true input.
  function pickBest(runs, n) {
    let best = 0;
    for (let i = 1; i < n; i++) if (runs[i].loss < runs[best].loss) best = i;
    return best;
  }

  // The whole attack: `restarts` descents from the client's first starting points.
  function attack(c, restarts, opts, th) {
    const runs = [];
    while (runs.length < restarts) addRestart(c, runs, opts, th);
    const best = pickBest(runs, runs.length);
    return { runs, best, outcome: runs[best].outcome, error: runs[best].error };
  }

  // The matching loss across one turn of guesses, for the landscape plot.
  function landscape(c, n) {
    const out = new Float64Array(n);
    for (let i = 0; i < n; i++) out[i] = matchLoss((TAU * i) / n, c.target, c.theta, c.reps, c.layers, c.y);
    return out;
  }

  return {
    TAU, DEFAULTS, rng, gauss, ry, rz, state, expZ, bloch, sampleZ, gradient, matchLoss, angleError,
    client, descend, outcome, addRestart, pickBest, attack, landscape,
  };
});
