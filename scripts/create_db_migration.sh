#!/bin/bash

# Bash scripting "safe" mode
set -euo pipefail

git_root="$(git rev-parse --show-toplevel)"
cd "$git_root/backend/database"
export $(grep -v '^#' "$git_root/.lizard.env" | xargs -d '\n')
export DB_HOST=0.0.0.0
export DB_PORT=6546

poetry run alembic revision --autogenerate -m "$@"
