#!/usr/bin/env bash

# grep for dataclasses that are not frozen
find src -type f  | grep -E .py$ | parallel -j 1 'grep -n dataclass\( {} /dev/null' | grep -v "(frozen=True)"

# run shellcheck on all scripts
shellcheck scripts/*sh

# run mypy to check for missing types
mypy --namespace-packages --disallow-untyped-defs -p src
mypy --namespace-packages --disallow-untyped-defs -p test

flake8 src
flake8 test
mypy test/*.py
