#!/usr/bin/env python
from os.path import dirname, join
from sys import argv, path, modules
from timeit import timeit

NTESTS = 10
Ntimeits = 500

spinner = ["|", "/", "-", "\\"]
Root = dirname(dirname(argv[0]))
path.insert(0, join(Root, "trc"))
path.insert(0, join(Root, "src"))

from globals import *
from generate import gen_filled_grid

print(f"Benchmark create_puzzle(), best of {NTESTS}, Ntimeits: {Ntimeits}")
print(f"Interpreted code: {spinner[3]}", end="", flush = True)
Times = []; M0 = 99999.0
for i in range(NTESTS):
    Times.append(timeit(lambda: gen_filled_grid(), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    M0 = min(M0, Times[-1])
M0T = M0 * 1000.0; M0E = M0T / Ntimeits
print(f"\bT:{M0T:9.4f} ms, Ea:{M0E:9.4f} ms")

# unload src modules so that lib modules load.
modules.pop('generate')
modules.pop('solve_utils')  # loaded by generate

path.insert(0, join(Root, "lib"))
from generate import gen_filled_grid
print(f"Compiled Code:    {spinner[3]}", end ="", flush = True)
Times = []; M1 = 99999.0
for i in range(NTESTS):
    Times.append(timeit(lambda: gen_filled_grid(), number = Ntimeits))
    print(f"\b{spinner[i%4]}", end = "", flush = True)
    M1 = min(M1, Times[-1])
M1T = M1 * 1000.0; M1E = M1T / Ntimeits
print(f"\bT:{M1T:9.4f} ms, Ea:{M1E:9.4f} ms")
print(f"Improvement:    {(M0/M1):9.4f} times ")

