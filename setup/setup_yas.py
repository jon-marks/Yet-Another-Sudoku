#!/usr/bin/env python
# Adaptation of setup_yas.py to follow YAS's directory environment nates: Appendix A
# in the Sudoku.odt # document and the changes to get mingw64 gcc to work in appendix C
# NOTE:
# 1.  I would like to find a way to specify the locations of the Cython *.c and *.html
#     targets individually.  (--build-lib on the command line works for *.pyd files).
#     This work around copies the source files to compile into the tmp/ directory and processes
#     from the tmp directory.
# 2.  Introduced a timestamp dependency on this file setup_yas.py

from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext

from sys import argv, path
from os import makedirs, remove, getenv  # , putenv,
from os.path import dirname, join, split, exists, getmtime
from shutil import copy2
from glob import glob
from pathlib import Path

Dev = bool(getenv('BLD', 'DEV') == 'DEV')

# Start of User configurable stuff.  However still tread cautiously when making changes.
# Setup Parameters
Name = 'Yet Another Sudoku',
YASVer = '0.0.0'
Author = "Jonathan Marks",
License = "Mozilla Public Licence 2.0",

# Directories off the project root.
LibDir   = "lib"
LibdDir  = "libd"
SetupDir = "setup"
SrcDir   = "src"
TgtDir   = LibdDir if Dev else LibDir
TmpDir   = "tmp"
TrcDir   = "trc"
SrcExt   = ".pyx"

# Additional GCC parameters:
Defs = [  # translates to -D options on the gcc command lile.
        ]
if Dev: Defs.extend([('CYTHON_TRACE_NOGIL', '1')])

CompArgs = ['-Wall',       # all warnings
            ]
if Dev: CompArgs.extend(['-O0', '-ggdb'])  # no optimisation (fast compile)and full debug info.
else: CompArgs.extend(['-O3', '-g0'])  # highy optimised (slow compile) and no debug info

LinkArgs = ['-static-libgcc',
            '-static-libstdc++',
            '-Wl,-Bstatic,--whole-archive',
            '-lwinpthread',
            '-Wl,--no-whole-archive',
            ]

# Cythonize compiler directives
if Dev:
    CythonDirectives = {
                        'language_level': 3,
                        'linetrace': True,
                        'overflowcheck': True,
                        'warn.maybe_uninitialized': True,
                        'warn.unused': True,
                        'warn.unused_arg': True,
                        'warn.unused_result': True,  # shows many false warnings
                        # 'optimize.unpack_method_calls': False
                        }
else:
    CythonDirectives = {
                        'language_level': 3,
                        'boundscheck': False,  # for faster code with less checking
                        'wraparound': False,
                        'cdivision': True
                        }
# End of user configurable stuff.

Root = dirname(dirname(argv[0]))
path.insert(0, f"{join(Root, TrcDir)}")
path.insert(0, f"{join(Root, SrcDir)}")
if Dev: print(f"sys.path = {path}")

NwrSetup = join(TmpDir, ".newersetup_yas")
Setup = join(SetupDir, "setup_yas.py")

SrcPaths = glob(join(SrcDir, "*" + SrcExt))

if not exists(TgtDir): makedirs(TgtDir)
if not exists(TmpDir): makedirs(TmpDir)
if (not exists(NwrSetup)) or getmtime(NwrSetup) < getmtime(Setup):
    for path in [*SrcPaths, *[NwrSetup]]: Path(path).touch()

TmpPaths = []
for SrcPath in SrcPaths:
    SrcDir, SrcFile = split(SrcPath)
    TmpPath = join(TmpDir, SrcFile)
    if exists(TmpPath): remove(TmpPath)
    copy2(SrcPath, TmpPath)
    TmpPaths.append(TmpPath)

class Build(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'mingw32':
            for e in self.extensions:
                e.define_macros = Defs
                e.extra_compile_args = CompArgs
                e.extra_link_args = LinkArgs
        super(Build, self).build_extensions()

setup(
      name = Name,
      version = YASVer,
      author = Author,
      license = License,
      cmdclass = {'build_ext': Build},
      ext_modules = cythonize(TmpPaths,
                              compiler_directives = CythonDirectives,
                              # show_all_warnings = True,
                              annotate = True,
                              ),
      zip_safe = False,
     )
