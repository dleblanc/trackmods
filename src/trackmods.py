import os
import os.path

def get_maven_modules(dirData):

    # TODO: strip off the leading bit
    modules = []

    if isMavenDir(dirData):
        for subDir in dirData.subdirs:
            for subModule in get_maven_modules(subDir):
                modules.append(dirData.dirName() + "/" + subModule)

        # If no children, this might be the leaf node
        if not modules:
            modules.append(dirData.dirName())

    return modules

def isMavenDir(dirData):
    return dirData.fileExists("pom.xml")

class Dir:
    def __init__(self, dirPath):
        self.dirPath = dirPath

    def subDirs(self):
        return [Dir(os.path.join(self.dirPath, dirName)) for dirName in os.listdir(self.dirPath) if os.path.isdir(os.path.join(self.dirPath, dirName))]

    def fileExists(self, fileName):
        path = os.path.join(self.dirPath, fileName)
        return os.path.isfile(path)

    def dirName(self):
        return os.path.split(self.dirPath)[-1]
