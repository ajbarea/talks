# Video Script: How a Fleet of AI Agents Builds My Software

Production Mode: Mode A (Google Vids, AJ's personal avatar)
Long version: Landscape 16:9 (1920x1080), 2:30
Short: Vertical 9:16 (1080x1920), 50 seconds
Delivery Tone: Friendly behind-the-scenes tour for people who code a little.
Look: one charcoal t-shirt and two sets (the desk, the control room), the same in every segment.
On screen: only made-up names and the two public repository links; no private repository, account, email, token or key.

Sources (cited here, never voiced), public READMEs only:

- [ajbarea/klepsydra README](https://github.com/ajbarea/klepsydra#readme). Segments 2, 4 to 8, 12 to 14, S2, S3: the usage bar and a portrait per Claude Code session; the fleet wall with a card per session (status, repo, worktree and branch, last exchange); the status badges (orange 'needs you', blue 'working', green 'done') with sessions that need you first; the orchestrator that keeps the queue file; `fleet/launch.sh` starting an agent from its brief; the resume service resuming a limited session at its reset; CI watch's read-only triage and its line under 'Needs you'; the local-only ledger of tokens and blocked calls.
- [ajbarea/techne README](https://github.com/ajbarea/techne#readme). Segments 9 to 11, S4: `techne:elenchus`, an independent reviewer that reproduces the load-bearing claim, traces every consumer and walks a bug-class rubric; phylax's opt-in guards on `git commit` that block attribution lines.

## Long version (16:9, 1920x1080)

### Segment 1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Leans back, relaxed, hands folded. At 0:05, gestures to the side as if toward many screens.
* **Visual Overlay:** Several small terminal windows tile in around the avatar, each with a blinking cursor and a made-up name: 'app-a', 'docs-site', 'api'.
* **Spoken Script:**
  "Right now, several AI coding agents are working on my projects at once. Here's how I keep them from making a mess."
* **Vocal Direction:** Casual and confident, a little playful on 'making a mess'.

---

### Segment 2 (0:10 – 0:20): One Orchestrator

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 0:12, taps the center panel. At 0:16, sweeps a hand outward to the side panels.
* **Visual Overlay:** One large card in the center reads 'orchestrator: keeps the to-do list'. Lines run from it to three smaller cards, each holding a short note labeled 'brief'.
* **Spoken Script:**
  "One orchestrator agent keeps the to-do list. Each task gets a written brief, and a script starts a fresh agent with it."
* **Vocal Direction:** Clear and even. Stress 'one orchestrator' and 'written brief'.

---

### Segment 3 (0:20 – 0:30): Its Own Copy of the Code

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 0:23, holds both hands apart, palms facing, as if holding two separate boxes.
* **Visual Overlay:** Each agent card gets its own folder icon with a branch label: 'app-a / fix-login', 'docs-site / new-page'. A caption: 'git worktree = a separate copy of the code on its own branch'.
* **Spoken Script:**
  "Each agent works in its own repo or git worktree: a separate copy of the code on its own branch."
* **Vocal Direction:** Plain and patient; say 'worktree' slowly, like a new word.

---

### Segment 4 (0:30 – 0:40): They Run in the Background

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 0:34, glances over one shoulder at the monitor, then back to the camera.
* **Visual Overlay:** The terminal windows shrink and slide off screen, still blinking. A caption: 'Claude Code sessions, running in the background'.
* **Spoken Script:**
  "The agents are Claude Code sessions running in the background. So I need one place to see them all."
* **Vocal Direction:** Matter-of-fact. Slight lift on 'all of them at once'.

---

### Segment 5 (0:40 – 0:50): klepsydra

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 0:43, points up toward the top of the frame where the bar appears.
* **Visual Overlay:** A thin bar slides across the top of the frame, filling from blue toward yellow, labeled 'usage used'. A row of small round portraits lines up beside it, one per session. A caption: 'klepsydra, open source'.
* **Spoken Script:**
  "That's klepsydra, my open-source tool. A thin bar shows how much of my usage limit is used, plus one portrait per session."
* **Vocal Direction:** Proud but low-key. Pronounce klepsydra 'KLEP-sih-druh'.

---

### Segment 6 (0:50 – 1:00): The Fleet Wall

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 0:52, mimes a click in the air. At 0:55, opens both hands toward the cards.
* **Visual Overlay:** The glass wall fills with a grid of cards, one per agent. Each card shows a portrait, a status, a made-up repo and branch such as 'app-a / fix-login', and a one-line last message.
* **Spoken Script:**
  "Click a portrait and the wall opens. One card per agent: its status, where it works, and its last message."
* **Vocal Direction:** Bright and clear, like a quick tour.

---

### Segment 7 (1:00 – 1:10): Status at a Glance

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 1:02, points to the orange card. At 1:05, points to a blue card. At 1:08, points to a green card.
* **Visual Overlay:** The cards sort themselves: orange diamond cards with '!' move to the front, labeled 'needs you'; blue circles with '…' read 'working'; green circles with '✓' read 'done'.
* **Spoken Script:**
  "Agents that need me come first. Orange means waiting on me, blue means working, green means done."
* **Vocal Direction:** Crisp. One beat per color, matched to the pointing.

---

### Segment 8 (1:10 – 1:20): Back After a Limit

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 1:13, taps a wrist as if checking a watch. At 1:17, opens one palm, relaxed.
* **Visual Overlay:** One card dims with a label 'usage limit: resets at 3:00 PM'. A small clock spins forward, and the card lights back up: 'resumed'.
* **Spoken Script:**
  "When an agent hits a usage limit, a background service resumes it at the reset time. I don't have to babysit it."
* **Vocal Direction:** Relaxed and a little relieved on 'babysit'.

---

### Segment 9 (1:20 – 1:30): A Second Reader

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 1:22, raises one finger. At 1:26, points from one card to a different card.
* **Visual Overlay:** A change card labeled 'pull request' moves from one agent to a different agent card labeled 'reviewer'. A caption: 'the reviewer did not write this code'.
* **Spoken Script:**
  "Agents make mistakes. So before a change merges, a different agent reviews it: one that didn't write the code."
* **Vocal Direction:** Serious turn. Slow down on 'one that didn't write the code'.

---

### Segment 10 (1:30 – 1:40): What the Reviewer Does

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 1:32, counts one finger. At 1:35, shows two. At 1:38, shows three.
* **Visual Overlay:** Three checks tick on, one at a time: 'tests the main claim by running it', 'traces what uses the code', 'checks a list of known bug types'.
* **Spoken Script:**
  "It doesn't just read the change. It runs the main claim, traces what uses the code, and checks known bug types."
* **Vocal Direction:** Steady, one item per beat, matched to the counting.

---

### Segment 11 (1:40 – 1:50): Gates

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 1:44, makes a firm, flat 'stop' hand toward the camera.
* **Visual Overlay:** A commit card slides toward a gate. The gate reads the message, finds a banned line highlighted in red, and stops it. A caption: 'a check in code, not a request in a prompt'.
* **Spoken Script:**
  "Then gates: checks in code, not requests in a prompt. My techne plugins can block a commit that carries a banned line."
* **Vocal Direction:** Firm and plain. Stress 'checks in code'. Pronounce techne 'TEK-nee'.

---

### Segment 12 (1:50 – 2:00): Watching CI

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 1:53, points to a red light. At 1:57, points to a list on the side panel.
* **Visual Overlay:** A row of check lights shows one turning red, labeled 'check failed on GitHub'. A short report card appears, then a new line drops into a to-do list under 'Needs you'.
* **Spoken Script:**
  "When a check fails on GitHub, a watcher spots it. An agent reports the cause, and my to-do file gets a line."
* **Vocal Direction:** Brisk and clear; land 'my to-do file' with a small nod.

---

### Segment 13 (2:00 – 2:10): The Ledger

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 2:03, taps the desk twice, as if tallying.
* **Visual Overlay:** A small ledger panel slides in with three made-up totals: 'tokens used', 'lines changed', 'blocked actions'. A padlock icon and caption: 'stays on this machine'.
* **Spoken Script:**
  "A ledger counts each session's usage and blocked actions, on my own machine. That data never leaves it."
* **Vocal Direction:** Calm and reassuring. Stress 'never leaves it'.

---

### Segment 14 (2:10 – 2:20): My Job

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk, leaning in. At 2:15, points gently to self.
* **Visual Overlay:** The orange 'needs you' cards glow softly in a small row along the bottom of the frame.
* **Spoken Script:**
  "My job is the part only a person can do. I choose the work and answer the agents waiting on me."
* **Vocal Direction:** Warm and honest. A small smile on 'only a person can do'.

---

### Segment 15 (2:20 – 2:30): Outro

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk, direct eye contact with the camera. At 2:25, raises both eyebrows, inviting an answer.
* **Visual Overlay:** Two cards slide up: 'klepsydra: github.com/ajbarea/klepsydra' and 'techne: github.com/ajbarea/techne'. A badge: 'Comment below'.
* **Spoken Script:**
  "Both tools are open source, linked below. Would you trust a team of AI agents with your code? Tell me why."
* **Vocal Direction:** Peer-to-peer and curious. End on eye contact.

---

## Short (9:16, 1080x1920)

### Segment S1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Leans toward the camera. At 0:05, gestures to the side as if toward many screens.
* **Visual Overlay:** Small terminal windows tile in around the avatar, each blinking, with made-up names: 'app-a', 'docs-site', 'api'.
* **Spoken Script:**
  "Several AI agents are coding for me right now. Here's how I keep them from making a mess."
* **Vocal Direction:** Fast, punchy hook.

---

### Segment S2 (0:10 – 0:20): Orchestrator and Worktrees

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 0:12, taps the center panel. At 0:16, holds two hands apart like two boxes.
* **Visual Overlay:** A center card 'orchestrator: keeps the to-do list' sends 'brief' notes to agent cards, each with its own folder and branch.
* **Spoken Script:**
  "One orchestrator keeps the to-do list. Each agent gets a written brief and its own repo or git worktree."
* **Vocal Direction:** Clear and quick.

---

### Segment S3 (0:20 – 0:30): The Wall

* **Environment & Lighting:** A dim control room at night: a curved wall of dark glass panels behind the avatar, lit by soft cyan and amber status lights, blank except for what the overlay draws. A warm key light on the face from the left. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands in front of the glass wall. At 0:23, points to an orange card. At 0:26, points to a blue one. At 0:28, points to a green one.
* **Visual Overlay:** A grid of agent cards sorts itself: orange 'needs you' first, blue 'working', green 'done'. Caption: 'klepsydra, open source'.
* **Spoken Script:**
  "My open-source tool, klepsydra, puts every agent on one wall. Orange waits on me, blue is working, green is done."
* **Vocal Direction:** Bright. Pronounce klepsydra 'KLEP-sih-druh'.

---

### Segment S4 (0:30 – 0:40): Reviewers and Gates

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk. At 0:33, points from one side to the other. At 0:37, makes a firm 'stop' hand.
* **Visual Overlay:** A pull request passes to a different agent labeled 'reviewer'. Then a commit hits a gate and is stopped, a banned line glowing red.
* **Spoken Script:**
  "Before code merges, a different agent reviews it. And gates in code block commits that break my rules."
* **Vocal Direction:** Firm and clear on 'different agent' and 'gates in code'.

---

### Segment S5 (0:40 – 0:50): Your Turn

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos, nothing readable on the monitor. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the desk, leaning in with direct eye contact. At 0:45, warm, open smile.
* **Visual Overlay:** A badge slides in: 'Comment below'. Small terminal windows named 'app-a', 'docs-site' and 'api' faintly reappear behind the avatar, ready to loop.
* **Spoken Script:**
  "Would you trust a team of AI agents with your code? Tell me why or why not, below."
* **Vocal Direction:** Warm and curious. End on eye contact, so the loop hands off to 'Several AI agents are coding for me'.

---

## Audio Prompt (30 s seamless loop, both cuts)

Instrumental only, 30 seconds, seamless loop. 96 BPM, key of A minor. Clean electronic: a soft pulsing synth bass, light glitch percussion, airy pads and a short arpeggio that feels like a busy but calm control room. Clean start and end for an infinite loop, no vocals. Mix at -22 dB under the voice.

---

## Transitions & SFX Schedule

Long version: a soft digital whoosh on each cut between the desk and the control room (0.6 s, centered on the cut). A quiet UI blip as each status color is named (1:02, 1:05, 1:08). A low gate 'clunk' as the commit is stopped (about 1:46). A light chime when the outro links appear (about 2:25).

Short: a quick whoosh into each cut (0:10, 0:20, 0:30, 0:40), 0.5 s each, and the loop bed carries 0:50 back to 0:00.

---

## YouTube Studio Metadata

**Long version**

Title: How a Fleet of AI Agents Builds My Software

Description:
Several AI coding agents work on my projects at once. Here is how I keep them in line.

One orchestrator keeps the to-do list and starts each agent from a written brief. Each agent works in its own repo or git worktree. My open-source tool klepsydra shows every agent on one wall, with the ones waiting on me first. Before a change merges, a different agent reviews it, and gates in code block commits that break my rules.

00:00 Several agents at once
00:10 One orchestrator
00:40 The fleet wall
01:20 Reviewers and gates
02:00 The ledger and my job
02:20 Your turn

klepsydra: https://github.com/ajbarea/klepsydra
techne: https://github.com/ajbarea/techne

An AI avatar of AJ narrates this video. It was made in Google Vids from AJ's own verified face and voice.

#AIagents #ClaudeCode #DevTools #OpenSource #SoftwareEngineering #Programming

Pinned comment: Would you trust a team of AI agents with your code? Tell me why or why not. klepsydra: https://github.com/ajbarea/klepsydra

Tags: AI agents, Claude Code, coding agents, multi-agent, orchestrator, git worktree, code review, AI code review, developer tools, open source, klepsydra, techne

**Short**

Title: My AI Agents Code While I Watch One Wall

Description: One orchestrator, an agent per repo, a different agent to review, and gates in code. Full video: (link the long version). An AI avatar of AJ narrates this video, made in Google Vids from his own verified face and voice. #Shorts #AIagents #ClaudeCode

Upload: tick 'Altered or synthetic content: Yes' in YouTube Studio for both cuts.

---

## Assets

- AJ's personal avatar, selected in the Vids character selector.
- Overlays, drawn as described with made-up names only: the tiled terminals, the orchestrator and brief cards, the worktree folders, the usage bar and portraits, the card wall with orange, blue and green badges, the resume clock, the reviewer hand-off, the three review checks, the commit gate, the failed-check light and to-do line, the ledger panel.
- Real klepsydra screenshots (its README's `assets/`) only after checking that no private repository name, email or account appears in them; otherwise the drawn overlays.
- The 30 s audio loop above, generated once and used under both cuts.
