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
from generate import *
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
                    f1.write(Line); f1.flush()
                    continue
                oPzl = PZL()
                Flds, sErr = pzl_str_to_pzl(Line, oPzl)
                if not Flds:
                    f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                    continue
                Test += 1
                TD = Line.rstrip(" \n").split("|")
                lenTD = len(TD)
                if not oPzl.Soln:
                    Found, oPzl.Soln = check_puzzle(oPzl.Grid)
                    if Found == 1: sSoln = grid_to_grid_str(oPzl.Soln, oPzl.Givens)
                    else:
                        st = f"Invalid Puzzle:  {Found} solutions found: {Line}"
                        f1.write(st); f1.flush()
                        continue
                else: sSoln = TD[5]  # if lenTD >= 6 else ""
                Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, oPzl.Method, oPzl.Soln, True)
                if Err:
                    Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, T_UNDEF, oPzl.Soln, True)
                    if Err:
                        f1.write(f"# Warning: Cannot solve next step on line: {Err}: {Line}\n")
                        TRCX(f"Line {i}, Test: {Test}, Expected: {sExpMeth}, Err: {Err}")
                        continue

                sActMeth = Tech[Step.Method].Text
                sCond = tkns_to_str(Step.Pattern).replace(" ", "").replace(".", "")
                sOutc = tkns_to_str(Step.Outcome).replace(" ", "").replace(".", "")
                sExpOutc = TD[4] if lenTD >= 5 else ""
                sExpCond = TD[3] if lenTD >= 4 else ""
                sExpMeth = TD[2] if lenTD >= 3 else ""
                sElims   = TD[1] if lenTD >= 2 else ""
                if not sExpMeth: sExpMeth = "Undefined"
                sGr = TD[0].replace("0", ".")
                if oPzl.Method != Step.Method or sExpCond != sCond or sExpOutc != sOutc:
                    # f1.write(f"# Expected Line: {i}: {TD[0]}|{sElims}|{sExpMeth}|{sExpCond}|{sExpOutc}|{sSoln}\n")
                    f1.write(f"{sGr}|{sElims}|{sActMeth}|{sCond}|{sOutc}|{sSoln}\n")
                    TRCX(f"Line {i}, Test: {Test}, Expected: {sExpMeth}, Actual: {sActMeth}")
                else:
                    f1.write(f"{sGr}|{sElims}|{sActMeth}|{sCond}|{sOutc}|{sSoln}\n")
                    TRCX(f"Line {i}, Test: {Test}, {sActMeth}")
                f1.flush()
    TRCX(f"End Run, Lines: {i}, Tests: {Test}")


if __name__ == "__main__":
    next_step()

