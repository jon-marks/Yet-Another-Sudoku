#!/usr/bin/env python
from os.path import dirname, join
from sys import argv, path, modules
from timeit import timeit

NTESTS = 10
Ntimeits = 1
#  Create the parameters to benchmark, same puzzle and shuffled deque for repeatability.
sG = "573964182418532769296781534367129845152478693984356271825643917731895426649217358"
H = [50, 46, 0, 57, 25, 24, 41, 30, 45, 80, 13, 3, 77, 44, 23, 68, 67, 78, 54, 37, 76, 55, 38, 56, 28, 43, 64, 10, 27, 42, 31, 61, 58, 14, 49, 29, 8, 17, 21, 12, 53, 16, 20, 71, 51, 73, 72, 52, 1, 74, 65, 18, 79, 39, 9, 6, 62, 2, 63, 33, 19, 70, 66, 34, 11, 22, 4, 36, 59, 75, 47, 35, 60, 5, 48, 69, 7, 32, 15, 26, 40]

spinner = ["|", "/", "-", "\\"]
Root = dirname(dirname(argv[0]))
path.insert(0, join(Root, "trc"))
path.insert(0, join(Root, "src"))

from globals import *
from misc import grid_str_to_grid
from generate import create_puzzle

# prep params for create_puzzle.
G = [[0 for c in range(9)] for r in range(9)]
grid_str_to_grid(sG, G)
Pzl = PZL(Sym = 0)

print(f"Benchmark create_puzzle(), best of {NTESTS}, Ntimeits: {Ntimeits}")
print(f"Interpreted code: {spinner[3]}", end="", flush = True)
Times = []; M0 = 99999.0
for i in range(NTESTS):
    Times.append(timeit(lambda: create_puzzle(Pzl, H, G), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    M0 = min(M0, Times[-1])
M0T = M0 * 1000.0; M0E = M0T / Ntimeits
print(f"\bT:{M0T:9.4f} ms, Ea:{M0E:9.4f} ms")

# unload src modules so that lib modules load.
modules.pop('generate')
modules.pop('solve_utils')  # loaded by generate

path.insert(0, join(Root, "lib"))
from generate import create_puzzle
print(f"Compiled Code:    {spinner[3]}", end ="", flush = True)
Times = []; M1 = 99999.0
for i in range(NTESTS):
    Times.append(timeit(lambda: create_puzzle(Pzl, H, G), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    M1 = min(M1, Times[-1])
M1T = M1 * 1000.0; M1E = M1T / Ntimeits
print(f"\bT:{M1T:9.4f} ms, Ea:{M1E:9.4f} ms")
print(f"Improvement:      {(M0/M1):9.7f} times ")
