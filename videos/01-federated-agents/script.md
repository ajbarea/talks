# Video Script: Why Your Tech Lead Rejects AI Code (And What I'm Testing)

Target Format: Vertical 9:16 (YouTube Shorts / Reels)
Target Duration: ~50 seconds
Look: a new set and outfit in each of segments 1 to 4, on purpose; segment 5 returns to the opening desk and t-shirt so the Short loops.
Source: the Federated Agents deck, [`federated-agents/index.html`](../../federated-agents/index.html), and its speaker notes; live at https://ajbarea.github.io/talks/federated-agents/

---

### Segment 1 (0:00 – 0:10): The Code Review Rejection

* **Environment & Lighting:** A dim, cinematic developer setup with dual ultrawide monitors glowing in deep indigo. A soft amber rim light contours the avatar.
* **The Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal t-shirt. Direct, conspiratorial eye contact. At 0:04, leans in half an inch with an energetic, knowing smirk.
* **Overlay Animation (The Hook):** A floating holographic IDE window shows an AI proudly autocompleting raw database code:
  `rows = psycopg2.connect(DSN).cursor().execute(q)`
  Instantly, a bright crimson code-review comment card slaps down over it:
  `✕ REJECTED: 'Use our db.query() helper. We NEVER open raw connections.'`
  A shower of red sparks reflects subtly against the avatar's face.
* **Spoken Script:**
  "Ever had an AI write code that works... only for your tech lead to reject it with: 'We don't do that here'?"
* **Vocal Direction:** Fast, conversational, punchy. After 'works', a 0.6 s pause with a knowing smile. Emphasize 'works' and drop into a playful, mock-serious tone on 'We don't do that here'.

---

### Segment 2 (0:10 – 0:20): The Unwritten Rules Problem

* **Environment & Lighting:** Seamless cut to an arctic ice cave / server vault. Massive blade racks encased in glowing, translucent blue glacial ice. Cool frosty lighting with a warm key light on the face.
* **The Avatar (Wardrobe & Physicality):** Heavy frost-dusted parka with a subtle high-tech golden collar. At 0:12, gestures with an open palm toward the frozen core.
* **Overlay Animation:** A massive, glowing crystalline neural network is frozen solid in ice (the Base Model). Review comment bubbles hover around it, but cannot penetrate the ice.
* **Spoken Script:**
  "AI misses your team's unwritten house rules. Code review teaches them, which AI never sees. No company wants to share its code."
* **Vocal Direction:** Clear, empathetic problem-statement pacing. Punch 'unwritten house rules' and stress 'share its code'.

---

### Segment 3 (0:20 – 0:30): The Twin-Adapter Idea

* **Environment & Lighting:** Cut to a moody Victorian library with mahogany bookshelves and a roaring fireplace. Rich amber and mahogany tones.
* **The Avatar (Wardrobe & Physicality):** Velvet burgundy jacket with an ascot. Sophisticated and relaxed. At 0:23, brings two hands up, each holding a glowing module.
* **Overlay Animation:** Hovering in front of the frozen core are two modular magnetic adapters:
  1. An Amber/Orange Adapter labeled 'PRIVATE' (fed by the repositories marked ✕: billing, snapping into the model).
  2. A Cyan/Blue Adapter labeled 'SHARED' (fed only by the repositories the company ticks on a short list: ✓ web-app ✓ docs ✕ billing).
* **Spoken Script:**
  "My idea: one frozen model, two add-ons. A private one stays home... a shared one learns only from projects marked shareable."
* **Vocal Direction:** Confident, clear, and intellectually exciting. Genuine smile. Treat 'private' and 'shared' as clean, intuitive concepts.

---

### Segment 4 (0:30 – 0:40): The Federated Punchline (Code Stays Home)

* **Environment & Lighting:** Cut to a futuristic spaceship command bridge looking out across an expansive starfield. Deep violet and golden nebula rim lighting.
* **The Avatar (Wardrobe & Physicality):** Futuristic fleet commander jacket. At 0:35, brings both hands together in a smooth, confident clasp.
* **Overlay Animation:** A network map of different companies (Company A, Company B, Company C). Shimmering blue streams flow from each company to a central server, carrying only updates to the blue shared add-on. Each company's private repository stays put with the text 'CODE STAYS HOME'. At 0:37 a question badge pops over the blue streams: 'WHOSE IS IT?'
* **Spoken Script:**
  "Federated learning shares updates, never code. First comes the data, then the add-ons, then a test: do updates reveal their owner?"
* **Vocal Direction:** Build energy on 'updates, never code', then drop to a curious, open tone and land on 'reveal their owner'.

---

### Segment 5 (0:40 – 0:50): The Community Call to Action

* **Environment & Lighting:** Smooth transition to a dim, cinematic developer setup with dual ultrawide monitors glowing in deep indigo. A soft amber rim light contours the avatar.
* **The Avatar (Wardrobe & Physicality):** Relaxed-fit heavyweight charcoal t-shirt. At 0:42, gives a friendly, conversational lean forward with an amused, curious expression.
* **Overlay Animation:** A sleek, minimalist dark-mode card slides up with the GitHub repository preview:
  `sphragis: open-source tool that turns public code review into datasets`
  Below it, a pulsing badge:
  `Pinned Comment ⬇`
* **Spoken Script:**
  "Open-source tool, link pinned. I follow each community's rules and never republish review text. What's the weirdest rule your reviewers enforce?"
* **Vocal Direction:** Casual, peer-to-peer, and genuinely curious. Smile when asking the question and finish on an upbeat, open-ended rhythm.
