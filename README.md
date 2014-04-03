## TrackMods

The problem:
 Maven takes a long while rebuilding child modules that haven't been modified. Assuming you're installing
 them locally, you're doing a lot of repeated work that's only slowing you down.

A solution:
 Let's track what source files have been modified, and build up a list of only the modified modules that
 need to be rebuilt. It's not perfect, but it will suffice in a majority of cases.

 Trackmods is a very simple Python script that monitors the changes to your Maven modules,
 and can yield a list of changed modules to build.


Usage:

> ifdirty.py && mvn install -pl `trackmods.py` && clearmods.py

This will invoke maven only if there are changes (ifdirty), trackmods returns a comma-separated list of modules to build,
and clearmods marks all changes as up to date.

Why Python:
 Super fast startup time, and a good language to write scripts in.

Requirements:

* Python 2.7
