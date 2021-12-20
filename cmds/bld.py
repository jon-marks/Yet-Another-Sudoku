#!/usr/bin/env python
from os.path import dirname, join
from os import chdir, system, putenv
from sys import argv
from pathlib import Path

Force   = False
Bld     = "DEV"
LibTgt  = "lib"
Tgt     = ""
Root    = dirname(dirname(argv[0]))
nArgs = min(4, len(argv))
for i in range(1, nArgs):
    if argv[i] in ["TRC", "Trc", "trc"]: Tgt = "trc"
    if argv[i] in ["YAS", "Yas", "yas"]: Tgt = "yas"
    if argv[i] in ["f", "F", "-f", "/f"]: Force = True
    if argv[i] in ["PROD", "Prod", "prod"]: Bld = "PROD"
    if argv[i] in ["h", "H", "-h", "?", "-?", "/?"]: Tgt = ""; break
if Tgt:
    putenv("BLD", Bld)
    if Tgt != "trc" and Bld == "DEV": LibTgt = "libd"
    Parms  = f"build_ext --build-lib {LibTgt}"
    Cmd    = join(join(Root, "setup"), f"setup_{Tgt}.py")
    if Force: Path(Cmd).touch()
    chdir(Root)
    if Bld == "DEV": print(f'"{Cmd}" {Parms}')
    system(f'"{Cmd}" {Parms}')
else:
    print("No/Incorrect application specified!\n"
          "Syntax: bld <app> [<type>] [f]\n"
          "     <app>:  (required) either TRC or YAS.\n"
          "     <type>: (optional) either DEV or PROD - Defaults to DEV, not used for TRC.\n"
          "     f:      (optional) overrides dependencies forcing complete build.")
