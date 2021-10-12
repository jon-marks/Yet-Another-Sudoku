
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
LK_ROW = 0x0010
LK_COL = 0x0020
LK_BOX = 0x0040
LK_ANY = 0x0070

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
     T_GL_KRAKEN_X_WING:            ["Group Linked Kraken Finned X-Wing", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_SWORDFISH:         ["Group Linked Kraken Finned Swordfish", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_JELLYFISH:         ["Group Linked Kraken Finned Jellyfish", LVL_ACCOMPLISHED, 100],
     T_GL_KRAKEN_W_WING:            ["Group Linked Kraken W-Wing", LVL_PROFICIENT, 95],

     T_BRUTE_FORCE:                 ["Brute Force", LVL_EXPERT, 1000]}

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

def link_house(N0, N1):
    # N0 and N1 must be linked, else erroneous LK_BOX cand be returned.
    r0, c0 = N0; r1, c1 = N1
    if r0 == r1: return LK_ROW
    if c0 == c1: return LK_COL
    # if r0//3 == r1//3 and c0//3 == c1//3: return LK_BOX
    return LK_BOX


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


def list_ccells_linked_to(r, c, Cand, Cands, Type = LK_STWK, GrpLks = False):
    # Returns a list of ccells that the ccell(r, c, Cand) can see.
    # If Type == LK_STRG, only strong links will be returned.
    # r, c can be a grouped link.
    # lists group links too.

    R = {r} if isinstance(r, int) else r
    C = {c} if isinstance(c, int) else c
    LCL = []
    # scan the row
    C1 = set()
    Twr = [set(), set(), set()]
    ct = list(C)[0]//3
    for r1 in sorted(R):
        for c1 in sorted(set(range(9)) - C):
            if Cand in Cands[r1][c1]:
                C1.add(c1)
                c1t = c1//3
                if ct != c1t:
                    Twr[c1t].add(c1)
        if len(C1) == 1:
            LCL.append((r1, C1.pop(), Cand, LK_STWK))
        elif Type & LK_WEAK:
            for c1 in sorted(C1):
                LCL.append((r1, c1, Cand,  LK_WEAK))
            # list group links
            if GrpLks:
                if len(Twr[0]) > 1:
                    if C1 - Twr[0]: LCL.append((r1, Twr[0], Cand, LK_WEAK))
                    else: LCL.append((r1, Twr[0], Cand, LK_STWK))
                if len(Twr[1]) > 1:
                    if C1 - Twr[1]: LCL.append((r1, Twr[1], Cand, LK_WEAK))
                    else: LCL.append((r1, Twr[1], Cand, LK_STWK))
                if len(Twr[2]) > 1:
                    if C1 - Twr[2]: LCL.append((r1, Twr[2], Cand, LK_WEAK))
                    else: LCL.append((r1, Twr[2], Cand, LK_STWK))

    # scan the column
    R1 = set()
    Flr = [set(), set(), set()]
    rf = list(R)[0]//3
    for c1 in sorted(C):
        for r1 in sorted(set(range(9)) - R):
            if Cand in Cands[r1][c1]:
                R1.add(r1)
                r1f = r1//3
                if rf != r1f:
                    Flr[r1f].add(r1)
        if len(R1) == 1:
            LCL.append((R1.pop(), c1, Cand, LK_STWK))
        elif Type & LK_WEAK:
            for r1 in sorted(R1):
                LCL.append((r1, c1, Cand, LK_WEAK))
            # look for group links
            if GrpLks:
                if len(Flr[0]) > 1:
                    if R1 - Flr[0]: LCL.append((Flr[0], c1, Cand, LK_WEAK))
                    else: LCL.append((Flr[0], c1, Cand, LK_STWK))
                if len(Flr[1]) > 1:
                    if R1 - Flr[1]: LCL.append((Flr[1], c1, Cand, LK_WEAK))
                    else: LCL.append((Flr[1], c1, Cand, LK_STWK))
                if len(Flr[2]) > 1:
                    if R1 - Flr[2]: LCL.append((Flr[2], c1, Cand, LK_WEAK))
                    else: LCL.append((Flr[2], c1, Cand, LK_STWK))

    if len(R) == len(C) == 1:
        # scan the box
        B1 = []
        rb = (r//3)*3; cb= (c//3)*3
        for rb1 in [rb, rb+1, rb+2]:
            for cb1 in [cb, cb+1, cb+2]:
                if (rb1 == r and cb1 == c) or Cand not in Cands[rb1][cb1]: continue
                B1.append((rb1, cb1))
        if len(B1) == 1:
            r1, c1 = B1[0]
            if r1 != r and c1 != c:
                LCL.append((r1, c1, Cand, LK_STWK))
        elif Type & LK_WEAK:
            for r1, c1 in B1:
                if r1 != r and c1 != c:
                    LCL.append((r1, c1, Cand, LK_WEAK))

        # Scan the candidates in the cell.
        if len(Cands[r][c]) == 2:
            LCL.append((r, c, (Cands[r][c] - {Cand}).pop(), LK_STWK))
        elif Type & LK_WEAK:
            for Cand1 in sorted(Cands[r][c] - {Cand}):
                LCL.append((r, c, Cand1, LK_WEAK))
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


def ccells_are_linked(RC1, Cand1, RC2, Cand2, Cands, Orient = LK_ANY):
    # if r1, c1, r2, c2 belong to a group link, the group is passed as a set.
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

    (r1, c1) = RC1; (r2, c2) = RC2
    R1 = {r1} if isinstance(r1, int) else r1
    C1 = {c1} if isinstance(c1, int) else c1
    R2 = {r2} if isinstance(r2, int) else r2
    C2 = {c2} if isinstance(c2, int) else c2
    R1iR2 = R1 & R2; C1iC2 = C1 & C2
    R1uR2 = R1 | R2; C1uC2 = C1 | C2

    if R1iR2 and C1iC2:  # the two (grouped) ccells intersect
        if Cand1 == Cand2:  # cell cannot link to itself
            return LK_NONE
        elif r1 == r2 and c1 == c2 and len(Cands[r1][c1]) == 2:  # only possible if all scalars
            return LK_STWK
        else:
            return LK_WEAK

    if Cand1 != Cand2:  # Cands must be same value if ccells are different or grouped ccells do not intersect.
        return LK_NONE

    Ccells = []
    for r in R1:
        for c in C1:
            Ccells.append((r, c))
    for r in R2:
        for c in C2:
            Ccells.append((r, c))

    if Orient & LK_BOX:
        for f in [0, 3, 6]:
            for t in [0, 3, 6]:
                if R1uR2 <= {f, f+1, f+2} and C1uC2 <= {t, t+1, t+2}:
                    # (Grouped) Ccells in the same box.
                    for r in [f, f+1, f+2]:
                        for c in [t, t+1, t+2]:
                            if (r, c) in Ccells: continue
                            if Cand1 in Cands[r][c]: return LK_WEAK
                    return LK_STWK
    # if R1iR2 and Orient & LK_ROW:  # if the rows intersect
    # if R1iR2 and len(R1uR2) == 1 and Orient & LK_ROW:  # if the rows intersect
    if len(R1uR2) == 1 and Orient & LK_ROW:  # if the rows intersect
        # for r in sorted(R1iR2):
        r = list(R1iR2)[0]
        for c in range(9):
            if (r, c) in Ccells: continue
            if Cand1 in Cands[r][c]: return LK_WEAK
        return LK_STWK
    # if C1iC2 and Orient  & LK_COL:  # if the columns intersect
    # if C1iC2 and len(C1uC2) == 1 and Orient & LK_COL:  # if the columns intersect
    if len(C1uC2) == 1 and Orient & LK_COL:  # if the columns intersect
        # for c in sorted(C1iC2):
        c = list(C1iC2)[0]
        for r in range(9):
            if (r, c) in Ccells: continue
            if Cand1 in Cands[r][c]: return LK_WEAK
        return LK_STWK
    return LK_NONE


def are_ccells_aic_linked(r1, c1, Cand1, r2, c2, Cand2, Cands, AIC = False, UsedCcells = None, Depth = 0, GrpLks = False):
    # if an odd length AIC with strong end links can be found then return a list
    # of the nodes of the chain, else None.  Includes same cand in house or
    # diff cands in a cell

    # UsedCcells are only used for descending into the recursion, not ascending
    # out of it.

#    if depth == 10: return []
#    print ("aic_linked", depth)
    lk = ccells_are_linked((r1, c1), Cand1, (r2, c2), Cand2, Cands)
    if lk & LK_NONE: return []

    if lk & LK_STRG:
        return [(r1, c1, Cand1, LK_STRG), (r2, c2, Cand2, -1)]

    if not AIC: return []

    # build out a list of strong links from both ccells 1 and 2
    LCLa = list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STRG, GrpLks = GrpLks)
    LCLb = list_ccells_linked_to(r2, c2, Cand2, Cands, LK_STRG, GrpLks = GrpLks)
    if not (LCLa and LCLb): return []
    if UsedCcells is None: UsedCcells = []
    # Scan for all possible links between ccells in LCLa and LCLb, before looking for
    # longer chains.
    for ra, ca, Canda, Lka in LCLa:
        if (ra, ca, Canda) in UsedCcells: continue
        for rb, cb, Candb, Lkb in LCLb:
            if (rb, cb, Candb) in UsedCcells: continue
            if (ra, ca, Canda) == (rb, cb, Candb): continue
            lk = ccells_are_linked((ra, ca), Canda, (rb, cb), Candb, Cands)
            if lk == LK_WEAK:
                return [(r1, c1, Cand1, Lka), (ra, ca, Canda, LK_WEAK),
                        (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
            elif lk == LK_STWK:
                return [(r1, c1, Cand1, Lka), (ra, ca, Canda, LK_WKST),
                        (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
    # nothing found at this length of chain, look at next nodes in the chain.
    for ra, ca, Canda, Lka in LCLa:
        if (ra, ca, Canda) in UsedCcells: continue
        for rb, cb, Candb, Lkb in LCLb:
            if (rb, cb, Candb) in UsedCcells: continue
            if (ra, ca, Canda) == (rb, cb, Candb): continue
            UC1 = UsedCcells + [(ra, ca, Canda), (rb, cb, Candb)]
            LCLc = list_ccells_linked_to(ra, ca, Canda, Cands, GrpLks = GrpLks)
            LCLd = list_ccells_linked_to(rb, cb, Candb, Cands, GrpLks = GrpLks)
            for rc, cc, Candc, Lkc in LCLc:
                if (rc, cc, Candc) in UC1: continue
                for rd, cd, Candd, Lkd in LCLd:
                    if (rd, cd, Candd) in UC1: continue
                    if (rc, cc, Candc) == (rd, cd, Candd): continue
                    UC1 += [(rc, cc, Candc), (rd, cd, Candd)]
                    Nodes = are_ccells_aic_linked(rc, cc, Candc, rd, cd, Candd, Cands,
                                                  AIC = AIC, UsedCcells = UC1, Depth = Depth+1, GrpLks = GrpLks)
                    if len(Nodes):
                        Nodes.pop()
                        if Lkc == LK_STWK: Lkc = LK_WKST
                        if Lkd == LK_STWK: Lkd = LK_WKST
                        return [(r1, c1, Cand1, Lka), (ra, ca, Canda, Lkc)] + Nodes + \
                               [(rd, cd, Candd, Lkd), (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
    return []

def are_ccells_weakly_linked(r1, c1, Cand1, r2, c2, Cand2, Cands, AIC = 0, GrpLks = False):
    # if the ccells are directly connected by a weak link, or are AIC linked in
    # an odd length chain with weak end links, then return the list of
    # connected ccells.
    # AIC == 0:  Only look for a weak link between the ccells.
    # AIC == 1:  Only look for a weak link or The Ccells see a strong link (A-X=Y-B)
    # AIC == 2:  Look for weak link, see strong link or weak-ended AIC. The ccells are weakly linked (A-P=Q-R=. . .=Z-B)

    # First check to see if the ccells are directly linked.
    lk = ccells_are_linked((r1, c1), Cand1, (r2, c2), Cand2, Cands)
    if lk & LK_NONE: return []

    if lk & LK_STRG:
        return [(r1, c1, Cand1, LK_WKST), (r2, c2, Cand2, -1)]
    elif lk & LK_WEAK:
        return [(r1, c1, Cand1, LK_WEAK), (r2, c2, Cand2, -1)]

    if not AIC: return []

    # Then check if the two ccells see a strong link or strong end link AIC.
    LCLa = list_ccells_linked_to(r1, c1, Cand1, Cands, GrpLks = GrpLks)
    LCLb = list_ccells_linked_to(r2, c2, Cand2, Cands, GrpLks = GrpLks)
    if not (len(LCLa) and len(LCLb)): return []
    if AIC == 1: AIC = False
    else: AIC = True
    for ra, ca, Canda, Lka in LCLa:
        for rb, cb, Candb, Lkb in LCLb:
            if (ra, ca, Canda) == (rb, cb, Candb): continue
            UsedCcells = [(r1, c1, Cand1), (r2, c2, Cand2), (ra, ca, Canda), (rb, cb, Candb)]
            Nodes = are_ccells_aic_linked(ra, ca, Canda, rb, cb, Candb, Cands,
                                          AIC = AIC, UsedCcells = UsedCcells, GrpLks = GrpLks)
            if Nodes:
                Nodes.pop()
                if Lka == LK_STWK: Lka = LK_WKST
                if Lkb == LK_STWK: Lkb = LK_WKST
                return [(r1, c1, Cand1, Lka)] + Nodes + \
                       [(rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
    return []


def are_cells_strongly_linked(r1, c1, Cand1, r2, c2, Cand2, Cands, OddLen = True):
    # if the cand/cells can be connected by the odd/even number of strong links then
    # return the tokenized list of the chain.  Includes same can in house and diff
    # cands in a ccell.
    return []
