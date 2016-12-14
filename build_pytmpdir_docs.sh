#!/usr/bin/env bash
echo "Building Sphinx documentation for pytmpdir!"
echo "Removing old documentation in build folder."
rm -frv docs/build
echo "Updating module rst files.  This will overwrite old rst files."
export PYTHONPATH="`pwd`"
sphinx-apidoc -f -e -o docs/source pytmpdir
echo "Build HTML files."
sphinx-build -b html docs/source docs/build
echo "Opening created documentation..."
start docs/build/index.html