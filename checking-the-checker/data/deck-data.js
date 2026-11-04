// Every number and quoted output this deck shows, each from the revised manuscript
// (cisc810 06-manuscript-revision-assignment/AJ-Barea-Checking-The-Checker-Revised.tex) or its evidence/ files.
// figs.js draws the figures from it and stops with a console error when a title's count disagrees.
window.DECK_DATA = {
  // Introduction: GhostCite (Xu et al., arXiv:2602.06718v2) and the ACL 2026 program chairs' statement.
  field: {
    models: 13, // recent models, among them GPT-5 and Claude Sonnet 4
    modelLow: 14, // percent of requested citations invalid, lowest model (14.23%, evidence/fabrication-rates.md)
    modelHigh: 95, // highest model (94.93%)
    venues: 8, // AI and security venues
    papersBefore: 0.89, // percent of accepted papers with an invalid citation, 2020 to 2024 average
    papersAfter: 1.61, // same, 2025
    aclFlagged: "over 100", // accepted ACL 2026 papers the checker flagged; chairs confirmed each by hand
    quoteErrors: 25.4, // Limitations: percent of quotations in medical journals that misdescribe the work (Jergas and Baethge)
  },
  // Section III-A: the shared bibliography the six cases come from.
  checker: { entries: 103, papers: 7, testsThen: 45 }, // testsThen: Section III-B, the suite during the four weeks
  // Table I. Days: from the commit that let a run produce the wrong result to its fix (evidence/hidden-for.md).
  // Case 5 took 21 minutes from trigger to fix; the paper prints it as under one day.
  cases: [
    { n: 1, group: "norun", what: "Build reported success with no bibliography", days: 71, shown: "71 days" },
    { n: 2, group: "norun", what: "Check skipped one paper", days: 25, shown: "25 days" },
    { n: 3, group: "input", what: "Score gave 100% to a paper that cites everything", days: 25, shown: "25 days" },
    { n: 4, group: "input", what: "Warning on a correct entry that no edit could clear", days: 2, shown: "2 days" },
    { n: 5, group: "input", what: "Fix blocked by old cached records", days: 0, shown: "under 1 day" },
    { n: 6, group: "report", what: "Refused lookups reported as missing entries", days: 27, shown: "27 days" },
  ],
  // Section IV: the details behind cases 1, 3, 5 and 7.
  case1: { citations: 20, days: 71 },
  case3: { entries: 77, realScore: 26 }, // entries then in the shared file; score of a paper citing 20
  case5: { fromCache: 29 }, // records read from the cache on the first run after the fix
  case7: { missing: 21, cited: 31 }, // Table I, the open seventh failure: missing of cited, stale local build
  // Section IV-F: the five runs on one day, and what the last one said.
  case6: { runs: [69, 69, 64, 67, 61], entries: 103, refusedLast: 61, resolvedMore: 6 },
  // Fig. 1 and Section V: the stage each group failed at, and its guard.
  groups: {
    norun: { name: "Did not run", stage: "Choose what to check", cases: "1, 2",
      guard: "Work out what to check, and name what was skipped" },
    input: { name: "Wrong inputs", stage: "Read the inputs", cases: "3, 4, 5",
      guard: "Break the check on purpose" },
    report: { name: "Misreported", stage: "Report the result", cases: "6",
      guard: "Report “no answer” apart from “not found”" },
  },
  // Sections III-C and IV-G; per-mutation counts from evidence/rebreak.md, techne dae4ca4, 490 tests.
  // 1b's two failures are the LaTeX build runner's tests, outside the 490.
  rebreak: {
    tests: 490,
    caught: 9,
    total: 11,
    mutations: [
      { id: "1a", n: 1, group: "norun", failed: 0, miss: "An empty compiled bibliography passed" },
      { id: "1b", n: 1, group: "norun", failed: 2 },
      { id: "2a", n: 2, group: "norun", failed: 4 },
      { id: "2b", n: 2, group: "norun", failed: 11 },
      { id: "2c", n: 2, group: "norun", failed: 1 },
      { id: "3", n: 3, group: "input", failed: 13 },
      { id: "4", n: 4, group: "input", failed: 8 },
      { id: "5", n: 5, group: "input", failed: 1 },
      { id: "6a", n: 6, group: "report", failed: 1 },
      { id: "6b", n: 6, group: "report", failed: 5 },
      { id: "6c", n: 6, group: "report", failed: 0, miss: "The note that a server refused requests, removed" },
    ],
  },
  // Table III: two guards run once per input on each tool, at its cited version, with no API keys.
  // kind: bad (a clean verdict after checking nothing, or a failed lookup called a finding),
  // warn (warned, then went on), good (said it checked nothing, or kept failed lookups apart),
  // mixed, none (not applicable). cleanAfterNothing and allNotFound are checked against the cells.
  checkers: {
    // HalRef's lines for the unreadable PDF, an excerpt of the run log (evidence/other-checkers-run.md).
    halrefNothing: ["No references extracted from /in/trunc.pdf", "All references verified OK"],
    cleanAfterNothing: 3,
    allNotFound: 2,
    tools: [
      { name: "CheckIfExist", cells: [
        { kind: "good", text: "“Invalid PDF structure”" },
        { kind: "warn", text: "Warns, then checks the text" },
        { kind: "bad", text: "10 of 10 “Not Found”", all: true } ] },
      { name: "HalluCiteChecker", cells: [
        { kind: "bad", text: "“All Clear!”", clean: true },
        { kind: "bad", text: "“All Clear!”", clean: true },
        { kind: "none", text: "Uses local databases" } ] },
      { name: "Hallucinator", cells: [
        { kind: "good", text: "“No references to check”" },
        { kind: "good", text: "“No references to check”" },
        { kind: "mixed", text: "10 of 10 “inconclusive”, but progress lines say “not found”" } ] },
      { name: "HalRef", cells: [
        { kind: "bad", text: "“All references verified OK”", clean: true },
        { kind: "warn", text: "Warns, then flags prose as references" },
        { kind: "bad", text: "10 of 10 “Not found in any database”", all: true } ] },
      { name: "RefChecker", cells: [
        { kind: "good", text: "Cannot read the paper, exit 1" },
        { kind: "bad", text: "“All references verified successfully!”", clean: true },
        { kind: "mixed", text: "10 of 10 “could not verify”; 4 also “Non-existent web page”" } ] },
    ],
  },
};
