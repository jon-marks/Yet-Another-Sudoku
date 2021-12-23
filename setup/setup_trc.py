#!/usr/bin/env python
# Simple setup_yas.py script to build the trc_x module.
from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext
import os
from shutil import copy2
from pathlib import Path

# Directories off the project root.
SetupDir = "setup"
SrcDir = "trc"
TgtDir = "lib"
TmpDir = "tmp"

compile_args = ['-O3',         # optimising for speed
                '-g0',         # strip out debug info.
                '-Wall',       # all warnings
                ]

link_args = ['-static-libgcc',
             '-static-libstdc++',
             '-Wl,-Bstatic,--whole-archive',
             '-lwinpthread',
             '-Wl,--no-whole-archive',
             ]

NwrSetup = os.path.join(TmpDir, ".newersetup_trc")
Setup = os.path.join(SetupDir, "setup_trc.py")
SrcFile = os.path.join(SrcDir, "trc.pyx")
TmpFile = os.path.join(TmpDir, "trc.pyx")

if not os.path.exists(TgtDir): os.makedirs(TgtDir)
if not os.path.exists(TmpDir): os.makedirs(TmpDir)
if (not os.path.exists(NwrSetup)) or os.path.getmtime(NwrSetup) < os.path.getmtime(Setup):
    Path(SrcFile).touch(); Path(NwrSetup).touch()

if os.path.exists(TmpFile): os.remove(TmpFile)
copy2(SrcFile, TmpFile)

class Build(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'mingw32':
            for e in self.extensions:
                if link_args: e.extra_link_args = link_args
                if compile_args: e.extra_compile_args = compile_args
        super(Build, self).build_extensions()

setup(
      cmdclass = {'build_ext': Build},
      name ='TRCX',
      version = "0.0.0",
      author = "Jonathan Marks",
      license = "Mozilla Public Licence 2.0",
      ext_modules = cythonize(TmpFile,
                              compiler_directives = {'language_level': 3,
                                                     'boundscheck': False,
                                                     'wraparound': False,
                                                     },
                              # show_all_warnings = True,
                              annotate = True,
                              ),
      zip_safe = False,
      )
