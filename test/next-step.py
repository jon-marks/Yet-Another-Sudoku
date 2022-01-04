#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path

INT  = 0x01
PROD = 0x02
DEV  = 0x04

LibDir   = "lib"
LibdDir  = "libd"
SrcDir   = "src"
TrcDir   = "trc"
TestDir  = "test"
TestDDir = "test-data"
SrcFile  = "next-step-1.0-in.txt"
DstFile  = "next-step-1.0-out.txt"

sRun = ""
Trc = False
Mods = INT | PROD
nArgs = min(3, len(argv))
for i in range(1, nArgs):
    if argv[i] in ["INT", "Int", "int"]: Mods = INT; sRun = " - Interpreted Only"
    elif argv[i] in ["PROD", "Prod", "prod"]: Mods = INT | PROD; sRun = ""
    elif argv[i] in ["DEV", "Dev", "dev"]: Mods = INT | PROD | DEV; sRun = " - Development Build"
    elif argv[i] in ["t", "T", "-t", "/t"]: Trc = True
    else:
        print("Incorrect syntax!\n"
              "Syntax: next_step.py  [<type>] [t]\n"
              "     <type>: (optional) one of INT, DEV or PROD - Defaults to PROD.\n"
              "     t:      (optional) activated TRCX functionality.\n"
              "                 INT:  use only interpreted Python code.\n"
              "                 DEV:  use existing development Cython compiled binaries instead\n"
              "                       of interpreted code (unoptimised and line trace support).\n"
              "                 PROD: use existing production Cython compiled binaries instead of\n"
              "                       interpreted code (optimised and no line trace support).")
        exit()

Root  = dirname(dirname(argv[0]))
chdir(Root)
if Mods & INT:
    path.insert(0, f"{join(Root, TrcDir)}")
    path.insert(0, f"{join(Root, SrcDir)}")
if Mods & PROD:
    path.insert(0, f"{join(Root, LibDir)}")
if Mods & DEV:
    path.insert(0, f"{join(Root, LibdDir)}")

if Trc: path.append(".trc_true")
else: path.append(".trc_false")

from globals import *
from trc import *
from misc import *
from solve import *
from solve_utils import *

def next_step():

    if Mods == INT | DEV | PROD: TRCX("Next step using development code.")
    elif Mods == INT | PROD: TRCX("Next step using production code.")
    else: TRCX("Next step using interpreted code.")
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src = join(TestDataDir, SrcFile)
    Dst = join(TestDataDir, DstFile)
    i = 0
    Test = 0
    with open(Src, "rt") as f:
        with open(Dst, "wt") as f1:
            while 1:
                Line = f.readline()
                i += 1
                if not Line: break
                if Line == "\n" or Line[0] == "#":
                    f1.write(Line)
                    f1.flush()
                    continue
                TD = Line.rstrip(" \n").split("|")
                if len(TD) > 2 and TD[2]: sMeth1 = TD[2]
                else: sMeth1 = "Unspecified"
                oPzl = PZL()
                Flds = pzl_str_to_pzl(Line, oPzl)
                if not Flds: continue
                Test += 1
                # TRCX(f"Line {i}, Test: {Test}, Method: {sMeth1}")
                Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, oPzl.Method)
                if Err:
                    Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, T_UNDEF)
                    if Err:
                        f1.write(f"# Warning: Cannot solve next step on line: {Err}: {Line}\n")
                        continue

                sMeth = Tech[Step.Method].Text
                sCond = tkns_to_str(Step.Pattern).replace(" ", "").replace(".", "")
                sOutc = tkns_to_str(Step.Outcome).replace(" ", "").replace(".", "")
                TD = Line.rstrip(" \n").split("|", 3)
                sGr = TD[0].replace("0", ".")
                if oPzl.Method != Step.Method:
                    if len(TD) == 2: TD.append("")
                    f1.write(f"# Info: Expected: {TD[2]}; Actual: {sMeth}, line: {Line}")
                    f1.write(f"# New: {sGr}|{TD[1]}|{sMeth}|{sCond}|{sOutc}\n")
                else: f1.write(f"{sGr}|{TD[1]}|{sMeth}|{sCond}|{sOutc}\n")
                f1.flush()
                TRC = False
    TRCX(f"End Run, Lines: {i}, Tests: {Test}")


if __name__ == "__main__":
    next_step()

