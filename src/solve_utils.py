
from globals import *

LK_ERR  = 0b1000
LK_NONE = 0b0000
LK_WEAK = 0b0001
LK_STRG = 0b0010
LK_STWK = 0b0011   # a strong link is also a weak link.
LK_WKST = 0b0100   # strong link masquerading as a weak link

# T enumerations
T_TXT  = 0  # Textual description
T_LVL  = 1  # Expertise level of technique
T_DIFF = 2  # Difficulty of technique

# The use of weak or strong ended AIC's to search for patterns where ccell's see
# each other, for example in covers seeing fins in finned fish or W wings, etc,
# adds the dimension of incremental difficulty in finding and solving a pattern
# based on the number of links in the chains used to solve a step.
AIC_LK_DIFF = 15

T = [[] for j in range(T_NR_TECHS)]
#                               Txt                        Lvl               Diff
T[T_EXPOSED_SINGLE]          = ["Exposed Single",          LVL_BEGINNER,       5]
T[T_HIDDEN_SINGLE]           = ["Hidden Single",           LVL_BEGINNER,       10]
T[T_CLAIMING_LOCKED_SINGLE]  = ["Claiming Locked Single",  LVL_NOVICE,         15]
T[T_POINTING_LOCKED_SINGLE]  = ["Pointing Locked Single",  LVL_NOVICE,         15]
T[T_EXPOSED_PAIR]            = ["Exposed Pair",            LVL_INTERMEDIATE,   15]
T[T_LOCKED_EXPOSED_PAIR]     = ["Locked Exposed Pair",     LVL_INTERMEDIATE,   20]
T[T_HIDDEN_PAIR]             = ["Hidden Pair",             LVL_INTERMEDIATE,   20]
T[T_EXPOSED_TRIPLE]          = ["Exposed Triple",          LVL_INTERMEDIATE,   20]
T[T_LOCKED_EXPOSED_TRIPLE]   = ["Locked Exposed Triple",   LVL_INTERMEDIATE,   25]
T[T_HIDDEN_TRIPLE]           = ["Hidden Triple",           LVL_INTERMEDIATE,   30]
T[T_EXPOSED_QUAD]            = ["Exposed Quad",            LVL_INTERMEDIATE,   35]
T[T_HIDDEN_QUAD]             = ["Hidden Quad",             LVL_INTERMEDIATE,   40]
T[T_X_WING]                  = ["X-Wing",                  LVL_PROFICIENT,     45]
T[T_SWORDFISH]               = ["Swordfish",               LVL_PROFICIENT,     50]
T[T_JELLYFISH]               = ["Jellyfish",               LVL_PROFICIENT,     55]
T[T_FINNED_X_WING]           = ["Finned X-Wing",           LVL_PROFICIENT,     60]
T[T_FINNED_SWORDFISH]        = ["Finned Swordfish",        LVL_PROFICIENT,     65]
T[T_FINNED_JELLYFISH]        = ["Finned Jellyfish",        LVL_PROFICIENT,     70]
T[T_ALMOST_X_WING]           = ["Almost X-Wing",           LVL_PROFICIENT,     80]
T[T_ALMOST_SWORDFISH]        = ["Almost Swordfish",        LVL_PROFICIENT,     90]
T[T_ALMOST_JELLYFISH]        = ["Almost Jellyfish",        LVL_PROFICIENT,    100]
T[T_KRAKEN_X_WING]           = ["Kraken X-Wing",           LVL_ACCOMPLISHED,  100]
T[T_KRAKEN_SWORDFISH]        = ["Kraken Swordfish",        LVL_ACCOMPLISHED,  100]
T[T_KRAKEN_JELLYFISH]        = ["Kraken Jellyfish",        LVL_ACCOMPLISHED,  100]
T[T_Y_WING]                  = ["Y-Wing",                  LVL_INTERMEDIATE,   50]
T[T_W_WING]                  = ["W-Wing",                  LVL_PROFICIENT,     55]
T[T_KRAKEN_W_WING]           = ["Kraken W-Wing",           LVL_PROFICIENT,     95]
T[T_XYZ_WING]                = ["XYZ-Wing",                LVL_PROFICIENT,     60]
T[T_WXYZ_WING]               = ["WXYZ-Wing",               LVL_PROFICIENT,     65]
T[T_EMPTY_RECT]              = ["Empty Rectangle",         LVL_PROFICIENT,     45]
T[T_X_CHAIN]                 = ["X-Chain",                 LVL_PROFICIENT,     60]
T[T_XY_CHAIN]                = ["XY-Chain",                LVL_PROFICIENT,     70]
T[T_CONTINOUS_LOOP]          = ["Continuous Loop",         LVL_PROFICIENT,     70]
# . . . .
T[T_BRUTE_FORCE]             = ["Brute Force",            LVL_EXPERT,        1000]


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
    #Cells see each other in same house
    if r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3):
        return True
    return False


