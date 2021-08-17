#import pytest
from copy import copy
from time import perf_counter
#import csv

from globals import *
from misc import grid_str_to_grid, tkns_to_str, parse_ccell_phrase
from solve import solve_next_step
from solve_utils import *

#RegrList = []

def convert():
    #  Does more than convert the format, also tests the puzzle spec for a solution
    #  and compares the result highlighting differences.

    with open("test-data/logic-step-regression-1.0.txt", "rt") as f:
        with open("test-data/logic-step-regression-1.1.txt", "wt") as f1:
            i = 0
            Test = 0
            while 1:
                Line = f.readline()
                i += 1
                print(f"{perf_counter():f}: Processing Line {i}, Test: {Test}")
                if not Line: break
                if Line[:7] == "Warning": continue  # or Line[:9] == "# Warning": continue
                if Line == "\n" or Line[0] == "#":
                    f1.write(Line)
                    continue
                TD = Line.rstrip("\n").split("|")
                if len(TD) != 5:
                    f1.write(f"# Warning: Wrong number of csv fields {len(TD)}, should be 5.|{Line}")
                    continue
                # Parse New format.
                # TD[0] ==> Givens + placed.
                TGrid = [[0 for c in range(9)] for r in range(9)]
                if not grid_str_to_grid(TD[0], TGrid, Placed = False):  # no need to differentiate btwn givens and placed.
                    f1.write(f"# Warning: Cannot translate grid string.|{Line}")
                    continue
                # TD[1] ==> removed candidates in cell grammar syntax.
                TElim = [[set() for c in range(9)] for r in range(9)]
                sElim = TD[1].replace(" ","").replace(".","")
                for sE in sElim.split(";"):
                    if not sE: continue
                    r, c, op, Cands = parse_ccell_phrase(sE)
                    if r < 0:
                        f1.write(f"# Warning: Cannot parse Cands to remove, field 2.|{Line}")
                        break
                    TElim[r][c] |= Cands
                else:
                    # TD[2] contains method to test.
                    for TId in range(T_NR_TECHS):
                        if T[TId][T_TXT] == TD[2]: break
                    else: TId = T_UNDEF
                    # TD[3] and TD[4] contains Expected condition and outcome, both can be empty
                    #   Condition is compared verbatim with Actual condition.
                    #   Outcome split into a set of cell grammar phrases to be compared
                    #   with actual. Set, as order of phrase may vary in original strings
                    sExpCond = TD[3].replace(" ","").replace(".","")
                    oExpOutc = set(TD[4].replace(" ","").replace(".","").split(";"))
                    Test += 1
                    # TStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_DIFF: 0, P_SUBS: []}
                    # if not solve_next_step(TGrid, TStep, TElim, Method = TId):
                    #     f1.write(f"# Warning: Cannot solve puzzle.|{Line}")
                    #     continue
                    #
                    # sMeth = T[TStep[P_TECH]][T_TXT]
                    # sCond = tkns_to_str(TStep[P_COND]).replace(" ","").replace(".","")
                    # sOutc = tkns_to_str(TStep[P_OUTC]).replace(" ","").replace(".","")
                    # # if sMeth != TD[2] or sCond != sExpCond or set(sOutc.split(";")) != oExpOutc:
                    # if sMeth != TD[2] or set(sOutc.split(";")) != oExpOutc:
                    #     f1.write(f"# Info: Different (possibly correct) Method, condition and/or outcome per next line.|{Line}")
                    # f1.write(f"{TD[0]}|{sElim}|{sMeth}|{sCond}|{sOutc}\n")
                    TStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_DIFF: 0, P_SUBS: []}
                    if not solve_next_step(TGrid, TStep, TElim, Method = TId):
                        TStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_DIFF: 0, P_SUBS: []}
                        if not solve_next_step(TGrid, TStep, TElim, Method = T_UNDEF):
                            f1.write(f"# Warning: Cannot solve next step on line: {Line}\n")
                            continue

                    sMeth = T[TStep[P_TECH]][T_TXT]
                    sCond = tkns_to_str(TStep[P_COND]).replace(" ", "").replace(".", "")
                    sOutc = tkns_to_str(TStep[P_OUTC]).replace(" ", "").replace(".", "")
                    if sMeth != TD[2]:
                        f1.write(f"# Info: Different (possibly correct) Method used for next line: Expected: {TD[2]}; Actual: {sMeth}, line: {Line}.| ")
                    f1.write(f"{TD[0]}|{sElim}|{sMeth}|{sCond}|{sOutc}\n")


if __name__ == "__main__":
    convert()
