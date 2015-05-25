buildabs
========

Checks the Arch Build System and automatically builds the specified package in /tmp.

Usage:

  ./buildabs.py [OPTIONS] PACKAGENAME

Options:

  -u, --update  Update ABS before building
  
  -e, --edit  Edit the PKGBUILD before building

  -s, --skippgpcheck  Skip PGP check before building
