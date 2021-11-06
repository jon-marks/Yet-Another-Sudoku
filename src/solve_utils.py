
#  Collection of common enums, structures, classes, and functions used in the solving
#  of puzzles.

#  Note many of the functions operate optimally and seamlessly on group linked ccells
#  and scalar ccells.  This is achieved by using a the flag GrpLks to indicate when
#  pattern searches using group links is required and and passing all (r, c) parameters as
#  sets.  That is when GrpLKS is set, r and c are set objects, when GrpLks is False,
#  r and c are scalars.
#

from copy import copy
from globals import *

# Link strength enumerations.
# LK_ERR  = 0x1000
LK_NONE = 0x0000   # must be 0, code relies on this.
LK_WEAK = 0x0001
LK_STRG = 0x0002
LK_STWK = 0x0003   # a strong link is also a weak link.
LK_WKST = 0x0007   # strong link masquerading as a weak link

# Link orientation enumerations
LK_ROW  = 0x0010
LK_COL  = 0x0020
LK_BOX  = 0x0040
LK_CELL = 0x0080
# LK_ANY_depreciated  = 0x0070

# T enumerations
T_TXT  = 0  # Textual description
T_LVL  = 1  # Expertise level of technique
T_DIFF = 2  # Difficulty of technique

# The use of weak or strong ended AIC's to search for patterns where ccell's see
# each other, for example in covers seeing fins in finned fish or W wings, etc,
# adds the dimension of incremental difficulty in finding and solving a pattern
# based on the number of links in the chains used to solve a step.
KRAKEN_LK_DIFF = 20  # per Kraken link
GRP_LK_DIFF    = 50  # per group link


