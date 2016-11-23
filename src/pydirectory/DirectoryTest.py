"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""
import random
import string
from tempfile import mkstemp

import os
from twisted.trial import unittest

from .Directory import Directory


class DirectoryTest(unittest.TestCase):
    @classmethod
    def makeRandomContents(cls, size=100):
        return ''.join([random.choice(string.ascii_uppercase + string.digits)
                        for _ in range(size)])

    @classmethod
    def makeRandomDirectory(cls):
        directory = Directory()
        dirs = ['']

        def addRecursiveDirs(path):
            if len(dirs) > 20:
                return

            for d in range(5):
                newPath = os.path.join(path, cls.makeRandomContents(10))
                # print "Creating new path %s" % newPath
                dirs.append(newPath)
                addRecursiveDirs(newPath)

                for x in range(10):
                    f = directory.createFile(path=newPath,
                                             name=cls.makeRandomContents(10))
                    with f.open(write=True) as fobj:
                        fobj.write(cls.makeRandomContents(4000))

        addRecursiveDirs('')
        return directory

    def testDir(self):
        d = Directory()
        assert (os.path.isdir(d.path))

        num = 10
        for x in range(num):
            (fd, name) = mkstemp(dir=d.path)
            with os.fdopen(fd, 'w') as f:
                f.write(self.makeRandomContents())

        d.scan()
        self.assertEqual(num, len(d.files))

        for x in range(num):
            d.createFile(name=self.makeRandomContents(10))
            d.createFile(path=self.makeRandomContents(10),
                         name=self.makeRandomContents(10))

        # Create files with bad paths
        self.assertEqual(d.createFile(pathName="/abspath/name1").pathName,
                         'abspath/name1')
        self.assertEqual(d.createFile(pathName="relpath/name2").pathName, "relpath/name2")
        self.assertRaises(AssertionError, d.createFile, pathName="/abspath/dir1/")
        self.assertRaises(AssertionError, d.createFile, pathName="relpath/dir2/")

        # Create a file that already exists
        d.createFile(pathName="clobber1")
        self.assertRaises(AssertionError, d.createFile, pathName="clobber1")

        self.assertEqual(num * 3 + 3, len(d.files))

        files = d.files[:]
        removeIndexes = list(range(0, len(files), 3))
        [files[i].delete() for i in removeIndexes]
        self.assertEqual(len(d.files), len(files) - len(removeIndexes))

        dirPath = d.path
        d = None
        self.assertTrue(not os.path.isdir(dirPath))
        print("COMPLETED makeRandomContents")