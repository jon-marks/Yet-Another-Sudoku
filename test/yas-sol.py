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
DstFile  = "patterns"
MthFile  = "methods"
FileExt  = ".txt"
DbExt    = ".sql"
Root = dirname(dirname(argv[0]))
chdir(Root)
path.insert(0, f"{join(Root, SrcDir)}")

from globals import *
# from trc import *
from generate import *
from misc import *
from solve import *
from solve_utils import *

M_SLVR = 0
M_SRCH = 1

def yas_sol():

    print(f"YAS - Pattern Batch Puzzle Solver. Run start: {datetime.now()}.", flush = True)  # , using {Code} code.", flush = True)
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src  = join(TestDataDir, SrcFile+FileExt)
    Dst  = join(TestDataDir, DstFile+FileExt)
    Db   = join(TestDataDir, SrcFile+DbExt)
    Mth  = join(TestDataDir, MthFile+FileExt)
    sPat = "Undefined"; Meth = -1
    Begin = 0; End = 999999
    sOverrides = ""; Overrides = {}
    Mode = M_SLVR
    for i in range(1, len(argv)):
        if argv[i][:2] in ["i=", "I="]: Src = argv[i][2:]
        elif argv[i][:2] in ["o=", "O="]: Dst = argv[i][2:]
        elif argv[i][:2] in ["b=", "B="]: Begin = int(argv[i][2:])
        elif argv[i][:2] in ["e=", "E="]: End = int(argv[i][2:])
        elif argv[i][:2] in ["d=", "D="]: Db = argv[i][2:]
        elif argv[i][:2] in ["a=", "A="]: Add = argV[i][2:]
        elif argv[i][:2] in ["m=", "M="]:
            Mode = M_SRCH
            if argv[i][2:]: Mth = argv[i][2:]
        elif argv[i][:2] in ["p=", "P="]: sPat = argv[i][2:]
        elif argv[i][:2] in ["v=", "V="]: sOverrides = argv[i][2:]
        else:
            print(f"Syntax: yas-sol.py [i=<input file path>] [o=<output file path>] [s=<n>] [e=<m>]\n"
                  f"  i=<path>:  (optional) input file path,\n"
                  f"             default: {Src}\n"
                  f"  o=<path>:  (optional) output file path,\n"
                  f"             default: {Dst}\n"
                  f"  b=<n>:     (optional) start testing from file line number, default: {Begin}\n"
                  f"  e=<m>:     (optional) stop testing after line number, default: {End}.\n"
                  "Complete Solver Mode Commands\n"
                  f"  d=<path>:  (optional) database file to create or append, if <path> not specified,\n"
                  f"             default: {Db}\n"
                  f"  a=<[e|d]>: (optional) additional fields - e: expertise level, d: difficulty\n"
                  "Selected Method Pattern Searcher Commands\n"
                  f"  m=<path>:  (required for this mode), file with ordered selected methods to use till stumped\n"
                  f"             default (empty value): {Mth}\n"
                  f"  p=<Meth>:  (required for this mode) Method pattern to search\n"
                  f"  v=<kvp>:   (optional) Override key=value pairs separated by semicolon suported by the method to constrain search\n")
            exit()
    i = 0; Test = 0; Diffs = 0; Errs = 0
    if Mode == M_SRCH:  # Selected Method Pattern Searcher Mode:
        print("    Pattern Searcher Mode", flush = True)
        Meths = []
        if sPat == "Undefined": print(f"Error: Invalid Search Method: {sPat} in 'p=' switch, or 'P=' not specifed\n"), exit()
        for k, v in Tech.items():
            if v.Text == sPat: Meth = k; break
        else:
            print(f"Error: Invalid Step: {sPat} in 'p=' switch.\n"); exit()
        with open(Mth, "rt") as f2:
            while 1:
                sMeth = f2.readline().rstrip('\n')
                if not sMeth: break
                for k, v in Tech.items():
                    if v.Text == sMeth: Meths.append(k); break
                else:
                    print(f"Error: Invalid method in {Mth} file: {sMeth}"); exit()
        for Oride in sOverrides.split(";"):
            if "=" in Oride: Key, Val = Oride.split("="); Overrides[Key] = Val
            else: print(f"Error: Malformed Overrides: {sOverrides} in v= switch.\n"); exit()
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
                    TD = Line.rstrip(" \n").split("|")
                    lenTD = len(TD)
                    oPzl = PZL()
                    if lenTD == 1: NrFlds, sErr = pzl_str_to_pzl(TD[0], oPzl)
                    else: NrFlds, sErr = pzl_str_to_pzl(TD[0] + "|" + TD[1], oPzl)
                    if not NrFlds:
                        f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                        print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Error: {sErr}", flush = True)
                        Errs += 1
                        continue
                    Test += 1
                    if lenTD >= 7:  # sSoln field.
                        oPzl.Soln = [[0 for c in range(9)] for r in range(9)]
                        sSoln = TD[6]
                        grid_str_to_grid(sSoln, oPzl.Soln)
                    else:
                        Found, oPzl.Soln = check_puzzle(oPzl.Grid)
                        if Found == 1: sSoln = grid_to_grid_str(oPzl.Soln, oPzl.Givens)
                        else:
                            St = f"Invalid Puzzle:  {Found} solutions found: {Line}"
                            f1.write(St); f1.flush()
                            print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Error: {St}", flush = True)
                            Errs += 1
                            continue

                    oPzl.NrEmpties, oPzl.Cands = determine_cands(oPzl.Grid, oPzl.Elims)
                    Steps, sErr = pattern_search(oPzl, Meths, Meth, Overrides)
                    for Step in Steps:
                        NrEmpties, Elims = determine_cands(Step.Grid, Step.Cands)
                        sPzl = f"{pzl_to_pzl_str(PZL(Grid = Step.Grid, Givens = oPzl.Givens, Elims = Elims, Method = Meth, Pattern = Step.Pattern, Outcome = Step.Outcome), sOverrides)}"
                        f1.write(f"{sPzl}\n"); f1.flush()
                        print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, {sPzl}", flush = True)
                    else:
                        if not Steps: print(f"{perf_counter():07f}: Line: {i}, Test: {Test}, Nothing found")

    else:  # Complete Solve Mode.l
        pass
    print(f"{perf_counter():07f}: End Run, Lines: {i}, Tests: {Test},  Differences: {Diffs}, Errors: {Errs}.")


if __name__ == "__main__":
    yas_sol()

