// Every number and map entry this deck shows, each with its source. Checked October 30, 2026; apps and hooks November 2.
window.DECK_DATA = {
  week: {
    // bonsai-neuro-ai: nn-library #17 and #18, torch-mlflow-template #3, each verified and reviewed.
    labPrs: 3,
    // nn-library #18: peak memory one chunsum call (one step of the CKA score) adds, without and with
    // opt-einsum (m = 100, n = 25,088, CPU): 968 MiB (1.02 GB) and 0.9 MiB (0.94 MB), said in plain units.
    memBefore: "about 1 GB",
    memAfter: "under 1 MB",
    // ajbarea/talks #46: every public video's page refreshed, each edit read back after a reload.
    videos: 169,
  },
  // Hook events each tool documents, counted November 2, 2026, from its hooks page (Sources slide).
  hooks: {
    claudeCode: 33, // code.claude.com/docs/en/hooks, the event table
    cursor: 21, // cursor.com/docs/agent/hooks
    codex: 14, // learn.chatgpt.com/docs/hooks; Copilot CLI also documents 14
    antigravity: 6, // antigravity.google/docs/hooks
    // techne plugins/phylax/hooks/hooks.json: PreToolUse, UserPromptSubmit, Stop, Notification,
    // SessionStart, SessionEnd.
    mine: 6,
  },
  // Placement from each product's own page; see the Sources slide.
  surfaces: {
    axes: {
      x: { label: "What it\nworks on", levels: ["A chat or\na draft", "Your accounts\nand apps", "Your code\nand data"] },
      y: { label: "Who starts the work:", levels: ["You ask", "On a schedule\nyou set", "It comes to\nyou unasked"] },
    },
    works: [
      // Claude Design moved into the chat on September 16, 2026, and Cowork began to, plan by plan (claude.com "Claude Cowork and
      // chat are now one Claude"; help center "Move from standalone Claude Design to Claude").
      { id: "web", label: "Claude chat", x: "A chat or\na draft", y: "You ask",
        oneLine: "The chat app on the web, desktop and phone; since September 16 it also makes the designs, design systems and slide decks Claude Design made on its own site." },
      { id: "science", label: "Claude Science", x: "Your code\nand data", y: "You ask",
        oneLine: "A desktop app (beta) that pairs Claude with an analysis environment on your computer." },
      { id: "cowork", label: "Claude Cowork", x: "Your accounts\nand apps", y: "On a schedule\nyou set",
        oneLine: "Longer tasks, moving into Claude chat since September 16 (Pro, Max, Ultra and Enterprise first); schedule one for any cadence and close the laptop." },
      { id: "web-code", label: "Code on the web", x: "Your code\nand data", y: "On a schedule\nyou set",
        oneLine: "Claude Code on a cloud computer, on a copy of your GitHub repository; a scheduled task runs it hourly, nightly or weekly." },
      { id: "code", label: "Claude Code", x: "Your code\nand data", y: "You ask", ours: true,
        oneLine: "Runs in your own repository and terminal, with your tools and your hooks." },
      { id: "duet", label: "Claude Duet", x: "Your accounts\nand apps", y: "It comes to\nyou unasked", ours: true,
        oneLine: "Checks your connected accounts every few hours on its own cloud computer and brings you what needs you." },
    ],
  },
};
