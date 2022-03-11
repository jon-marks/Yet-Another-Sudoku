#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path
from datetime import datetime
from time import perf_counter

INT  = 0x01
PROD = 0x02
DEV  = 0x04

LibDir   = "lib"
LibdDir  = "libd"
SrcDir   = "src"
TrcDir   = "trc"
TestDir  = "test"
TestDDir = "test-data"
SrcFile  = "next-step-1.0-in"
DstFile  = "next-step-1.0-out"
FileExt  = ".txt"

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

    if Mods == INT | DEV | PROD: Suff= "-dev"; Code = "Cython developoment"
    elif Mods == INT | PROD: Suff = "-prod"; Code = "Cython production"
    else: Suff = "-int"; Code = "interpreted"
    print(f"Regression test (next-step.py) run start: {datetime.now()}, using {Code} code.", flush = True)
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src = join(TestDataDir, SrcFile+FileExt)
    Dst = join(TestDataDir, DstFile+Suff+FileExt)
    i = 0
    Test = 0
    Diffs = 0; Errs = 0
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
                        St = f"Invalid Puzzle:  {Found} solutions found: {Line}"
                        f1.write(St); f1.flush()
                        print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Error: {St}", flush = True)
                        Errs += 1
                        continue
                else: sSoln = TD[5]  # if lenTD >= 6 else ""
                Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, oPzl.Method, oPzl.Soln, True)
                if Err:
                    Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, T_UNDEF, oPzl.Soln, True)
                    if Err:
                        f1.write(f"# Warning: Cannot solve next step on line: {Err}: {Line}")
                        print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Expected: {sExpMeth}, Error: {Err}", flush = True)
                        Errs += 1
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
                Match = True
                if oPzl.Method != Step.Method: Match = False
                if sExpCond:
                    if set(sExpCond.split(";")) != set(sCond.split(";")): Match = False
                if sExpOutc:
                    if set(sExpOutc.split(";")) != set(sOutc.split(";")): Match = False
                #
                A0 = set(sExpCond.split(";")); A1 = set(sCond.split(";")); A2 = set(sExpOutc.split(";")); A3 = set(sOutc.split(";"))
                pass
                #
                #     and sExpCond != sCond: Match = False
                # elif sExpOutc:
                #     oExpOutc = sorted(sExpOutc.split(";")); oOutc = sorted(sOutc.split(";"))
                #     if len(oOutc) != len(oExpOutc):  Match = False
                #     else:
                #         for k in range(len(oOutc)):
                #             if oOutc[k] != oExpOutc[k]: Match = False; break
                if Match: print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, {sActMeth}", flush = True)
                else:
                    print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, {sExpMeth}|{sExpCond}|{sExpOutc}, Actual: {sActMeth}|{sCond}|{sOutc}", flush = True)
                    Diffs += 1
                f1.write(f"{sGr}|{sElims}|{sActMeth}|{sCond}|{sOutc}|{sSoln}\n")
                f1.flush()
    print(f"{perf_counter():07f}: End Run, Lines: {i}, Tests: {Test},  Differences: {Diffs}, Errors: {Errs}.")


if __name__ == "__main__":
    next_step()

