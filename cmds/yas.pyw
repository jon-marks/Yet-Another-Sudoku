#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path
from pathlib import Path

INT  = 0x01
PROD = 0x02
DEV  = 0x04

LibDir   = "lib"
LibdDir  = "libd"
SrcDir   = "src"
TrcDir   = "trc"

Trc = False
Run = "prod"
nArgs = min(3, len(argv))
for i in range(1, nArgs):
    if argv[i] in ["INT", "Int", "int"]: Run = INT
    if argv[i] in ["PROD", "Prod", "Prod"]: Run = INT | PROD
    if argv[i] in ["DEV", "Dev", "dev"]: Run = INT | PROD | DEV
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
    path.insert(0, f"{join(Root, LibdDir)}")

sRun = ""
if Run == INT: sRun = " - Interpreted Only"
elif Run == DEV: sRun = " - Development Build"
if Trc:
    sRun += " + TRCX"
    # Hack using the end of sys.path to store truly global vars.
    path.append(".trc_true")
else:
    path.append(".trc_false")
if Run & (INT | DEV): print (f"sys.path = {path}")
chdir(Root)
from main import main
main(sRun)
