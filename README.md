# RobotEconomist

## Demo 

`python -m src.main --instrument=income --outcome=education`

## Adding a new corpus

- Add `jsonl` file in `json` directory with list of dictionaries containing and ID and text OR write txt files into the `txt` directory, typically to `f"data/{corpus}/txt"` 
- Create a `pipelines.pipeline_config` object w your settings; set the `corpus` parameter to your corpus
- Run `python -m pipelines.pipeline`

## Set up

#### Set up conda

There is an `config/econ.yml` file with all of the conda information in it
- To build the env for the first time: `conda env create -f config/econ.yml`
- To update the env: `make conda` 

#### Set up machine 

`brew install git-lfs`

`brew install jq`

## Repo tour 

`scrapers` stores code to get NBER abstracts (also Management Science?)