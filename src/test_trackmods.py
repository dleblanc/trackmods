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
    subDir = FakeDir("/module", files=["pom.xml"])
    rootDir = FakeDir("./", subdirs=[subDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["/module"]

def test_get_maven_modules_with_nested_module_doesnt_return_parent():
    childDir = FakeDir("/parent/child", files=["pom.xml"])
    parentDir = FakeDir("/parent", files=["pom.xml"], subdirs=[childDir])
    rootDir = FakeDir("/", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["/parent/child"]

def test_get_maven_modules_with_two_nested_children():
    childDir1 = FakeDir("/parent/child1", files=["pom.xml"])
    childDir2 = FakeDir("/parent/child2", files=["pom.xml"])
    parentDir = FakeDir("/parent", files=["pom.xml"], subdirs=[childDir1, childDir2])
    rootDir = FakeDir("/", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["/parent/child1", "/parent/child2"]

def test_get_maven_modules_with_nested_non_maven_child_returns_only_parent():
    childDir = FakeDir("parent/child")
    parentDir = FakeDir("parent", files=["pom.xml"], subdirs=[childDir])
    rootDir = FakeDir("/", subdirs=[parentDir], files=["pom.xml"])

    assert get_maven_modules(rootDir) == ["/parent"]

def test_get_maven_modules_with_non_maven_dir_returns_empty_list():
    rootDir = FakeDir("/dir")

    assert get_maven_modules(rootDir) == []



def test_get_all_files_in_module():

    dirPath = tempfile.mkdtemp(prefix="test-trackmods")
    pomPath = os.path.join(dirPath, "pom.xml")
    javaDirPath = os.path.join(dirPath, "src/main/java")
    javaFilePath = os.path.join(javaDirPath, "foo.java")

    os.makedirs(javaDirPath)
    open(pomPath, 'a').close()
    open(javaFilePath, 'a').close()
    try:
        all_files = get_all_files_from_module(FakeDir(dirPath))

        assert javaFilePath in all_files
        assert pomPath in all_files
    finally:
        os.remove(pomPath)
        os.remove(javaFilePath)
        os.removedirs(javaDirPath)


def test_get_hash_for_files():

    dirPath = tempfile.mkdtemp(prefix="test-trackmods")
    filePath = os.path.join(dirPath, "testfile.txt")
    fileObj = open(filePath, 'a')
    fileObj.writelines("lorem ipsum")
    fileObj.close()

    try:
        infoDict = info_for_files([filePath])
        assert len(infoDict) == 1
        onlyVal = infoDict.itervalues().next()
        assert onlyVal[0] > 0.0 # modification time
        assert onlyVal[1] == 11 # st_size
    finally:
        os.remove(filePath)
        os.removedirs(dirPath)



    # So - for every module, record a set of the file stats of all the relevant files


# find all modules
# for every module:
#   get a list of all relevant files
#   get a modification summary of those files
#   store module -> modification summary
#
# in topo-sorted order, run through modules, add dirty ones in order (NOTE: don't strictly need this with maven)