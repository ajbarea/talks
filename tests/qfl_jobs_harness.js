// Runs qfl-privacy/lab/jobs.js against the real lab/worker.js, loaded in a vm sandbox behind a
// fake Worker whose messages wait in one queue, and prints what each scenario saw as JSON.
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const lab = process.argv[2];
const Q = require(path.join(lab, "..", "lab-sim.js"));
const makeJobs = require(path.join(lab, "jobs.js"));
const TH = { recovered: 0.05, close: 0.2 };
const N = 6;

let queue = [];
const pump = (until = () => false) => {
  while (queue.length && !until()) queue.shift()();
};

function fakeWorker(failAt) {
  const on = { message: [], error: [] };
  const fake = { log: [], sent: [], terminated: false };
  // Its clock moves 30 ms a reading, so with its 40 ms budget it posts one input per tick.
  let clock = 0;
  const ctx = { QLab: Q, importScripts() {}, Date: { now: () => (clock += 30) }, setTimeout: (f) => queue.push(f) };
  ctx.self = ctx;
  ctx.postMessage = (d) =>
    fake.sent.push(d) &&
    queue.push(() => {
      if (fake.terminated) return;
      if (failAt && d.seed === failAt) on.error.forEach((h) => h({}));
      else on.message.forEach((h) => h({ data: d }));
    });
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(lab, "worker.js"), "utf8"), ctx);
  Object.assign(fake, {
    addEventListener: (t, h) => on[t].push(h),
    removeEventListener: (t, h) => (on[t] = on[t].filter((x) => x !== h)),
    postMessage: (d) => {
      fake.log.push(d);
      queue.push(() => !fake.terminated && ctx.onmessage({ data: d }));
    },
    terminate: () => (fake.terminated = true),
  });
  return fake;
}

function env(worker) {
  let next = 0;
  const dropped = new Set();
  return {
    Q,
    th: TH,
    makeWorker: () => worker,
    raf: (f) => {
      const h = ++next;
      queue.push(() => !dropped.has(h) && f());
      return h;
    },
    caf: (h) => dropped.add(h),
    now: () => Date.now(),
  };
}

function job(jobs, step) {
  const seen = { seeds: [], done: 0, right: true };
  seen.cancel = jobs.run(step, N, (seed, scores) => {
    seen.seeds.push(seed);
    if (JSON.stringify(scores) !== JSON.stringify(Q.tally(step, seed, TH))) seen.right = false;
  }, () => (seen.done += 1));
  return seen;
}
const brief = (s, jobs) => ({ seeds: s.seeds, done: s.done, right: s.right, current: jobs.isCurrent(s.cancel) });

const out = {};
// A second job cancels the first: the Worker hears the cancel before the new job.
{
  queue = [];
  const w = fakeWorker(0);
  const jobs = makeJobs(env(w));
  const a = job(jobs, "reps");
  const b = job(jobs, "restarts");
  pump();
  out.supersede = { a: brief(a, jobs), b: brief(b, jobs), log: w.log.map((d) => (d.cancel ? `cancel ${d.cancel}` : `job ${d.id}`)) };
}
// Midway: the first job has scored two inputs when the second starts; it scores no more.
{
  queue = [];
  const w = fakeWorker(0);
  const jobs = makeJobs(env(w));
  const a = job(jobs, "reps");
  pump(() => a.seeds.length >= 2);
  const mark = w.sent.length;
  const b = job(jobs, "shots");
  pump();
  // What the Worker still computed for the first job once the second began.
  const stale = w.sent.slice(mark).filter((d) => d.id === 1).length;
  out.midway = { a: brief(a, jobs), b: brief(b, jobs), stale };
}
// Cancelled with nothing after it (Back to a tab without rows): the Worker stops too.
{
  queue = [];
  const w = fakeWorker(0);
  const jobs = makeJobs(env(w));
  const a = job(jobs, "reps");
  pump(() => a.seeds.length >= 2);
  const mark = w.sent.length;
  jobs.cancel();
  pump();
  out.alone = { a: brief(a, jobs), stale: w.sent.slice(mark).length };
}
// The Worker fails at input 3: the job finishes on this thread, every input once, in order.
{
  queue = [];
  const w = fakeWorker(3);
  const jobs = makeJobs(env(w));
  const a = job(jobs, "shots");
  pump();
  out.failure = { ...brief(a, jobs), terminated: w.terminated, inWorker: jobs.inWorker };
}
// No Worker at all (a page opened from a file).
{
  queue = [];
  const jobs = makeJobs(env(null));
  const a = job(jobs, "reps");
  pump();
  out.thread = { ...brief(a, jobs), inWorker: jobs.inWorker };
}
// A view shown again reruns only rows that are unfinished or at another count.
{
  const jobs = makeJobs(env(null));
  out.shouldRun = [
    jobs.shouldRun(true, 20, 20),
    jobs.shouldRun(false, 20, 20),
    jobs.shouldRun(true, 20, 200),
  ];
}
console.log(JSON.stringify(out));
