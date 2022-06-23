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
# from trc import *
from generate import *
from misc import *
from solve import *
from solve_utils import *



def yas_prt():

    print(f"YAS Pattern Regression Tester.  Run start: {datetime.now()}.", flush = True)  # , using {Code} code.", flush = True)
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src = join(TestDataDir, SrcFile+FileExt)
    Dst = join(TestDataDir, SrcFile+DstSuff+FileExt)
    Begin = 0; End = 9999999
    for i in range(1, len(argv)):
        if argv[i][:2] in ["i=", "I="]: Src = argv[i][2:]
        elif argv[i][:2] in ["o=", "O="]: Dst = argv[i][2:]
        elif argv[i][:2] in ["b=", "B="]: Begin = int(argv[i][2:])
        elif argv[i][:2] in ["e=", "E="]: End = int(argv[i][2:])
        else:
            print(f"Syntax: next_step.py [i=<input file path>] [o=<output file path>] [s=<n>] [e=<m>]\n"
                  f"  i=<path>:  (optional) input file path, default: {Src}\n"
                  f"  o=<path>:  (optional) output file path, default: {Dst}\n"
                  f"  b=<n>:     (optional) begin testing from file line number, default: {Begin}\n"
                  f"  e=<m>:     (optional) stop testing after line number, default: {End}.\n")
            exit()

    i = 0; Test = 0; Diffs = 0; Errs = 0
    with open(Src, "rt") as f:
        with open(Dst, "wt") as f1:
            while 1:
                Line = f.readline()
                if not Line: break
                i += 1
                if not Begin <= i <= End: continue
                if Line[:3] == "## ": print(f"\n{perf_counter():07f}: Line: {i}, Test: {Test}, {Line[0:-1]}", flush = True)

                if Line == "\n" or Line[0] == "#":
                    f1.write(Line); f1.flush()
                    continue
                oPzl = PZL()
                NrFlds, sErr = pzl_str_to_pzl(Line, oPzl)
                if not NrFlds:
                    f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                    print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Error: {sErr}", flush = True)
                    Errs += 1
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
                else: sSoln = TD[6]  # if lenTD >= 6 else ""
                Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, oPzl.Method, oPzl.Soln, True, oPzl.Overrides)
                if Err:
                    f1.write(f"# Warning: Error encountered: {Err}, Solving:  {Line}")
                    print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Expected: {sExpMeth}, Actual: {Tech[Step.Method].Text}, Error: {Err}", flush = True)
                    Errs += 1
                    continue
                    # Step, Err = solve_next_step(oPzl.Grid, oPzl.Elims, T_UNDEF, oPzl.Soln, True)
                    # if Err:
                    #     f1.write(f"# Warning: Error encountered: {Err}, Solving:  {Line}")
                    #     print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Expected: {sExpMeth}, Actual: {Tech[Step.Method].Text}, Error: {Err}", flush = True)
                    #     Errs += 1
                    #     continue

                sActMeth = Tech[Step.Method].Text
                sCond = tkns_to_str(Step.Pattern).replace(" ", "").replace(".", "")
                sOutc = tkns_to_str(Step.Outcome).replace(" ", "").replace(".", "")
                sExpOutc = TD[5] if lenTD >= 6 else ""
                sExpCond = TD[4] if lenTD >= 5 else ""
                sOverrides = TD[3] if lenTD >= 4 else ""
                sExpMeth = TD[2] if lenTD >= 3 else ""
                sElims   = TD[1] if lenTD >= 2 else ""
                if not sExpMeth: sExpMeth = "Undefined"
                sGr = TD[0].replace("0", ".")
                Match = True
                if oPzl.Method != Step.Method: Match = False
                if Step.Method != T_BRUTE_FORCE:
                    if sExpCond:
                        if set(sExpCond.split(";")) != set(sCond.split(";")): Match = False
                    if sExpOutc:
                        if set(sExpOutc.split(";")) != set(sOutc.split(";")): Match = False
                if Match: print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, {sActMeth}", flush = True)
                else:
                    if (sExpMeth != sActMeth):  sWarn = "Different Method"
                    elif (sExpOutc != sOutc):   sWarn = "Different Outcome"
                    elif (sExpCond != sCond):   sWarn = "Different Pattern"
                    f1.write(f"# Warning: {sWarn} found for: {Line}")
                    print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Warning: {sWarn}: {sExpMeth}|{sExpCond}|{sExpOutc}, Actual: {sActMeth}|{sCond}|{sOutc}", flush = True)
                    Diffs += 1
                f1.write(f"{sGr}|{sElims}|{sActMeth}|{sOverrides}|{sCond}|{sOutc}|{sSoln}\n")
                f1.flush()
    print(f"{perf_counter():07f}: End Run, Lines: {i}, Tests: {Test},  Differences: {Diffs}, Errors: {Errs}.")


if __name__ == "__main__":
    yas_prt()

