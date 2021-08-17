from time import perf_counter
import os

from globals import *
from misc import grid_str_to_grid, grid_to_grid_str
from generate import check_puzzle



def batch_solve():
    with open("bat-data/sudoku.txt", "rt") as f:
        with open ("bat-data/puzzles1.txt", "wt") as f1:
            i = 0; sSt = ""
            while 1:
                 # if sSt:
                t = perf_counter()
                d = int(t//86400)
                h = int(t%86400//3600)
                m = int(t%3600//60)
                s = t%60
                print(f"{d},{h:02d}:{m:02d}:{s:06.3f}|{i}|{sSt}")
                i += 1
                Line = f.readline()
                if not Line: break
                (Line, Hash, Comment) = Line.partition("#")
                if Line == "\n": continue
                Line = Line.strip().split(",")
                # line is now a two element array of pzl and soln.
                Pzl = [[0 for c in range(9)] for r in range(9)]
                if not grid_str_to_grid(Line[0], Pzl):
                    sSt =  f"# Warning: {i}: cannot translate grid_str_to_grid: {line}"
                    f1.write(f"{sSt}\n")
                    continue
                Soln = {S_FOUND:0, S_GRID: None}
                check_puzzle(Pzl, Soln)
                if Soln[S_FOUND] != 1:
                    sSt = f"# Warning: {i}: Invalid puzzle, {Soln[S_FOUND]} soultions: {Line}"
                    f1.write(f"{sSt}\n")
                    continue
                sSoln = grid_to_grid_str(Soln[S_GRID])
                if len(Line) > 1 and Line[1] != sSoln:
                    sSt = f"# Warning: {i}: Different Solution found: {sSoln}: {line}"
                    f1.write(f"{sSt}\n")
                    continue
                sSt = f"{grid_to_grid_str(Pzl)},{sSoln}"
                f1.write(f"{sSt}\n")
                f1.flush()

if __name__ == "__main__":
    batch_solve()
