#!/usr/bin/env python
from os.path import dirname, join
from os import chdir, name
from sys import argv, exit, path
from time import perf_counter, localtime, strftime, time

SrcDir   = "src"
TestDir  = "test"
TestDDir = "test-data"
SrcFile  = "pattern-reg-test-1.0"
DstFile  = "patterns"
MthFile  = "methods"
FileExt  = ".txt"
DbExt    = ".sql"

CWP = ""
if name == 'nt': CWP = argv[0].replace("/", "\\")
elif name == 'posix': CWP = argv[0].replace("\\", "/")

Root = dirname(dirname(CWP))
if not Root: Root = "."

chdir(Root)
path.insert(0, f"{join(Root, SrcDir)}")

from globals import *
from generate import *
from misc import *
from solve import *
from solve_utils import *

M_SLVR = 0
M_SRCH = 1

def yas_sol():
    print(f"YAS - Pattern Batch Puzzle Solver.")
    print(VERSION)
    print(f"Run start: {strftime('%a, %d %b %Y, %H:%M:%S', localtime(time()))}")
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src  = join(TestDataDir, SrcFile+FileExt)
    Dst  = join(TestDataDir, DstFile+FileExt)
    Db   = join(TestDataDir, SrcFile+DbExt)
    Mth  = join(TestDataDir, MthFile+FileExt)
    sPat = "Undefined"; Meth = -1
    sPzl = ""
    Begin = 0; End = 999999
    sOverrides = ""; Overrides = {}
    Mode = M_SLVR
    Add = False
    for i in range(1, len(argv)):
        if argv[i][:2] in ["s=", "S="]: sPzl = argv[i][2:]
        elif argv[i][:2] in ["i=", "I="]:
            if argv[i][:2]: Src = argv[i][2:]
        elif argv[i][:2] in ["o=", "O="]:
            if argv[i][:2]: Dst = argv[i][2:]
        elif argv[i][:2] in ["b=", "B="]: Begin = int(argv[i][2:])
        elif argv[i][:2] in ["e=", "E="]: End = int(argv[i][2:])
        elif argv[i][:2] in ["d=", "D="]: Db = argv[i][2:]
        elif argv[i][0] in ["a", "A"]: Add = True
        elif argv[i][:2] in ["m=", "M="]:
            Mode = M_SRCH
            if argv[i][2:]: Mth = argv[i][2:]
        elif argv[i][:2] in ["p=", "P="]: sPat = argv[i][2:]
        elif argv[i][:2] in ["v=", "V="]: sOverrides = argv[i][2:]
        else:
            print(f"Syntax: yas-sol.py [i=<input file path>] [o=<output file path>] [s=<n>] [e=<m>]\n"
                  f"  s=<str>    (optional) puzzle string of individual puzzle to solve instead of i= switch\n"
                  f"             only recognises givens in puzzle string\n"
                  f"  i=<path>:  (optional) input file path,\n"
                  f"             default: {Src}\n"
                  f"  o=<path>:  (optional) output file path,\n"
                  f"             default: {Dst}\n"
                  f"  b=<n>:     (optional) start testing from file line number, default: {Begin}\n"
                  f"  e=<m>:     (optional) stop testing after line number, default: {End}.\n"
                  "Complete Solver Mode Commands\n"
                  f"  d=<path>:  (optional) database file to create or append, if <path> not specified,\n"
                  f"             default: {Db}\n"
                  f"  a:         (optional) additional fields - e: expertise level, d: difficulty\n"
                  "Selected Method Pattern Searcher Commands\n"
                  f"  m=<path>:  (required for this mode), file with ordered selected methods to use till stumped\n"
                  f"             default (empty value): {Mth}\n"
                  f"  p=<Meth>:  (required for this mode) Method pattern to search.  Can be a substring,\n"
                  f"             and all Methods containing substring will be searched.\n"
                  f"  v=<kvp>:   (optional) Override key=value pairs separated by semicolon supported by the method to constrain search\n")
            exit()
    nLine = nPzl = nFound = Errs = 0
    if Mode == M_SRCH:  # Selected Method Pattern Searcher Mode:
        print("    Pattern Searcher Mode", flush = True)
        if sPat == "Undefined": print(f"Error| Invalid Search Method| {sPat} in 'p=' switch, or 'p=' not specified\n"), exit()
        PSMeths = []
        for k, v in Tech.items():
            if v.Text.find(sPat) < 0: continue
            else: PSMeths.append(k)   # == sPat: Meth = k; break
        if not PSMeths: print(f"Error: Invalid Step| {sPat} in 'p=' switch.\n"); exit()

        print("  ")
        Meths = []
        with open(Mth, "rt") as f2:
            while 1:
                sMeth = f2.readline().rstrip('\n')
                if not sMeth: break
                for k, v in Tech.items():
                    if v.Text == sMeth: Meths.append(k); break
                else:
                    print(f"Error: Invalid method in {Mth} file: {sMeth}"); exit()
        if sOverrides:
            for Oride in sOverrides.split(";"):
                if "=" in Oride: Key, Val = Oride.split("="); Overrides[Key] = Val
                else: print(f"Error: Malformed Overrides: {sOverrides} in v= switch.\n"); exit()
        BTime = perf_counter()
        with open(Src, "rt") as f:
            with open(Dst, "wt") as f1:
                while 1:
                    StTime = perf_counter()
                    Line = f.readline()
                    if not Line: break
                    nLine += 1
                    if not Begin <= nLine <= End: continue
                    if Line[:3] == "## ": print(f"\n{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| {Line[:-1]}", flush = True)
                    if Line == "\n" or Line[0] == "#" or Line[:2] == "//":
                        f1.write(Line); f1.flush()
                        continue
                    Line, SlashSlash, Comment = Line.partition("//")
                    TD = Line.rstrip(" \n").split("|")
                    lenTD = len(TD)
                    oPzl = PZL()
                    if lenTD == 1: NrFlds, sErr = pzl_str_to_pzl(TD[0], oPzl)
                    else: NrFlds, sErr = pzl_str_to_pzl(TD[0] + "|" + TD[1], oPzl)
                    if not NrFlds:
                        if Comment: f1.write(f"# Error: {sErr}: {Line}//{Comment}")
                        else: f1.write(f"# Error: {sErr}: {Line}")
                        f1.flush()
                        print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {sErr}", flush = True)
                        Errs += 1
                        continue
                    nPzl += 1
                    if lenTD >= 7:  # sSoln field.
                        oPzl.Soln = [[0 for c in range(9)] for r in range(9)]
                        sSoln = TD[6]
                        grid_str_to_grid(sSoln, oPzl.Soln)
                    else:
                        Found, oPzl.Soln = check_puzzle(oPzl.Grid)
                        if Found == 1: sSoln = grid_to_grid_str(oPzl.Soln, oPzl.Givens)
                        else:
                            St = f"Invalid Puzzle|  {Found} solutions found| {Line}"
                            if Comment: St += f"//{Comment}"
                            f1.write(St); f1.flush()
                            print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle:{nPzl}| Error:{St}", flush = True)
                            Errs += 1
                            continue

                    oPzl.NrEmpties, oPzl.Cands = determine_cands(oPzl.Grid, oPzl.Elims)
                    Steps, sErr = pattern_search(oPzl, Meths, PSMeths, Overrides)
                    for Step in Steps:
                        NrEmpties, Elims = determine_cands(Step.Grid, Step.Cands)
                        sPzl = f"{pzl_to_pzl_str(PZL(Grid = Step.Grid, Givens = oPzl.Givens, Elims = Elims, Method = Step.Method, Pattern = Step.Pattern, Outcome = Step.Outcome), sOverrides, sSoln)}"
                        f1.write(f"{sPzl}\n"); f1.flush()
                        print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| {sPzl}", flush = True)
                        nFound += 1
                    else:
                        if not Steps: print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| Nothing found")
        print(f"{time_str(BTime, StTime)}| End Run| Lines: {nLine}| Puzzles: {nPzl},  Found: {nFound}, Errors: {Errs}.")
    else:  # Complete Solve Mode.
        BTime = perf_counter()
        print("Complete Solve Mode:")
        if sPzl:
            StTime = perf_counter()
            oPzl = PZL()
            nFlds, sErr = pzl_str_to_pzl(sPzl, oPzl)
            if nFlds:
                nFound, oPzl.Soln = check_puzzle(oPzl.Givens)
                if nFound == 1:
                    Expertise, Steps, sErr = logic_solve_puzzle(Grid = oPzl.Givens, Soln = oPzl.Soln)
                    if not sErr:
                        Difficulty = 0
                        for Step in Steps:
                            Step.Difficulty = Tech[Step.Method].Difficulty+(Step.NrLks-Step.NrGrpLks)*LK_DIFF+Step.NrGrpLks*GRP_LK_DIFF
                            Difficulty += Step.Difficulty
                        sOut = f"{pzl_to_pzl_str(PZL(Givens = oPzl.Givens, Grid = oPzl.Grid, Soln = oPzl.Soln))}|{EXPS[Expertise]}|{Difficulty}"
                        sOut = sOut.replace("+", "")
                        print(f"{time_str(BTime, StTime)}|{sOut}")
                        exit()
                else: sErr = f"Invalid puzzle, {nFound} solutions"
            print(f"{time_str(BTime, StTime)}|Error: {sErr}")
            exit()
        with open(Src, "rt") as f:
            with open(Dst, "wt") as f1:
                # nPzl = nLine = 0
                while 1:
                    StTime = perf_counter()
                    Line = f.readline()
                    if not Line: break
                    nLine += 1
                    if not Begin <= nLine <= End: continue
                    if Line[:3] == "## ": print(f"\n{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| {Line[:-1]}", flush = True)
                    if Line == "\n" or Line[0] == "#":
                        f1.write(Line); f1.flush()
                        continue
                    TD = Line.rstrip(" \n").split("|")
                    lenTD = len(TD)
                    oPzl = PZL()
                    nPzl += 1
                    if lenTD == 1: NrFlds, sErr = pzl_str_to_pzl(TD[0], oPzl)
                    else: NrFlds, sErr = pzl_str_to_pzl(TD[0] + "|" + TD[1], oPzl)
                    if not NrFlds:
                        f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                        print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {sErr}", flush = True)
                        Errs += 1
                        continue
                    nFound, oPzl.Soln = check_puzzle(oPzl.Grid)
                    if nFound == 1:  # only one solution
                        Expertise, Steps, Err = logic_solve_puzzle(Grid = oPzl.Grid, Soln = oPzl.Soln)
                    else: Err = f"Invalid puzzle, {nFound} solutions"
                    if Err:
                        f1.write(f"# Error: {Err}| {Line}"); f1.flush()
                        print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {Err}:", flush = True)
                        Errs += 1
                        continue
                    sAdd = ""
                    if Add:
                        Difficulty = 0
                        for Step in Steps:
                            Step.Difficulty = Tech[Step.Method].Difficulty+(Step.NrLks-Step.NrGrpLks)*LK_DIFF+Step.NrGrpLks*GRP_LK_DIFF
                            Difficulty     += Step.Difficulty
                        sAdd = f"|{EXPS[Expertise]}|{Difficulty}"
                    sOut = f"{pzl_to_pzl_str(PZL(Givens = oPzl.Givens, Grid = oPzl.Grid, Soln = oPzl.Soln))}{sAdd}"
                    sOut = sOut.replace("+", "")
                    f1.write(sOut + "\n"); f1.flush()
                    print(f"{time_str(BTime, StTime)}| Line: {nLine}| Puzzle: {nPzl}|{sOut}", flush = True)
        print(f"{time_str(BTime, StTinme)}| End Run| Lines: {nLine}| Puzzles: {nPzl}, Errors: {Errs}.")

def time_str(BTime, STime = 0):

    ETime = perf_counter()
    DTime = ETime - STime
    ETime -= BTime
    ESecs = ETime % 60; EMins = int((ETime//60)%60); EHrs = int(ETime//3600)
    DSecs = DTime % 60; DMins = int((DTime//60)%60); DHrs = int(DTime//3600)
    return f"{EHrs:02d}:{EMins:02d}:{ESecs:010.7f}|{DHrs:02d}:{DMins:02d}:{DSecs:010.7f}"

if __name__ == "__main__":
    yas_sol()
