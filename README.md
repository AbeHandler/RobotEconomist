# RobotEconomist

## Demo 

`python -m src.main --instrument=income --outcome=education`

## Processing s2orc

- s2orc is processed in the data repo on Alpine. See `data/s2orc/process_full_dataset.slurm` for details. This gets data ready for the pipeline. The last line of the script will try to copy into RobotEconomist on `alpine/scratch`
- The source of truth for s2orc on CURC is `/pl/active/abha4861/abha4861s2orc` and `process_full_dataset` starts by rsynching this to `/alpine/scratch`.

## Adding a new corpus

- Add a `papers.jsonl` file in `json` directory (e.g. `data/nber_abstracts/json/papers.jsonl`). This file should have the form `{"id":1001,"text": ...}`. In the config object, for this example, set `docs_text_field` to `text` and `docs_id_field` to `id`
- Set `debug_mode` to False and `clear_cache` to True
- Create a `pipelines.pipeline_config` object w your settings; set the `corpus` parameter to your corpus
- Run `python -m pipelines.pipeline`


## Set up

#### Set up conda

There is an `config/econ.yml` file with all of the conda information in it
- To build the env for the first time: `conda env create -f config/econ.yml`
- To update the env: `make conda` 

#### Set up machine 

`brew install jq`

## Repo tour 

`scrapers` stores code to get NBER abstracts, ISR abstracts and MGMT Science abstracts
