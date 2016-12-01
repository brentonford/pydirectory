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
    """ Directory Settings

    Configuration.
    """

    tmpDirPath = '/tmp'
    defaultDirChmod = 0o700


__author__ = 'synerty'

textChars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(list(range(0x20,
                                                                        0x100)))

isWindows = system() is "Windows"


def is_binary_string(bytes_):
    """ Is Binary String

    Determines if the input variable contains specific ASCII
    characters.

    @param bytes_: Input variable being checked if string.
    @return: True if variable is string.
    """

    return bool(bytes_.translate(None, textChars))


class FileDisappearedError(Exception):
    """ File Disappeared Error

    Raise Exception if file does not exist .
    """

    pass


class FileClobberError(Exception):
    """ File Clobber Error

    Raise Exception if path does not exist.
    """

    pass


class Directory(object):
    def __init__(self, initWithDir: bool = None,
                 autoDelete: bool = True,
                 inDir: str = None):
        """ Directory

        If the directory doesn't exist create a temporary folder.

        @param initWithDir: Force creation of temporary directory.
        @param autoDelete: Remove temporary files and folders.
        @param inDir: Current directory
        @type initWithDir: Boolean
        @type autoDelete: Boolean
        @type inDir: String
        """

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
            """ Cleanup

            Recursively delete a directory tree of the created path.
            """
            if autoDelete:
                shutil.rmtree(closurePath)

        self.__cleanupRef = weakref.ref(self, cleanup)

    @property
    def files(self) -> ['File']:
        """ Files

        @return: A list of the Directory.File objects
        """
        return list(self._files.values())

    @property
    def pathNames(self) -> [str]:
        """ Path Names

        @return: A list of path + name of each file, relative to the directory
        root
        """
        return [f.pathName for f in list(self._files.values())]

    @property
    def paths(self) -> [str]:
        """ Paths

        @return: A list of the path names, effectively a list of relative
        directory names
        """
        return set([f.path for f in list(self._files.values())])

    def getFile(self, path: str = '', name: str = None,
                pathName: str = None) -> 'File':
        """ Get File

        Get File name corresponding to a path name.

        @param path: File path.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @type path: String
        @type name: String
        @type pathName: String
        @return: Specific file from dictionary.
        """

        assert (name or pathName)
        pathName = (pathName if pathName else os.path.join(path, name))
        return self._files.get(pathName)

    def createFile(self, path: str = "", name: str = None,
                   pathName: str = None) -> 'File':
        """ Create File

        Creates a new file and updates file dictionary.

        @param path: File path.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @type path: String
        @type name: String
        @type pathName: String
        @return: Created file.
        """

        file = File(self, path=path, name=name, pathName=pathName)
        self._files[file.pathName] = file
        return file

    def createHiddenFolder(self) -> 'File':
        """ Create Hidden Folder

        Create a hidden folder.  Raise exception if auto delete isn't True.

        @return: Created folder.
        """

        if not self._autoDelete:
            raise Exception("Hidden folders can only be created within"
                            " an autoDelete directory")
        return tempfile.mkdtemp(dir=self.path, prefix=".")

    def _listFilesWin(self) -> ['File']:
        """ List Files for Windows OS

        Search and list the files and folder in the current directory for the
        Windows file system.

        @return: List of directory files and folders.
        """

        output = []
        for dirname, dirnames, filenames in os.walk(self.path):
            for subdirname in dirnames:
                output.append(os.path.join(dirname, subdirname))
            for filename in filenames:
                output.append(os.path.join(dirname, filename))
        return output

    def _listFilesPosix(self) -> ['File']:
        """ List Files for POSIX

        Search and list the files and folder in the current directory for the
        POSIX file system.

        @return: List of directory files and folders.
        """

        find = "find %s -type f" % self.path
        output = check_output(args=find.split()).strip().decode().split(
            '\n')
        return output

    def scan(self) -> ['File']:
        """ Scan

        Scan the directory for files and folders and update the file dictionary.

        @return: List of files
        """

        self._files = {}
        output = self._listFilesWin() if isWindows else self._listFilesPosix()
        output = [line for line in output if "__MACOSX" not in line]
        for pathName in output:
            if not pathName:  # Sometimes we get empty lines
                continue

            pathName = pathName[len(self.path) + 1:]
            file = File(self, pathName=pathName, exists=True)
            self._files[file.pathName] = file

        return self.files

    def clone(self, autoDelete: bool = True) -> 'Directory':
        """ Clone

        Recursively copy a directory tree.  Removes the destination
        directory as the destination directory must not already exist.

        @param autoDelete: Used to clean up files on completion.
        @type autoDelete: Boolean
        @return: The cloned directory.
        """
        d = Directory(autoDelete=autoDelete)
        os.rmdir(d.path)  # shutil doesn't like it existing
        shutil.copytree(self.path, d.path)
        d.scan()
        return d

    def _fileDeleted(self, file: 'File'):
        """ File Deleted

        Drop the file name from dictionary.

        @param file: File name.
        @type file: File
        """

        self._files.pop(file.pathName)

    def _fileMoved(self, oldPathName: str, file: 'File'):
        """ File Moved

        Drop the old file name from the dictionary and add the new file name.

        @param oldPathName: Previous dictionary path name.
        @param file: File name.
        @type oldPathName: String
        @type file: File
        """

        self._files.pop(oldPathName)
        self._files[file.pathName] = file


