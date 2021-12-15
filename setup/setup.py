# Adaptation of setup.py to follow YAS's directory enviroment nates: Appedix A in the Sudoku.odt
# document and the changes to get mingw64 gcc to work in appendix C
# NOTE:
# 1.  I would like to find a way to specify the locations of the Cython *.c and *.html
#     targets individually.  (--build-lib on the command line works for *.pyd files).
#     This work around copies the source files to compile into the tmp/ directory and processes
#     from the tmp directory.
# 2.  Introduced a timestamp dependency on this file setup.py

from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext
import os
import shutil
from glob import glob
from pathlib import Path

# Start of User configurable stuff.  However still tread cautiously when making changes.
# Setup Parameters
Name = 'Yet Another Sudoku',
YASVer = '0.0.0'
Author = "Jonathan Marks",
License = "Mozilla Public Licence 2.0",

# Directories off the project root.
SetupDir = "setup"
SrcDir = "src"
TgtDir = "lib"
TmpDir = "tmp"
SrcSufs = ["_c.py", "_x.pyx"]

# Additional GCC parameters:
Defs = [  # translates to -D options on the gcc command lile.
         # ('CYTHON_TRACE', '1')
        ]

CompArgs = ['-O3',         # optimising for speed
            '-Wall',       # all warnings
            ]

LinkArgs = ['-static-libgcc',
            '-static-libstdc++',
            '-Wl,-Bstatic,--whole-archive',
            '-lwinpthread',
            '-Wl,--no-whole-archive',
            ]
# Cythonize compiler directives
CythonDirectives = {
                    'language_level': 3,
                    'boundscheck': False,  # for faster code with less checking
                    'wraparound': False,
                    # ' profile: True,
                    # 'linetrace': True,
                    # 'binding': True,
                    }
# End of user configurable stuff.

NwrSetup = os.path.join(TmpDir, ".newersetup")
Setup = os.path.join(SetupDir, "setup.py")

SrcFiles = []
for SrcSuf in SrcSufs:
    SrcFiles.extend(glob(os.path.join(SrcDir, "*" + SrcSuf)))

if not os.path.exists(TgtDir): os.makedirs(TgtDir)
if not os.path.exists(TmpDir): os.makedirs(TmpDir)
if (not os.path.exists(NwrSetup)) or os.path.getmtime(NwrSetup) < os.path.getmtime(Setup):
    for path in [*SrcFiles, *[NwrSetup]]: Path(path).touch()

TmpFiles = []
for SrcFile in SrcFiles:
    SrcDir, SrcFileSpec = os.path.split(SrcFile)
    SrcFileN, Sep, SrcExt = SrcFileSpec.rpartition(".")
    TmpFile = os.path.join(TmpDir, SrcFileSpec)
    if os.path.exists(TmpFile): os.remove(TmpFile)
    shutil.copy2(SrcFile, TmpFile)
    TmpFiles.append(TmpFile)

class Build(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'mingw32':
            for e in self.extensions:
                e.define_macros = Defs
                e.extra_compile_args = CompArgs
                e.extra_link_args = LinkArgs
        super(Build, self).build_extensions()

YASVer = '0.0.0'
setup(
      name = Name,
      version = YASVer,
      author = Author,
      license = License,
      cmdclass = {'build_ext': Build},
      ext_modules = cythonize(TmpFiles,
                              compiler_directives = CythonDirectives,
                              annotate = True,
                              ),
      zip_safe = False,
     )

# NOTE for line tracing add the following compilier dierctives 'profile': True, 'linetrace': True"
# also add CYTHON_TRACE_NOGIL=1 to the setup.py run configuration.
# also try 'binding': True compiler directive. instead of 'profile': True see second ref.
# Refs:
# https://cython.readthedocs.io/en/latest/src/tutorial/profiling_tutorial.html#profiling-tutorial
# https://stackoverflow.com/questions/28301931/how-to-profile-cython-functions-line-by-line
