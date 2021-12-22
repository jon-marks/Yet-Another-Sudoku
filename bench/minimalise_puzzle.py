#!/usr/bin/env python

# For this benchmark test, the first interpreted test is always under 2 seconds and following tests
# are always # greater than 4 seconds.  I suspect this is because of garbage collecting or other
# under the hood magic that Python may be doing.  Nevertheless as it is a consistent outlier, it is
# fair to exclude it from the test results.
from os.path import dirname, join
from sys import argv, path, modules
from timeit import timeit
from copy import deepcopy

NTESTS = 5
Ntimeits = 1
sG = ".5267.3.8.3...562767..325.128...61.5.6....2.4714523869827314956.9.267483346958712"

# T_H's suffix is the avg time to mimimalise this puzzle digging the remaining holes sorted as folls.'
T_H5   = [(8, 7), (6, 4), (5, 0), (3, 0), (7, 6), (5, 7), (0, 6), (6, 2), (2, 6), (7, 8), (0, 1), (3, 5), (1, 1), (8, 4), (6, 1), (3, 1), (2, 8), (6, 5), (7, 7), (5, 4), (8, 5), (8, 6), (6, 0), (4, 6), (5, 5), (8, 3), (0, 8), (0, 3), (7, 5), (1, 5), (0, 2), (6, 3), (0, 4), (7, 3), (6, 8), (2, 1), (2, 5), (6, 6), (5, 6), (8, 2), (8, 8), (4, 1), (8, 0), (2, 0), (2, 4), (1, 6), (3, 6), (5, 8), (8, 1), (7, 4), (5, 3), (1, 7), (5, 2), (7, 1), (6, 7), (5, 1), (3, 8), (1, 8), (4, 8)]
T_H18  = [(0, 6), (7, 5), (8, 8), (8, 6), (1, 6), (6, 2), (2, 4), (4, 8), (2, 8), (2, 0), (7, 6), (5, 4), (6, 4), (8, 1), (5, 5), (7, 1), (5, 0), (5, 7), (5, 8), (0, 1), (0, 3), (6, 1), (3, 5), (7, 4), (8, 3), (3, 1), (5, 1), (8, 5), (7, 8), (8, 2), (6, 0), (1, 7), (1, 1), (0, 4), (5, 2), (8, 4), (1, 8), (4, 6), (2, 5), (7, 7), (3, 0), (0, 2), (2, 6), (2, 1), (3, 8), (6, 6), (6, 3), (8, 7), (1, 5), (6, 5), (3, 6), (0, 8), (4, 1), (8, 0), (7, 3), (6, 7), (6, 8), (5, 6), (5, 3)]
T_H45  = [(5, 2), (8, 0), (6, 8), (3, 0), (2, 6), (8, 3), (5, 1), (0, 6), (5, 8), (2, 4), (0, 1), (7, 4), (1, 8), (3, 5), (0, 8), (5, 7), (7, 7), (2, 0), (2, 5), (5, 3), (8, 1), (7, 3), (2, 8), (6, 2), (6, 0), (4, 6), (8, 2), (5, 0), (7, 5), (7, 1), (8, 4), (7, 6), (3, 1), (6, 3), (3, 8), (8, 7), (8, 6), (1, 5), (5, 6), (8, 8), (2, 1), (4, 1), (6, 7), (6, 1), (8, 5), (3, 6), (6, 6), (1, 6), (6, 5), (6, 4), (0, 3), (0, 2), (1, 7), (7, 8), (5, 5), (1, 1), (0, 4), (5, 4), (4, 8)]
T_H115 = [(2, 1), (5, 8), (5, 4), (6, 2), (7, 3), (6, 8), (7, 6), (0, 8), (1, 5), (8, 0), (8, 5), (8, 7), (4, 6), (5, 2), (5, 3), (8, 8), (0, 1), (0, 2), (6, 7), (6, 4), (2, 5), (2, 6), (8, 1), (7, 5), (3, 6), (6, 1), (1, 8), (7, 4), (2, 0), (0, 4), (3, 0), (8, 6), (3, 8), (0, 6), (6, 6), (7, 8), (1, 7), (6, 0), (8, 3), (6, 5), (1, 1), (7, 1), (3, 1), (1, 6), (8, 2), (2, 4), (6, 3), (4, 1), (5, 5), (3, 5), (5, 0), (5, 6), (5, 7), (2, 8), (0, 3), (5, 1), (7, 7), (4, 8), (8, 4)]
T_H540 = [(2, 6), (8, 7), (8, 4), (2, 0), (3, 8), (3, 5), (3, 6), (5, 7), (6, 2), (5, 5), (7, 8), (4, 6), (4, 8), (5, 2), (8, 3), (0, 6), (6, 5), (5, 1), (2, 4), (5, 4), (8, 6), (7, 6), (6, 1), (0, 4), (1, 8), (7, 5), (1, 7), (1, 6), (6, 4), (7, 3), (8, 2), (8, 8), (2, 1), (3, 1), (4, 1), (7, 4), (1, 1), (5, 3), (6, 7), (6, 3), (5, 8), (8, 1), (2, 8), (0, 1), (0, 3), (6, 8), (8, 0), (1, 5), (0, 2), (6, 6), (3, 0), (5, 0), (8, 5), (6, 0), (2, 5), (7, 7), (5, 6), (7, 1), (0, 8)]
T_H = T_H5
spinner = ["|", "/", "-", "\\"]
Root = dirname(dirname(argv[0]))
path.insert(0, join(Root, "src"))

from globals import *
from misc import grid_str_to_grid
from generate import minimalise_puzzle

# prep params for create_puzzle.
G = [[0 for c in range(9)] for r in range(9)]
grid_str_to_grid(sG, G)

print(f"Benchmark minimalise_puzzle(), best of {NTESTS}, Ntimeits: {Ntimeits}")
print(f"Interpreted code: {spinner[3]}", end="", flush = True)
Times = []; M0 = 9999999.0
for i in range(NTESTS+1):
    Times.append(timeit(lambda: minimalise_puzzle(G, T_H), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    if i: M0 = min(M0, Times[-1])
M0T = M0 * 1000.0; M0E = M0T / Ntimeits
print(f"\bT:{M0T:11.4f} ms, Ea:{M0E:11.4f} ms")

# unload src modules so that lib modules load.
modules.pop('generate')
modules.pop('solve_utils')  # loaded by generate

path.insert(0, join(Root, "lib"))
from generate import minimalise_puzzle
print(f"Compiled Code:    {spinner[3]}", end ="", flush = True)
Times = []; M1 = 9999999.0
for i in range(NTESTS):
    Times.append(timeit(lambda: minimalise_puzzle(G, T_H), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    M1 = min(M1, Times[-1])
M1T = M1 * 1000.0; M1E = M1T / Ntimeits
print(f"\bT:{M1T:11.4f} ms, Ea:{M1E:11.4f} ms")
print(f"Improvement:      {(M0/M1):9.7f} times ")
