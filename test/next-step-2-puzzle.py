
from globals import *
from misc import *
from solve import *
from solve_utils import *


def next_step_to_puzzle():
    with open("test-data/next-step-1.0-in.txt", "rt") as f:
        with open ("../bat/bat-data/puzzle-1.0-in.txt", "wt") as f1:
            f1.write("# Puzzle\n")
            lPzls = []
            while 1:
                Line = f.readline()
                if not Line: break
                if Line == "\n" or Line[0] == "#": continue
                i = 0; Pzl = ""
                while Line[i] != "|":  # < len(Pzl-1):
                    if Line[i] == "+": Pzl += "0"; i += 2
                    elif Line[i] == ".": Pzl += "0"; i += 1
                    else: Pzl += (Line[i]); i += 1

                oPzl = PZL()  # {PZL_GRID: [], PZL_ELIMS: [], PZL_METH: T_UNDEF, PZL_PTRN: "", PZL_OUTC: ""}
                Flds = pzl_str_to_pzl(Line, oPzl)  # parse_pzl_str_depreciated(Line, Opzl)
                if not Flds: continue
                mPzl = grid_to_grid_str(minimalise_puzzle(Opzl.Grid)) # [PZL_GRID]))
                if mPzl and mPzl in lPzls: continue
                oPzls.append(mPzl)
                f1.write(mPzl+"\n")

if __name__ == "__main__":
    next_step_to_puzzle()