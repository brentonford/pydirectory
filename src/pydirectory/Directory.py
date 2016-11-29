"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""

import os
import shutil
import tempfile
import weakref
from subprocess import check_output
from platform import system


class DirSettings:
    tmpDirPath = '/tmp'
    defaultDirChmod = 0o700


__author__ = 'synerty'

textchars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(list(range(0x20, 0x100)))
is_binary_string = lambda bytes_: bool(bytes_.translate(None, textchars))


class FileDisappearedError(Exception):
    pass


class FileClobberError(Exception):
    pass


class Directory(object):
    def __init__(self, initWithDir: bool = None,
                 autoDelete: bool = True,
                 inDir: str = None):
        self._files = {}
        self._autoDelete = autoDelete

        if initWithDir:
            self.path = initWithDir
            self.scan()

        else:
            if (os.path.isdir(inDir if inDir else
                              DirSettings.tmpDirPath) is False):
                os.mkdir(inDir if inDir else DirSettings.tmpDirPath)
            self.path = tempfile.mkdtemp(dir=(inDir if inDir else
                                              DirSettings.tmpDirPath))

        closurePath = self.path

        def cleanup(me):
            if autoDelete:
                shutil.rmtree(closurePath)

        self.__cleanupRef = weakref.ref(self, cleanup)

    @property
    def files(self) -> ['File']:
        """ Files
        :return: A list of the Directory.File objects
        """
        return list(self._files.values())

    @property
    def pathNames(self) -> [str]:
        """ Path Names
        :return: A list of path + name of each file, relative to the directory root
        """
        return [f.pathName for f in list(self._files.values())]

    @property
    def paths(self) -> [str]:
        """ Paths
        :return: A list of the path names, effectively a list of relative directory
                  names
        """
        return set([f.path for f in list(self._files.values())])

    def getFile(self, path: str = '', name: str = None, pathName: str = None) -> 'File':
        assert (name or pathName)
        pathName = (pathName if pathName else os.path.join(path, name))
        return self._files.get(pathName)

    def createFile(self, path: str = "", name: str = None, pathName: str = None) -> 'File':
        file = File(self, path=path, name=name, pathName=pathName)
        self._files[file.pathName] = file
        return file

    def createHiddenFolder(self):
        if not self._autoDelete:
            raise Exception("Hidden folders can only be created within"
                            " an autoDelete directory")
        return tempfile.mkdtemp(dir=self.path, prefix=".")

    def listFilesWin(self):
        output = []
        for dirname, dirnames, filenames in os.walk(self.path):
            for subdirname in dirnames:
                output.append(os.path.join(dirname, subdirname))
            for filename in filenames:
                output.append(os.path.join(dirname, filename))
        return output

    def listFilesLinux(self):
        find = "find %s -type f" % self.path
        output = check_output(args=find.split()).strip().decode().split(
            '\n')
        return output

    def scan(self):
        self._files = {}
        if system() is "Windows":
            output = self.listFilesWin()
        else:
            output = self.listFilesLinux()
        output = [line for line in output if "__MACOSX" not in line]
        for pathName in output:
            if not pathName:  # Sometimes we get empty lines
                continue

            pathName = pathName[len(self.path) + 1:]
            file = File(self, pathName=pathName, exists=True)
            self._files[file.pathName] = file

        return self.files

    def clone(self, autoDelete=True):
        d = Directory(autoDelete=autoDelete)
        os.rmdir(d.path)  # shutil doesn't like it existing
        shutil.copytree(self.path, d.path)
        d.scan()
        return d

    def _fileDeleted(self, file):
        self._files.pop(file.pathName)

    def _fileMoved(self, oldPathName, file):
        self._files.pop(oldPathName)
        self._files[file.pathName] = file


class File(object):
    def __init__(self, directory, path='', name=None, pathName=None,
                 exists=False):
        assert (isinstance(directory, Directory))
        assert (name or pathName)

        self._directory = weakref.ref(directory)

        if name:
            path = path if path else ''
            self._pathName = os.path.join(path, name)

        elif pathName:
            self._pathName = pathName

        self._pathName = self.sanitise(self._pathName)

        if not exists and os.path.exists(self.realPath):
            raise FileClobberError(self.realPath)

        if exists and not os.path.exists(self.realPath):
            raise FileDisappearedError(self.realPath)

        if not os.path.exists(self.realPath):
            with self.open(append=True):
                os.utime(self.realPath, None)
                os.chmod(self.realPath, 0o600)

    # ----- Name and Path setters
    @property
    def path(self):
        return os.path.dirname(self.pathName)

    @path.setter
    def path(self, path):
        path = path if path else ''
        self.pathName = os.path.join(path, self.name)

    @property
    def name(self):
        return os.path.basename(self.pathName)

    @name.setter
    def name(self, name):
        self.pathName = os.path.join(self.path, name)

    # ----- pathName functions

    @property
    def pathName(self):
        return self._pathName

    @pathName.setter
    def pathName(self, pathName):
        if self.pathName == pathName:
            return

        pathName = self.sanitise(pathName)
        before = self.realPath
        after = self._realPath(pathName)

        assert (not os.path.exists(after))

        newRealDir = os.path.dirname(after)
        if not os.path.exists(newRealDir):
            os.makedirs(newRealDir, DirSettings.defaultDirChmod)

        shutil.move(before, after)

        oldPathName = self._pathName
        self._pathName = pathName

        self._directory()._fileMoved(oldPathName, self)

    # ----- Util functions

    def open(self, append=False, write=False):
        flag = {(False, False): 'r',
                (True, False): 'a',
                (True, True): 'a',
                (False, True): 'w'}[(append, write)]

        realPath = self.realPath
        realDir = os.path.dirname(realPath)
        if not os.path.exists(realDir):
            os.makedirs(realDir, DirSettings.defaultDirChmod)
        return open(self.realPath, flag)

    def delete(self):
        directory = self._directory()
        assert isinstance(directory, Directory)

        realPath = self.realPath
        assert (os.path.exists(realPath))
        os.remove(realPath)

        directory._fileDeleted(self)

    def remove(self):
        """ Remove
        Removes the file from the Directory object, file on file system remains on disk
        """
        directory = self._directory()
        assert isinstance(directory, Directory)
        directory._fileDeleted(self)

    @property
    def size(self):
        return os.stat(self.realPath).st_size

    @property
    def mtime(self):
        return os.path.getmtime(self.realPath)

    @property
    def isContentText(self):
        with self.open() as f:
            return not is_binary_string(self.open().read(40000))

    @property
    def realPath(self):
        return self._realPath()

    def _realPath(self, newPathName=None):
        directory = self._directory()
        assert (directory)
        return os.path.join(directory.path,
                            newPathName if newPathName else self._pathName)

    def sanitise(self, pathName):
        assert isinstance(pathName, str)
        assert not '..' in pathName
        assert not pathName.endswith(os.sep)

        while pathName.startswith(os.sep):
            pathName = pathName[1:]

        return pathName
