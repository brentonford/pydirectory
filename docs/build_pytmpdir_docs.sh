#!/usr/bin/env bash
echo "Building Sphinx documentation for pytmpdir!"
echo "Removing old documentation in build folder."
rm -frv build
echo "Updating module rst files.  This will overwrite old rst files."
set PYTHONPATH="C:\Users\brentonford\Documents\ORMOB\pytmpdir"
sphinx-apidoc -f -o ../docs/source ../pytmpdir
echo "Build HTML files."
sphinx-build -b html source build
echo "Opening created documentation..."
start build/index.html