## 0.7.0 (2022-09-20)

### Feat

- support phrase extraction and semantic similiarty in pipeline

### Refactor

- refactor pipeline to allow for multiple similiarities files
- update pipeline to do phrase extraction
- **`rule_based_extractor.py`-and-some-`scripts`**: modify `rule_based_extractor.py` to use the `MatcherFactory`
- modify kdt provider to take an extractions file reader, to allow them to be swapped ourt

## 0.6.0 (2022-09-19)

### Feat

- Print reports of possible violations to terminal
- add noisy instrumental variable extractor to `iv_extractors`

### Fix

- fix some little file name bugs in pipeline while writing to `txt`
- **`src/auditor.py`**: work around bug in networkx dfs

### Refactor

- big refactor, introduced a `PossibleViolation` object
- adjusting pipeline and printers a little to make it easy and fast to read reports
- moving code around to get `scripts.hunt_for_violoations` to work
- change `src.extractors` to have a a single heuristic extractor that can do both iv and outcomes
- created an `extractors` directory that holds `iv_extractors` and `outcome_extractors`
- refactor pipeline while adding ivis corpus

## 0.5.0 (2022-09-17)

### Feat

- add semantic similarity to the dag
- Add a similarity indexing component to the pipelines
- add a controls command to `main.py` which tells you what affects a variable
- add support for s2orc datasets

### Fix

- make minor fixes to update pipeline for `s2orc` corpus

### Refactor

- adjustments to s2orc pipeline to use a config and load semantically similar edges from disk
- refactor graph builder to use edge builder
- updates more parts of pipeline to use a config
- move semantic suggester into `src.semantic_suggester` and refactor into a KDT provider and KDT consumer

## 0.4.9 (2022-09-12)

### Fix

- remove typer dependency. It is causing headaches w/ package compatibility. It is also causing headaches w/ default args

## 0.4.7 (2022-09-12)

### Fix

- **`src/main.py`**: update src.main to include missing self

## 0.4.5 (2022-09-12)

### Fix

- typer version in setup.cfg did not exist, change to 0.4.2

## 0.4.3 (2022-09-12)

### Fix

- **fixing-`setup.cfg`-name**: updates changelog to reflect new name in `setup.cfg`

## 0.4.2 (2022-09-12)

### Fix

- update build to include path_printers in the pip packge

## 0.4.0 (2022-09-12)

### Feat

- add support for paper summaries when reporting violations; add nber_abstracts corpus

### Fix

- **`src/main.py`-and-`src/auditor.py`**: program does not crash when user queries for unknown variable
- fixes some small bugs in the src.pipelines
- fixes issue with paths in pipeline; Path.iterdir > glob, apparently

### Refactor

- **`src/corpus`,-`src/dag`-and-`src/*py`**: moves old code to an `old` directory in case it is needed again. System runs without it fine. Speculative generalization?
- remove old tests which are for abstractions we may not need. This was speculative generalization. See `old/test_all.py` for old tests
- adjust corpus processing code to handle different corpus, and make more readable
- handles errors when not in dag

## 0.3.9 (2022-09-08)

### Feat

- makes a package that can be installed via `$ pip install roboteconomist`

## 0.3.8 (2022-09-08)

### Feat

- makes a package that can be installed via `$ pip install roboteconomist`

## v0.2.0 (2022-09-06)

### Feat

- **`main.py`,-`src/semantic_suggester.py`,-`scripts/build_simple_graph.py`-and-`scripts/rule_based_matcher.py`**: start support for (1) CLI in `main.py`, (2) graph construction, (3) rule-based matching and (4) query similarity suggestion

### Refactor

- refactoring `scripts/query_neighbors.py` to get it ready to be imported into main library

## list (2022-09-04)

### Feat

- add initial support for rule-based extraction from the nber corpus
