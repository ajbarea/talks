# Video Script: Why Your AI Agent Gets Dumber the More Rules You Give It

Production Mode: Mode A (Google Vids, AJ's personal avatar)
Long version: Landscape 16:9 (1920x1080), 2:40
Short: Vertical 9:16 (1080x1920), 50 seconds
Delivery Tone: Friendly explainer for people who code a little; calm, clear, a little wry.
Look: one charcoal t-shirt and two sets (the desk, the whiteboard wall), the same in every segment.

Sources (cited here, never voiced):

- Kelly Hong, Anton Troynikov and Jeff Huber, [Context Rot: How Increasing Input Tokens Impacts LLM Performance](https://www.trychroma.com/research/context-rot), Chroma technical report, July 2025. Segments 2 to 6, S1: 18 models tested; performance is not consistent across input lengths; on the repeated-words task, performance degrades across all models as length grows; distractors have non-uniform impact; how information is presented matters more than whether it is present.
- Diane Sarkis, [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop), Anthropic, October 22, 2026. Segments 7, 8, 10, 12 to 15, S2 to S4: the Frankenprompt; hard limits such as validation and approval gates belong in tools; short descriptions in context, full skills loaded only when needed; Claude Code's system prompt for more advanced models cut by over 80%; 10 golden examples are enough to start an eval set; run each task more than once; change one thing at a time and keep what holds up.
- Claude Code docs, [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide). Segments 10 and 11, S3: hooks are shell commands Claude Code runs at set points, so an action always happens rather than relying on the model to choose to run it.

## Long version (16:9, 1920x1080)

### Segment 1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Leans back at the start, arms loosely crossed. At 0:05, tilts the head and raises one eyebrow at the camera.
* **Visual Overlay:** A text file titled `AGENTS.md` scrolls up beside the avatar, adding a line every half second. A counter in the top corner climbs from '1 rule' to '50 rules'. At the end, three of the lines flash red.
* **Spoken Script:**
  "Say you give your AI agent fifty rules. It breaks one, forgets another, and gets worse at the job. Here's why."
* **Vocal Direction:** Relaxed, curious, a little wry. Slow down on 'gets worse at the job'. Land 'Here's why' with a small smile.

---

### Segment 2 (0:10 – 0:20): Context Rot

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Leans forward slightly, hands resting on the desk. At 0:14, opens one palm toward the overlay.
* **Visual Overlay:** The words 'context rot' type out in large white letters. Below them, a smaller line fades in: 'context = everything the model reads before it answers'.
* **Spoken Script:**
  "It has a name: context rot. Everything you give a model sits in its context, the text it reads before it answers."
* **Vocal Direction:** Clear and steady, like defining a word for a friend. Stress 'context rot' and 'before it answers'.

---

### Segment 3 (0:20 – 0:30): Chroma Tested 18 Models

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard, facing the camera. At 0:23, points to the chart as it draws.
* **Visual Overlay:** A simple line chart draws itself on the whiteboard: the x-axis reads 'input length', the y-axis reads 'reliability', and the line slopes down. A small caption: 'Chroma, July 2025: 18 models tested'.
* **Spoken Script:**
  "In 2025, researchers at Chroma tested 18 AI models. As the input got longer, the models got less reliable, even on simple tasks."
* **Vocal Direction:** Even and factual. Say '18' clearly. A short pause before 'even on simple tasks'.

---

### Segment 4 (0:30 – 0:40): The Repeated-Words Test

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:32, mimes copying with one hand, as if writing in the air. At 0:37, shakes the head once.
* **Visual Overlay:** On the whiteboard, a row of the word 'apple' repeats across the board, getting longer. A copy appears below it with small red marks where words are missing or wrong; more red marks appear as the row grows.
* **Spoken Script:**
  "One test just asked models to copy a list of repeated words. The longer the list, the worse every model did."
* **Vocal Direction:** Light and a bit amused on 'just asked', then plain and firm on 'every model'.

---

### Segment 5 (0:40 – 0:50): Look-Alike Text Distracts

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:43, sweeps a hand across the board as the decoy cards appear.
* **Visual Overlay:** One green card on the whiteboard reads 'the right answer'. Grey decoy cards that look almost the same pop in around it, each labeled 'looks related, wrong'. A dotted arrow wanders away from the green card toward a decoy.
* **Spoken Script:**
  "Text that looks related but is wrong pulls models off track, and some of it distracts more than the rest."
* **Vocal Direction:** Measured. Stress 'looks related but is wrong'.

---

### Segment 6 (0:50 – 1:00): How It's Presented Matters

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 0:52, holds up one finger. At 0:56, taps the desk once on 'your rules'.
* **Visual Overlay:** A clean card fades in: 'Having the right information is not enough. How it is presented matters more.' Small source line below it: 'Chroma, Context Rot, 2025'.
* **Spoken Script:**
  "Their takeaway: having the right information in there is not enough. How it's presented matters more. And your rules are information too."
* **Vocal Direction:** Thoughtful, slower. Pause before 'And your rules are information too', then deliver it as the turn.

---

### Segment 7 (1:00 – 1:10): The Frankenprompt

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 1:03, lifts both hands and mimes stacking blocks, one on another, until they wobble.
* **Visual Overlay:** A system prompt card grows as sticky notes from different teams slap onto it, each a different color. Two notes glow red where they contradict: 'always ask first' beside 'never ask, just do it'. A label stamps on top: 'The Frankenprompt'.
* **Spoken Script:**
  "Anthropic calls one failure the Frankenprompt. Every team adds a sentence to the prompt, and the rules start to conflict."
* **Vocal Direction:** Playful on 'Frankenprompt', then plain on 'the rules start to conflict'.

---

### Segment 8 (1:10 – 1:20): Give Each Rule a Home

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:11, opens both arms wide toward the board. At 1:16, counts to four on one hand.
* **Visual Overlay:** Four boxes draw themselves on the whiteboard, left to right: 'principles', 'hooks and gates', 'reference files', 'evals'. Each box gets a small number from 1 to 4.
* **Spoken Script:**
  "So don't pile every rule into one prompt. Give each rule the right home. There are four."
* **Vocal Direction:** Confident and upbeat. A beat before 'There are four'.

---

### Segment 9 (1:20 – 1:30): Home One: Principles

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:22, taps box 1. At 1:26, pinches thumb and finger together to show 'small'.
* **Visual Overlay:** Box 1, 'principles', zooms in. Inside it, three short lines appear one by one: 'Ask before deleting.', 'Run the tests.', 'Keep replies short.' A small badge: 'always loaded'.
* **Spoken Script:**
  "Home one: a few one-line principles the agent always reads. Keep them short and few. Every extra line is more to wade through."
* **Vocal Direction:** Friendly and practical. Stress 'short and few'.

---

### Segment 10 (1:30 – 1:40): Home Two: Hooks and Gates

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:32, taps box 2. At 1:36, makes a firm, flat 'stop' hand.
* **Visual Overlay:** Box 2, 'hooks and gates', zooms in. A code change slides toward a gate; the gate checks it and a green tick appears. A second change with a red problem gets stopped by the gate. Caption: 'runs every time'.
* **Spoken Script:**
  "Home two: rules that must always hold go in code, not in the prompt. A hook or a gate checks them every time."
* **Vocal Direction:** Firm and clear. Stress 'must always hold' and 'every time'.

---

### Segment 11 (1:40 – 1:50): What a Hook Is

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 1:43, points down at the desk as if at a terminal. At 1:47, shrugs lightly on 'just runs'.
* **Visual Overlay:** A small terminal window fades in. A line reads `hook: before each command -> check-rules.sh`, and a green 'ran' tick appears beside it each time a new command scrolls past.
* **Spoken Script:**
  "In Claude Code, a hook is a shell command that runs at set moments. It doesn't rely on the model choosing to run it."
* **Vocal Direction:** Plain and reassuring. Stress 'doesn't rely on the model'.

---

### Segment 12 (1:50 – 2:00): Home Three: Reference Files

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 1:52, taps box 3. At 1:56, mimes pulling a book off a shelf.
* **Visual Overlay:** Box 3, 'reference files', zooms in. A shelf of thick folders appears, each with a one-line label on its spine. One folder slides out and opens only when the agent asks for it. Caption: 'loaded when needed'.
* **Spoken Script:**
  "Home three: long how-to guides live in reference files. The agent sees a short description and loads the full file only when needed."
* **Vocal Direction:** Easy and clear. Stress 'only when needed'.

---

### Segment 13 (2:00 – 2:10): An 80 Percent Cut

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 2:03, brings both hands together to show something shrinking.
* **Visual Overlay:** A tall prompt bar shrinks to a short one. A label reads 'over 80% shorter'. Small source line: 'Anthropic, October 2026: Claude Code system prompt, more advanced models'.
* **Spoken Script:**
  "Anthropic cut Claude Code's system prompt by over 80 percent for its more advanced models. Part of that came from loading skills on demand."
* **Vocal Direction:** Impressed but factual. Stress 'over 80 percent'.

---

### Segment 14 (2:10 – 2:20): Home Four: Evals

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 2:12, taps box 4. At 2:16, holds up ten fingers, then lowers them.
* **Visual Overlay:** Box 4, 'evals', zooms in. Ten small task cards line up in a row, each with a check box. A label reads '10 examples with known good answers'.
* **Spoken Script:**
  "Home four: evals. An eval is a set of test tasks with known good answers. Ten good examples is enough to start."
* **Vocal Direction:** Encouraging. Make 'enough to start' sound doable.

---

### Segment 15 (2:20 – 2:30): Change One Thing

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 2:22, holds up one finger. At 2:26, nods once.
* **Visual Overlay:** The ten task cards run twice. A before-and-after score appears for one change; the change gets a green 'keep' stamp. Caption: 'one change at a time'.
* **Spoken Script:**
  "Change one thing at a time, run each task more than once, and keep what holds up. That's how you know a rule helps."
* **Vocal Direction:** Steady and confident. Stress 'one thing at a time' and 'holds up'.

---

### Segment 16 (2:30 – 2:40): Outro

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, leaning in toward the camera with direct eye contact. At 2:35, gives a warm, open smile.
* **Visual Overlay:** The four homes appear as small icons along the bottom: 'principles', 'hooks and gates', 'reference files', 'evals'. A badge slides in: 'Comment below'.
* **Spoken Script:**
  "Principles, hooks, reference files, evals. Which rule does your agent keep breaking? Tell me in the comments, and where you think it belongs."
* **Vocal Direction:** Warm and peer-to-peer. Genuinely curious on the question. End on eye contact.

---

## Short (9:16, 1080x1920)

### Segment S1 (0:00 – 0:10): The Hook

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Leans toward the camera. At 0:04, raises one eyebrow.
* **Visual Overlay:** A rules file titled `AGENTS.md` grows fast beside the avatar; a counter climbs to '50 rules'. Then a line chart drops in: 'input length' up, 'reliability' down. Caption: 'Chroma, 2025: 18 models'.
* **Spoken Script:**
  "More rules can make your AI agent worse. Researchers at Chroma tested 18 models: the longer the input, the less reliable they got."
* **Vocal Direction:** Fast and punchy hook. Stress 'worse' and 'less reliable'.

---

### Segment S2 (0:10 – 0:20): The Frankenprompt

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk. At 0:13, mimes stacking blocks until they wobble.
* **Visual Overlay:** Sticky notes from different teams slap onto a prompt card. Two glow red where they clash. A stamp: 'The Frankenprompt'.
* **Spoken Script:**
  "Pile every rule into one prompt and they start to conflict. Anthropic calls that the Frankenprompt. So give each rule a home."
* **Vocal Direction:** Playful on 'Frankenprompt', then clear on 'give each rule a home'.

---

### Segment S3 (0:20 – 0:30): Principles, Hooks and Gates

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:22, counts one finger. At 0:26, makes a firm 'stop' hand.
* **Visual Overlay:** Box 'principles' with three one-line rules. Then box 'hooks and gates': a gate stops a change with a red problem. Caption: 'runs every time'.
* **Spoken Script:**
  "A few one-line principles it always reads. Rules that must hold go in hooks and gates: code that checks every time."
* **Vocal Direction:** Brisk and clear. Stress 'must hold' and 'every time'.

---

### Segment S4 (0:30 – 0:40): Reference Files and Evals

* **Environment & Lighting:** A home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Stands beside the whiteboard. At 0:32, mimes pulling a book off a shelf. At 0:36, gives a thumbs-up.
* **Visual Overlay:** Box 'reference files': one folder slides off a shelf only when asked for. Box 'evals': ten task cards with check boxes and a 'keep' stamp.
* **Spoken Script:**
  "Long guides go in reference files it loads only when needed. And a small set of evals tells you if a change helped."
* **Vocal Direction:** Upbeat and practical.

---

### Segment S5 (0:40 – 0:50): Your Turn

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry; same look in every segment. Seated at the desk, leaning in with direct eye contact. At 0:45, warm, open smile.
* **Visual Overlay:** A badge slides in: 'Comment below'. The opening `AGENTS.md` file faintly reappears behind the avatar, ready to loop.
* **Spoken Script:**
  "Which rule does your AI agent keep breaking? Tell me below, and say where you'd put it."
* **Vocal Direction:** Warm and curious. End on eye contact, so the loop hands off to 'More rules can make your AI agent worse'.

---

## Audio Prompt (30 s seamless loop, both cuts)

Instrumental only, 30 seconds, seamless loop. 88 BPM, key of F major. Warm lo-fi: soft Rhodes chords, a muted kick and brushed hi-hat, a gentle bass line and a light plucked-synth motif. Calm and curious, never busy. Clean start and end for an infinite loop, no vocals. Mix at -22 dB under the voice.

---

## Transitions & SFX Schedule

Long version: hard cuts between the desk and the whiteboard, each with a soft paper-swipe (0.6 s, half before the cut, half after). One marker squeak as each whiteboard box draws (0:20, 1:10). A low 'thunk' as the Frankenprompt stamp lands (about 1:07). A light chime when the outro badge appears (about 2:35).

Short: a quick whoosh into each cut (0:10, 0:20, 0:30, 0:40), 0.5 s each, and the loop bed carries 0:50 back to 0:00.

---

## YouTube Studio Metadata

**Long version**

Title: Why Your AI Agent Gets Dumber the More Rules You Give It

Description:
More rules can make an AI agent worse. Here is why, and where each rule should live instead.

Chroma tested 18 models in 2025 and found they get less reliable as the input grows longer, even on simple tasks. Anthropic calls one result the Frankenprompt: every team adds a sentence and the rules start to conflict. The fix is to give each rule a home: a few one-line principles, hooks and gates for rules that must hold, reference files loaded only when needed, and evals to check that a change helped.

00:00 More rules, worse agent
00:10 Context rot
00:20 What Chroma found
01:00 The Frankenprompt
01:10 Four homes for your rules
02:20 Change one thing at a time
02:30 Your turn

Sources:
Chroma, Context Rot (2025): https://www.trychroma.com/research/context-rot
Anthropic, When to fold subagents into your main agent loop (2026): https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
Claude Code hooks: https://code.claude.com/docs/en/hooks-guide

An AI avatar of AJ narrates this video. It was made in Google Vids from AJ's own verified face and voice.

#AIagents #ClaudeCode #PromptEngineering #ContextEngineering #LLM #Programming

Pinned comment: Which rule does your AI agent keep breaking, and where would you put it: a principle, a hook, a reference file or an eval?

Tags: AI agents, context rot, prompt engineering, context engineering, Claude Code, hooks, agent rules, AGENTS.md, LLM evals, coding agents, AI for beginners, Chroma context rot

**Short**

Title: More Rules Make Your AI Agent Worse

Description: Chroma tested 18 models: the longer the input, the less reliable they got. Give each rule a home instead. Full video: (link the long version). An AI avatar of AJ narrates this video, made in Google Vids from his own verified face and voice. #Shorts #AIagents #ClaudeCode

Upload: tick 'Altered or synthetic content: Yes' in YouTube Studio for both cuts.

---

## Assets

- AJ's personal avatar, selected in the Vids character selector.
- Overlays: the growing `AGENTS.md` file, the reliability line chart, the repeated-words row, the decoy cards, the Frankenprompt notes, the four boxes, the gate, the hook terminal line, the 80% bar, the ten task cards. All are drawn as described; no real repository or account appears.
- The 30 s audio loop above, generated once and used under both cuts.
