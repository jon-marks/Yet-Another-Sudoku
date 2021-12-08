#!/usr/bin/env python

import os, shutil, sys
from timeit import timeit

if not os.getenv("PYCHARM_HOSTED"):
    cwd = os.getcwd()
    sys.path.insert(0, os.path.join(cwd, "src"))
    sys.path.insert(0, os.path.join(cwd, "lib"))

NTESTS = 10
Ntimeits = 500
Cols = 3

b = [[0.0 for j in range(Cols)] for i in range(NTESTS)]
Min = [0.0] * Cols
Avg = [0.0] * Cols
print("Col 1: gen_filled_grid() from generate.py - interpreted")
print("Col 2: gen_filled_grid() from generate_x.pyx - compiled")
print(f"timeit()'s number: {Ntimeits}")
print("Runs, Col 1,     Col 2")  # ,      Col 3")
for i in range(NTESTS):
    b[i][0] = timeit(f"gen_filled_grid()", f"from generate import gen_filled_grid", number = Ntimeits)
    b[i][1] = timeit(f"gen_filled_grid()", f"from generate_x import gen_filled_grid", number = Ntimeits)
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

    
