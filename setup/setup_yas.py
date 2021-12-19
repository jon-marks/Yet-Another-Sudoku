#!/usr/bin/env python
# Adaptation of setup_yas.py to follow YAS's directory enviroment nates: Appendix A in the Sudoku.odt
# document and the changes to get mingw64 gcc to work in appendix C
# NOTE:
# 1.  I would like to find a way to specify the locations of the Cython *.c and *.html
#     targets individually.  (--build-lib on the command line works for *.pyd files).
#     This work around copies the source files to compile into the tmp/ directory and processes
#     from the tmp directory.
# 2.  Introduced a timestamp dependency on this file setup_yas.py

from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext
import os
from shutil import copy2
from glob import glob
from pathlib import Path

DEV = bool(os.getenv('BLD', 'DEV') == 'DEV')

# Start of User configurable stuff.  However still tread cautiously when making changes.
# Setup Parameters
Name = 'Yet Another Sudoku',
YASVer = '0.0.0'
Author = "Jonathan Marks",
License = "Mozilla Public Licence 2.0",

# Directories off the project root.
SetupDir = "setup"
SrcDir = "src"

TgtDir = "libd" if DEV else "lib"
TmpDir = "tmp"
SrcExt = ".pyx"

# Additional GCC parameters:
Defs = [  # translates to -D options on the gcc command lile.
        ]
if DEV: Defs.extend([('CYTHON_TRACE_NOGIL', '1')])

CompArgs = ['-Wall',       # all warnings
            ]
if DEV: CompArgs.extend(['-O0', '-ggdb'])  # no optimisation (fast compile)and full debug info.
else: CompArgs.extend(['-O3', '-g0'])  # highy optimised (slow compile) and no debug info

LinkArgs = ['-static-libgcc',
            '-static-libstdc++',
            '-Wl,-Bstatic,--whole-archive',
            '-lwinpthread',
            '-Wl,--no-whole-archive',
            ]

# Cythonize compiler directives
if DEV:
    CythonDirectives = {
                        'language_level': 3,
                        'linetrace': True,
                        }
else:
    CythonDirectives = {
                        'language_level': 3,
                        'boundscheck': False,  # for faster code with less checking
                        'wraparound': False,
                        }
# End of user configurable stuff.

NwrSetup = os.path.join(TmpDir, ".newersetup_yas")
Setup = os.path.join(SetupDir, "setup_yas.py")

SrcPaths = glob(os.path.join(SrcDir, "*" + SrcExt))

if not os.path.exists(TgtDir): os.makedirs(TgtDir)
if not os.path.exists(TmpDir): os.makedirs(TmpDir)
if (not os.path.exists(NwrSetup)) or os.path.getmtime(NwrSetup) < os.path.getmtime(Setup):
    for path in [*SrcPaths, *[NwrSetup]]: Path(path).touch()

TmpPaths = []
for SrcPath in SrcPaths:
    SrcDir, SrcFile = os.path.split(SrcPath)
    TmpPath = os.path.join(TmpDir, SrcFile)
    if os.path.exists(TmpPath): os.remove(TmpPath)
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
                              annotate = True,
                              ),
      zip_safe = False,
     )

# NOTE for line tracing add the following compilier dierctives 'profile': True, 'linetrace': True"
# also add CYTHON_TRACE_NOGIL=1 to the setup_yas.py run configuration.
# also try 'binding': True compiler directive. instead of 'profile': True see second ref.
# Refs:
# https://cython.readthedocs.io/en/latest/src/tutorial/profiling_tutorial.html#profiling-tutorial
# https://stackoverflow.com/questions/28301931/how-to-profile-cython-functions-line-by-line
