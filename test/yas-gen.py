#!/usr/bin/env python
from os.path import dirname, join
from os import chdir
from sys import argv, exit, path
from datetime import datetime
from time import perf_counter
from random import shuffle, randrange, seed

SrcDir   = "src"
TestDir  = "test"
TestDDir = "test-data"
SrcFile  = "pattern-reg-test-1.0"
DstFile  = "patterns"
FileExt  = ".txt"
DbExt    = ".sql"
Root = dirname(dirname(argv[0]))
chdir(Root)
path.insert(0, f"{join(Root, SrcDir)}")

from globals import *

from generate import *
from misc import *
from solve import *
from solve_utils import *

# Operating Modes
M_NONE     = 0x00
M_GEN      = 0x01
M_DIG      = 0x02
M_SHUFFLE  = 0x04
M_FILE     = 0x08

ROW = 0
COL = 1
TWR = 2
FLR = 3
DGT = 4
XPS = 5

Keys = ['r', 'c', 't', 'f', 'd', 'x']
NONE = 0
RAND = 1

seed()

def yas_gen():

    print(f"YAS - Puzzle Generator / Modifier.")
    print(VERSION)
    print(f"\nRun start: {datetime.now()}.", flush = True)  # , using {Code} code.", flush = True))
    TestDataDir = join(join(Root, TestDir), TestDDir)
    Src  = join(TestDataDir, SrcFile+FileExt)
    Dst  = join(TestDataDir, DstFile+FileExt)
    Db   = join(TestDataDir, SrcFile+DbExt)

    Mode = M_NONE
    Begin = 0; End = 999999
    nPzls = 1
    sShuffleSpec = ""
    sPPzl = ""

    for i in range(1, len(argv)):
        if argv[i][:2] in ["i=", "I="]:
            Mode |= M_FILE
            if argv[i][2:]: Src = argv[i][2:]
        elif argv[i][:2] in ["o=", "O="]:
            Mode |= M_FILE
            if argv[i][2:]: Dst = argv[i][2:]
        elif argv[i][:2] in ["b=", "B="]: Begin = int(argv[i][2:])
        elif argv[i][:2] in ["e=", "E="]: End = int(argv[i][2:])
        elif argv[i][:2] in ["s=", "S="]: sSoln = argv[i][2:]; Mode |= M_DIG
        elif argv[i][:2] in ["p=", "P="]: sPPzl = argv[i][2:]; Mode |= M_SHUFFLE
        elif argv[i][:2] in ["m=", "M="]: sMPzl = argv[i][2:]; Mode |= M_DIG
        elif argv[i][:2] in ["n=", "N="]: nPzls= int(argv[i][2:]); Mode |= M_GEN
        elif argv[i][:2] in ["j=", "J="]: sShuffleSpec = argv[i][2:]
        elif argv[i][:2] in ["d=", "D="]: Db = argv[i][2:]
        elif argv[i][:2] in ["a=", "A="]: Add = argV[i][2:]
        else:
            print(f"Syntax: yas-sol.py [i=<input file path>] [o=<output file path>] [s=<n>] [e=<m>]\n"
                  f"  i=<path>:  (optional) input file path,\n"
                  f"             default: {Src}\n"
                  f"  o=<path>:  (optional) output file path,\n"
                  f"             default: {Dst}\n"
                  f"  b=<n>:     (optional) start from file line number, default: {Begin}\n"
                  f"  e=<m>:     (optional) stop after line number, default: {End}.\n"
                  f"  s=<Pzl Spec>:  Randomly dig holes in file spec until minimal puzzle is found.\n"
                  f"                 Only the grid is considered in the puzzle spec string, Givens are\n"
                  f"                 not preserved.\n"
                  f"                 Up to 'n' puzzles will be generated per spec if 'n=' is specified.\n"
                  f"                 if <Pzl Spec> is empty, then specs are taken from <input file path>"
                  f"  m=<Pzl Spec>:  Synonym for s= switch.\n"
                  f"  p=<Pzl Spec>:  Puzzles created by shuffling the puzzle string. The 'j' switch is used to control\n"
                  f"                 the shuffling.  If j is not specified then all shuffing steps are applied randomly.\n"
                  f"                 Up to 'n' puzzles will be generated per spec if 'n=' is specified.\n"
                  f"                 Givens will be preserved as shuffled.\n"
                  f"                 If <Pzl Spec> is empty, then specs are taken from <input file path>"
                  f"             if p= and s= are both specified with a <Pzl Spec> then the latter spec is used\n"
                  f"  n=<n>:     (optional) up to number of puzzles to generate from each input puzzle spec.\n"
                  f"             default: {nPzls}\n"
                  f"             If no other option is supplied will generate minimal puzzles from scratch.\n"
                  f"  j=. . .    Controls jumbles/scrambles puzzle provided by p switch n times.\n"
                  f"             If nothing is specified after 'j=' then random shuffling is ignored\n"
                  f"             Semicolon separated strings starting with:\n"
                  f"                r:  shuffle rows in floors\n"
                  f"                f:  shuffle floors\n"
                  f"                c:  shuffle columns in towers\n"
                  f"                t:  shuffle towers\n"
                  f"                d:  shuffle digits\n"
                  f"                x:  Transpose cells\n"
                  f"                s:  Transform Spatial Domains - To be implemented\n"
                  f"             The semicolon separated strings must be in the listed order if present\n"
                  f"             for all of r, f, c, t, d, they can be post fixed with [R|N,<n><m>[,<o><p>,..] where:\n"
                  f"                if nothing specified, shuffle randomly\n"
                  f"                R: shuffle randomly exceot for . . .\n"
                  f"                N: no shuffling except for . . .\n"
                  f"                <m><n>,... exchanging the those rows, cols, floors, towers or digits\n"
                  f"             for x, the post-fixed digit 0..8 specifies\n"
                  f"                 0:   No transposition\n"
                  f"                 1:   G[r][8-c]\n"
                  f"                 2:   G[8-r][c]\n"
                  f"                 3:   G[8-r][8-c]\n"
                  f"                 4:   G[c][r]\n"
                  f"                 5:   G[c][8-r]\n"
                  f"                 6:   G[8-c][r]\n"
                  f"                 7:   G[8-c][8-r]\n"
                  f"                 8:   Randomly choose transposition"
                  f"             for s, the post-fixed digit 0..5 specifies: To be implemented\n"
                  f"                 0:   No transformation\n"
                  f"                 1:   G[r][c] = v  --> G[v][c] = r\n"
                  f"                 2:   G[r][c] = v  --> G[v][r] = c\n"
                  f"                 3:   G[r][c] = v  --> G[b][d] = v\n"
                  f"                 4:   G[r][c] = v  --> G[v][b] = d\n"
                  f"                 5:   G[r][c] = v  --> G[v][d] = b\n"
                  f"                Where: r: row, c: col, v: val, b: box, d: cell in box\n"
                  f" d=<path>:  (optional) Path to solution database. Will not be genenerated if d= is not specified.\n"
                  f"            To be implemented "
                  f"            default: {Db}\n"
                  f"  a=<[e|d]>: (optional) additional fields - e: expertise level, d: difficulty\n"
                  f"Note:  The s= switch does not produce repeatable results as there can be multiple minimal puzzles\n"
                  f"from any non minimal puzzle, and the remaining holes to dig are selected randomly.")
            exit()

    if Mode & M_FILE: # I/O to and from files.
        print("File I/O Mode")
        with open(Src, "rt") as f:
            with open(Dst, "wt") as f1:
                nPzl = nLine = nDups = Errs = 0
                lPzls = []
                while 1:
                    StTime = perf_counter()
                    Line = f.readline()
                    if not Line: break
                    nLine += 1
                    if not Begin <= nLine <= End: continue
                    # if Line[:3] == "## ": print(f"\n{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| {Line[:-1]}", flush = True)
                    if Line == "\n" or Line[0] == "#":
                        # f1.write(Line); f1.flush()
                        continue
                    TD = Line.rstrip(" \n").split("|")
                    lenTD = len(TD)
                    oPzl = PZL()
                    if lenTD == 1: NrFlds, sErr = pzl_str_to_pzl(TD[0], oPzl)
                    else: NrFlds, sErr = pzl_str_to_pzl(TD[0] + "|" + TD[1], oPzl)
                    if not NrFlds:
                        f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                        print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {sErr}", flush = True)
                        Errs += 1
                        continue
                    if Mode & M_DIG:
                        nFound, oPzl.Soln = check_puzzle(oPzl.Givens)
                        if nFound == 1: # only one solution
                            for nn in range(nPzls):
                                mPzl = grid_to_grid_str(minimalise_puzzle(oPzl.Givens))
                                if mPzl and mPzl in lPzls: nDups += 1; continue
                                lPzls.append(mPzl)
                                nPzl += 1
                                f1.write(mPzl+"\n"); f1.flush()
                                print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}|{mPzl}", flush = True)
                        else:
                            sErr = f"Givens yield {nFound} Solutions"
                            f1.write(f"# Error: {sErr}: {Line}"); f1.flush()
                            print(f"{time_str(StTime)}| Line: {nLine}| Puzzle: {nPzl}| Error: {sErr}", flush = True)
                    else: print("Generating and Shuffling using file I/O not yet supported", flush = True)
        print(f"{time_str()}| End Run| Lines: {nLine}| Puzzles: {nPzl}, Duplicates: {nDups}, Errors: {Errs}.")
    else:  # console entry
        if Mode & M_SHUFFLE:
            ShuffleSpec = parse_shuffle_spec(sShuffleSpec)
            oPzl = PZL()
            NrFlds, Err = pzl_str_to_pzl(sPPzl, oPzl)
            if not NrFlds: print(f"Error: {Err}"); exit()

            Rows = [[r+(f*3) for r in range(3)] for f in range(3)]
            Cols = [[c+(t*3) for c in range(3)] for t in range(3)]
            Digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            Xps = 8
            for Key, Val in ShuffleSpec.items():
                if Key == ROW:
                    R1 = [(), (), ()]
                    for r0, r1 in Val[1:]:
                        rf0 = r0//3; rf1 = r1//3
                        if rf0 != rf1: print("Rows to shuffle can't be on different floors"); exit()
                        R1[rf0] = (r0, r1)
                    for i, RX in enumerate(R1):
                        if RX: r0, r1 = RX; Rows[i][r0%3] = r1; Rows[i][r1%3] = r0
                        elif not Val or Val[0] == RAND: shuffle(Rows[i])
                elif Key == FLR:
                        if len(Val) >= 2:
                            f0, f1 = Val[1]
                            Fx = Rows[f0]; Rows[f0] = Rows[f1]; Rows[f1] = Fx
                        elif not Val or Val[0] == RAND: shuffle(Rows)
                elif Key == COL:
                    C1 = [(), (), ()]
                    for c0, c1 in Val[1:]:
                        ct0 = c0//3; ct1 = c1//3
                        if ct0 != ct1: print("Columns to shuffle can't be in different towers"); exit()
                        C1[ct0] = (c0, c1)
                    for i, CX in enumerate(C1):
                        if CX: c0, c1 = CX; Cols[i][c0%3] = c1; Cols[i][c1%3] = c0
                        elif not Val or Val[0] == RAND: shuffle(Cols[i])
                elif Key == TWR:
                    if len(Val) >= 2:
                        t0, t1 = Val[1]
                        Tx = Cols[t0]; Cols[t0] = Cols[t1]; Cols[t1] = Tx
                    elif not Val or Val[0] == RAND: shuffle(Cols)
                elif Key == DGT:
                    Val1 = []
                    for d0, d1 in Val[1:]:
                        if d0 > d1: Val1.append((d0, d1))
                        else: Val1.append((d1, d0))
                    Val1 = sorted(Val1, reverse = True)
                    lenVal1 = len(Val1)
                    if lenVal1:
                        l = 9; j = 0
                        while l:
                            d0, d1 = Val1[j]
                            if l == d0:
                                rr = d1-1
                                j += 1
                                if j < lenVal1: d0, d1 = Val1[j]
                            elif Val[0] == RAND: rr = randrange(l)
                            else: rr = l-1
                            l -= 1
                            t = Digits[l]; Digits[l] = Digits[rr]; Digits[rr] = t
                    elif Val[0]: shuffle(Digits)
                elif Key == XPS:
                    Xps = Val

            # shuffle rows
            Grid = []; Givens = []
            for r0 in range(9):
                rf = r0//3; rb = r0%3
                Grid.append(oPzl.Grid[Rows[rf][rb]]); Givens.append(oPzl.Givens[Rows[rf][rb]])

            # shuffle cols by Transposing grid and shuffling transposed rows
            Grid1 =  [[Grid[c][r] for c in range(9)] for r in range(9)]
            Givens1 = [[Givens[c][r] for c in range(9)] for r in range(9)]
            Grid = []; Givens = []
            for c0 in range(9):
                ct = c0//3; cb = c0%3
                Grid.append(Grid1[Cols[ct][cb]]); Givens.append(Givens1[Cols[ct][cb]])

            # shuffle digits and transpose in one step, accommodating the already r/c transposition.
            Digits.insert(0, 0)
            if Xps == 8: Xps = randrange(8)
            if Xps == 0:
                oPzl = PZL(Grid = [[Digits[Grid[c][r]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens[c][r]] for c in range(9)] for r in range(9)])
            elif Xps == 1:  # G[r][8-c]
                oPzl = PZL(Grid = [[Digits[Grid[c][8-r]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens[c][8-r]] for c in range(9)] for r in range(9)])
            elif Xps == 2:  # G[8-r][c]
                oPzl = PZL(Grid = [[Digits[Grid[8-c][r]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens[8-c][r]] for c in range(9)] for r in range(9)])
            elif Xps == 3:  # G[8-r][8-c]
                oPzl = PZL(Grid = [[Digits[Grid[8-c][8-r]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens1[8-c][8-r]] for c in range(9)] for r in range(9)])
            elif Xps == 4:  # G[c][r]
                oPzl = PZL(Grid = Grid, Givens = Givens)
            elif Xps == 5:  # G[c][8-r]
                oPzl = PZL(Grid = [[Digits[Grid[r][8-c]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens[r][8-c]] for c in range(9)] for r in range(9)])
            elif Xps == 6:  # G[8-c][r]
                oPzl = PZL(Grid = [[Digits[Grid[8-r][c]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens[8-r][c]] for c in range(9)] for r in range(9)])
            elif Xps == 7:  # G[8-c][8-r]
                oPzl = PZL(Grid = [[Digits[Grid1[8-r][8-c]] for c in range(9)] for r in range(9)],
                           Givens = [[Digits[Givens1[8-r][8-c]] for c in range(9)] for r in range(9)])
            print(pzl_to_pzl_str(oPzl))
        else: print("Digging and minimizing in Console mode not yet supported")

