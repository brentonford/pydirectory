.. _README:


=======
Read Me
=======

pytmpdir
--------
A class representing a file system directory, that deletes on garbage collect.

Requirements
------------
- Python 3.3+ (Tested on python 3.5)

The Directory object can be
---------------------------
- Initialised on an existing directory
- Scan that directory
- Be interrogated for the file list
- Create new files
- Open files

It can also be used when a temporary directory of files is needed, that will be 
garbage collected when it falls out of scope.

This is especially use full when using the tarfile, etc packages.

Usage
-----
Creating a directory, that will auto delete when it falls out of scope.
For other options, see the documentation.

Getting Started
---------------
The pytmpdir package can be installed from pypi::

  pip install pytmpdir

