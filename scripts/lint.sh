#!/usr/bin/env bash

git_root=$(git rev-parse --show-toplevel)

set -e

pushd "${git_root}" >/dev/null

echo -e "\nChecking compile types via mypy..."
echo -e "\nSource: application.py..."
mypy backend/application.py
echo -e "\nSource: tests folder..."
mypy tests

popd > /dev/null