# make create_training_data, collins file induces some kind of spacy bug so delete
create_training_data :
	rm -f data/rain/conll/*
	python -m src.utils
	head -40000 data/rain/conll/all.conll > data/rain/conll/train.conll
	tail -6438 data/rain/conll/all.conll > data/rain/conll/dev.conll
	python -m spacy convert data/rain/conll data/train/rain --converter conll

.PHONY: conda
conda:
	conda env update --file config/econ.yml --prune -n econ

.PHONY: test
test:
	conda run -n econ --no-capture-output pytest test

train:
	python -m spacy train config.cfg --paths.train data/train/rain/train.spacy --paths.dev data/train/rain/dev.spacy

# you should be able to overfit the dev set
sanity:
	python -m spacy train config.cfg --paths.train data/train/rain/dev.spacy --paths.dev data/train/rain/dev.spacy

# in the data repo there is a folder called "nber" that runs on alpine. This downloads from alpine to local repo.
# Note that some nber files error out and I never investigated the error.
# If we need a scientifically complete version of nber that has to get fixed. But maybe not high priority for now
data/nber/txt:
	rsync -a abha4861@login13.rc.colorado.edu:/scratch/alpine/abha4861/backupdata/nber/local/txts/ data/nber
	tar -czf data/gzipd/nber.tar.gz data/nber/txt
	# alternately ...
	# mkdir data/nber
	# git lfs install
	# git lfs pull # brew install git-lfs
	# tar -xf data/gzipd/nber.tar.gz data/nber/txt

# use the data repo in AbeHandler/data/nber on alpine to build the tar.gz file
data/nber_abstracts/abstracts.tar.gz:
	tar -xzf data/nber_abstracts/abstracts.tar.gz
	find abstracts -type f | parallel --eta "mv {} data/nber_abstracts/json"
	cat abstracts/*jsonl > data/nber_abstracts/json/papers.jsonl
	rm -rf abstracts


data/nber/spacy/nber.9.spacy.docbin:
	./process_corpus_locally_with_spacy.sh nber

data/gzipd/nber.tar.gz: data/nber/txt
	git lfs track data/gzipd/nber.tar.gz
	git add .gitattributes
	git add data/gzipd/nber.tar.gz
	git commit -m "Adding nber"
	git push origin main

initenv:
	sbatch scripts/initenv.slurm

# from the spacy docs, https://spacy.io/usage/training
initspacy:
	python -m spacy init fill-config base_config.cfg config.cfg

data/doccano/abstracts.doccano.jsonl:
	find data/rain/*json | parallel -j 1 "python scripts/doccano_helper.py {}"

lint:
	./scripts/my_linter.sh

scrapers/mnsc.urls.txt:
	cd scrapers && ./get_informs_paper_urls.sh mnsc 70


### Build stuff

.PHONY: build 
build:
	cz ch  --incremental
	cz bump
	python -m build
	./scripts/build_notice.sh

.PHONY: pypi
pypi:
	python scripts/util/twine_upload.py