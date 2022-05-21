#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path, version, stderr
from datetime import datetime
# INT  = 0x01
# PROD = 0x02
# DEV  = 0x04

# LibDir   = "lib"
# LibdDir  = "libd"
SrcDir   = "src"
TrcDir   = "trc"

sRun = ""
Trc = False
# Mods = INT | PROD
# nArgs = min(3, len(argv))
for i in range(1, len(argv)):  # nArgs):
    # if argv[i] in ["INT", "Int", "int"]: Mods = INT; sRun = ""
    # elif argv[i] in ["PROD", "Prod", "prod"]: Mods = INT | PROD; sRun = " - Production Build"
    # elif argv[i] in ["DEV", "Dev", "dev"]: Mods = INT | PROD | DEV; sRun = " - Development Build"
    if argv[i] in ["t", "T", "-t", "/t"]: Trc = True
    else:
        print("Incorrect syntax!\n"
              "Syntax: yas.py [t]\n"
              "     t:      (optional) activated TRCX functionality.\n")
              # "                 INT:  use only interpreted Python code.\n"
              # "                 DEV:  use existing development Cython compiled binaries instead\n"
              # "                       of interpreted code (unoptimised and line trace support).\n"
              # "                 PROD: use existing production Cython compiled binaries instead of\n"
              # "                       interpreted code (optimised and no line trace support).")
        exit()

Root  = dirname(dirname(argv[0]))
# if Mods & INT:
path.insert(0, f"{join(Root, TrcDir)}")
path.insert(0, f"{join(Root, SrcDir)}")
# if Mods & PROD:
#     path.insert(0, f"{join(Root, LibDir)}")
# if Mods & DEV:
#     path.insert(0, f"{join(Root, LibdDir)}")

if Trc:
    sRun += " + TRCX"
    # Hack using the end of sys.path to store truly global vars.
    path.append(".trc_true")
    from trc import TRCX
    print(f"Run Start: {datetime.now()}", file = stderr, flush = True)
    print(f"Python {version}", file = stderr, flush = True)
    print(f"sys.path: {path}", file = stderr, flush = True)
else:
    path.append(".trc_false")

chdir(Root)
from main import main
main(sRun)
