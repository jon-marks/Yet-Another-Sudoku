import pytest
from copy import copy
import os
#import csv

from globals import *
from misc import tkns_to_str, parse_ccell_phrase
from solve import solve_next_step
from solve_utils import *

#@pytest.fixture
def create_regrlist(RegrList):
    asdfsf = os.getcwd()
    with open("test-data/logic-step-regression-1.0.txt", "rt") as f:
        TLine = 0
        while 1:
            Line = f.readline()
            TLine += 1
            if not Line: break
            if Line == "\n" or Line[0] == "#": continue
            TD = Line.removesuffix("\n").split("|")
            if len(TD) != 5:
                print(f"Warning: Line {i}: Wrong number of csv fields {len(TD)}, should be 5.|{Line}")
                continue
            TGrid = [[0 for c in range(9)] for r in range(9)]
            if not grid_str_to_grid(TD[0], TGrid, Placed = False):
                print(f"Warning: Line {i}: Cannot translate grid string.|{Line}")
                continue
            sElim = TD[1].replace(" ", "").replace(".", "")
            TElim = [[set() for c in range(9)] for r in range(9)]
            for sE in sElim.split(";"):
                if not sE: continue
                r, c, op, Cands = parse_ccell_phrase(sE)
                if r < 0:
                    print(f"Warning: Line {i}: Cannot parse Cands to remove, field 2.|{Line}")
                    break
                TElim[r][c] |= Cands
            else:
                # TD[2] contains method to test.
                for Tx in T: # TTech in range(len):
                    if T[Tx][T_TXT] == TD[2]: break
                else:
                    if TD[2]: print(f"Info: Line {TLine}: Cannot find method \'{TD[2]}\' Will find best method.")
                    TId = T_UNDEF
                # TD[3] and TD[4] contains Expected condition and outcome, both can be empty
                #   Condition is compared verbatim with Actual condition.
                #   Outcome split into a set of cell grammar phrases to be compared
                #   with actual. Set, as order of phrase may vary in original strings
                sExpCond = TD[3].replace(" ", "").replace(".", "")
                osExpOutc = set(TD[4].replace(" ", "").replace(".", "").split(";"))
                RegrList.append((TLine, TD, TTech, TGrid, TElim, sExpCond, osExpOutc))
    return RegrList
        # end of while loop.

Regr = []
create_regrlist(Regr)

@pytest.mark.parametrize("TLine, TD, TTech, TGrid, TElim, sExpCond, osExpOutc", Regr)
def test_solve_next_step(TLine, TD, TTech, TGrid, TElim, sExpCond, osExpOutc):

    TStep = {P_TECH: T_UNDEF, P_PTRN: [], P_OUTC: [], P_DIFF: 0}
    res = solve_next_step(TGrid, TStep, TElim, Method = TTech)
    res1 = True
    if not res:
        # The step could not solved with the method specified in TTech.  Can it
        # find a method to solve the next step?
        res1 = solve_next_Step(TGrid, TStep, TElim)

    if res:
        # possibilities here are that the same or different condition and outcome was found
        sCond = tkns_to_str(TStep[P_PTRN]).replace(" ", "").replace(".", "")
        osOutc = set(tkns_to_str(TStep[P_OUTC]).replace(" ", "").replace(".", "").split(";"))
        assert sCond == sExpCond and osOutc == osExpOutc,\
            f"{TLine}|Passed with different condition and ouctome:" \
            f"Expected: {sExpCond}|{sorted(osExpOutc)}, " \
            f"Actual: {sCond}|{sorted(osOutc)}"
    elif res1:
        # test passed using a with different method
        sCond = tkns_to_str(TStep[P_PTRN]).replace(" ", "").replace(".", "")
        osOutc = set(tkns_to_str(TStep[P_OUTC]).replace(" ", "").replace(".", "").split(";"))
        assert Tstep[P_TECH] == TTECH,\
            f"{TLine}:Passed with with different method:" \
            f"Expected: {T[TTECH][T_TXT]}|{sExpCond}|{sorted(osExpOutc)}, " \
            f"Actual: {T[TStep[P_TECH]][T_TXT]}|{sCond}|{sorted(osOutc)}"
    else:  # test truly failed.
        assert False, f"{TLine}:Failed"
