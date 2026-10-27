# Federated Agents

The talk on Federated Agents: coding agents that learn each company's house rules without its
code leaving. A short talk for someone new to the work, then a list of frequently asked questions
whose items link to their answers.

**No figure is typed by hand.** `figures.py` derives every figure from the sphragis artifacts
and writes `data/readings.js`, which the slides bind to with `data-value`, `data-dots` and
`data-if`. `figures.py --check` fails when the committed copy no longer matches, and CI runs it
daily. To add a figure, add it to `readings()` and bind a slide to its name. The study's time windows come from sphragis `sphragis/corpus/windows.py`, the module its
collection and experiment code read them from.

**The rivals map** (`data/related.js`) places published designs by who decides what is shared and
whether the shared part is tested. Each placement comes from a full-text read of the paper, with
the page noted beside it.

**The PDF version** of this talk imports `readings()` from here, so both versions show the same
figures. Changing `readings()` makes the PDF version's own check fail until it is rebuilt, so
rebuild it in step.

```
python figures.py           # write data/readings.js
python figures.py --check   # is it current?
```

`SPHRAGIS` points at a sphragis checkout; the default is a sibling of this repository.
