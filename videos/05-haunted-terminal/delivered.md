<!-- budget: 1100 words -->
# The Terminal That Haunted Me (as delivered)

What the final 50-second cut says and shows, beat by beat. AJ made it in Google Vids from example 3 in [the director skill's examples](../youtube-director/references/examples.md), cut to five 10-second clips. The spoken lines are the cleaned captions (`spooky.en.srt`), checked word for word against a local speech-to-text pass.

Production Mode: Mode A (Google Vids, AJ's personal avatar)
Long version: Landscape 16:9 (1920x1080), 0:50, 30 fps
Short: Vertical 9:16 (1080x1920), 0:50, cut from the long version with one crop per shot
Delivery Tone: Halloween tech-comedy thriller, whispered to warm.
Look: a dark knit crew-neck in the apartment, the desk and the monitors; a black hoodie in the red room; a black t-shirt in the bright home office. The Gemini sparkle mark sits bottom-right in every clip and stays.
On screen: no private repository, account, email, token or key. The terminal text is generated.

This file is a record, not a recording script, so it is named `delivered.md` and the script lint skips it. Its lines run faster than `vids-rules.md` allows (the lint's 150 words a minute); Vids fit them by speaking faster:

| Beat | Words | Spoken span (ASR) | Rate |
|---|---|---|---|
| 1 | 24 | 0.74 to 9.02 s | 174 wpm |
| 2 | 29 | 9.92 to 19.52 s | 181 wpm |
| 3 | 34 | 20.12 to 29.46 s | 218 wpm |
| 4 | 21 | 30.08 to 38.72 s, with a 1.6 s pause | 146 wpm |
| 5 | 34 | 40.18 to 49.78 s | 213 wpm |

Sources: none. The story is a made-up Halloween sketch; the pinned comment links [ajbarea/klepsydra](https://github.com/ajbarea/klepsydra#readme), whose wall keeps each session's subagents and background shells and has a button to end a session.

## Long version (16:9, 1920x1080)

### Segment 1 (0:00 – 0:10): The Haunted Apartment

* **Environment & Lighting:** A dim apartment at night. Moonlight through window blinds throws stripes on the wall; a worn patterned couch; the blue glow of a laptop. Shots: hands typing on the laptop, the avatar on the couch looking around, a profile turn, a wide shot of the couch, then a wide-eyed close-up. 16:9.
* **Avatar (Wardrobe & Physicality):** Dark knit crew-neck. Seated on the couch with the laptop, glancing around the room. At 0:03, turns to look over a shoulder. At 0:08, stares wide-eyed into the camera.
* **Visual Overlay:** None.
* **Spoken Script:**
  "I thought my apartment was haunted. Seriously, every night at 3 AM, the lights on my router flicker and I swear I hear whispering."
* **Vocal Direction:** Whispered, paranoid, suspenseful.

---

### Segment 2 (0:10 – 0:20): The Router and the Logs

* **Environment & Lighting:** A nearly black room. A desk with a router and a tangle of cables, lit from below by orange power-strip lights; green router LEDs blink in a close-up. Handheld, low light. 16:9.
* **Avatar (Wardrobe & Physicality):** Dark knit crew-neck, mostly in shadow. Walks to the desk. At 0:17, points a hand at the router.
* **Visual Overlay:** None.
* **Spoken Script:**
  "I went to inspect the anomaly. Power cycling did nothing. Unplugging the smart-home hub did nothing. But when I checked the logs, there was no ghost. It was worse."
* **Vocal Direction:** Low, building tension, peaking on 'worse'.

---

### Segment 3 (0:20 – 0:30): The Recursive Loop

* **Environment & Lighting:** Over the shoulder at two monitors in deep indigo light: an IDE and a terminal with red text scrolling without end. 16:9.
* **Avatar (Wardrobe & Physicality):** Dark knit crew-neck. Head in one hand, then a hand over the jaw in disbelief. At 0:26, leans in toward the screen.
* **Visual Overlay:** Terminal lines repeating '[CALL] get_active_sessions() -> spawning 5 child threads...'.
* **Spoken Script:**
  "An old recursive debug call I forgot to kill months ago. Waking up to fetch updates, trigger errors, spawn threads and then crawl right back in until the CPU fan screeched like a specter."
* **Vocal Direction:** Fast, exasperated realization.

---

### Segment 4 (0:30 – 0:40): The Kill Signal

* **Environment & Lighting:** A room lit deep red. Terminal text projects onto the avatar's face; a keyboard close-up shows 'KILL -9 14022'; a black screen reads 'PROCESS KILLED'; then the avatar in a dark gaming chair against the red wall. 16:9.
* **Avatar (Wardrobe & Physicality):** Black hoodie, hood up. Types the command. At 0:34, leans back in the chair, eyes closed, and pulls the hood back.
* **Visual Overlay:** 'KILL -9 14022', then 'PROCESS KILLED'. Lines above the command are generated gibberish.
* **Spoken Script:**
  "One quick kill signal and the haunting was over. Silence, just a frozen recursive agent trying to satisfy a promise forever."
* **Vocal Direction:** Quiet and slow, an exhale before 'Silence'.

---

### Segment 5 (0:40 – 0:50): Your Spookiest Bug

* **Environment & Lighting:** A bright home office: several monitors with code, a small laptop, a purple PC fan light, a beige wall. Eye-level medium shot. 16:9.
* **Avatar (Wardrobe & Physicality):** Black t-shirt. Faces the camera holding a coffee mug, amused and tired. At 0:49, sips the coffee.
* **Visual Overlay:** Top left, a dark card with a GitHub mark and 'Pinned Comment ↓' (the line appears twice). Bottom right, a small subscribe chip.
* **Spoken Script:**
  "If you want to keep your agents from spawning recursive haunts, check the repo in the pinned comment. Tell me, what's the spookiest code bug you've ever had to hunt down? Put it below."
* **Vocal Direction:** Warm and natural, winding down.

## Short (9:16, 1080x1920)

The same 50 seconds and audio, cropped to 608x1080 per shot and scaled to 1080x1920. Each crop keeps the face or the screen; the 11-frame 'PROCESS KILLED' shot is letterboxed so the words fit. The Gemini mark is redrawn top-right in every frame, since the crops cut the original. The baked 'Pinned Comment' card falls outside the outro crop; a pasted copy showed its animation and an empty box, so the spoken line carries the call to action. Crop table and commands: [TOOLING-NOTES.md](TOOLING-NOTES.md).
