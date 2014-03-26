from trackmods import *

import pytest
import tempfile

class FakeDir:
    def __init__(self, dirPath, files = [], subdirs = []):
        self.dirPath = dirPath
        self.files = files
        self.subdirs = subdirs

    def subDirs(self):
        return self.subdirs

    def fileExists(self, fileName):
        return fileName in self.files

    def dirName(self):
        return os.path.split(self.dirPath)[-1]


def test_fake_dir_count():
    d1 = FakeDir("d1")
    d2 = FakeDir("d2")

    topDir = FakeDir("top", files = ["file1.tmp"], subdirs = [d1, d2])

    assert len(topDir.subDirs()) == 2

def test_fake_file_exists():
    dir = FakeDir("dir", files=["foo.txt"])

    assert dir.fileExists("foo.txt") == True


# use -m "not integration" to skip integration tests.

@pytest.mark.integration
def test_real_file_exists():

    dirPath = tempfile.mkdtemp(prefix="test-trackmods")
    fileName = "file.txt"
    filePath = os.path.join(dirPath, fileName)
    open(filePath, 'a').close()
    try:
        d = Dir(dirPath)

        assert d.fileExists(fileName)

    finally:
        os.remove(filePath)
        os.rmdir(dirPath)


@pytest.mark.integration
def test_real_find_subdirs():
    dirPath = tempfile.mkdtemp(prefix="test-trackmods")
    subPath = os.path.join(dirPath, "first")

    os.mkdir(subPath)
    try:
        d = Dir(dirPath)

        assert len(d.subDirs()) == 1
        subDirNames = [subDir.dirPath for subDir in d.subDirs()]
        assert subDirNames[0] == subPath
    finally:
        os.rmdir(subPath)
        os.rmdir(dirPath)


def test_get_maven_modules_with_single_maven_sub_module():
    subDir = FakeDir("/dir/module", files=["pom.xml"])
    rootDir = FakeDir("/dir", subdirs=[subDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["dir/module"]

def test_get_maven_modules_with_nested_module_doesnt_return_parent():
    childDir = FakeDir("/dir/parent/child", files=["pom.xml"])
    parentDir = FakeDir("/dir/parent", files=["pom.xml"], subdirs=[childDir])
    rootDir = FakeDir("/dir", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["dir/parent/child"]

def test_get_maven_modules_with_two_nested_children():
    childDir1 = FakeDir("/dir/parent/child1", files=["pom.xml"])
    childDir2 = FakeDir("/dir/parent/child2", files=["pom.xml"])
    parentDir = FakeDir("/dir/parent", files=["pom.xml"], subdirs=[childDir1, childDir2])
    rootDir = FakeDir("/dir", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["dir/parent/child1", "dir/parent/child2"]

def test_get_maven_modules_with_nested_non_maven_child_returns_only_parent():
    childDir = FakeDir("/dir/parent/child")
    parentDir = FakeDir("/dir/parent", files=["pom.xml"], subdirs=[childDir])
    rootDir = FakeDir("/dir", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["dir/parent"]

def test_get_maven_modules_with_non_maven_dir_returns_empty_list():
    rootDir = FakeDir("/dir")

    assert get_maven_modules(rootDir) == []