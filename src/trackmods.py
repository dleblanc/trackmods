#!/usr/bin/env python

import os
import os.path
import anydbm
import pickle
import string

def get_maven_modules(dirData):

    # TODO: strip off the leading bit
    modules = []

    if isMavenDir(dirData):
        for subDir in dirData.subDirs():
            for subModule in get_maven_modules(subDir):
                modules.append(os.path.join(dirData.dirName() + "/" + subModule))

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

def load_saved_modules_modification_summary(rootpath):
    db = anydbm.open(os.path.join(rootpath, 'trackmods'), 'c')
    try:
        saved_mod_summary = {}
        if rootpath in db:
            saved_mod_summary = pickle.loads(db[rootpath])

        return saved_mod_summary
    finally:
        db.close()

def save_updated_modification_state(rootpath, mod_summary):
    db = anydbm.open(os.path.join(rootpath, 'trackmods'), 'c')
    try:
        db[rootpath] = pickle.dumps(mod_summary)
    finally:
        db.close()

def get_modified_modules(saved_mod_summary, current_mod_summary):

    mods = []

    # TODO: externalize this to the command line (or a cfg file)
    excluded_modules = ["./console-brand", "./dist", "./functional-tests"]
    for module in current_mod_summary.keys():
        if not module in saved_mod_summary or current_mod_summary[module] != saved_mod_summary[module]:
            #print "module: " + module + " is modified"
            if module in excluded_modules:
                continue
            mods.append(module)

    return mods


if __name__ == "__main__":
    #abspath = os.path.abspath(".")
    rootpath = "."
    modules = get_maven_modules(Dir(rootpath))

    saved_mod_summary = load_saved_modules_modification_summary(rootpath)

    module_modification_summary = {module: info_for_files(get_all_files_from_module(Dir(module))) for module in modules}

    modified_modules = get_modified_modules(saved_mod_summary, module_modification_summary)

    print string.join(modified_modules, ",")