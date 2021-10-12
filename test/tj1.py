#import pytest
from copy import copy
from time import perf_counter

from globals import *
from misc import parse_pzl_str, parse_ccell_phrase, tkns_to_str
from solve import *
from solve_utils import *


def convert():
    #  Does more than convert the format, also tests the puzzle spec for a solution
    #  and compares the result highlighting differences.

    with open("test-data/td.txt", "rt") as f:
        with open("test-data/tr.txt", "wt") as f1:
            i = 0
            Test = 0
            while 1:
                Line= f.readline()
                i += 1
                print(f"{perf_counter():f}: Processing Line {i}, Test: {Test}")
                if not Line: break
                if Line[:7] == "Warning": continue  # or Line[:9] == "# Warning": continue
                if Line == "\n" or Line[0] == "#":
                    f1.write(Line)
                    continue
                oPzl = {PZL_GRID: [], PZL_ELIMS: [], PZL_METH: T_UNDEF, PZL_PTRN: "", PZL_OUTC: ""}
                Flds = parse_pzl_str(Line, oPzl)
                if not Flds:  continue

                TGrid = [[oPzl[PZL_GRID][r][c] %10 for c in range(9)] for r in range(9)]
                Test += 1
                TStep = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0}
                if not solve_next_step(TGrid, TStep, oPzl[PZL_ELIMS], oPzl[PZL_METH]):
                    TStep = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0}
                    if not solve_next_step(TGrid, TStep, oPzl[PZL_ELIMS], T_UNDEF):
                        f1.write(f"# Warning: Cannot solve next step on line: {Line}\n")
                        continue

                sMeth = T[TStep[P_TECH]][T_TXT]
                sCond = tkns_to_str(TStep[P_PTRN]).replace(" ", "").replace(".", "")
                sOutc = tkns_to_str(TStep[P_OUTC]).replace(" ", "").replace(".", "")
                TD = Line.rstrip(" \n").split("|", 3)
                if oPzl[PZL_METH] != TStep[P_TECH]:
                    f1.write(f"# Info: Expected: {TD[2]}; Actual: {sMeth}, line: {Line}")
                f1.write(f"{TD[0]}|{TD[1]}|{sMeth}|{sCond}|{sOutc}\n")
                f1.flush()


if __name__ == "__main__":
    convert()
