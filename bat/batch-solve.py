from time import perf_counter
import os

from globals import *
# from misc import grid_str_to_grid, grid_to_grid_str_depreciated
from generate1 import check_puzzle
from solve import logic_solve_puzzle
from solve_utils import T, T_DIFF



def batch_solve():
    with open("bat-data/puzzle-1.0-in.txt", "rt") as f:
        with open ("bat-data/puzzles1.txt", "wt") as f1:
            i = 0; sSt = ""
            f1.write("# Puzzle                                                                          Solution                                                                          Chk Time  Val Time  Diff  Level        Chk Steps\n")
            while 1:
                t1 = perf_counter()
                i += 1
                sPzl = f.readline()
                if not sPzl: break
                if sPzl == "\n" or sPzl[0] == "#": continue
                Pzl = [[int(sPzl[(r*9)+c]) if sPzl[(r*9)+c].isdigit() else 0 for c in range(9)] for r in range(9)]
                Found, Soln, Rsteps = check_puzzle(Pzl)
                if Found != 1:
                    f1.write(f"{sPzl[:81]}  *** INVALID PUZZLE!\n")
                    continue
                sSoln = ""
                for r in range(9):
                    for c in range(9):
                        sSoln += str(Soln[r][c])
                t2 = perf_counter()
                Lvl, Steps = logic_solve_puzzle(Pzl, None, None, Soln)
                if Lvl < 0:
                    f1.write(f"{sPzl[:81]} {sSoln}  *** BUG: Error in logic soln!\n")
                    continue
                Diff = 0
                for Step in Steps:
                    Diff += T[Step[P_TECH]][T_DIFF] if Step[P_DIFF] == 0 else Step[P_DIFF]
                t3 = perf_counter()
                ta = t2 - t1
                tb = t3 - t2
                sTChk = f"{int(ta//60):02d}:{ta%60:06.3f}"
                sTVal = f"{int(ta//3600):02d}:{int((tb%3600)//60):02d}:{tb%60:06.3f}"

                f1.write(f"{sPzl[:81]} {sSoln} {sTChk} {sTVal} {Diff: 5d} {EXPS[Lvl]:12s} {Rsteps: 9}\n")
                f1.flush()

if __name__ == "__main__":
    batch_solve()
