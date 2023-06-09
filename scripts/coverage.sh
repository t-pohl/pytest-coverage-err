#!/usr/bin/env bash

# Bash scripting "safe" mode
set -euo pipefail
export DB_HOST=0.0.0.0
export DB_PORT=7003
pytest --cov --cov-report term-missing