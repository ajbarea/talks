---
date: 2026-04-18
url: https://www.linkedin.com/feed/update/urn:li:activity:7451396209396838400/
impressions_2026_11_05: 609
---

135× faster than Python FedAvg at 1M params. 138× at 10M.
Python: the right glue, the wrong hot path.

VelocityFL is the uv of federated learning. A PyO3 extension does aggregation, attack simulation, and round orchestration; a thin Python API wraps HuggingFace, PEFT, and PyTorch.

→ Eight Rust-backed strategies, every major Byzantine-robust aggregator from the literature: FedAvg · FedProx · FedMedian · TrimmedMean · Krum · MultiKrum · Bulyan · GeometricMedian, plus a documented path for adding your own.
→ Attack simulation built in: model poisoning, Sybil, Gaussian noise, label flipping.
→ Prefect-native flows for round-level observability. Pure-Python fallback when the Rust extension isn't built.
→ Reproducible: make bench lands you on the same hardware-pinned numbers, full methodology in docs/benchmarks.md.

Where else has "port the hot path to Rust" paid back the integration tax, and where has it bit you instead?

https://lnkd.in/eHckqRU9

#Rust #FederatedLearning #PyO3

<!-- post details, not part of the post text -->
## Details

- Upgraded 2026-11-05: Unicode bold/italic to plain text, em dashes replaced, hashtags cut to 3. Wording, numbers, links and question unchanged.