def list_ccells_linked_to(r, c, Cand, Cands, Type = LK_STWK):
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
            if len(Twr[0]) > 1:
                if C1 - Twr[0]: LCL.append((r1, Twr[0], Cand, LK_WEAK))
                else: LCL.append((r1, Twr[0], Cand, LK_STWK))
            if len(Twr[1]) > 1:
                if C1 - Twr[1]: LCL.append((r1, Twr[1], Cand, LK_WEAK))
                else: LCL.append((r1, Twr[1], Cand, LK_STWK))
            if len(Twr[2]) > 1:
                if C1 - Twr[2]: LCL.append((r1, Twr[2], Cand, LK_WEAK))
                else: LCL.append((r1, Twr[2], Cand, LK_STWK))
        # # only interested in strong group links where there are weak links.
        # t0 = len(T[0]); t1 = len(T[1]); t2 = len(T[2])
        # if t0 > 1 and not t1 and not t2:
        #     LCL.append((r, sorted(T[0]), Cand, LK_STWK))
        # elif not t0 and t1 > 1 and not t2:
        #     LCL.append((r, sorted(T[1]), Cand, LK_STWK))
        # elif not t0 and not t1 and t2 > 1:
        #     LCL.append((r, sorted(T[2]), Cand, LK_STWK))

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
            if len(Flr[0]) > 1:
                if R1 - Flr[0]: LCL.append((Flr[0], c1, Cand, LK_WEAK))
                else: LCL.append((Flr[0], c1, Cand, LK_STWK))
            if len(Flr[1]) > 1:
                if R1 - Flr[1]: LCL.append((Flr[1], c1, Cand, LK_WEAK))
                else: LCL.append((Flr[1], c1, Cand, LK_STWK))
            if len(Flr[2]) > 1:
                if R1 - Flr[2]: LCL.append((Flr[2], c1, Cand, LK_WEAK))
                else: LCL.append((Flr[2], c1, Cand, LK_STWK))
        # f0 = len(F[0]); f1 = len(F[1]); f2 = len(F[2])
        # if f0 > 1 and not f1 and not f2:
        #     LCL.append((sorted(F[0]), c, Cand, LK_STWK))
        # elif not f0 and f1 > 1 and not f2:
        #     LCL.append((sorted(F[1]), c, Cand, LK_STWK))
        # elif not f0 and not f1 and f2 > 1:
        #     LCL.append((sorted(F[2]), c, Cand, LK_STWK))

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

