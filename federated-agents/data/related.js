// Published designs placed on the rivals map, each from a full-text read of the paper
// (2026-10-10; FedSelect 2026-10-18); the page each placement rests on is noted.
// x: who decides what the shared part learns. y: whether anything tested the shared part for
// leaks, and whether that test asks which client it came from.
window.DECK_DATA = Object.assign(window.DECK_DATA || {}, {
  related: {
    axes: {
      x: {
        label: "Who decides\nwhat is shared",
        levels: ["nothing\nis split", "training\nsorts it", "a fixed\nlayer rule", "judged by a filter,\nserver or AI", "the company,\nbefore training"],
      },
      y: {
        label: "Is the shared part tested?",
        levels: ["for whose\nit is", "for other\nleaks", "not tested"],
      },
    },
    works: [
      {
        // p2: only the global LoRA is uploaded; both train on all local data. p7: privacy asserted, not tested.
        id: "fdlora",
        label: "FDLoRA",
        year: 2024,
        group: "shared + private parts",
        x: "training\nsorts it",
        y: "not tested",
        oneLine: "Each client keeps a shared and a private adapter trained on the same data, then blends them.",
      },
      {
        // NeurIPS 2024. p5: global adapter by FL training, local adapter kept. p19: assumes no attacks.
        id: "feddpa",
        label: "FedDPA",
        year: 2024,
        group: "shared + private parts",
        x: "training\nsorts it",
        y: "not tested",
        oneLine: "A shared and a private adapter per client, mixed per question to handle new kinds of questions.",
      },
      {
        // p3: local optimization fills both modules; p4, p7: DP noise on the shared module, no attack.
        id: "sdflora",
        label: "SDFLoRA",
        year: 2026,
        group: "shared + private parts",
        x: "training\nsorts it",
        y: "for other\nleaks",
        oneLine: "Splits each client's adapter into a shared part, sent with optional noise, and a private part.",
      },
      {
        // CVPR 2024. p3: each client grows its own mask of parameters kept local; p8: attacks named as open, none run.
        id: "fedselect",
        label: "FedSelect",
        year: 2024,
        group: "shared + private parts",
        x: "training\nsorts it",
        y: "not tested",
        oneLine: "Each client keeps the parameters that changed most during training, shares the rest.",
      },
      {
        // ACL 2026. p4: NER masks personal details for the shared adapter; p6: extraction and PII inference attacks.
        id: "securegate",
        label: "SecureGate",
        year: 2026,
        group: "shared + private parts",
        x: "judged by a filter,\nserver or AI",
        y: "for other\nleaks",
        oneLine: "Shares an adapter trained on text with personal details masked, keeps one trained on raw text.",
      },
      {
        // ICLR 2025. p2, p5: A matrices shared, B kept local, by design. No leakage evaluation.
        id: "fedsalora",
        label: "FedSA-LoRA",
        year: 2025,
        group: "split by layer",
        x: "a fixed\nlayer rule",
        y: "not tested",
        oneLine: "Shares one half of each adapter (matrix A) and keeps the other half (matrix B) at home.",
      },
      {
        // p4: query/key adapters shared, value/output private, by projection type. p1, p10: no attack test.
        id: "pfadapter",
        label: "PFAdapter",
        year: 2026,
        group: "split by layer",
        x: "a fixed\nlayer rule",
        y: "not tested",
        oneLine: "Shares two of four attention adapters and keeps the other two private, for image-and-text tasks.",
      },
      {
        // p3-5: shared expert plus server-assigned experts, all averaged, no private part. p6, p12: noise on uploaded embeddings.
        id: "fedamole",
        label: "FedAMoLE",
        year: 2024,
        group: "no private part",
        x: "nothing\nis split",
        y: "for other\nleaks",
        oneLine: "A server hands each client its own mix of adapter experts, chosen by data similarity.",
      },
      {
        // p7-8: aggregation rule for adapters of different ranks; no private part, no leakage test.
        id: "rbla",
        label: "RBLA",
        year: 2024,
        group: "no private part",
        x: "nothing\nis split",
        y: "not tested",
        oneLine: "A way to average adapters of different sizes without diluting them.",
      },
      {
        // Findings of EACL 2026. p2: each client sends its whole adapter; p1: privacy asserted only.
        id: "rblora",
        label: "RB-LoRA",
        year: 2026,
        group: "no private part",
        x: "nothing\nis split",
        y: "not tested",
        oneLine: "A better way for the server to average client adapters of different sizes.",
      },
      {
        // TSE 2024. p3: one in-house model per organization, nothing shared; p8, p12: public benchmarks, no leakage test.
        id: "codementor",
        label: "CodeMentor",
        year: 2024,
        group: "no private part",
        x: "nothing\nis split",
        y: "not tested",
        oneLine: "Tunes a model on one company's own review history, in-house; nothing is shared.",
      },
      {
        // arXiv:2608.01561. p3-5: the server labels each rule's scope from cross-client evidence by fixed thresholds. No privacy evaluation.
        id: "fedworld",
        label: "FedWorld",
        year: 2026,
        group: "agent memory and skills",
        x: "judged by a filter,\nserver or AI",
        y: "not tested",
        oneLine: "Agents share if-then rules about their tools; a server decides where each rule holds from clients' evidence.",
      },
      {
        // arXiv:2609.32511. p3-4: LLM managers decide what enters the shared pool. p9-10: misuse audit of a variant only.
        id: "sharemem",
        label: "ShareMem",
        year: 2026,
        group: "agent memory and skills",
        x: "judged by a filter,\nserver or AI",
        y: "not tested",
        oneLine: "Users' agents pool how-to experience while each user's preferences stay private; an AI decides what is pooled.",
      },
      {
        // arXiv:2606.03143. p4: each client's AI judges what is a general lesson. App. E p17-18: sensitive-entity leak audit, not source.
        id: "federatedskill",
        label: "FederatedSkill",
        year: 2026,
        group: "agent memory and skills",
        x: "judged by a filter,\nserver or AI",
        y: "for other\nleaks",
        oneLine: "Each agent's AI writes up lessons as skill patches; only those leave, and a server agent merges them.",
      },
      {
        id: "ours",
        label: "This work",
        year: 2026,
        group: "shared + private parts",
        x: "the company,\nbefore training",
        y: "for whose\nit is",
        oneLine: "The company lists what may feed the shared adapter before training, and the shared adapter is tested for which company it came from.",
        ours: true,
      },
    ],
  },
});
