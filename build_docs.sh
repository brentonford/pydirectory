#!/usr/bin/env bash
PACKAGE="pytmpdir"

set -o nounset
set -o errexit

echo "Retrieving latest version tag"
VER=$(git describe --tags `git rev-list --tags --max-count=1`)

echo "Setting version to $VER"
sed -i "s;.*version.*;__version__ = '${VER}';" ${PACKAGE}/__init__.py

echo "==========================================="
echo "Building Sphinx documentation for pytmpdir!"
echo "==========================================="

echo "Removing old documentation in build folder."
rm -fr docs/build

echo "Updating module rst files.  This will overwrite old rst files."
export PYTHONPATH="`pwd`"
sphinx-apidoc -f -e -o docs/source pytmpdir '*Test.py'

echo "Build HTML files."
sphinx-build -b html docs/source docs/build

echo "Opening created documentation..."
start docs/build/index.html