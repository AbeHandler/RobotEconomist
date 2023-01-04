---
id: cwb9leinatyjkb9kqncgw3l
title: Annotation
desc: ''
updated: 1672786738220
created: 1662602743620
---

### Jan 3, 2023

- Ran a turk pilot on Amazon. In a few cases, workers found things that affect productivity. They agreed on reasonable stuff
- Cohen's kappa is a little low = .3, if you exclude one bad faith case where the worker did not copy/paste something from the actual sentence.

- Would a multi-step process work where you run this task to filter cases where something may affect productivity. You interpret this task as a filter to identify reasonable candidates. Then for cases where there is a span overlap, you run a second task where you ask people: does this sentence say that X affects Y? For that, you would have to insert random Qs where the answer is clearly no. Pick a random NP and productivity. You would likely get good answers for that. I think that is the next thing to test. If we got economists to validate it, that would help.

## Annotation

Here’s an issue. We need to be more precise about what we mean by setting. Is it a it a place? Europe, India,. What about time. Decade? Century? Sector?

#### Some notes on token-level annotation:
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6174533/
- https://academic.oup.com/jamia/article/12/3/296/812057
- https://support.prodi.gy/t/proper-way-to-calculate-inter-annotator-agreement-for-spans-ner/5760

Another option might be to automatically tag NPs in the corpus and ask people about particular spans. So like pre define the possible spans that the economist can choose.
