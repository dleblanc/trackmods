#!/usr/bin/env python

from trackmods import *

if __name__ == "__main__":
    rootpath = "."
    modules = get_maven_modules(Dir(rootpath))

    module_modification_summary = {module: info_for_files(get_all_files_from_module(Dir(module))) for module in modules }

    save_updated_modification_state(rootpath, module_modification_summary)