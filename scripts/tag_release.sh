#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"
cd ..

PORCELAIN=$(git status --porcelain)
if [[ ${#PORCELAIN} -ne 0 ]]; then
  echo "ERROR: cannot release from dirty directory!"
  exit 1
fi

PYTHON_VERSION=$(python setup.py --version)
export VERSION_TAG=v$PYTHON_VERSION

git fetch --tags origin
if [ $(git rev-parse --verify "$VERSION_TAG^{tag}" 2> /dev/null) ]; then
  echo "ERROR: tag $VERSION_TAG already exists!"
  exit 1
fi

LATEST_TAG_VERSION=$(git tag | grep -E ^v\\d+\\.\\d+\\.\\d+ | cut -c 2- | sort -V | tail -1)
newer_tag=$(echo -e "$LATEST_TAG_VERSION\n$PYTHON_VERSION" | sort -V | tail -1)
if [ "$newer_tag" != "$PYTHON_VERSION" ]; then
  echo "ERROR: $PYTHON_VERSION is not newer than $LATEST_TAG_VERSION!"
  exit 1
fi

echo "Tagging $VERSION_TAG..."
git tag $VERSION_TAG main --message "tagging ${VERSION_TAG%%*( )}"

echo "Pushing tags to origin..."
git push --follow-tags
