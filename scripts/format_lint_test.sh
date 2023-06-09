#!/bin/bash

# Bash scripting "safe" mode
set -euo pipefail

git_root=$(git rev-parse --show-toplevel)

$git_root/scripts/format.sh
$git_root/scripts/lint.sh
$git_root/scripts/test.sh
