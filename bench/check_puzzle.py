#!/usr/bin/env python

import os, shutil, sys
from timeit import timeit

if not os.getenv("PYCHARM_HOSTED"):
    cwd = os.getcwd()
    sys.path.insert(0, os.path.join(cwd, "src"))
    sys.path.insert(0, os.path.join(cwd, "lib"))

from misc import grid_str_to_grid
import generate as gen
import generate_x as genx

NTESTS = 10
Ntimeits = 1
Cols = 2

sG = "1.......2.9.4...5...6...7...5.9.3.......7.......85..4.7.....6...3...9.8...2.....1"
# This puzzle requires just under 720K recursion steps to check. This is a very large amount
# and therefore a good test

G = [[0 for c in range(9)] for r in range(9)]
grid_str_to_grid(sG, G)

b = [[0.0 for j in range(Cols)] for i in range(NTESTS)]
Min = [0.0] * Cols
Avg = [0.0] * Cols
print("Col 1: check_puzzle() from generate.py - interpreted")
print("Col 2: check_puzzle() from generate_x.pyx - compiled")
print(f"timeit()'s number: {Ntimeits}")
print("Runs, Col 1,     Col 2")
for i in range(NTESTS):
    b[i][0] = timeit(lambda: gen.check_puzzle(G), number = Ntimeits)
    b[i][1] = timeit(lambda: genx.check_puzzle(G), number = Ntimeits)
    print(f"{i+1: 4d}, {b[i][0]:9.7f}, {b[i][1]:9.7f}")  # , {b[i][2]:9.7f}")
for j in range(Cols):
    A = 0.0
    M = 999999.0
    for i in range(NTESTS):
        A += b[i][j]
        M = min(M, b[i][j])
    Avg[j] = A/NTESTS
    Min[j] = M

print(f" Avg, {Avg[0]:9.7f}, {Avg[1]:9.7f}")
print(f" Min, {Min[0]:9.7f}, {Min[1]:9.7f}")
print(f" Imp,            {(Min[0]/Min[1]): 8.2f}x")
