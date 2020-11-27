#!/bin/bash
VENV="venv/bin/activate"

if [[ ! -f $VENV ]]; then
    python3 -m venv venv
    . $VENV

    pip install --upgrade pip setuptools
    pip install  "dbt>=0.18.0,<0.19.0"
fi

. $VENV
cd integration_tests

if [[ ! -e ~/.dbt/profiles.yml ]]; then
    mkdir -p ~/.dbt
    cp ci/sample.profiles.yml ~/.dbt/profiles.yml
fi

_models=""
_seeds="--full-refresh"
if [[ ! -z $2 ]]; then _models="--models $2"; fi
if [[ ! -z $3 ]]; then _seeds="--select $3 --full-refresh"; fi

dbt deps --target $1
dbt seed --target $1 $_seeds
dbt run --target $1 $_models
dbt test --target $1 $_models
