#!/usr/bin/env python

import sys

from trackmods import *

if __name__ == "__main__":
    rootpath = "."
    modules = get_maven_modules(Dir(rootpath))

    saved_mod_summary = load_saved_modules_modification_summary(rootpath)

    module_modification_summary = {module: info_for_files(get_all_files_from_module(Dir(module))) for module in modules}

    modified_modules = get_modified_modules(saved_mod_summary, module_modification_summary)

    # TODO: handle exclusions here

    if not modified_modules:
        print "No modified modules"
        sys.exit(1)