def time_str(STime = 0):

    ETime = perf_counter()
    DTime = ETime - STime
    ESecs = ETime % 60; EMins = int((ETime//60)%60); EHrs = int(ETime//3600)
    DSecs = DTime % 60; DMins = int((DTime//60)%60); DHrs = int(DTime//3600)
    return f"{EHrs:02d}:{EMins:02d}:{ESecs:07.4f}|{DHrs:02d}:{DMins:02d}:{DSecs:07.4f}"

def parse_shuffle_spec(sShuffleSpec):
    # empty value list implies random shuffle.
    oShuffleSpec = {ROW: [], COL: [], TWR: [], FLR: [], DGT: [], XPS: []}
    lShuffleSpec = sShuffleSpec.replace(" ", "").split(";")
    for SSpec in lShuffleSpec:
        if SSpec[0] in {'r', 'c', 't', 'f', 'd'}:
            Key, Val = parse_sub_spec(SSpec)
            if Key == -1: print(f"Shuffle Spec fragment '{SSpec} not recognised"); exit()
            oShuffleSpec[Key] = Val
        elif SSpec [0] == 'x':
            if len(SSpec) > 1 and SSpec[1] in {'0', '1', '2', '3', '4', '5', '6', '7', '8'}:
                oShuffleSpec[XPS] = int(SSpec[1])
        else:
            print(f"Shuffle Spec fragment '{SSpec} not recognised"); exit()
    return oShuffleSpec

def parse_sub_spec(SSpec):

    Key = Keys.index(SSpec[0])
    SubSpec = []
    lSSpec = SSpec[1:].split(",")
    if lSSpec:
        if lSSpec[0] == 'R': SubSpec.append(RAND)
        else: SubSpec.append(NONE)
        for SSS in lSSpec[1:]:
            if len(SSS) != 2: return -1, []
            SubSpec.append((int(SSS[0])-1, int(SSS[1])-1))
    return Key, SubSpec


if __name__ == "__main__":
    yas_gen()