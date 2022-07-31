#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path
from datetime import datetime
from time import perf_counter

SrcDir   = "src"
TestDir  = "test"
TestDDir = "test-data"
SrcFile  = "pattern-reg-test-1.0"
DstSuff  = "-out"
FileExt  = ".txt"
Root = dirname(dirname(argv[0]))
chdir(Root)
path.insert(0, f"{join(Root, SrcDir)}")

from globals import *
from generate import *
from misc import *
from solve import *
from solve_utils import *

def yas_prt():

    print(f"YAS Pattern Regression Tester.")
    print(VERSION)
    print(f"Run start: {datetime.now()}.", flush = True)  # , using {Code} code.", flush = True)
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src = join(TestDataDir, SrcFile+FileExt)
    Dst = join(TestDataDir, SrcFile+DstSuff+FileExt)
    Begin = 0; End = 9999999
    Methods = []; Firsts = []; Ignore = False
    for i in range(1, len(argv)):
        if argv[i][:2] in ["i=", "I="]:
            if argv[i][:2]: Src = argv[i][2:]
        elif argv[i][:2] in ["o=", "O="]:
            if argv[i][:2]: Dst = argv[i][2:]
        elif argv[i][:2] in ["b=", "B="]: Begin = int(argv[i][2:])
        elif argv[i][:2] in ["e=", "E="]: End = int(argv[i][2:])
        elif argv[i][:2] in ["m=", "M="]: Methods = argv[i][2:].replace(" ", "").split(",")
        elif argv[i][:2] in ["f=", "F="]: Firsts = argv[i][2:].split(",")
        elif argv[i] in ["g", "g"]: Ignore = True
        else:
            print(f"Syntax: next_step.py [i=<input file path>] [o=<output file path>] [s=<n>] [e=<m>]\n"
                  f"  i=<path>:  (optional) input file path,"
                  f"             default: {Src}\n"
                  f"  o=<path>:  (optional) output file path,"
                  f"             default: {Dst}\n"
                  f"  b=<n>:     (optional) begin testing from file line number, default: {Begin}\n"
                  f"  e=<m>:     (optional) stop testing after line number, default: {End}\n"
                  f"  m=<Mthds>: (optional) A list of comma separated methods to filter in puzzle specs.\n"
                  f"             Only evaluate puzzles with these methods, ignore all other puzzles\n"
                  f"  f=<Mthds>: (optional) A list of comma separated methods to try first for each puzzle spec\n"
                  f"             Try these methods first before attempting method in puzzle spec\n"
                  f"  g:         (optional) iGgnore Method and overrides in puzzle specs.\n")
            exit()

    lMeths = []
    for sMethod in Firsts:
        sM = sMethod.strip()
        for Meth, TInfo in Tech.items():  # m in range(len(T):
            if TInfo.Text == sM:
                if Meth not in lMeths: lMeths.append(Meth)
                break

    nLine = 0; nPzl = 0; Diffs = 0; Errs = 0
    with open(Src, "rt") as f:
        with open(Dst, "wt") as f1:
            while 1:
                StTime = perf_counter()
                Line = f.readline()
                if not Line: break
                nLine += 1
                if not Begin <= nLine <= End: continue
                if Line[:3] == "## ": print(f"\n{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| {Line[0:-1]}", flush = True)
                if Line == "\n" or Line[0] == "#":
                    f1.write(Line); f1.flush()
                    continue
                oPzl = PZL()
                NrFlds, sErr = pzl_str_to_pzl(Line, oPzl)
                if not NrFlds:
                    f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                    print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {sErr}", flush = True)
                    Errs += 1
                    continue
                nPzl += 1
                TD = Line.rstrip(" \n").split("|")
                lenTD = len(TD)
                if Methods and lenTD > 2 and TD[2] and TD[2] not in Methods: continue
                if Ignore:
                    if lenTD > 2: TD[2] = ""
                    if lenTD > 3: TD[3] = ""
                    oPzl.Method = T_UNDEF
                if not oPzl.Soln:
                    Found, oPzl.Soln = check_puzzle(oPzl.Grid)
                    if Found == 1: sSoln = grid_to_grid_str(oPzl.Soln, oPzl.Givens)
                    else:
                        St = f"Invalid Puzzle:  {Found} solutions found: {Line}"
                        f1.write(St); f1.flush()
                        print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {St}", flush = True)
                        Errs += 1
                        continue
                else: sSoln = TD[6]  # if lenTD >= 6 else ""

                sExpOutc = TD[5] if lenTD >= 6 else ""
                sExpCond = TD[4] if lenTD >= 5 else ""
                sOverrides = TD[3] if lenTD >= 4 else ""
                sExpMeth = TD[2] if lenTD >= 3 else ""
                sElims   = TD[1] if lenTD >= 2 else ""
                if not sExpMeth: sExpMeth = "Undefined"

                for Meth in lMeths:
                    Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, Meth, oPzl.Soln, True, oPzl.Overrides, JustThisMeth = True)
                    if Err or Step.Method == Meth: break
                else:
                    Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, oPzl.Method, oPzl.Soln, True, oPzl.Overrides)
                if Err:
                    f1.write(f"# Warning: Error encountered: {Err}, Actual: {Tech[Step.Method].Text}, Solving:  {Line}")
                    print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Expected: {sExpMeth}| Actual: {Tech[Step.Method].Text}, Error: {Err}", flush = True)
                    Errs += 1
                    continue

                sActMeth = Tech[Step.Method].Text
                sCond = tkns_to_str(Step.Pattern).replace(" ", "").replace(".", "")
                sOutc = tkns_to_str(Step.Outcome).replace(" ", "").replace(".", "")

                sGr = TD[0].replace("0", ".")
                Match = True
                if oPzl.Method != Step.Method: Match = False
                if Step.Method != T_BRUTE_FORCE:
                    if sExpCond:
                        if set(sExpCond.split(";")) != set(sCond.split(";")): Match = False
                    if sExpOutc:
                        if set(sExpOutc.split(";")) != set(sOutc.split(";")): Match = False
                if Match or Ignore: print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| {sActMeth}", flush = True)
                else:
                    if sExpMeth != sActMeth:  sWarn = "Different Method"
                    elif sExpOutc != sOutc:   sWarn = "Different Outcome"
                    elif sExpCond != sCond:   sWarn = "Different Pattern"
                    f1.write(f"# Warning: {sWarn} found for: {Line}")
                    print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Warning: {sWarn}|{sExpMeth}|{sExpCond}|{sExpOutc}| Actual: {sActMeth}|{sCond}|{sOutc}", flush = True)
                    Diffs += 1
                f1.write(f"{sGr}|{sElims}|{sActMeth}|{sOverrides}|{sCond}|{sOutc}|{sSoln}\n")
                f1.flush()
    print(f"{time_str()}| End Run| Lines: {nLine}| Puzzles: {nPzl},  Differences: {Diffs}, Errors: {Errs}.")

def time_str(STime = 0):

    ETime = perf_counter()
    DTime = ETime - STime
    ESecs = ETime % 60; EMins = int((ETime//60)%60); EHrs = int(ETime//3600)
    DSecs = DTime % 60; DMins = int((DTime//60)%60); DHrs = int(DTime//3600)
    return f"{EHrs:02d}:{EMins:02d}:{ESecs:07.4f}|{DHrs:02d}:{DMins:02d}:{DSecs:07.4f}"

if __name__ == "__main__":
    yas_prt()
