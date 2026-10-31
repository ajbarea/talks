// Every number and map entry this deck shows, each with its source. Checked October 30, 2026.
window.DECK_DATA = {
  week: {
    // bonsai-neuro-ai: nn-library #17 and #18, torch-mlflow-template #3, each verified and reviewed.
    labPrs: 3,
    // nn-library #18: peak memory one CKA call adds, without and with opt-einsum (m = 100, n = 25,088, CPU).
    memBefore: "968 MiB",
    memAfter: "0.9 MiB",
    // ajbarea/talks #46: every public video's page refreshed, each edit read back after a reload.
    videos: 169,
    // ajbarea/sphragis #233: "reviewed until clean (five rounds, a fresh reviewer each; the fifth found nothing)".
    rounds: 5,
  },
  // Placement from each product's own page; see the Sources slide.
  surfaces: {
    axes: {
      x: { label: "What it\nworks on", levels: ["A chat or\na draft", "Your accounts,\nfiles and apps", "Your code\nand data"] },
      y: { label: "Who starts the work", levels: ["You ask", "On a schedule\nyou set", "It decides\nwhen to look"] },
    },
    works: [
      { id: "web", label: "claude.ai", x: "A chat or\na draft", y: "You ask",
        oneLine: "The chat app, on the web, desktop and phone." },
      { id: "design", label: "Claude Design", x: "A chat or\na draft", y: "You ask",
        oneLine: "Designs, prototypes, slides and one-pagers, now inside any Claude chat." },
      { id: "science", label: "Claude Science", x: "Your code\nand data", y: "You ask",
        oneLine: "A desktop app (beta) that pairs Claude with an analysis environment on your computer." },
      { id: "cowork", label: "Claude Cowork", x: "Your accounts,\nfiles and apps", y: "On a schedule\nyou set",
        oneLine: "Longer tasks in the desktop app; schedule one for any cadence and close the laptop." },
      { id: "web-code", label: "Code on the web", x: "Your code\nand data", y: "On a schedule\nyou set",
        oneLine: "Claude Code on a cloud computer, on a copy of your GitHub repository; a scheduled task runs it hourly, nightly or weekly." },
      { id: "code", label: "Claude Code", x: "Your code\nand data", y: "You ask", ours: true,
        oneLine: "Runs in your own repository and terminal, with your tools and your hooks." },
      { id: "duet", label: "Claude Duet", x: "Your accounts,\nfiles and apps", y: "It decides\nwhen to look", ours: true,
        oneLine: "Checks your connected accounts every few hours on its own cloud computer and comes to you." },
    ],
  },
};