T = {T_EXPOSED_SINGLE:              ["Exposed Single", LVL_BEGINNER, 5],
     T_HIDDEN_SINGLE:               ["Hidden Single", LVL_BEGINNER, 10],
     T_CLAIMING_LOCKED_SINGLE:      ["Claiming Locked Single", LVL_NOVICE, 15],
     T_POINTING_LOCKED_SINGLE:      ["Pointing Locked Single", LVL_NOVICE, 15],
     T_EXPOSED_PAIR:                ["Exposed Pair", LVL_INTERMEDIATE, 15],
     T_LOCKED_EXPOSED_PAIR:         ["Locked Exposed Pair", LVL_INTERMEDIATE, 20],
     T_HIDDEN_PAIR:                 ["Hidden Pair", LVL_INTERMEDIATE, 20],
     T_EXPOSED_TRIPLE:              ["Exposed Triple", LVL_INTERMEDIATE, 20],
     T_LOCKED_EXPOSED_TRIPLE:       ["Locked Exposed Triple", LVL_INTERMEDIATE, 25],
     T_HIDDEN_TRIPLE:               ["Hidden Triple", LVL_INTERMEDIATE, 30],
     T_EXPOSED_QUAD:                ["Exposed Quad", LVL_INTERMEDIATE, 35],
     T_HIDDEN_QUAD:                 ["Hidden Quad", LVL_INTERMEDIATE, 40],
     T_X_WING:                      ["X-Wing", LVL_PROFICIENT, 45],
     T_SWORDFISH:                   ["Swordfish", LVL_PROFICIENT, 50],
     T_JELLYFISH:                   ["Jellyfish", LVL_PROFICIENT, 55],
     T_FINNED_X_WING:               ["Finned X-Wing", LVL_PROFICIENT, 60],
     T_FINNED_SWORDFISH:            ["Finned Swordfish", LVL_PROFICIENT, 65],
     T_FINNED_JELLYFISH:            ["Finned Jellyfish", LVL_PROFICIENT, 70],
     T_SKYSCRAPER:                  ["Skyscraper", LVL_PROFICIENT, 45],
     T_TWO_STRING_KITE:             ["Two String Kite", LVL_PROFICIENT, 45],
     T_TURBOT_FISH:                 ["Turbot Fish", LVL_PROFICIENT, 50],
     T_EMPTY_RECT:                  ["Empty Rectangle", LVL_PROFICIENT, 45],
     T_Y_WING:                      ["Y-Wing", LVL_INTERMEDIATE, 50],
     T_W_WING:                      ["W-Wing", LVL_PROFICIENT, 55],
     T_XYZ_WING:                    ["XYZ-Wing", LVL_PROFICIENT, 60],
     T_WXYZ_WING:                   ["WXYZ-Wing", LVL_ACCOMPLISHED, 100],
     T_BENT_EXPOSED_QUAD:           ["Bent Exposed Quad", LVL_ACCOMPLISHED, 110],
     T_X_CHAIN:                     ["X-Chain", LVL_PROFICIENT, 70],
     T_EVEN_X_LOOP:                 ["Even X-Loop", LVL_PROFICIENT, 70],
     T_STRONG_X_LOOP:               ["Strong X-Loop", LVL_PROFICIENT, 70],
     T_REMOTE_PAIR:                 ["Remote Pair", LVL_ACCOMPLISHED, 80],
     T_XY_CHAIN:                    ["XY-Chain", LVL_ACCOMPLISHED, 80],
     T_XY_LOOP:                     ["XY-Loop", LVL_ACCOMPLISHED, 80],
     T_SC_AI_CHAIN:                 ["Same End Candidate AI-Chain", LVL_PROFICIENT, 70],
     T_DC_AI_CHAIN:                 ["Different End Candidate AI-Chain", LVL_ACCOMPLISHED, 80],
     T_EVEN_AI_LOOP:                ["Even AI-Loop", LVL_ACCOMPLISHED, 80],
     T_STRONG_AI_LOOP:              ["Strong AI-Loop", LVL_ACCOMPLISHED, 80],
     T_KRAKEN_X_WING:               ["Kraken Finned X-Wing", LVL_ACCOMPLISHED, 100],
     T_KRAKEN_SWORDFISH:            ["Kraken Finned Swordfish", LVL_ACCOMPLISHED, 100],
     T_KRAKEN_JELLYFISH:            ["Kraken Finned Jellyfish", LVL_ACCOMPLISHED, 100],
     T_KRAKEN_W_WING:               ["Kraken W-Wing", LVL_PROFICIENT, 95],
     T_GL_W_WING:                   ["Group Linked W-Wing", LVL_PROFICIENT, 45],
     T_GL_SKYSCRAPER:               ["Group Linked Skyscraper", LVL_PROFICIENT, 45],
     T_GL_TWO_STRING_KITE:          ["Group Linked Two String Kite", LVL_PROFICIENT, 45],
     T_GL_TURBOT_FISH:              ["Group Linked Turbot Fish", LVL_PROFICIENT, 50],
     T_GL_X_CHAIN:                  ["Group Linked X-Chain", LVL_PROFICIENT, 70],
     T_GL_EVEN_X_LOOP:              ["Group Linked Even X-Loop", LVL_PROFICIENT, 70],
     T_GL_STRONG_X_LOOP:            ["Group Linked Strong X-Loop", LVL_PROFICIENT, 70],
     T_GL_XY_CHAIN:                 ["Group Linked XY-Chain", LVL_PROFICIENT, 70],
     T_GL_SC_AI_CHAIN:              ["Group Linked Same End Candidates AI-Chain", LVL_PROFICIENT, 70],
     T_GL_DC_AI_CHAIN:              ["Group Linked Different End Candidates AI-Chain", LVL_ACCOMPLISHED, 80],
     T_GL_EVEN_AI_LOOP:             ["Group Linked Even AI-Loop", LVL_ACCOMPLISHED, 80],
     T_GL_STRONG_AI_LOOP:           ["Group Linked Strong AI-Loop", LVL_ACCOMPLISHED, 80],
     T_GL_KRAKEN_X_WING:            ["Group Linked Kraken Finned X-Wing", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_SWORDFISH:         ["Group Linked Kraken Finned Swordfish", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_JELLYFISH:         ["Group Linked Kraken Finned Jellyfish", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_W_WING:            ["Group Linked Kraken W-Wing", LVL_PROFICIENT, 95],

     T_BRUTE_FORCE:                 ["Brute Force", LVL_EXPERT, 1000]}

class TNODE:
    # This is the tree node (branch) structure used in constructing AI chains.
    def __init__(self, r = -1, c = -1, Cand = -1, Lk = -1, Chain = None, Parent = None, Children = None):
        self.r = r              # row
        self.c = c              # col
        self.Cand = Cand        # Candidate
        self.Lk = Lk            # link to parent (LK_ enums)
        self.Chain = [] if Chain is None else Chain  # List of path from root to current Node. (NODE(r, c, Cand, Lk_type_to_next)
        self.Parent = Parent
        self.Children = [] if Children is None else Children

class STATUS:
    def __init__(self, Tech = T_UNDEF, Pattern = None, Outcome = None):
        self.Tech = Tech
        self.Pattern = Pattern if Pattern else []
        self.Outcome = Outcome if Outcome else []

def walk_ai_trees(Orchards, path):
    # Walks an orchard of AI trees printing out the nodes and their branches.
    # Trees is list of orchards, one per candidate.  The next level up is the list of trees in the
    # orchard for that candidate.  The following level up is the first level of branches per tree
    # which is the start of chains.
    Lvl = 0
    with open(path, "wt") as f:
        for i, Trees in enumerate(Orchards):
            f.write(f"Candidate {i+1} Orchard\n")
            for Tree in Trees: traverse_branch(Tree, Lvl, f)

def traverse_branch(B, Lvl, f):
    sLk = ""
    sL = ""
    for i in range(Lvl): sL += "| "
    sL += f"+{ascii_lk(B.Lk)}{B.Cand}r{B.r+1}c{B.c+1}"
    if B.Chain:
        sL += f", Chain: "
        for r, c, Cand, Lk in B.Chain:
           sL += f"{Cand}r{r+1}c{c+1}{ascii_lk(Lk)}"
    if B.Parent: sL += f", Parent: {B.Parent.Cand}r{B.Parent.r+1}c{B.Parent.c+1}"
    f.write(sL + "\n")
    for SB in B.Children: traverse_branch(SB, Lvl+1, f)

def ascii_lk(Lk):
    if Lk == LK_WEAK: return "-"
    elif Lk == LK_STRG or Lk == LK_STWK: return "="
    elif Lk == LK_WKST: return "~"
    else: return "*"

def cell_val_has_no_conflicts(v, grid, r, c):
    #  Checks that value v obeys sudoku rules in grid[r][c], the 9x9 matrix
    #  v:     IN:  value to test in the grid
    #  grid:  IN:  grid to test value
    #  r, c   IN:  row and column in grid for test.
    # Check that val not in row

    if not (v in grid[r]):
        # Check that not in col
        if not (v in [grid[0][c], grid[1][c], grid[2][c],
                      grid[3][c], grid[4][c], grid[5][c],
                      grid[6][c], grid[7][c], grid[8][c]]):
            # Check that not in block/box
            br = (r//3)*3
            bc = (c//3)*3
            if not (v in (grid[br][bc:bc+3]
                          +grid[br+1][bc:bc+3]
                          +grid[br+2][bc:bc+3])):
                return True
    return False

def cell_val_has_conflicts(grid, r, c, val = 0):
    # if val != 0 then grid[r][c] is zero, else caller made a mistake.
    # and unpredictable results.
    #  Checks that value v obeys sudoku rules in grid[r][c], the 9x9 matrix

    if val == grid[r][c] == 0: return False  # empty cell cannot be conflicted.

    if val: v = val
    else: v = grid[r][c]; grid[r][c] = 0

    if not (v in grid[r]):
        # Check that not in col
        if not (v in [grid[0][c], grid[1][c], grid[2][c],
                      grid[3][c], grid[4][c], grid[5][c],
                      grid[6][c], grid[7][c], grid[8][c]]):
            # Check that not in block/box
            br = (r//3)*3
            bc = (c//3)*3
            if not (v in (grid[br][bc:bc+3]
                          +grid[br+1][bc:bc+3]
                          +grid[br+2][bc:bc+3])):
                if not val: grid[r][c] = v
                return False
    if not val: grid[r][c] = v
    return True

def token_link(Lk):
    if Lk == LK_WEAK: return OP_WLK
    if Lk == LK_STRG or Lk == LK_STWK: return OP_SLK
    if Lk == LK_WKST: return OP_WSLK
    return -1

def discard_cand_from_peers(Cand, r, c, Cands):
    for r1 in range(9):
        Cands[r1][c].discard(Cand)
    for c1 in range(9):
        Cands[r][c1].discard(Cand)
    br = (r//3)*3; bc = (c//3)*3
    for r1 in range(br, br+3):
        for c1 in range(bc, bc+3):
            Cands[r1][c1].discard(Cand)

def cells_in_same_house(r1, c1, r2, c2):
    # Cells see each other in same house
    if r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3):
        return True
    return False

def is_in_chain(r, c, Cand, Chain, GrpLks):
    # Chain is a list of Node tuples (r, c, Cand, Lk).
    # returns the node location in the chain (0 is first location) or -1 if not found.

    for i, (rc, cc, Candc, Lkc) in enumerate(Chain):
        if are_same_ccells(r, c, Cand, rc, cc, Candc, GrpLks): return i
    return -1

def list_ccells_linked_to(r, c, Cand, Cands, Type = LK_STWK, GrpLks = False):
    # Returns a list of (r, c, Cand, LkType, LkHouse) tuples that the ccell(r, c, Cand) can see.
    # LkType is one of LK_STWK or LK_WEAK, LkHouse is one of LK_ROW, LK_COL, LK_BOX, or LK_CELL
    # If Type == LK_STRG, only strong links will be returned.
    # if GrpLks is True r and c are passed and returned as sets, else r, c are passed and
    # returned as scalars.

    # Note when working with non-group links, if the link is in the intersection of two
    # houses (a line and a box), it may be strong in one house and weak in the other.
    # This is an opportunity to for pointing or claiming locked singles eliminations (which
    # BTW should have been cleared by earlier steps than when these higher level of
    # complexity functions are used.

    LCL = []
    if GrpLks:
        if len(r) == 1:  # scan the row
            r0 = list(r)[0]
            ct = list(c)[0]//3
            C1 = set()
            Twr = [set(), set(), set()]
            for c1 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - c):
                if Cand in Cands[r0][c1]:
                    C1.add(c1)
                    Twr[c1//3].add(c1)
            if len(C1) == 1:
                LCL.append((r, C1, Cand, LK_STWK, LK_ROW))
            elif Type & LK_WEAK:
                for c1 in sorted(C1):
                    LCL.append((r, {c1}, Cand, LK_WEAK, LK_ROW))
            lenTwr0 = len(Twr[0]); lenTwr1 = len(Twr[1]); lenTwr2 = len(Twr[2])
            if ct == 0:
                if lenTwr0 == 0:
                    if lenTwr1 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK, LK_ROW))
                    elif lenTwr1 > 1 and lenTwr2 == 0: LCL.append((r, Twr[1], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr1 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[1], Cand, LK_WEAK, LK_ROW), (r, Twr[2], Cand, LK_WEAK, LK_ROW)])
            if ct == 1:
                if lenTwr1 == 0:
                    if lenTwr0 == 0 and lenTwr2 > 1: LCL.append((r, Twr[2], Cand, LK_STWK, LK_ROW))
                    elif lenTwr0 > 1 and lenTwr2 == 0: LCL.append((r, Twr[0], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr2 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK, LK_ROW), (r, Twr[2], Cand, LK_WEAK, LK_ROW)])
            if ct == 2:
                if lenTwr2 == 0:
                    if lenTwr0 == 0 and lenTwr1 > 1: LCL.append((r, Twr[1], Cand, LK_STWK, LK_ROW))
                    elif lenTwr0 > 1 and lenTwr1 == 0: LCL.append((r, Twr[0], Cand, LK_STWK, LK_ROW))
                elif Type & LK_WEAK and lenTwr0 > 1 and lenTwr1 > 1: LCL.extend([(r, Twr[0], Cand, LK_WEAK, LK_ROW), (r, Twr[1], Cand, LK_WEAK, LK_ROW)])

        if len(C) == 1:  # scan the col
            c0 = list(c)[0]
            rf = list(r)[0]//3
            R1 = set()
            Flr = [set(), set(), set()]
            for r1 in sorted({0, 1, 2, 3, 4, 5, 6, 7, 8} - r):
                if Cand in Cands[r1][c]:
                    R1.add(r1)
                    Flr[r1//3].add(r1)
            if len(R1) == 1:
                LCL.append((R1, c, Cand, LK_STWK, LK_COL))
            elif Type & LK_WEAK:
                for r1 in sorted(R1):
                    LCL.append(({r1}, c, Cand, LK_WEAK, LK_COL))
            lenFlr0 = len(Flr[0]); lenFlr1 = len(Flr[1]); lenFlr2 = len(Flr[2])
            if rf == 0:
                if lenFlr0 == 0:
                    if lenFlr1 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr1 > 1 and lenFlr2 == 0: LCL.append((Flr[1], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr1 > 1 and lenFlr2 > 1: LCL.extend([(Flr[1], c, Cand, LK_WEAK, LK_COL), (Flr[2], c, Cand, LK_WEAK, LK_COL)])
            if rf == 1:
                if lenFlr1 == 0:
                    if lenFlr0 == 0 and lenFlr2 > 1: LCL.append((Flr[2], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr0 > 1 and lenFlr2 == 0: LCL.append((Flr[0], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr2 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK, LK_COL), (Flr[2], c, Cand, LK_WEAK, LK_COL)])
            if rf == 2:
                if lenFlr2 == 0:
                    if lenFlr0 == 0 and lenFlr1 > 1: LCL.append((Flr[1], c, Cand, LK_STWK, LK_COL))
                    elif lenFlr0 > 1 and lenFlr1 == 0: LCL.append((Flr[0], c, Cand, LK_STWK, LK_COL))
                elif Type & LK_WEAK and lenFlr0 > 1 and lenFlr1 > 1: LCL.extend([(Flr[0], c, Cand, LK_WEAK, LK_COL), (Flr[1], c, Cand, LK_WEAK, LK_COL)])

        # scan the box.  (Grouped) Node is always contained in a box
        rb = (list(R)[0]//3)*3; cb = (list(C)[0]//3)*3; rb1 = rb+1; rb2 = rb+2; cb1 = cb+1; cb2 = cb+2
        B1 = []
        RB = [set(), set(), set()]; CB = [set(), set(), set()]
        for i, r0 in enumerate([rb, rb1, rb2]):
            for j, c0 in enumerate([cb, cb1, cb2]):
                if r0 in r and c0 in c: continue
                if Cand in Cands[r0][c0]: B1.append((r0, c0)); RB[i].add(c0); CB[j].add(r0)
        if len(B1) == 1:
            r1, c1 = B1[0]; LCL.append(({r1}, {c1}, Cand, LK_STWK, LK_BOX))
        elif Type & LK_WEAK:
            for r1, c1 in B1: LCL.append(({r1}, {c1}, Cand, LK_WEAK, LK_BOX))
        BX = []
        B1 = sorted(B1)
        for i in [0, 1, 2]:
            if RB[i]: BX.append(({rb+i}, RB[i]))
            if CB[i]: BX.append((CB[i], {cb+i}))
        for r2, c2 in BX:
            B2 = []; lr2 = len(r2); lc2 = len(c2)
            if lr2 == lc2 == 1: B2.append((list(r2)[0], list(c2)[0]))
            elif lc2 == 1:
                for rx in r2: B2.append((rx, list(c2)[0]))
            elif lr2 == 1:
                for cx in c2: B2.append((list(r2)[0], cx))
            if B1 == sorted(B2): LCL.append((r2, c2, Cand, LK_STWK, LK_BOX))
            elif Type & LK_WEAK: LCL.append((r2, c2, Cand, LK_WEAK, LK_BOX))
    else:  # no GrpLks
        # Scan the row.
        n = 0; LCL0 = []
        for c0 in [0, 1, 2, 3, 4, 5, 6, 7, 8].remove(c):
            if Cand in Cands[r][c0]:
                n +=1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r, c0, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_ROW) for r, c, Cand in LCL0])
        # Scan the col
        n = 0; LCL = []
        for r0 in [0, 1, 2, 3, 4, 5, 6, 7, 8].remove(r):
            if Cand in Cands[r0][c]:
                n += 1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r0, c, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_COL) for r, c, Cand in LCL0])
        # Scan the box
        rb = (r//3)*3; cb = (c//3)*3; rb1 = rb+1; rb2 = rb+2; cb1 = cb+1; cb2 = cb+2
        n = 0; LCL0 = []
        for r0, c0 in [(rb, cb), (rb, cb1), (rb, cb2), (rb1, cb), (rb1, cb1), (rb1, cb2), (rb2, cb), (rb2, cb1), (rb2, cb2)].remove((r, c)):
            if Cand in Cands[r0][c0]:
                n += 1
                if n > 1 and Type == LK_STRG: break
                LCL0.append((r0, c0, Cand))
        else:
            Lk = LK_WEAK if n > 1 else LK_STWK
            LCL.extend([(r, c, Cand, Lk, LK_COL) for r, c, Cand in LCL0])
        # Check in the cell - cell will always have two or more candidates
        if len(Cands[r][c] == 2): LCL.append((r, c, (copy(Cands[r][c])).remove(Cand)[0], LK_STWK, LK_CELL))
        elif Type & LK_WEAK:
            for Cand0 in sorted(Cands[r][c] - {Cand}):
                LCL.append((r, c, Cand0, LK_WEAK, ))
    return LCL

def cells_that_see_all_of(Cells):
    # Cells = list of two to four (r,c) tuples.  Returns another list of (r, c) tuples that
    # can see all the passed cells.

    # For three or more cells to be seen by
    # any other cell, the cells to be seen, and the cell that is doing the seeing
    # all need to be in the same chute.

    Cells1 = []
    for r, c in Cells:
        if isinstance(r, int) and isinstance(c, int): Cells1.append((r, c))
        elif isinstance(c, int):
            for r0 in r: Cells1.append((r0, c))
        elif isinstance(r, int):
            for c0 in c: Cells1.append((r, c0))

    sR = set(); sC = set(); sF = set(); sT = set()
    for r, c in Cells1: sR.add(r); sC.add(c); sF.add((r//3)*3); sT.add((c//3)*3)

    rtn = set()
    if len(Cells) == len(sF) == len(sT) == 2:  # 2 (grouped) cells in separate houses
        (r0, c0) = Cells[0]; r1, c1 = Cells[1]
        if isinstance(r0, int) and isinstance(c1, int): rtn.add((r0, c1))
        if isinstance(r1, int) and isinstance(c0, int): rtn.add((r1, c0))
        return sorted(rtn)

    if len(sF) == len(sT) == 1:  # all cells are in the same box.
        f = list(sF)[0]; t = list(sT)[0]
        rtn = {(f, t), (f, t+1), (f, t+2), (f+1, t), (f+1, t+1), (f+1, t+2), (f+2, t), (f+2, t+1), (f+2, t+2)} - set(Cells1)
        if len(sR) == 1:  # and in the same row.
            r = list(sR)[0]
            for c in sorted(set(range(9)) - {t, t+1, t+2}):
                rtn.add((r, c))
        if len(sC) == 1:  # and in the same col.
            c = list(sC)[0]
            for r in sorted(set(range(9)) - {f, f+1, f+2}):
                rtn.add((r, c))
        return sorted(rtn)
    rtn = set()
    if len(sF) == 1:  # cells are all on the same floor.
        for r0 in sR:
            for c0 in range(9):
                if (r0, c0) in Cells1: continue
                for r1, c1 in Cells1:
                    if not cells_in_same_house(r0, c0, r1, c1):
                        break
                else:  # r0,c0 can see all cells in patterns
                    rtn.add((r0, c0))
        return sorted(rtn)

    if len(sT) == 1:  # cells are all in the same tower
        for c0 in sC:
            for r0 in range(9):
                if (r0, c0) in Cells1: continue
                for r1, c1 in Cells1:
                    if not cells_in_same_house(r0, c0, r1, c1):
                        break
                else:  # r0, c0 can see all the cell patterns
                    rtn.add((r0, c0))
    return sorted(rtn)

def are_same_ccells(r0, c0, Cand0, r1, c1, Cand1, GrpLks = False):
    # Returns True or False depending on whether ccells match or not.
    # Necessary to compare ccells seamlessly because group links use sets objects
    # where equivalence checks for the same instance of set rather than the same
    # contents of the set.

    if GrpLks:
        return (not (R0 ^ R1 or C0 ^ C1)) and Cand0 == Cand1
    else:
        return r0 == r1 and c0 == c1 and Cand0 == Cand1

def how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands, GrpLks = False):
    # returns LkType, LkHouse
    #    Where: LkType is one of: LK_NONE, LK_WEAK, or LK_STWK
    #           LkHouse is one of: LK_NONE, LK_ROW, LK_COL, LK_BOX, LK_ROW | LK_BOX, LK_ROW | LK_BOX
    # Two ccells are directly linked if:
    #   * they are two different candidates in the same cell, or
    #     +  strongly if they are the only two candidates in that cell.
    #     +  weakly if there are other candidates in that cell
    #   * they are same value candidates in different cells in a common house.
    #     +  strongly if they are the only occurrences of that candidate value
    #        in the house.
    #     +  weakly if there other candidate values in that cell.
    # Note that a strong link can masquerade as a weak link, but a weak link
    # cannot masquerade as a strong link.

    if GrpLks:
        lenr0 = len(r0); lenc0 = len(c0); lenr1 = len(r1); lenc1 = len(c1)
        r00 = list(r0)[0]; c00 = list(c0)[0]; r10 = list(r1)[0]; c10 = list(c1)[0]
        if lenr0 == lenr1 == lenc0 == lenc1 == 1:  # no grouped ccells
            if not (r0 ^ r1 or c0 ^ c1):  # same cell.
                if Cand0 == Cand1: return LK_NONE, LK_NONE  # cells cannot link on themselves
                if len(Cands[r00][c00]) == 2: return LK_STWK, LK_CELL
                else: return LK_WEAK, LK_CELL
        # different cells, grouped or ungrouped
        if Cand0 != Cand1: return LK_NONE, LK_NONE
        if lenr0 == lenr1 == 1 and r00 == r10:  # house is a row
            for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (c0 | c1):
                if Cand0 in cands[r00]: return LK_WEAK, LK_ROW
            return LK_STRG, LK_ROW
        if lenc0 == lenc1 == 1 and c00 == c10:  # house is a column
            for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - (r0 | r1):
                if Cand0 in Cands[r][c00]: return LK_WEAK, LK_COL
            return LK_STRG, LK_COL
        F = set(); T = set()
        for r in r0 | r1: F.add(r//3)
        for c in c0 | c1: T.add(c//3)
        if len(F) == len(T) == 1:  # house is a box.
            for rb in range(list(F)[0]*3, 3):
                for cb in range(list(T)[0]*3, 3):
                    if (rb in r0 | r1) and (cb in c0 | c1): continue
                    if Cand0 in Cands[rb][cb]: return LK_WEAK, LK_BOX
            return LK_STWK, LK_BOX
        return LK_NONE, LK_NONE
    else:
        if r0 == r1 and c0 == c1:
            if Cand0 == Cand1: return LK_NONE, LK_NONE  # ccells cannot link on themselves
            if len(Cands[r0][c0]) == 2: return LK_STWK, LK_CELL
            return LK_WEAK, CELL
        # different cells, therefore linked by same candidate
        if Cand0 != Cand1: return LK_NONE, LK_NONE
        if r0 == r1:  # house is a row
            LkHse = LK_ROW | LK_BOX if c0//3 == c1//3 else LK_ROW
            for c in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {c0, c1}:
                if Cand0 in Cands[r0][c]: return LK_WEAK, LkHse
            return LK_STWK, LkHse
        if c0 == c1:  # house is a column
            LkHse = LK_COL | LK_BOX if r0//3 == r1//3 else LK_COL
            for r in {0, 1, 2, 3, 4, 5, 6, 7, 8} - {r0, r1}:
                if Cand0 in Cands[r][c0]: return LK_WEAK, LkHse
            return LK_STWK, LkHse
        rb0 = (r0//3)*3; cb0 = (c0//3)*3; rb1 = (r1//3)*3; cb1 = (c1//3)*3
        if rb0 == rb1 and cb0 == cb1:  # house is a box
            for rb in [rb0, rb0+1, rb0+2]:
                for cb in [cb0, cb0+1, cb0+2]:
                    if (rb, cb) in {(r0, c0), (r1, c1)}: continue
                    if Cand0 in Cands[rb][cb]: return LK_WEAK, LK_BOX
            return LK_STWK, LK_BOX
        return LK_NONE, LK_NONE


def find_all_strong_cand_links(Cand, Cands, GrpLks = False):
    # Finds all the strong links for a candidate and enters makes two entries
    # in the list for same cand links in house, one from each side.  Returns
    # a list of (r, c, Cand) tuples not CCELLS as tuples are compared literally
    # but comparision of classes will compare the pointers to the instance and
    # not the contents of the class.

    SLks = find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks)

    for r in range(9):
        for c in range(9):
            if len(Cands[r][c])== 2 and Cand in Cands[r][c]:
                SLks.append(((r, c, Cand), (r, c, (Cands[r][c] ^ {Cand}).pop())))
    return SLks

def find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks = False):
    # only finds strong links for the passed cand between cells.
    # returns Lks[((r0, c0), (r1, c1)), . . .] without the cand.
    # Note that ((r0, c0), (r1, c1)) and ((r1, c1), (r0, c0)) are seen as distinct
    # and both tuples are returned in the list for the same candidate.

    # Note that if GrpLks is True, then all coords are returned as sets.  If GrpLks are
    # False, all coords are scalars.

    Lks = []
    if GrpLks:
        # look in rows
        for r in range(9):
            C = []; Twr = [set(), set(), set()]
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c); Twr[c//3].add(c)
            if len(C) == 2:  # and (((r, C[0]), (r, C[1])) not in Lks and ((r, C[1]), (r, C[0])) not in Lks):
                Lks.extend([((r, C[0], Cand), (r, C[1], Cand)), ((r, C[1], Cand), (r, C[0], Cand))])
            else:
                if Twr[0] and Twr[1] and Twr[2]: continue
                if Twr[0] and Twr[1]:   Lks.extend([((r, Twr[0], Cand), (r, Twr[1], Cand)), ((r, Twr[1], Cand), (r, Twr[0], Cand))])
                elif Twr[0] and Twr[2]: Lks.extend([((r, Twr[0], Cand), (r, Twr[2], Cand)), ((r, Twr[2], Cand), (r, Twr[0], Cand))])
                elif Twr[1] and Twr[2]: Lks.extend([((r, Twr[1], Cand), (r, Twr[2], Cand)), ((r, Twr[2], Cand), (r, Twr[1], Cand))])
        # look in cols
        for c in range(9):
            R = []; Flr = [set(), set(), set()]
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r); Flr[r//3].add(r)
            if len(R) == 2 and (((R[0], c), (R[1], c)) not in Lks and ((R[1], c), (R[0], c)) not in Lks):
                Lks.extend([((R[0], c, Cand), (R[1], c, Cand)), ((R[1], c, Cand), (R[0], c, Cand))])
            else:
                if Flr[0] and Flr[1] and Flr[2]: continue
                if Flr[0] and Flr[1]:   Lks.extend([((Flr[0], c, Cand), (Flr[1], c, Cand)), ((Flr[1], c, Cand), (Flr[0], c, Cand))])
                elif Flr[0] and Flr[2]: Lks.extend([((Flr[0], c, Cand), (Flr[2], c, Cand)), ((Flr[2], c, Cand), (Flr[0], c, Cand))])
                elif Flr[1] and Flr[2]: Lks.extend([((Flr[1], c, Cand), (Flr[2], c, Cand)), ((Flr[2], c, Cand), (Flr[1], c, Cand))])
        # #look in boxes
        for br, bc in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
            # 1.  Examine the ccells in the box
            B1 = []
            RB = [set(), set(), set()]; CB = [set(), set(), set()]
            br1 = br+1; br2 = br+2; bc1 = bc+1; bc2 = bc+2
            for i, j, r, c in [(0, 0, br, bc), (0, 1, br, bc1), (0, 2, br, bc2),
                               (1, 0, br1, bc), (1, 1, br1, bc1), (1, 2, br1, bc2),
                               (2, 0, br2, bc), (2, 1, br2, bc1), (2, 2, br2, bc2)]:
                if Cand in Cands[r][c]:
                    B1.append((r, c))
                    RB[i].add(c); CB[j].add(r)
            lenRB0 = len(RB[0]); lenRB1 = len(RB[1]); lenRB2 = len(RB[2])
            lenCB0 = len(CB[0]); lenCB1 = len(CB[1]); lenCB2 = len(CB[2])
            # 2. Check out rows patterns
            if lenRB0 > 0 and lenRB1 > 0 and lenRB2 == 0:   Lks.extend([((br, RB[0], Cand), (br1, RB[1], Cand)), ((br1, RB[1], Cand), (br, RB[0], Cand))])
            elif lenRB0 > 0 and lenRB1 == 0 and lenRB2 > 0: Lks.extend([((br, RB[0], Cand), (br2, RB[2], Cand)), ((br2, RB[2], Cand), (br, RB[0], Cand))])
            elif lenRB0 == 0 and lenRB1 > 0 and lenRB2 > 0: Lks.extend([((br1, RB[1], Cand), (br2, RB[2], Cand)), ((br2, RB[2], Cand), (br1, RB[1], Cand))])
            # 3. Check out col patterns
            if lenCB0 > 0 and lenCB1 > 0 and lenCB2 == 0:   Lks.extend([((CB[0], bc, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (CB[0], bc, Cand))])
            elif lenCB0 > 0 and lenCB1 == 0 and lenCB2 > 0: Lks.extend([((CB[0], bc, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (CB[0], bc, Cand))])
            elif lenCB0 == 0 and lenCB1 > 0 and lenCB2 > 0: Lks.extend([((CB[1], bc1, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (CB[1], bc1, Cand))])
            # 4. Check out row/col patterns
            RP = sorted([lenRB0, lenRB1, lenRB2]); CP = sorted([lenCB0, lenCB1, lenCB2])
            if RP == CP == [1, 1, 2]:
                # |** |   |* *| Family
                # |  *|   | * |
                # |  *|   | * |
                if lenRB0 == 2:
                    if lenCB0 == 2:   Lks.extend([((br, RB[0], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br, RB[0], Cand))])
                    elif lenCB1 == 2: Lks.extend([((br, RB[0], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br, RB[0], Cand))])
                    elif lenCB2 == 2: Lks.extend([((br, RB[0], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br, RB[0], Cand))])
                elif lenRB1 == 2:
                    if lenCB0 == 2:   Lks.extend([((br1, RB[1], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br1, RB[1], Cand))])
                    elif lenCB1 == 2: Lks.extend([((br1, RB[1], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br1, RB[1], Cand))])
                    elif lenCB2 == 2: Lks.extend([((br1, RB[1], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br1, RB[1], Cand))])
                elif lenRB2 == 2:
                    if lenCB0 == 2:   Lks.extend([((br2, RB[0], Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br2, RB[2], Cand))])
                    elif lenCB1 == 2: Lks.extend([((br2, RB[0], Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br2, RB[2], Cand))])
                    elif lenCB2 == 2: Lks.extend([((br2, RB[0], Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br2, RB[2], Cand))])
            elif RP == [0, 1, 3] and CP == [1, 1, 2]:
                # |   |  |  +| Family
                # |  +|  |   |
                # |**+|  |**+|
                if lenRB0 == 3:  # and lenRB1 == 1:
                    if lenCB0 == 2:   Lks.extend([((br, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br, {bc, bc1}, Cand))])
                elif lenRB1 == 3:
                    if lenCB0 == 2:   Lks.extend([((br1, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br1, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br1, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br1, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br1, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br1, {bc, bc1}, Cand))])
                elif lenRB2 == 3:
                    if lenCB0 == 2:   Lks.extend([((br2, {bc1, bc2}, Cand), (CB[0], bc, Cand)), ((CB[0], bc, Cand), (br2, {bc1, bc2}, Cand))])
                    elif lenCB1 == 2: Lks.extend([((br2, {bc, bc2}, Cand), (CB[1], bc1, Cand)), ((CB[1], bc1, Cand), (br2, {bc, bc2}, Cand))])
                    elif lenCB2 == 2: Lks.extend([((br2, {bc, bc1}, Cand), (CB[2], bc2, Cand)), ((CB[2], bc2, Cand), (br2, {bc, bc1}, Cand))])
            elif RP == [1, 1, 2] and CP == [0, 1, 3]:
                # above patterns rotated by 90degs
                if lenCB0 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc, Cand)), (({br1, br2}, bc, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc, Cand)), (({br, br2}, bc, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc, Cand)), (({br, br1}, bc, Cand), (br2, RB[2], Cand))])
                elif lenCB1 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc1, Cand)), (({br1, br2}, bc1, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc1, Cand)), (({br, br2}, bc1, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc1, Cand)), (({br, br1}, bc1, Cand), (br2, RB[2], Cand))])
                elif lenCB2 == 3:
                    if lenRB0 == 2:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc2, Cand)), (({br1, br2}, bc2, Cand), (br, RB[0], Cand))])
                    elif lenRB1 == 2: Lks.extend([((br1, RB[1], Cand), ({br, br2}, bc2, Cand)), (({br, br2}, bc2, Cand), (br1, RB[1], Cand))])
                    elif lenRB2 == 2: Lks.extend([((br2, RB[2], Cand), ({br, br1}, bc2, Cand)), (({br, br1}, bc2, Cand), (br2, RB[2], Cand))])
            elif RP == CP == [1, 1, 3]:
                # |  +|  |  +| Family
                # |  +|  |  +|
                # |**+|  |***|
                if lenRB0 == 3:
                    if lenCB0 == 3:   Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc, Cand)),  ((CB[0], bc, Cand), (br, {bc1, bc2}, Cand)), (({br1, br2}, bc, Cand), (br, RB[0], Cand)),  ((br, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc1, Cand)), ((CB[0], bc1, Cand), (br, {bc, bc2}, Cand)), (({br1, br2}, bc1, Cand), (br, RB[0], Cand)), ((br, {bc, bc2}, Cand), (CB[0], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br, RB[0], Cand), ({br1, br2}, bc2, Cand)), ((CB[0], bc2, Cand), (br, {bc, bc1}, Cand)), (({br1, br2}, bc2, Cand), (br, RB[0], Cand)), ((br, {bc, bc1}, Cand), (CB[0], bc2, Cand))])
                elif lenRB1 == 3:
                    if lenCB0 == 3:   Lks.extend([((br1, RB[0], Cand), ({br, br2}, bc, Cand)),  ((CB[0], bc, Cand), (br1, {bc1, bc2}, Cand)), (({br, br2}, bc, Cand), (br1, RB[0], Cand)),  ((br1, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br1, RB[0], Cand), ({br, br2}, bc1, Cand)), ((CB[0], bc1, Cand), (br1, {bc, bc2}, Cand)), (({br, br2}, bc1, Cand), (br1, RB[0], Cand)), ((br1, {bc, bc2}, Cand), (CB[0], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br1, RB[0], Cand), ({br, br2}, bc2, Cand)), ((CB[0], bc2, Cand), (br1, {bc, bc1}, Cand)), (({br, br2}, bc2, Cand), (br1, RB[0], Cand)), ((br1, {bc, bc1}, Cand), (CB[0], bc2, Cand))])
                elif lenRB2 == 3:
                    if lenCB0 == 3:   Lks.extend([((br2, RB[0], Cand), ({br, br1}, bc, Cand)),  ((CB[0], bc, Cand), (br2, {bc1, bc2}, Cand)), (({br, br1}, bc, Cand), (br2, RB[0], Cand)),  ((br2, {bc1, bc2}, Cand), (CB[0], bc, Cand))])
                    elif lenCB1 == 3: Lks.extend([((br2, RB[0], Cand), ({br, br1}, bc1, Cand)), ((CB[0], bc1, Cand), (br2, {bc, bc2}, Cand)), (({br, br1}, bc1, Cand), (br2, RB[0], Cand)), ((br2, {bc, bc2}, Cand), (CB[0], bc1, Cand))])
                    elif lenCB2 == 3: Lks.extend([((br2, RB[0], Cand), ({br, br1}, bc2, Cand)), ((CB[0], bc2, Cand), (br2, {bc, bc1}, Cand)), (({br, br1}, bc2, Cand), (br2, RB[0], Cand)), ((br2, {bc, bc1}, Cand), (CB[0], bc2, Cand))])
        # cleanup, convert all cell coords to sets and remove duplicates.
        Lks1 = []
        for ((r0, c0, Cand0), (r1, c1, Cand1)) in Lks:
            R0 = {r0} if isinstance(r0, int) else r0
            C0 = {c0} if isinstance(c0, int) else c0
            R1 = {r1} if isinstance(r1, int) else r1
            C1 = {c1} if isinstance(c1, int) else c1

            for ((Ra, Ca, Canda), (Rb, Cb, Candb)) in Lks1:
                if are_same_ccells(Ra, Ca, Canda, R0, C0, Cand0, GrpLks) and are_same_ccells(Rb, Cb, Candb, R1, C1, Cand1, GrpLks): continue
            else: Lks1.append(((R0, C0, Cand0), (R1, C1, Cand1)))
    else:  # No group links
        # look in rows
        for r in range(9):
            C = []
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c)
            if len(C) == 2:  # and (((r, C[0]), (r, C[1])) not in Lks and ((r, C[1]), (r, C[0])) not in Lks):
                Lks.extend([((r, C[0], Cand), (r, C[1], Cand)), ((r, C[1], Cand), (r, C[0], Cand))])
        # look in cols
        for c in range(9):
            R = []
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r)
            if len(R) == 2:  # and (((R[0], c), (R[1], c)) not in Lks and ((R[1], c), (R[0], c)) not in Lks):
                Lks.extend([((R[0], c, Cand), (R[1], c, Cand)), ((R[1], c, Cand), (R[0], c, Cand))])
        # look in boxes
        for b in range(9):
            rb = (b//3)*3; cb = (b%3)*3
            B = []
            for r in [rb, rb+1, rb+2]:
                for c in [cb, cb+1, cb+2]:
                    if Cand in Cands[r][c]: B.append((r, c, Cand))
            if len(B) == 2:
                if (B[0], B[1]) not in Lks: Lks.extend([(B[0], B[1]), (B[1], B[0])])
        # cleanup, convert single candidate sets and remove duplicates.
        Lks1 = []
        for ((ra, ca, Canda), (rb, cb, Candb)) in Lks:
            if ((ra, ca, Canda), (rb, cb, Candb)) in Lks1: continue
            # if ((ra, ca), (rb, cb)) in Lks1 or ((rb, cb), (ra, ca)) in Lks: continue
            Lks1.append(((ra, ca, Candb), (rb, cb, Candb)))
    return Lks1
