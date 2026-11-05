---
date: 2026-05-02
url: https://www.linkedin.com/feed/update/urn:li:activity:7456492311187828736/
impressions_2026_11_05: 748
---

The hardest part of an AI agent isn't the AI.
It's keeping it inside the lines.

Orchestrate Triage: a multi-domain support-triage AI agent. 10/10/10 on the labeled sample (3 graded columns). 29/29 on the production batch.

Solo build for HackerRank Orchestrate. 24h given, ~2h used. CSV in, CSV out: status, request_type, product_area, corpus-grounded response, justification.

Three ecosystems, three shipped corpora:
→ HackerRank Support: 580K tokens
→ Claude Help Center: 540K tokens
→ Visa Support: 18K tokens

Design choices that did the work:
→ Claude Opus 4.7 for prod. Sonnet 4.6 (1M context) for cheaper dev iteration.
→ Per-domain corpus stuffing. No RAG. Anthropic 1-hour extended cache TTL.
→ Forced single submit_triage tool call. Schema-validated TicketOutput rows in one round-trip.
→ Prompt-injection defense: <user_ticket> XML spotlighting + system instruction to treat contents as data.
→ Async Message Batches API for 50% off. Full prod run: 29 tickets, ~$20, 4 min wall time.

Python 3.12 · anthropic-python · pydantic · uv · Zensical docs.

Where do you draw the line: RAG, full-corpus stuffing, or somewhere in between?

Docs: https://lnkd.in/e_5HtN9j

#AIAgents #LLMOps #HackerRank

<!-- post details, not part of the post text -->
## Details

- Upgraded 2026-11-05: Unicode bold/italic to plain text, em dashes replaced, hashtags cut to 3. Wording, numbers, links and question unchanged.
