# Checking the Checker

CISC-810 Research Foundations, Group 1 (November 10, 12 or 17, 2026). Eight minutes with a hard
cut-off, then two minutes of questions. Light theme for a lit room. The audience is CISC PhD
students from many areas of computing, not citation or language-processing specialists.

**Main point:** a clean report counts only if the checker can fail and says what it skipped.
Slide 2 states it; every main slide serves it.

## Structure

| # | Slide | Chapter |
|---|---|---|
| 1 | Title (magnifier over a check mark, Follow-along QR) | |
| 2 | The point: HalRef's real output after checking nothing; what I did, why you should care (`data-contribution`) | 1 · The point |
| 3 | Why it matters: models invent references, papers keep them, ACL 2026 checks by software | 2 · Why it matters |
| 4 | Six silent failures, days each lasted, coloured by group | 3 · My checker |
| 5 | Three groups by step, each with its guard; a test reaches only two | 3 · My checker |
| 6 | Re-break: tests that failed per defect put back, 9 of 11 caught | 3 · My checker |
| 7 | Five public checkers by three faults: three printed a clean result after checking nothing | 4 · Other checkers |
| 8 | Conclusion: the main point, three results, the three guards, two open problems (`data-conclusion`) | |
| 9 | Thank you, questions (closing QR) | |

No agenda slide: slide 2 does that job, and the chapter rail follows `data-chapter`. Nothing
announces a pause; the title's notes invite interruptions, and questions come at the end. The
spoken script is capped at 7 minutes (`CAP_MINUTES` in `scripts/script_length.py`).

Backup, for questions: what is new over ordinary bugs (and Hill 2026), one tool and its author,
the Table II public-record matrix, why a test cannot catch a check that never ran (and the open
seventh failure), why a false "not found" matters, Case 6's five runs, how the other checkers
were tested, cases 3 to 5 up close, what "verified" means, references.

## Sources

Every number and quoted output is in `data/deck-data.js`, each with the section, table or
evidence file it comes from: the revised manuscript
`classes/cisc810-research-foundations/03-assignments/06-manuscript-revision-assignment/AJ-Barea-Checking-The-Checker-Revised.tex`
and its `evidence/` (`hidden-for.md`, `rebreak.md`, `other-checkers-run.md`,
`fabrication-rates.md`). That folder is not in this repository, so CI cannot recheck the values;
`figs.js` recounts the counts the titles state (9 of 11, three of five, two all "not found") from
the data and fails the deck's gates on a mismatch.

The manuscript is a course paper; the case history behind it stays in a private repository.
Nothing here quotes it beyond what the manuscript prints.

## Figures

`figs.js` draws this talk's charts from the data before `../shared/deck.js` runs: the case bars
(`data-bars`), the re-break columns (`data-columns`), the checker matrix (`data-matrix`), the
Case 6 runs (`data-runs`), and bars sized to a value (`data-bar`, `data-range`). The groups
are plum, orange and sky, named in the figures; marks in the matrix repeat the colour as a symbol.
