---
date: 2026-12-01
url: pending
impressions_2026_11_05: not posted
---

An AI agent can query every data store an analyst is granted. In makesense, plain code, not a language model, decides which queries run.

Our paper on makesense is accepted as an oral at IAAI-27, in the Emerging Applications of AI track. Ben and I present it in Montréal in February.

Intelligence analysts follow one person or organization across graph, relational and document stores. Agentic coding tools can do that legwork, but the result is only usable if oversight can see which queries ran, under what policy, and where each claim came from.

So the analyst's own agent (Claude Code, Codex, OpenCode or Antigravity) is the only generative model. Every governed query passes through a deterministic server: a policy floor no setting can switch off, read-only access, stores you lack access to kept hidden, a tamper-evident audit log, and a report linter that flags uncited claims.

We measured before hardening. A red-team battery on salary disclosure, scored with no language model, found 6 of 8 measurable probes got through ungated. After the fix, 0 of 10 did. We wrote those probes; outside ones come next.

We ran the same 30 questions through ten setups pairing three agent harnesses with five models. The server decided correctly in every one. The one leak came from a model: it obtained a salary under a purpose that allowed it and reported it under one that did not. Purpose governs access, not use.

It all runs on public baseball data under a fictional franchise, so answers score against known facts, not opinions.

Thank you to my co-authors Ben Johnson, Jacob Tarosky and Jewel Padilla, and to Stephen and Mike at the Laboratory for Analytic Sciences, NC State, where this began at SCADS 2026.

The extended version is in the first comment.

#AgenticAI #AIGovernance #AAAI

<!-- post details, not part of the post text -->
## Details

- Collaborators (invite): Ben Johnson, Jacob Tarosky, Jewel Padilla. No tags. Stephen and Mike (LAS): first names only, no tag. A web search found none of the three profiles, so pick each in the composer by affiliation: Ben shows NC State / LAS or Johns Hopkins (his current email is at jhu.edu); Jacob and Jewel show NC State / LAS. Check each is 1st-degree; invite only those who are.
- Image (1200x1200, padded): Figure 1 of the paper, the architecture. Alt text: "Architecture diagram. The analyst's agentic harness (Claude Code, Codex, OpenCode, Antigravity) is the only generative model. Below a trust boundary, a deterministic MCP server with no language model gates every query, enforces policy and read-only access, and feeds an audit log, report linter and handoff bundle."
- First comment: "Extended version, free to read: https://doi.org/10.5281/zenodo.24537544"
- Planned: Tuesday 12-01, about 8:00 AM ET (the first hour ends before the 9:30 class).
- Source of record: scads-makesense `makesense/manuscripts/iaai-2027/barea.tex` (branch crc-arxiv-link, the Zenodo build); LAS approved the camera-ready and extended versions in pre-publication review on 11-21.
- Left out: any award (the Deployed Application Award is for the Deployed track only); the 8-cell judged zero-leak result (a selection a reader could over-read next to the matrix leak); "air-gapped" and "offline" (the harness's model is served separately).
