#!/usr/bin/env python
from os.path import dirname, join
from os import chdir, system, putenv
from sys import argv, exit
from pathlib import Path

Force   = False
Bld     = "DEV"
LibTgt  = "lib"
# Asm     = ""
Tgt     = ""
Root    = dirname(dirname(argv[0]))
nArgs = min(4, len(argv))
for i in range(1, nArgs):
    if argv[i] in ["TRC", "Trc", "trc"]: Tgt = "trc"
    elif argv[i] in ["YAS", "Yas", "yas"]: Tgt = "yas"
    elif argv[i] in ["DEV", "Dev", "dev"]: Bld = "DEV"
    elif argv[i] in ["PROD", "Prod", "prod"]: Bld = "PROD"
    elif argv[i] in ["f", "F", "-f", "/f"]: Force = True
    else:
        print("Incorrect syntax!\n"
              "Syntax: bld <app> [<type>] [f]\n"
              "     <app>:  (required) either TRC or YAS.\n"
              "     <type>: (optional) either DEV or PROD - Defaults to DEV, not used for TRC.\n"
              "     f:      (optional) overrides dependencies forcing complete build.")
        exit()

# if Asm: putenv("ASM", "1")
putenv("BLD", Bld)
if Tgt != "trc" and Bld == "DEV": LibTgt = "libd"
Parms  = f"build_ext --build-lib {LibTgt}"
Cmd    = join(join(Root, "setup"), f"setup_{Tgt}.py")
if Force: putenv("FORCE", "1")
# if Force: Path(Cmd).touch()
chdir(Root)
if Bld == "DEV": print(f'"{Cmd}" {Parms}')
system(f'"{Cmd}" {Parms}')
