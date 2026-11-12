// The lab page's job runner: a step's tally over hidden inputs 1 to n, in a Worker, or on the
// page's thread a frame's budget at a time where a Worker cannot start (a page opened from a
// file) or fails mid-job. One job runs at a time; starting another cancels the last.
// No DOM: node runs it in tests/test_qfl_lab_page.py with a fake Worker and frame clock.
(function (root, make) {
  if (typeof module === "object" && module.exports) module.exports = make;
  else root.QLabJobs = make;
})(typeof self !== "undefined" ? self : this, function (env) {
  "use strict";

  // env: Q (the simulator), th (the outcome thresholds), makeWorker() (a Worker, or null where
  // none can start), raf / caf (the frame clock), now() (milliseconds).
  const { Q, th, makeWorker, raf, caf, now } = env;
  let worker = null;
  let workerOk = true;
  let jobId = 0;
  let cancelCurrent = null;
  // If the Worker fails mid-job, the job carries on here from the next hidden input.
  let onWorkerError = null;

  function startWorker() {
    if (!workerOk || worker) return worker;
    try {
      worker = makeWorker();
    } catch {
      worker = null;
    }
    if (!worker) {
      workerOk = false;
      return null;
    }
    worker.addEventListener("error", (e) => {
      if (e && e.preventDefault) e.preventDefault();
      workerOk = false;
      worker.terminate();
      worker = null;
      const resume = onWorkerError;
      onWorkerError = null;
      if (resume) resume();
    });
    return worker;
  }

  // Starts a job and returns its cancel function. onScore(seed, scores) runs once per hidden
  // input, in order; onDone() once at the end, never after a cancel.
  function run(step, n, onScore, onDone) {
    if (cancelCurrent) cancelCurrent();
    const id = ++jobId;
    let seed = 1;
    let frame = 0;
    let handler = null;
    const w = startWorker();
    const cancel = () => {
      caf(frame);
      // The Worker stops this job too, rather than finishing it for nobody.
      if (handler && w) {
        w.removeEventListener("message", handler);
        w.postMessage({ cancel: id });
      }
      handler = null;
      if (onWorkerError === onThread) onWorkerError = null;
      if (cancelCurrent === cancel) cancelCurrent = null;
    };
    const finish = () => {
      cancel();
      onDone();
    };
    function onThread() {
      if (handler && w) w.removeEventListener("message", handler);
      handler = null;
      let jobs = seed <= n ? Q.tallyJobs(step, seed) : [];
      const tick = () => {
        if (id !== jobId) return;
        const until = now() + 8;
        while (seed <= n && now() < until) {
          const j = jobs.find((x) => x.runs.length < x.n);
          if (j) {
            Q.addRestart(j.c, j.runs, undefined, th);
            continue;
          }
          onScore(seed, Q.tallyScore(step, jobs, th));
          seed += 1;
          if (seed <= n) jobs = Q.tallyJobs(step, seed);
        }
        if (seed > n) finish();
        else frame = raf(tick);
      };
      frame = raf(tick);
    }
    cancelCurrent = cancel;
    if (w) {
      handler = (e) => {
        if (e.data.id !== id) return;
        if (e.data.done) finish();
        else {
          onScore(e.data.seed, e.data.scores);
          seed = e.data.seed + 1;
        }
      };
      w.addEventListener("message", handler);
      onWorkerError = onThread;
      w.postMessage({ id, step, from: 1, to: n, th });
    } else onThread();
    return cancel;
  }

  return {
    run,
    // Whether the job with this cancel function is still the one running.
    isCurrent: (cancel) => cancel !== null && cancelCurrent === cancel,
    cancel: () => cancelCurrent && cancelCurrent(),
    get inWorker() {
      return worker !== null;
    },
    // A view shown again reruns its rows unless they are finished or running, at the count wanted.
    shouldRun: (settled, count, want) => !settled || count !== want,
  };
});
