# import pytest
from copy import copy
from time import perf_counter
# import csv

from globals import *
from misc import grid_str_to_grid, tkns_to_str, parse_ccell_phrase
from solve import solve_next_step
from solve_utils import *

# RegrList = []

def convert():
    #  Does more than convert the format, also tests the puzzle spec for a solution
    #  and compares the result highlighting differences.

    with open("test-data/logic-step-regression-1.0.txt", "rt") as f:
        with open("test-data/logic-step-regression-0.5.txt", "wt") as f1:
            i = 0
            while 1:
                Line = f.readline()
                i += 1
                print(f"{perf_counter():f}: Processing Line {i}")
                if not Line: break
                if Line[:7] == "Warning": continue  # or Line[:9] == "# Warning": continue
                if Line == "\n" or Line[0] == "#":
                    f1.write(Line)
                    continue
                TD = Line.rstrip("\n").split("|")
                # Parse New format.
                # TD[0] ==> Givens + placed.
                f1.write(f"{TD[0]}|{TD[1]}|{TD[2]}\n")




if __name__ == "__main__":
    convert()
