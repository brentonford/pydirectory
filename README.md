# pydirectory
A class representing a file system directory, that deletes on garbage collect.

Required:
* Python 3.5

The Directory object can be 
* Initialised on an existing directory
* Scan that directory
* Be interigated for the file list
* Create new files
* Open files

It can also be used when a temporary directory of files is needed, that will be garbage
collected when it falls out of scope.

This is especially usefull when using the tarfile, etc packages.
