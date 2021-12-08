from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext
import os
import shutil
from glob import glob
from pathlib import Path

# Directories are off the project root.
SetupDir = "setup"
SrcDir = "src"
TgtDir = "lib"
TmpDir = "tmp"
SrcSufs = ["_c.py", "_x.pyx"]
NwrSetup = os.path.join(TmpDir, ".newersetup")
Setup = os.path.join(SetupDir, "setup.py")

SrcFiles = []
for SrcSuf in SrcSufs:
    SrcFiles.extend(glob(os.path.join(SrcDir, "*" + SrcSuf)))
# the only way I can find that does not clutter the src dir with cython working
# files (c, html output which I want to keep temporarily) is to copy the src to
# the tmp directory and compile it there.
# Requires a timestamp dependency check on this file setup.py
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

link_args = ['-static-libgcc',
             '-static-libstdc++',
             '-Wl,-Bstatic,--whole-archive',
             '-lwinpthread',
             '-Wl,--no-whole-archive',
            ]

compile_args = ['-O3',         # optimising for speed
                '-Wall',       # all warnings
               ]

class Build(build_ext):
    def build_extensions(self):
        if self.compiler.compiler_type == 'mingw32':
            for e in self.extensions:
                if link_args: e.extra_link_args = link_args
                if compile_args: e.extra_compile_args = compile_args
        super(Build, self).build_extensions()

setup(
      cmdclass = {'build_ext': Build},
      name ='Yet Another Sudoku',
      version = "0.0.0",
      author = "Jonathan Marks",
      license = "Mozilla Public Licence 2.0",
      ext_modules = cythonize(TmpFiles,
                              compiler_directives = {'language_level': 3,
                                                     'boundscheck': False, # for faster code with less checking
                                                     'wraparound': False},
                              annotate = True  # = 'fullc'
                              ),
      zip_safe = False,
     )
