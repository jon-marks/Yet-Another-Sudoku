#!/usr/bin/env python

import os, shutil, sys
from timeit import timeit


from globals import *
from misc import grid_str_to_grid
import generate as gen
import generate_x as genx

NTESTS = 10
Ntimeits = 1
Cols = 2

#  Create the parameters to benchmark, same puzzle and shuffled deque for repeatability.
sG = "573964182418532769296781534367129845152478693984356271825643917731895426649217358"
H = [50, 46, 0, 57, 25, 24, 41, 30, 45, 80, 13, 3, 77, 44, 23, 68, 67, 78, 54, 37, 76, 55, 38, 56, 28, 43, 64, 10, 27, 42, 31, 61, 58, 14, 49, 29, 8, 17, 21, 12, 53, 16, 20, 71, 51, 73, 72, 52, 1, 74, 65, 18, 79, 39, 9, 6, 62, 2, 63, 33, 19, 70, 66, 34, 11, 22, 4, 36, 59, 75, 47, 35, 60, 5, 48, 69, 7, 32, 15, 26, 40]
G = [[0 for c in range(9)] for r in range(9)]
grid_str_to_grid(sG, G)
Pzl = PZL(Sym = 0)

b = [[0.0 for j in range(Cols)] for i in range(NTESTS)]
Min = [0.0] * Cols
Avg = [0.0] * Cols
print("Col 1: create_puzzle() from generate.py - interpreted")
print("Col 2: create_puzzle() from generate.pyx - compiled")
print(f"timeit()'s number: {Ntimeits}")
print("Runs, Col 1,     Col 2")
for i in range(NTESTS):
    b[i][0] = timeit(lambda: gen.create_puzzle(Pzl, H, G), number = Ntimeits)
    b[i][1] = timeit(lambda: genx.create_puzzle(Pzl, H, G), number = Ntimeits)
    print(f"{i+1: 4d}, {b[i][0]:9.7f}, {b[i][1]:9.7f}")
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
