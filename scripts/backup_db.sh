#!/bin/bash

# This script is meant to be run as a cronjob

# Bash scripting "safe" mode
set -euo pipefail

docker_cmd=$(which docker)

backup_dir="$1"

created_at=$(date +%Y_%m_%d)
$docker_cmd exec -t lizard_db pg_dump -F c -U postgres_user -p 5432 -h localhost -d lizard > "${backup_dir}/${created_at}.dump"
