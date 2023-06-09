#!/usr/bin/env bash

git_root=$(git rev-parse --show-toplevel)

git_mode=${1-false}

set -e

pushd "${git_root}" >/dev/null

echo -e "\nFormat with black..."
black .
echo -e "\nRemove unused imports with autoflake..."
autoflake -r -i .
echo -e "\nSorting imports with isort..."
isort .

# add files which were added before again such that commit gets modified
if [[ $git_mode == true ]]; then
  git diff --name-only --cached | xargs -I {} git add {}
fi

popd > /dev/null
