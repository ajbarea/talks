# Video Script: Why Your AI Agent Gets Dumber the More Rules You Give It

Production Mode: Mode A (Google Vids, AJ's personal avatar), a two-character bit
Long version: Landscape 16:9 (1920x1080), 3:00
Short: Vertical 9:16 (1080x1920), 50 seconds
Delivery Tone: Comedy sketch with a calm explainer; for people who code a little.
Characters (both are AJ's avatar; each segment names its character):
- Overloaded AJ plays the AI agent: mustard hoodie covered in sticky notes, at a cluttered desk under flickering green fluorescent light. Fast, frazzled voice.
- Calm AJ is the developer: charcoal t-shirt, at a tidy desk or whiteboard under a warm lamp. Unhurried, warm voice.

The agent's 50 rules and its lines are a dramatization. The four homes are AJ's own grouping of the advice below.

Sources (cited here, never voiced):

- Kelly Hong, Anton Troynikov and Jeff Huber, [Context Rot: How Increasing Input Tokens Impacts LLM Performance](https://www.trychroma.com/research/context-rot), Chroma technical report, July 2025. Segments 2 to 8, S2: 18 models tested; performance is not consistent across input lengths; on the repeated-words task, performance degrades across all models as length grows; distractors have non-uniform impact; how information is presented matters more than whether it is present. The chart is an illustration, not the report's data.
- Diane Sarkis, [Building agents: When to fold subagents into your main agent loop](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop), Anthropic, October 22, 2026. Segments 9, 10, 12, 14 to 16, S3, S4: the Frankenprompt (every team adds a sentence to the system prompt, and the rules conflict); hard limits such as validation and approval gates belong in tools; short descriptions in context, full skills loaded only when needed; Claude Code's system prompt for more advanced models cut by over 80%, partly by disclosing skills and tools progressively; 10 golden examples are enough to start an eval set; change one thing at a time and keep what holds up.
- Claude Code docs, [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide). Segments 12 and 13, S3: hooks are shell commands Claude Code runs at set points, so an action always happens rather than relying on the model to choose to run it.

## Long version (16:9, 1920x1080)

### Segment 1 (0:00 – 0:10): Two Rules, One Agent

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. Holds a rule sheet in each hand, eyes darting between them. At 0:06, drops both sheets and grabs the hood with both hands.
* **Visual Overlay:** Two sticky notes zoom up beside the head: 'Rule 47: always ask first' and 'Rule 12: never ask, just do it'. They flash red where they clash. A counter in the corner reads '50 rules'.
* **Spoken Script:**
  "Okay, rule forty-seven: always ask first. Rule twelve: never ask, just do it. Wait. Which one wins?"
* **Vocal Direction:** Overloaded AJ's voice: fast, frazzled, a little too loud. Pause before 'Wait'; the voice cracks on 'Which one wins?'.

---

### Segment 2 (0:10 – 0:20): Meet My Agent

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 0:13, gestures over one shoulder, as if toward the cluttered desk. At 0:17, shrugs lightly.
* **Visual Overlay:** A small picture-in-picture window in the corner shows the cluttered desk and the mustard hoodie, sticky notes fluttering. A label reads 'my AI agent, 50 rules'.
* **Spoken Script:**
  "That's my AI agent, holding fifty rules. It keeps getting worse. Part of the reason has a name: context rot."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. A small, sympathetic smile. Stress 'context rot'.

---

### Segment 3 (0:20 – 0:30): What Context Is

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 0:22, draws a box in the air. At 0:26, stretches both hands apart.
* **Visual Overlay:** On the whiteboard, a box labeled 'context' fills with lines of text. A new rule slides in at the bottom and the box stretches taller each time. Caption: 'context = all the text a model reads before it answers'.
* **Spoken Script:**
  "Context is all the text a model reads before it answers. Every rule you add makes that text longer."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Stress 'every rule'.

---

### Segment 4 (0:30 – 0:40): Chroma Tested 18 Models

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 0:33, points to the chart as it draws.
* **Visual Overlay:** A simple line chart draws itself on the whiteboard: the x-axis reads 'input length', the y-axis reads 'reliability', and the line slopes down. Caption: 'illustration; Chroma, July 2025: 18 models tested'.
* **Spoken Script:**
  "In 2025, Chroma tested 18 AI models. As the input got longer, they got less reliable, even on simple tasks."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Say '18' clearly. A short pause before 'even on simple tasks'.

---

### Segment 5 (0:40 – 0:50): Apple, Apple, Apple

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. Squints at a long paper strip, tracing it with a finger. At 0:46, loses the place, looks up, mouth half open.
* **Visual Overlay:** A paper strip reading 'apple apple apple apple' unrolls across the frame and keeps going. A copy below it picks up small red marks where words go missing.
* **Spoken Script:**
  "Copy this list of repeated words? Easy! Apple, apple, apple... wait, how many apples was that?"
* **Vocal Direction:** Overloaded AJ's voice: fast, frazzled, a little too loud. Confident on 'Easy!', then lost on 'how many apples'.

---

### Segment 6 (0:50 – 1:00): The Repeated-Words Test

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 0:52, mimes copying a line in the air. At 0:57, shakes the head once.
* **Visual Overlay:** On the whiteboard, a row of the word 'apple' grows longer. More red marks appear in the copy as the row grows. Caption: 'longer row, more mistakes, in every model'.
* **Spoken Script:**
  "That was one of Chroma's tests: copy a long run of repeated words. The longer the run, the worse every model did."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Plain and firm on 'every model'.

---

### Segment 7 (1:00 – 1:10): Which One Was It?

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. Holds up one sticky note, then another, then a third, each closer to the face. At 1:07, freezes with all three held up.
* **Visual Overlay:** Three nearly identical sticky notes glow: 'deploy on Friday', 'deploy on Fridays?', 'never deploy Friday'. A question mark spins above them.
* **Spoken Script:**
  "This note looks right. So does this one. And this one. Which one was the actual answer?"
* **Vocal Direction:** Overloaded AJ's voice: fast, frazzled, a little too loud. Speed up with each note, then stall on the question.

---

### Segment 8 (1:10 – 1:20): How It's Presented

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 1:12, holds up one finger. At 1:16, opens one palm toward the camera.
* **Visual Overlay:** One green card reads 'the right answer'; grey look-alike cards crowd around it. Then a clean card fades in: 'How information is presented matters more than whether it is there.' Source line: 'Chroma, Context Rot, 2025'.
* **Spoken Script:**
  "Look-alike text pulls models off track. Chroma's takeaway: how the information is presented matters more than just having it in there."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Thoughtful; stress 'how' and 'presented'.

---

### Segment 9 (1:20 – 1:30): Everyone Added a Sentence

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. Turns in a slow circle as new sticky notes land on the hoodie. At 1:26, throws both hands up.
* **Visual Overlay:** Sticky notes in different colors slap onto a tall prompt card, each tagged with a team name: 'design', 'security', 'support'. Two notes glow red where they contradict.
* **Spoken Script:**
  "Every team added a sentence to my prompt. Now my rules fight each other!"
* **Vocal Direction:** Overloaded AJ's voice: fast, frazzled, a little too loud. Exasperated, near a shout on 'fight each other'.

---

### Segment 10 (1:30 – 1:40): The Frankenprompt

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 1:33, mimes stacking blocks until they wobble. At 1:37, sets both hands flat on the desk.
* **Visual Overlay:** A stamp lands on the tall prompt card: 'The Frankenprompt'. Then four empty boxes slide in below it: 'principles', 'hooks and gates', 'reference files', 'evals'.
* **Spoken Script:**
  "Anthropic calls that the Frankenprompt. My fix: give each rule one of four homes, so nothing piles up in one prompt."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Playful on 'Frankenprompt', confident on 'four homes'.

---

### Segment 11 (1:40 – 1:50): Home One: Principles

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 1:42, taps box 1. At 1:46, pinches thumb and finger together to show 'small'.
* **Visual Overlay:** Box 1, 'principles', zooms in. Three short lines appear one by one: 'Ask before deleting.', 'Run the tests.', 'Keep replies short.' A small badge: 'always loaded'.
* **Spoken Script:**
  "Home one: a few one-line principles the agent always reads. Keep them short and few, since every line adds to the pile."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Stress 'short and few'.

---

### Segment 12 (1:50 – 2:00): Home Two: Hooks and Gates

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 1:52, taps box 2. At 1:56, makes a firm, flat 'stop' hand.
* **Visual Overlay:** Box 2, 'hooks and gates', zooms in. A code change slides toward a gate; it passes with a green tick. A second change with a red problem gets stopped. Caption: 'runs every time'.
* **Spoken Script:**
  "Home two: rules that must always hold go in code, not the prompt. A hook or gate checks them every time."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Firm; stress 'must always hold' and 'every time'.

---

### Segment 13 (2:00 – 2:10): What a Hook Is

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 2:03, points down at the desk as if at a terminal. At 2:07, shrugs lightly.
* **Visual Overlay:** A small terminal window fades in. A line reads `hook: before each command -> check-rules.sh`, and a green 'ran' tick appears beside it each time a new command scrolls past.
* **Spoken Script:**
  "In Claude Code, a hook is a shell command that runs at set moments. The model doesn't choose whether it runs."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Reassuring; stress 'doesn't choose'.

---

### Segment 14 (2:10 – 2:20): Home Three: Reference Files

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 2:12, taps box 3. At 2:16, mimes pulling a book off a shelf.
* **Visual Overlay:** Box 3, 'reference files', zooms in. A shelf of thick folders appears, each with a one-line label on its spine. One folder slides out and opens only when the agent asks for it. Caption: 'loaded when needed'.
* **Spoken Script:**
  "Home three: long how-to guides go in reference files. The agent sees a short description and loads the rest when needed."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Stress 'when needed'.

---

### Segment 15 (2:20 – 2:30): An 80 Percent Cut

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 2:23, brings both hands together to show something shrinking.
* **Visual Overlay:** A tall bar labeled 'built-in instructions' shrinks to a short one: 'over 80% shorter'. A small note: 'skills = how-to guides, loaded on demand'. Source line: 'Anthropic, October 2026'.
* **Spoken Script:**
  "Anthropic cut Claude Code's built-in instructions by over 80 percent for its more advanced models. Loading skills on demand helped."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Impressed but factual. Stress 'over 80 percent'.

---

### Segment 16 (2:30 – 2:40): Home Four: Evals

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, medium-wide shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 2:32, taps box 4. At 2:35, holds up ten fingers. At 2:38, holds up one finger.
* **Visual Overlay:** Box 4, 'evals', zooms in. Ten task cards line up, each with a check box and 'known good answer'. Caption: 'one change at a time'.
* **Spoken Script:**
  "Home four: evals, test tasks with known good answers. Ten examples is enough to start. Change one thing at a time."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Encouraging; make 'enough to start' sound doable.

---

### Segment 17 (2:40 – 2:50): I Can Breathe

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. The hood falls back as sticky notes peel off the hoodie and float away. At 2:45, takes a big, slow breath and smiles.
* **Visual Overlay:** The paper stacks shrink. The four boxes, 'principles', 'hooks and gates', 'reference files', 'evals', glow softly behind the avatar, each holding its rules.
* **Spoken Script:**
  "Wait... a few short principles, and the rest loads only when needed? I can breathe again!"
* **Vocal Direction:** Overloaded AJ's voice, now slowing down: relieved, almost laughing on 'breathe again'.

---

### Segment 18 (2:50 – 3:00): Your Turn

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, medium shot, 16:9.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk, leaning in with direct eye contact. At 2:55, gives a warm, open smile.
* **Visual Overlay:** The four homes appear as small icons along the bottom. A badge slides in: 'Comment below'.
* **Spoken Script:**
  "Principles, hooks, reference files, evals. Which rule does your agent keep breaking? Tell me below, and where it belongs."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Peer-to-peer and curious. End on eye contact.

---

## Short (9:16, 1080x1920)

### Segment S1 (0:00 – 0:10): Which One Wins?

* **Environment & Lighting:** A cramped desk buried under stacks of printed rule sheets and hundreds of pastel sticky notes, papers sliding off the edges. Harsh, flickering overhead fluorescent light with a cold green tint; a monitor behind shows a wall of scrolling text, nothing readable. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Character: Overloaded AJ, playing the AI agent. Oversized, wrinkled mustard-yellow hoodie with the hood half up, a dozen pastel sticky notes stuck to the chest and sleeves, a pencil tucked behind one ear. Holds a rule sheet in each hand, eyes darting between them. At 0:07, grabs the hood with both hands.
* **Visual Overlay:** Two sticky notes zoom up: 'Rule 47: always ask first' and 'Rule 12: never ask, just do it'. They flash red. Counter: '50 rules'.
* **Spoken Script:**
  "Rule forty-seven: always ask first. Rule twelve: never ask, just do it. Which one wins? My head hurts."
* **Vocal Direction:** Overloaded AJ's voice: fast, frazzled, a little too loud.

---

### Segment S2 (0:10 – 0:20): Context Rot

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk. At 0:13, gestures over one shoulder. At 0:17, points up at the chart.
* **Visual Overlay:** A line chart drops in: 'input length' along the bottom, 'reliability' sliding down. Caption: 'illustration; Chroma, 2025: 18 models'.
* **Spoken Script:**
  "Every rule you add makes your agent's input longer. Chroma tested 18 models: the longer the input, the less reliable they got."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Stress 'longer' and 'less reliable'.

---

### Segment S3 (0:20 – 0:30): Principles, Hooks and Gates

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 0:22, holds up one finger. At 0:26, makes a firm 'stop' hand.
* **Visual Overlay:** Box 'principles' with three one-line rules. Then box 'hooks and gates': a gate stops a change with a red problem. Caption: 'runs every time'.
* **Spoken Script:**
  "So give each rule a home. A few one-line principles it always reads. Rules that must hold go in hooks and gates."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Brisk and clear.

---

### Segment S4 (0:30 – 0:40): Reference Files and Evals

* **Environment & Lighting:** A tidy home office at night, facing a large whiteboard wall that is blank except for what the overlay draws. A warm desk lamp lights the face from the left; soft blue monitor glow from the right. No brand logos. Eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Stands beside the whiteboard. At 0:32, mimes pulling a book off a shelf. At 0:36, gives a thumbs-up.
* **Visual Overlay:** Box 'reference files': one folder slides off a shelf only when asked for. Box 'evals': ten task cards with check boxes.
* **Spoken Script:**
  "Long guides go in reference files, loaded only when needed. And a few evals tell you if a change helped."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. Upbeat and practical.

---

### Segment S5 (0:40 – 0:50): Your Turn

* **Environment & Lighting:** A tidy home developer desk at night. One ultrawide monitor behind the avatar glows soft blue, nothing readable on it; a warm desk lamp on the left lights the face. Wooden desk, a mug, a small plant, no brand logos. Shallow depth of field, eye-level camera, chest-up vertical framing, 9:16.
* **Avatar (Wardrobe & Physicality):** Character: Calm AJ, the developer. Relaxed-fit heavyweight charcoal crew-neck t-shirt, no logos, no jewelry. Seated at the tidy desk, leaning in with direct eye contact. At 0:45, gives a warm, open smile.
* **Visual Overlay:** A badge slides in: 'Comment below'. A few sticky notes drift across the frame, ready to loop into the clutter.
* **Spoken Script:**
  "Which rule does your AI agent keep breaking? Tell me below, and say where you'd put it."
* **Vocal Direction:** Calm AJ's voice: steady, warm and clear. End on eye contact, on an open note, so the Short loops.

---

## Audio Prompt (30 s seamless loop, both cuts)

Instrumental only, 30 seconds, seamless loop. 92 BPM, key of F major. Playful lo-fi: soft Rhodes chords, a bouncy muted bass, brushed drums and a light pizzicato motif that can feel either busy or calm. Clean start and end for an infinite loop, no vocals. Mix at -22 dB under the voice.

---

## Transitions & SFX Schedule

Long version: every cut into the cluttered desk gets a paper-rustle and a fluorescent buzz (0.8 s, half before the cut, half after: 0:40, 1:00, 1:20, 2:40); every cut back to Calm AJ gets a soft, clean swipe (0.6 s: 0:10, 0:50, 1:10, 1:30, 2:50), and every cut from one Calm set to the other a quieter swipe (0.4 s: 0:20, 1:50, 2:00, 2:10, 2:20, 2:30). A marker squeak as the chart draws (0:30) and as the four boxes fill (1:40). A low 'thunk' as the Frankenprompt stamp lands (about 1:31). Sticky notes fluttering away (2:40 to 2:46). A light chime as the outro badge appears (about 2:55).

Short: a paper-rustle into S1's clutter and a clean swipe into each Calm cut (0:10, 0:20, 0:30, 0:40), 0.5 s each; the loop bed carries 0:50 back to 0:00.

---

## YouTube Studio Metadata

**Long version**

Title: Why Your AI Agent Gets Dumber the More Rules You Give It

Description:
Every rule you add makes an AI agent's input longer, and longer input makes models less reliable. Here is where each rule should live instead.

Two versions of AJ's AI avatar play it out: Overloaded AJ, an agent buried in fifty rules, and Calm AJ, who sorts each rule into its home. Chroma tested 18 models in 2025 and found they get less reliable as the input grows longer, even on simple tasks. Anthropic names one failure the Frankenprompt: every team adds a sentence and the rules start to conflict. My fix is to give each rule a home: a few one-line principles, hooks and gates for rules that must hold, reference files loaded only when needed, and evals to check that a change helped.

00:00 Fifty rules, one agent
00:10 Context rot
00:30 What Chroma found
01:20 The Frankenprompt
01:40 Four homes for your rules
02:40 Breathing again
02:50 Your turn

Sources:
Chroma, Context Rot (2025): https://www.trychroma.com/research/context-rot
Anthropic, When to fold subagents into your main agent loop (2026): https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop
Claude Code hooks: https://code.claude.com/docs/en/hooks-guide

An AI avatar of AJ plays both characters and narrates this video. It was made in Google Vids from AJ's own verified face and voice.

#AIagents #ClaudeCode #PromptEngineering #ContextEngineering #LLM #Programming

Pinned comment: Which rule does your AI agent keep breaking, and where would you put it: a principle, a hook, a reference file or an eval?

Tags: AI agents, context rot, prompt engineering, context engineering, Claude Code, hooks, agent rules, AGENTS.md, LLM evals, coding agents, AI for beginners, Chroma context rot

**Short**

Title: Why More Rules Can Make Your AI Agent Worse

Description: Every rule makes your agent's input longer, and Chroma found 18 models got less reliable as input grew. Give each rule a home instead. Full video: (link the long version). An AI avatar of AJ plays both characters, made in Google Vids from his own verified face and voice. #Shorts #AIagents #ClaudeCode

Upload: tick 'Altered or synthetic content: Yes' in YouTube Studio for both cuts.

---

## Assets

- AJ's personal avatar, selected in the Vids character selector, for both characters. The look comes from each segment's wardrobe and set.
- Props named in the prompts: rule sheets, sticky notes, a paper strip, a pencil.
- Overlays, drawn as described: the clashing rule notes and counter, the picture-in-picture of the cluttered desk, the context box, the reliability chart (an illustration), the apple strip, the look-alike notes and cards, the team-tagged prompt card and Frankenprompt stamp, the four boxes, the gate, the hook terminal line, the shrinking instructions bar, the ten task cards. No real repository or account appears.
- The 30 s audio loop above, generated once and used under both cuts.
