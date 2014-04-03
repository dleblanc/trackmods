import os
import os.path
import anydbm
import pickle

def get_maven_modules(dirData):

    # TODO: strip off the leading bit
    modules = []

    if isMavenDir(dirData):
        for subDir in dirData.subDirs():
            for subModule in get_maven_modules(subDir):
                modules.append(dirData.dirName() + "/" + subModule)

        # If no children, this might be the leaf node
        if not modules:
            modules.append(dirData.dirName())

    return modules

def isMavenDir(dirData):
    return dirData.fileExists("pom.xml")


# TODO: make these work in-memory (eg: put an "recursiveFiles" generator on the Dir object)
def get_all_files_from_module(module):
    all_files = []
    all_files.append(os.path.join(module.dirPath, "pom.xml"))
    all_files.extend(get_from_subdir(os.path.join(module.dirPath, "src")))
    return all_files

def get_from_subdir(subdir):

    all_files = []
    for root, dirs, files in os.walk(subdir):

        for name in files:
            path = os.path.join(root, name)
            all_files.append(path)

    return all_files

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


def info_for_files(files):
    infos = {}
    for filePath in files:
        stat = os.stat(filePath)
        infos[filePath] = (stat.st_mtime, stat.st_size)

    return infos


if __name__ == "__main__":
    modules = get_maven_modules(Dir("."))

    module_modification_summary = {}
    for module in modules:
        #print module

        # TODO: unify Dir usage here
        files = get_all_files_from_module(Dir(module))
        for f in files:
        #    print "\t" + f
            pass

        module_modification_summary[module] = info_for_files(files)


    db = anydbm.open('./trackmods', 'c')
    saved_mod_summary = {}
    for module in modules:
        if module in db:
            saved_mod_summary[module] = pickle.loads(db[module])

    for module in modules:
        if not module in saved_mod_summary or module_modification_summary[module] != saved_mod_summary[module]:
            print "module: " + module + " is modified"

    try:
        for module in modules:
            # save it
            db[module] = pickle.dumps(module_modification_summary[module])
    finally:
        db.close()