def cells_seen_by_both(r1, c1, r2, c2):
    # returns a list of (r, c) tuples that both cells can see.  Both cells are
    # in different boxes.

    f1 = (r1//3)*3; f2 = (r2//3)*3
    t1 = (c1//3)*3; t2 = (c2//3)*3

    if f1 == f2 and t1 == t2:
        return []  # r1,c1 and r2,c2 cannot be in same box.
    if f1 == f2:  # both cells on same floor
        return [(r1, t2), (r1, t2+1), (r1, t2+2), (r2, t1), (r2, t1+1), (r2, t1+2)]
    if t1 == t2:  # both cells in the same tower
        return [(f1, c2), (f1+1, c2), (f1+2, c2), (f2, c1), (f2+1, c1), (f2+2, c1)]
    # boxes cannot see each other
    return [(r1, c2), (r2, c1)]

def ccells_are_linked(r1, c1, Cand1, r2, c2, Cand2, Cands):
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

    R1 = {r1} if isinstance(r1, int) else r1
    C1 = {c1} if isinstance(c1, int) else c1
    R2 = {r2} if isinstance(r2, int) else r2
    C2 = {c2} if isinstance(c2, int) else c2
    R1iR2 = R1 & R2; C1iC2 = C1 & C2
    R1uR2 = R1 | R2; C1uC2 = C1 | C2

    if R1iR2 and C1iC2:  # the two (grouped) ccells intersect
        if Cand1 == Cand2:  # cell cannot link to itself
            return LK_ERR
        elif r1 == r2 and c1 == c2 and len(Cands[r1][c1]) == 2:  # only possible if all scalars
            return LK_STWK
        else:
            return LK_WEAK

    if Cand1 != Cand2:  # Cands must be same value if ccells are different or grouped ccells do not intersect.
        return LK_ERR

    Ccells = []
    for r in R1:
        for c in C1:
            Ccells.append((r, c))
    for r in R2:
        for c in C2:
            Ccells.append((r, c))

    for f in [0, 3, 6]:
        for t in [0, 3, 6]:
            if R1uR2 <= {f, f+1, f+2} and C1uC2 <= {t, t+1, t+2}:
                # (Grouped) Ccells in the same box.
                for r in [f, f+1, f+2]:
                    for c in [t, t+1, t+2]:
                        if (r, c) in Ccells: continue
                        if Cand1 in Cands[r][c]: return LK_WEAK
                return LK_STWK

    if R1iR2:  # if the rows intersect
        for r in sorted(R1iR2):
            for c in range(9):
                if (r, c) in Ccells: continue
                if Cand1 in Cands[r][c]: return LK_WEAK
        return LK_STWK
    if C1iC2:  # if the columns intersect
        for c in sorted(C1iC2):
            for r in range(9):
                if (r, c) in Ccells: continue
                if Cand1 in Cands[r][c]: return LK_WEAK
        return LK_STWK
    return LK_NONE


    # if R1iR2:  # if the rows intersect: (can only happen if on the same floor).
    #     f = (list(R1iR2)[0]//3)*3
    #     for t in [0, 3, 6]:  # if they are in same tower as well as floor, ie house
    #         Cx = {t, t+1, t+2} - C1uC2
    #         if not Cx:  # Cx is either empty or single value set if ccells in same tower.
    #             # if Cx is empty, then if the remaining cells do not contain the candidate
    #             # then there is a strong link, else it is a weak link.
    #             for ra in [f, f+1, f+2]:
    #                 for ca in [t, t+1, t+2]:
    #                     if (ra, ca, Cand1) in Ccells: continue
    #                     return LK_WEAK
    #             return LK_STWK
    #         elif len(Cx) ==  1:
    #             ca = Cx.pop()
    #             for ra in [f, f+1, f+2]:
    #                 if Cand1 == Cands[ra][ca]:
    #                     return LK_WEAK
    #             return LK_STWK
    # # not in the same tower.
    # # if these ccells contain the only candidate values in the intersection
    # # of rows across the remaining columns, then it is a strong link, else weak.
    # for ra in sorted(R1iR2):
    #     for ca in range(9):
    #         if (ra, ca, Cand1) in Ccells: continue
    #         return LK_WEAK
    #     return LK_STWK
    #
    # for ca in sorted(C1iC2):
    #     for ra in range(9):
    #         if (ra, ca, Cand1) in Ccells: continue
    #         return LK_WEAK
    #     return LK_STWK
    # return LK_NONE
    #

    # if Cand1 not in Cands[r1][c1] or Cand1 not in Cands[r2][c2]:
    #     return LK_ERR  # Candidate not in one or both cells
    # if r1 == r2:  # cells in same row.
    #     for c in set(range(9)) - {c1, c2}:
    #         if Cand1 in Cands[r1][c]: return LK_WEAK
    #     return LK_STWK
    #
    # if c1 == c2:  # cells in same col
    #     for r in set(range(9)) - {r1, r2}:
    #         if Cand1 in Cands[r][c1]: return LK_WEAK
    #     return LK_STWK
    #
    # f1 = (r1//3)*3; f2 = (r2//3)*3
    # t1 = (c1//3)*3; t2 = (c2//3)*3
    # if f1 == f2 and t1 == t2:  # cells are in the same box.
    #     n = 0
    #     for r in [f1, f1+1, f1+2]:
    #         for c in [t1, t1+1, t1+2]:
    #             if Cand1 in Cands[r][c]: n += 1
    #             if n > 2: return LK_WEAK
    #     if n == 2: return LK_STWK
    # # No link found.
    # return LK_NONE

def are_ccells_aic_linked(r1, c1, Cand1, r2, c2, Cand2, Cands, AIC = False, UsedCcells = None, Depth = 0):
    # if an odd length AIC with strong end links can be found then return a list
    # of the nodes of the chain, else None.  Includes same cand in house or
    # diff cands in a cell

    # UsedCcells are only used for descending into the recursion, not ascending
    # out of it.

#    if depth == 10: return []
#    print ("aic_linked", depth)
    lk = ccells_are_linked(r1, c1, Cand1, r2, c2, Cand2, Cands)
    if lk & LK_ERR: return []

    if lk & LK_STRG:
        return [(r1, c1, Cand1, LK_STRG), (r2, c2, Cand2, -1)]

    if not AIC: return []

    # build out a list of strong links from both ccells 1 and 2
    LCLa = list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STRG)
    LCLb = list_ccells_linked_to(r2, c2, Cand2, Cands, LK_STRG)
    if not (LCLa and LCLb): return []
    if UsedCcells is None: UsedCcells = []
    for ra, ca, Canda, Lka in LCLa:
        if (ra, ca, Canda) in UsedCcells: continue
        for rb, cb, Candb, Lkb in LCLb:
            if (rb, cb, Candb) in UsedCcells: continue
            if (ra, ca, Canda) == (rb, cb, Candb): continue
            lk = ccells_are_linked(ra, ca, Canda, rb, cb, Candb, Cands)
            if lk == LK_ERR: return []
            if lk == LK_WEAK:
                return [(r1, c1, Cand1, Lka), (ra, ca, Canda, LK_WEAK),
                        (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
            elif lk == LK_STWK:
                return [(r1, c1, Cand1, Lka), (ra, ca, Canda, LK_WKST),
                        (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
            else:  # LK_NONE:
                # build out nodes of weak links from ccells a and b.
                UC1 = UsedCcells + [(ra, ca, Canda), (rb, cb, Candb)]
                LCLc = list_ccells_linked_to(ra, ca, Canda, Cands)
                LCLd = list_ccells_linked_to(rb, cb, Candb, Cands)
                for rc, cc, Candc, Lkc in LCLc:
                    if (rc, cc, Candc) in UC1: continue
                    for rd, cd, Candd, Lkd in LCLd:
                        if (rd, cd, Candd) in UC1: continue
                        if (rc, cc, Candc) == (rd, cd, Candd): continue
                        UC1 += [(rc, cc, Candc), (rd, cd, Candd)]
                        Nodes = are_ccells_aic_linked(rc, cc, Candc, rd, cd, Candd, Cands,
                                                      AIC = AIC, UsedCcells = UC1, Depth = Depth+1)
                        if len(Nodes):
                            Nodes.pop()
                            if Lkc == LK_STWK: Lkc = LK_WKST
                            if Lkd == LK_STWK: Lkd = LK_WKST
                            return [(r1, c1, Cand1, Lka), (ra, ca, Canda, Lkc)] + Nodes + \
                                   [(rd, cd, Candd, Lkd), (rb, cb, Candb, Lkb), (r2, c2, Cand2, -1)]
    return []

def are_ccells_weakly_linked(r1, c1, Cand1, r2, c2, Cand2, Cands, AIC = 0):
    # if the ccells are directly connected by a weak link, or are AIC linked in
    # an odd length chain with weak end links, then return the list of
    # connected ccells.
    # AIC == 0:  Only look for a weak link between the ccells.
    # AIC == 1:  Only look for a weak link or The Ccells see a strong link (A-X=Y-B)
    # AIC == 2:  Look for weak link, see strong link or weak-ended AIC. The ccells are weakly linked (A-P=Q-R=. . .=Z-B)

    # First check to see if the ccells are directly linked.
    lk = ccells_are_linked(r1, c1, Cand1, r2, c2, Cand2, Cands)
    if lk & LK_ERR: return []

    if lk & LK_STRG:
        return [(r1, c1, Cand1, LK_WKST), (r2, c2, Cand2, -1)]
    elif lk & LK_WEAK:
        return [(r1, c1, Cand1, LK_WEAK), (r2, c2, Cand2, -1)]

    if not AIC: return []

    # Then check if the two ccells see a strong link or strong end link AIC.
    LCLa = list_ccells_linked_to(r1, c1, Cand1, Cands)
    LCLb = list_ccells_linked_to(r2, c2, Cand2, Cands)
    if not (len(LCLa) and len(LCLb)): return []
    if AIC == 1: AIC = False
    else: AIC = True
    for ra, ca, Canda, Lka in LCLa:
        for rb, cb, Candb, Lkb in LCLb:
            if (ra, ca, Canda) == (rb, cb, Candb): continue
            UsedCcells = [(r1, c1, Cand1), (r2, c2, Cand2), (ra, ca, Canda), (rb, cb, Candb)]
            Nodes = are_ccells_aic_linked(ra, ca, Canda, rb, cb, Candb, Cands,
                                          AIC = AIC, UsedCcells = UsedCcells)
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

# def cells_see_a_strong_link(r1, c1, r2, c2, Cand, Cands, Depth = 0):
#     # either an direct strong link or through an X-Chain.
#     # Returns the coords of the strong link,
#
#     LCL1 = list_cells_linked_to(r1, c1, Cand, Cands)
#     LCL2 = list_cells_linked_to(r2, c2, Cand, Cands)
#     if not (len(LCL1) and len(LCL2)): return False
#     for ra, ca, Lka in LCL1:
#         for rb, cb, Lkb in LCL2:
#             if cells_are_strongly_linked(ra, ca, rb, cb, Cand, Cands, Depth):
#                 return True
#     return False
#
# def cells_are_strongly_linked(r1, c1, r2, c2, Cand, Cands, Depth=0):
#     # Linked through an X-chain where the starting and ending link are strong.
#     # (An X-chain is an alternating strong/weak link chain on the same candidate
#     # value).  Another implication is that the X-chain has an odd number of
#     # links
#
#     # The simplest case is where the two cells are directly linked by a single
#     # strong link.
#     if cells_are_group_linked(r1, c1, r2, c2, Cand, Cands) & LK_STRG:
#         return True
#     # Now, not so simple, start building out the X-Chain simultaneously from both
#     # ends.  First try two strong links, connected in the middle by a weak link.
#     LCL1 = list_cells_linked_to(r1, c1, Cand, Cands)
#     LCL2 = list_cells_linked_to(r2, c2, Cand, Cands)
#     if not (len(LCL1) and len(LCL2)): return False
#     for ra, ca, Lka in LCL1:
#         for rb, cb, Lkb in LCL2:
#             if Lka & Lkb & LK_STRG:
#                 if cells_in_same_house(ra, ca, rb, cb):  # at least a weak link
#                     return True
#                 if Depth == 1:
#                     continue  # reached the 9 link limit.
#                 if cells_see_a_strong_link(ra, ca, rb, cb, Cand, Cands, Depth+1):
#                     return True
#     return False

# def flist(hl):
#     fl = []  # list()
#     for i in hl:
#         if isinstance(i, list):
#             fl.extend(flist(i))
#         else:
#             fl.append(i)
#     return fl

