#!/usr/bin/env python
from os.path import dirname, join
from os import chdir, getcwd, system, putenv
from sys import argv, exit
from pathlib import Path

INT  = 0x01
PROD = 0x03
DEV  = 0x07

LibDir   = "lib"
LibdDir  = "libd"
SrcDir   = "src"
TrcDir   = "trc"

Trc = False
Run = "prod"
nArgs = min(3, len(argv))
for i in range(1, nArgs):
    if argv[i] in ["INT", "Int", "int"]: Run = INT
    if argv[i] in ["DEV", "Dev", "dev"]: Run = DEV
    if argv[i] in ["PROD", "Prod", "Prod"]: Run = PROD
    if argv[i] in ["t", "T", "-t", "/t"]: Trc = True
    if argv[i] in ["h", "H", "-h", "?", "-?", "/?"]:
        print("Incorrect syntax!\n"
              "Syntax: yas [<type>] [t]\n"
              "     <type>: (optional) one of INT, DEV or PROD - Defaults to PROD.\n"
              "     t:      (optional) activated TRCX functionality.\n"
              "                 INT:  use only interpreted Python code.\n"
              "                 DEV:  use existing development Cython compiled binaries instead\n"
              "                       of interpreted code (unoptimised and line trace support).\n"
              "                 PROD: use existing production Cython compiled binaries instead of\n"
              "                       interpreted code (optimised and no line trace support).")
        exit()

Root  = dirname(dirname(argv[0]))
if Run & INT:
    path.insert(0, f"{join(Root, TrcDir)}")
    path.insert(0, f"{join(Root, SrcDir)}")
if Run & PROD:
    path.insert(0, f"{join(Root, LibDir)}")
if Run & DEV:
    path.insert(0, f"{join(Root, LibDir)}")

sRun = ""
if Run == INT: sRun = " - Interpreted Only"
elif Run == DEV: sRun = " - Development Build"
if Trc: sRun += " + TRCX"

from main import main
main(sRun)
