#!/bin/bash

# Bash scripting "safe" mode
set -euo pipefail

usage() {
    echo "Usage: run_db_migrations [-d] [REVISION]"
    exit 1
}

command="upgrade"
prod=false
while getopts "pd1" FLAG; do
    case "${FLAG}" in
        d)
            command="downgrade"
            ;;
        1)
            alembic_revision="-1"
            ;;
        p) # PROD setup --> do not override DB_HOST and DB_PORT
            prod=true
            ;;
        *)
            usage
            ;;
    esac
done

git_root="$(git rev-parse --show-toplevel)"
cd "$git_root/backend/database"

shift $((OPTIND-1))
set +u
if (( $# > 1 )); then
    usage
elif (( $# == 1 )); then
    alembic_revision="$1"
elif [[ -z $alembic_revision ]]; then
    # default value: take last revision
    alembic_revision="$(alembic history | grep '(head),' | sed -E 's/.*-> ([a-z0-9]+) \(head\),.*/\1/')"
fi
set -u


if [ "$prod" = false ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' "$git_root/.lizard.env" | xargs -d '\n')
    export DB_HOST=0.0.0.0
    export DB_PORT=6546
fi

alembic $command "$alembic_revision"
