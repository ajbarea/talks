<!-- budget: 650 words -->
# Videos

AJ's explainer videos, made in Google Vids with his personal avatar: his own verified face and voice, animated by Gemini Omni. They are for students and people who code a little.

## The plan

- **Format:** a 2 to 4 minute explainer (16:9) and a 45 to 50 second Short (9:16) cut from the same script.
- **Cadence:** one video every other week, recorded in batches.
- **Source:** each video adapts something that already exists: a talk deck, a published paper or a repository README. Where a deck exists, the narration comes from its speaker notes (`graphe:slides`).
- **Writing:** every script follows [vids-rules.md](vids-rules.md), and [check_script.py](check_script.py) lints it. The [YouTube director skill](youtube-director/SKILL.md) covers the full workflow, from storyboard to upload metadata.
- **Ready to record:** AJ records in Vids when Claude tokens run out, so every queued item needs a 'ready to record' state he can pick up cold: the script passes the lint, and its assets, audio prompt and metadata are written down.

## Guardrails

1. **Say that an AI avatar narrates.** On upload, tick 'Altered or synthetic content' in YouTube Studio, and say in the description that an AI avatar of AJ narrates the video. A text-to-speech narrator is disclosed the same way. YouTube requires disclosure of realistic synthetic media, and a synthetically generated voice narrating a video is one of its examples ([YouTube, March 2024](https://blog.youtube/news-and-events/disclosing-ai-generated-content)).
2. **Only published work.** Never cover a paper while it is under double-blind review, or lab results that are not yet published. Videos cover published papers, public repositories and general concepts.
3. **Nothing private on screen.** No private repository, account, email, token or key in an overlay or a screenshot; overlays use made-up names.

## Queue

States: **ready to upload** (recorded; the upload package is written), **ready to record** (lint passes, assets and metadata written), **script lint-clean** (the segments pass; other parts are still missing), **in progress** (work outside this folder), **idea** (no script yet).

Work already in progress, top of the queue:

| # | Title | Source | Status | Left to do | Due |
|---|---|---|---|---|---|
| – | ISTE-782 Assignment 3: earthquakes | AJ's class repository | in progress | the fix list, the final cut, submit | Sun, Nov 1, 11:59 PM (graded) |
| 01 | Why Your Tech Lead Rejects AI Code (Federated Agents Short) | [script](01-federated-agents/script.md), from the [Federated Agents deck](../federated-agents/) | script lint-clean | audio prompt, SFX schedule, metadata with the disclosure, assets list | – |
| – | Hackathon: driving a robot with one forearm | AJ's hackathon notes | in progress | record the screen, the sim and the arm, then edit | – |
| – | Akira motorcycle-scene homage | AJ's ideas | idea | a script | – |
| – | Skateboard tricks (Alex's idea) | AJ's ideas | in progress | finish the first draft against the rules | – |

New in this track:

| # | Title | Source | Status | Left to do | Due |
|---|---|---|---|---|---|
| 02 | [Why Your AI Agent Gets Dumber the More Rules You Give It](02-context-rot/script.md), a two-character bit | Chroma's Context Rot report (2025); Anthropic, When to fold subagents into your main agent loop (2026); Claude Code hooks docs | ready to record | record | – |
| 03 | [How a Fleet of AI Agents Builds My Software](03-agent-fleet/script.md) | the klepsydra and techne READMEs | ready to record | record | – |
| 04 | [What Is an Attack on Federated Learning?](04-fl-attacks/script.md) | McMahan et al. 2017; Blanchard et al. 2017; Li et al. 2019; Lamport et al. 1982 | ready to record | record | – |
| 05 | [The Terminal That Haunted Me](05-haunted-terminal/metadata.md), a Halloween sketch | [director example 2](youtube-director/references/examples.md) | ready to upload | upload both cuts | Sat, Oct 31 |

## Layout

- `NN-slug/script.md`: one video's script, both cuts.
- `NN-slug/description.txt`, `metadata.md`: a recorded video's upload package.
- `vids-rules.md`: the writing rules and the pre-flight checklist.
- `check_script.py`: the lint (`make videos-check`; `make test` runs it too).
- `youtube_check.py`: lints each `description.txt`; `make videos-verify ID=...` checks a live page.
- `tools/`: thumbnail and slow-zoom helpers.
- `channel/`: the refresh of every public upload: hand-written Tier 1 descriptions in `tier1/`, the concert and gaming tables that `refresh.py` renders, and `review.md`.
- `youtube-director/`: the director skill, with its worked examples in `references/`.

The site build skips this folder: it has no `index.html`, so it is not a talk.
