# AWARE-AI Winter Symposium: midpoint talk

AJ's 5-minute trainee midpoint talk, Tuesday, January 12, 2027 (2 minutes of Q&A after; the organizers cut speakers off at 5:00). Every trainee's slides live in one shared Google Slides deck, so this talk has no web deck. Instead, `build.py` makes AJ's six slides as a .pptx on that deck's own template, to import into his slot.

| File | Holds |
|---|---|
| `build.py` | Builds the six slides: AJ's name slide from the template, then five content slides with native, editable figures |
| `script.md` | What AJ says on each slide; `build.py` fills in its figures and checks it against the slides and the time budget |

## Build

1. In the shared deck, choose File > Download > Microsoft PowerPoint (.pptx). Save it under `_exports/`, which git ignores, because it holds the whole cohort's slides.
2. Run `uv run aware-ai-midpoint-2027/build.py _exports/symposium.pptx _exports/aware-ai-midpoint-2027`.

The build writes `aware-ai-midpoint-2027.pptx` and `script.md`, with the figures filled in, and prints each slide's words and seconds at 140 words a minute. It fails if the script's sections do not match the slide titles, or if the script runs past 4.5 minutes.

The numbers on the slides come from `federated-agents/data/readings.js`, which that talk's `figures.py` generates from the sphragis artifacts. None is typed by hand.

## Put the slides in the shared deck

1. In the shared deck, select AJ's "Please delete this slide" placeholder.
2. Choose File > Import slides > Upload, pick the built .pptx, and select all six slides. Leave "Keep original theme" unticked, so the slides take the deck's own theme.
3. Delete the old "AJ Barea" slide and the placeholder. The imported name slide replaces them.

Touch no other slide: the title slide, the other trainees' slots and the theme belong to the organizers and the cohort.

## Refresh in January

The dashed **FILL** boxes mark facts that are true only after November 2026. Replace each box with the fact, or delete it, and update the matching script line:

- Slide 5, AWARE-AI: trainee council, AFRL visit, TA work, outreach, if any.
- Slide 5, Dissemination: the CISC-810 and LDQIS lab talks (November), and anything new.
- Slide 6: whether the Stage 1 report went in on November 20, and what the December 23 reviews said. If the dates moved, move the timeline too.

## Look

The slides keep the template's look: white, black Arial text. One accent colour, the Federated Agents deck's navy (`federated-agents/deck.css`, `--label`), ties them to that talk. Each slide has a claim title and one figure, built from shapes rather than pictures, so it stays sharp on a projector and editable in Google Slides.

<!-- research(2026-11): five-minute talks teach one new idea (Carroll, Discover "How to Write a 5 Minute Talk");
     assertion-evidence slides (Alley; Harvard Catalyst slide guide); feedback criteria from the symposium form. -->
