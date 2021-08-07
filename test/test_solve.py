import pytest
from copy import copy
#import csv

from globals import *
from misc import grid_str_to_grid
from solve import solve_next_step
from solve_utils import *

RegrList = []

with open("test-data/logic_step_regression.csv", "rt") as f:
    i = 0
    while 1:
        Line = f.readline()
        i += 1
        if not Line: break
        if Line == "\n": continue
        Line = Line.removesuffix("\n")
        (Csv, Hash, Cmt) = Line.partition("#")  # discard Hash & Cmt
        if not Csv or Csv == "": continue
        TD = Csv.split(",")
        if len(TD) != 7:
            print(f"Warning: Discarding line {i}: Wrong number of csv fields {len(TD)}, should be 7.")
            continue
        for t in range(T_NR_TECHS):
            if T[t][T_TXT] == TD[0]:
                TestLine = i
                TestIdx  = t

                # TestTxt = copy(TD[0])
                break
        else:
            print(f"Warning: Discarding line {i}: Logic Method \'{TD[0]}\' not found.")
            continue
        if not len(TD[1]):
            print(f"Warning: Discarding line {i}: At least one candidate is required in field 2.")
            continue
        TestCands = [int(TD[1][i]) for i in range(len(TD[1]))]
        TestGrid = [[0 for c in range(9)] for r in range(9)]
        if not grid_str_to_grid(TD[2], TestGrid, Placed = False):
            print(f"Warning: Discarding line {i}: Could not parse test grid in field 3.")
            continue
        TestElim = [[set() for c in range(9)] for r in range(9)]
        SlvdElim = []
        SlvdPlcd = []
        SlvdXtra = copy(TD[6])
        List     = TD[3].split()  # TestElim
        for E in List:  # 1 <= xx <= 9
            if len(E) == 3:
                Ccell = (int(E[1]), int(E[2]), int(E[0]))
                if 1 <= Ccell[0] <= 9 and 1 <= Ccell[1] <= 9 and 1 <= Ccell[2] <= 9:
                    TestElim[Ccell[0]-1][Ccell[1]-1].add(Ccell[2])
                else: break
            else: break
        else:
            List = TD[4].split()
            for E in List:
                if len(E) == 3:
                    Ccell = (int(E[1]), int(E[2]), int(E[0]))
                    if 1 <= Ccell[0] <= 9 and 1 <= Ccell[1] <= 9 and 1 <= Ccell[2] <= 9:
                        SlvdElim.append(Ccell)
                    else: break
                else: break
            else:
                List = TD[5].split()
                for E in List:
                    if len(E) == 3:
                        Ccell = (int(E[1]), int(E[2]), int(E[0]))
                        if 1 <= Ccell[0] <= 9 and 1 <= Ccell[1] <= 9 and 1 <= Ccell[2] <= 9:
                            SlvdPlcd.append(Ccell)
                        else: break
                    else: break
                else:
                    RegrList.append((TD, TestLine, TestIdx, TestCands, TestGrid, TestElim, SlvdElim, SlvdPlcd, SlvdXtra))
                    continue
                print(f"Warning: Discarding line {i}: Error parsing solved placements, field 6.")
                continue
            print(f"Warning: Discarding line {i}: Error parsing solved eliminations, field 5.")
            continue
        print(f"Warning: Discarding line {i}: Error parsing test eliminations, field 4.")
    # end of while loop.

@pytest.mark.parametrize("TD1, TLine, TIdx, TCands, TGrid, TElim, SElim, SPlcd, SXtra", RegrList)
def test_solve_next_step(TD1, TLine, TIdx, TCands, TGrid, TElim, SElim, SPlcd, SXtra):

    TStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_DIFF: 0, P_SUBS: []}
    assert solve_next_step(TGrid, TStep, TElim), f"Line {TLine}: Unable to solve step!"

    assert T[TStep[P_TECH]][T_TXT] == TD1[0], f"Line {TLine}: Solved with different logic technique!"

    Outcome = set(construct_str(TStep[P_OUTC]).replace(" ", "").split(";"))


    result = set()
abd = [("1+1",2), ("2+2",4)]

# @pytest.mark.parametrize("test_input, expected", abd)
# def test_eval(test_input, expected):
#     sdf = RegrList
#
#     assert eval(test_input) == expected
