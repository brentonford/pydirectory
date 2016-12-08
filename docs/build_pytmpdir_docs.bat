@echo off
title Build pytmpdir docs!
echo Building documentation for pytmpdir!
echo Removing old documentation in build folder.
rmdir build /s /q
echo Updating module rst files.  This will overwrite old rst files.
rmdir source\scripts /s /q
mkdir source\scripts
copy ..\pytmpdir\Directory.py source\scripts
sphinx-apidoc -f -o source source\scripts
echo Build HTML files.
sphinx-build -b html source build
echo Opening created documentation...
start build\index.html