class File(object):
    def __init__(self, directory: Directory, path: str = '', name: str = None,
                 pathName: str = None, exists: bool = False):
        """ File

        Test whether a path exists.  Set the access and modified time of
        path.  Change the access
        permissions of a file.

        @param directory: Directory instance.
        @param path: File path.
        @param name: File name to be used if passed.
        @param pathName: Joined file name and path to be used if passed.
        @param exists: passed argument default as False.
        @type directory: Directory
        @type path: String
        @type name: String
        @type pathName: String
        @type exists: Boolean
        """

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
    def path(self) -> str:
        """ Path

        Determines directory name.

        @return: Path as string.
        """

        return os.path.dirname(self.pathName)

    @path.setter
    def path(self, path: str):
        """ Path Setter

        Set path with passed in variable.

        @param path: New path string.
        @type path: String
        """

        path = path if path else ''
        self.pathName = os.path.join(path, self.name)

    @property
    def name(self) -> str:
        """ Name

        Determines working directory.

        @return: Directory name as string.
        """

        return os.path.basename(self.pathName)

    @name.setter
    def name(self, name: str):
        """ Name Setter

        Set name with passed in variable.

        @param name: New name string.
        @type name: String
        """

        self.pathName = os.path.join(self.path, name)

    @property
    def pathName(self) -> str:
        """ Path Name

        Returns stored path name.

        @return: Path Name as string.
        """

        return self._pathName

    @pathName.setter
    def pathName(self, pathName: str):
        """ Path Name Setter

        Set path name with passed in variable, create new directory and move
        previous directory contents to new path name.

        @param pathName: New path name string.
        @type pathName: String
        """

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

    def open(self, append: bool = False, write: bool = False):
        """ Open

        Pass arguments and return open file.

        @param append: Open for writing, appending to the end of the file if
        it exists.
        @param write: Open for writing, truncating the file first.
        @type append: Boolean
        @type write: Boolean
        @return: Open file function.
        """

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
        """ Delete

        Deletes directory and drops the file name from dictionary.  File on
        file system removed on disk.
        """

        directory = self._directory()
        assert isinstance(directory, Directory)

        realPath = self.realPath
        assert (os.path.exists(realPath))
        os.remove(realPath)

        directory._fileDeleted(self)

    def remove(self):
        """ Remove

        Removes the file from the Directory object, file on file system
        remains on disk.
        """

        directory = self._directory()
        assert isinstance(directory, Directory)
        directory._fileDeleted(self)

    @property
    def size(self) -> str:
        """ Size

        Determines size of directory.

        @return: Total size, in bytes.
        """

        return os.stat(self.realPath).st_size

    @property
    def mTime(self) -> str:
        """ mTime

        Return the last modification time of a file, reported by os.stat().

        @return: Time as string.
        """

        return os.path.getmtime(self.realPath)

    @property
    def isContentText(self):
        """ Is Content Text

        Determine if the file contains text.

        @return: True if file contains text.
        """

        with self.open() as f:
            return not is_binary_string(self.open().read(40000))

    @property
    def realPath(self) -> str:
        """ Real Path

        Get path name.

        @return: Path Name as string.
        """

        return self._realPath()

    def _realPath(self, newPathName: str = None) -> str:
        """ Private Real Path

        Get path name.

        @param newPathName: variable for new path name if passed argument.
        @type newPathName: String
        @return: Path Name as string.
        """

        directory = self._directory()
        assert directory
        return os.path.join(directory.path,
                            newPathName if newPathName else self._pathName)

    def sanitise(self, pathName: str) -> str:
        """ Sanitise

        Clean unwanted characters from the pathName string.

        @param pathName: Path name variable.
        @type pathName: String
        @return: Path name as string.
        """

        assert isinstance(pathName, str)
        assert '..' not in pathName
        assert not pathName.endswith(os.sep)

        while pathName.startswith(os.sep):
            pathName = pathName[1:]

        return pathName
