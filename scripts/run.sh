#!/usr/bin/env bash

# This script is intended for locally running the application for dev purposes

set -e

git_root="$(git rev-parse --show-toplevel)"

# The following line makes sure that the key value pairs from the .env file are converted to real env vars
# see https://stackoverflow.com/questions/19331497/set-environment-variables-from-file-of-key-value-pairs
export $(grep -v '^#' "$git_root/.lizard.env" | xargs -d '\n')
export DB_HOST=0.0.0.0
export DB_PORT=6546

pushd "$git_root" >/dev/null

docker-compose up -d lizard_db

popd >/dev/null

python -m uvicorn backend.application:app --reload