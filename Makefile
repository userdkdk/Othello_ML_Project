PYTHON ?= python3

.PHONY: meta meta-check runtime training train-resume

meta:
	$(PYTHON) scripts/build_meta_index.py

meta-check:
	$(PYTHON) scripts/check_meta_index.py

runtime:
	./scripts/run-runtime.sh

training:
	./scripts/run-training.sh

train-resume:
	./scripts/train-resume.sh
