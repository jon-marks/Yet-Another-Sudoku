
from copy import copy

from globals import *
from solve_utils import *



# def tech_y_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
#     # Y Wings only involve bi-value cells.   AB sees AC through a different
#     # house to that where it sees BC.  In any cell that sees both BC and AC, C
#     # (if present) can be eliminated.
#     #
#     # Find a cell with 2 cands.  This is cell BC which cands Cb, Cc.
#     # Then look, NS, then EW then in the box for AB.  If AB is found, then look
#     # in the other "directions" for AC.
#
#     if Method != T_UNDEF and Method != T_Y_WING: return -1
#     for r0 in range(9):
#         for c0 in range(9):
#             if len(Cands[r0][c0]) == 2:
#                 #  Found a possible BC, with cands Cb and Cc.  look for AB.
#                 for Cb in Cands[r0][c0]:
#                     # Look along the column (north to south) for AB from BC
#                     for r1 in sorted(set(range(9)) - {r0}):
#                         if len(Cands[r1][c0]) == 2 and Cb in Cands[r1][c0]:
#                             # Found a possible AB with cands Ca and Cb, scan the
#                             # remaining directions (EW, box) for AC.
#                             Ca = (Cands[r1][c0] - {Cb}).pop()
#                             Cc = (Cands[r0][c0] - {Cb}).pop()
#                             # Look West to east.
#                             for c1 in sorted(set(range(9)) - {c0}):
#                                 if Cands[r1][c1] == {Ca, Cc}:
#                                     # found an Y-Wing
#                                     if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, r1, c0, r1, c1,
#                                                                Cands, ElimCands, Step):
#                                         return 0
#                             # Else look in the box.
#                             # but first make sure r1 is not in the same box as r0
#                             rb = r1//3
#                             if rb != r0//3:
#                                 rb *= 3
#                                 cb = (c0//3)*3
#                                 for rb1 in sorted({rb, rb+1, rb+2} - {r0}):
#                                     for cb1 in sorted({cb, cb+1, cb+2} - {c0}):
#                                         if Cands[rb1][cb1] == {Ca, Cc}:
#                                             # found an Y-Wing
#                                             if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, r1, c0, rb1, cb1,
#                                                                        Cands, ElimCands, Step):
#                                                 return 0
#                     # Look for AB in the row (east to west) from BC
#                     for c1 in sorted(set(range(9)) - {c0}):
#                         if len(Cands[r0][c1]) == 2 and Cb in Cands[r0][c1]:
#                             # found a possible AB with cands Ca and Cb, scan the
#                             # remaining directions (NS, box) for AC
#                             Ca = (Cands[r0][c1] - {Cb}).pop()
#                             Cc = (Cands[r0][c0] - {Cb}).pop()
#                             # Look north to south.
#                             for r1 in sorted(set(range(9)) - {r0}):
#                                 if Cands[r1][c1] == {Ca, Cc}:
#                                     # found an Y-Wing
#                                     if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, r0, c1, r1, c1,
#                                                                Cands, ElimCands, Step):
#                                         return 0
#                             # Else look in the box but first make sure c1 is not
#                             # in the same box as c0
#                             cb = c1//3
#                             if cb != c0//3:
#                                 cb *= 3
#                                 rb = (r0//3)*3
#                                 for cb1 in sorted({cb, cb+1, cb+2} - {c0}):
#                                     for rb1 in sorted({rb, rb+1, rb+2} - {r0}):
#                                         if Cands[rb1][cb1] == {Ca, Cc}:
#                                             # found an Y-wing
#                                             if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, r0, c1, rb1, cb1,
#                                                                        Cands, ElimCands, Step):
#                                                 return 0
#                     # look in the box for AB from BC
#                     rb = (r0//3)*3
#                     cb = (c0//3)*3
#                     for rb1 in [rb, rb+1, rb+2]:
#                         for cb1 in [cb, cb+1, cb+2]:
#                             if rb1 != r0 or cb1 != c0:
#                                 if len(Cands[rb1][cb1]) == 2 and Cb in Cands[rb1][cb1]:
#                                     # found a possible AB, scan the remaining directions
#                                     # NS or EW for AC.
#                                     Ca = (Cands[rb1][cb1] -{Cb}).pop()
#                                     Cc = (Cands[r0][c0] - {Cb}).pop()
#                                     # look NS for AC if BC and AB  are not in the same column.
#                                     if c0 != cb1:
#                                         for r1 in sorted(set(range(9)) - {rb1}):
#                                             if Cands[r1][cb1] == {Ca, Cc}:
#                                                 # found an Y-Wing.
#                                                 if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, rb1, cb1, r1, cb1,
#                                                                            Cands, ElimCands, Step):
#                                                     return 0
#                                     # look EW for AC if BC and AB are not in the same raw.
#                                     if r0 != rb1:
#                                         for c1 in sorted(set(range(9)) - {cb1}):
#                                             if Cands[rb1][c1] == {Ca, Cc}:
#                                                 # found an Y-Wing.
#                                                 if _elim_bent_triple_cands(Ca, Cb, Cc, r0, c0, rb1, cb1, rb1, c1,
#                                                                            Cands, ElimCands, Step):
#                                                     return 0
#     return -1

def tech_w_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_W_WING: return -1
    return _tech_w_wings(Grid, Step, Cands, ElimCands, AIC = 1)

def tech_kraken_w_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_W_WING: return -1
    return _tech_w_wings(Grid, Step, Cands, ElimCands, AIC = 2)

def _tech_w_wings(Grid, Step, Cands, ElimCands = None, AIC = 1):
    # Defined by two bi-value cells with the same candidates that cannot
    # directly "see each other, but are connected by a strong link on one of the
    # candidates.  Any other cells with the other candidate value that both
    # bi-value cells see, can eliminate the other candidate value.

    # scan the grid looking for bi-value cells.
    BVList = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2:
                BVList.append([r, c, sorted(Cands[r][c])])
    if len(BVList) > 1:
        BVList = sorted(sorted(BVList, key = lambda a: a[2][1]), key = lambda a: a[2][0])
        for i in range(len(BVList)-1):
            r1, c1, BVCand1 = BVList[i]
            for j in range(i+1, len(BVList)):
                r2, c2, BVCand2 = BVList[j]

                if BVCand1 != BVCand2 or cells_in_same_house(r1, c1, r2, c2): continue
                # Here we have a pair of identical bi-value cells that are not
                # in the same house (because list is sorted on cands, can break
                # when cands are no longer equal
                #
                # Attempt to build a chain on each of the values.  For all links
                # branching out of both BV cells, see if the other ends of the
                # link form a strong link.
                Cand1, Cand2 = BVCand1
                for Cand, Candx in zip([Cand1, Cand2], [Cand2, Cand1]):
                    Nodes = are_ccells_weakly_linked(r1, c1, Cand, r2, c2, Cand, Cands, AIC = AIC)
                    if not Nodes: continue
                    # for r0, c0 in cells_that_see_both(r1, c1, r2, c2):
                    for r0, c0 in cells_that_see_all_of([(r1, c1), (r2, c2)]):
                        if Candx in Cands[r0][c0]:
                            Cands[r0][c0].discard(Candx)
                            if Step[P_OUTC]:
                                Step[P_OUTC].append([P_SEP, ])
                            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0],
                                                 [P_OP, OP_ELIM], [P_VAL, Candx]])
                            if ElimCands is not None:
                                ElimCands[r0][c0].add(Candx)
                    if Step[P_OUTC]:
                        Lks = len(Nodes) - 1
                        Step[P_TECH] = T_W_WING if Lks <= 3 else T_KRAKEN_W_WING
                        Step[P_DIFF] = T[T_W_WING][T_DIFF] + (Lks - 3) * AIC_LK_DIFF
                        Step[P_OUTC].append([P_END, ])
                        Chain = []
                        for (r, c, Cand0, Lk) in Nodes:
                            if Lk == -1:
                                Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c]])
                            else:
                                Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
                        Step[P_COND] = [[P_VAL, Cand1, Cand2], [P_OP, OP_EQ],
                                        [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                        [P_ROW, r2], [P_COL, c2], [P_SEP, ]]
                        Step[P_COND].extend(Chain)
                        Step[P_COND].append([P_END, ])
                        return 0
    return -1

def tech_y_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_Y_WING: return -1
    return _tech_bent_exposed_triples(Grid, Step, Cands, ElimCands, Method = T_Y_WING)

def tech_xyz_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_XYZ_WING: return -1
    return _tech_bent_exposed_triples(Grid, Step, Cands, ElimCands, Method = T_XYZ_WING)

def _tech_bent_exposed_triples(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # a bent (exposed) triple can only be either a Y-Wing or a XYZ-Wing.
    # Note that in a bent triple, the pincers (URC) cells can only have 2 pincers
    # for the pattern to be valid.  If there are three candidates in either/both
    # pincer cells, then there is more than one URC in the pattern invalidating it
    # as a bent triple.

    # The row column search is only applicable to Y wings (each of the three cells
    # only has 2 cands) and each cell is in a separate box.  If the there is a
    # common chute then it will be found in the line/box searches.

    # if Method != T_UNDEF and (Method != T_Y_WING or Method != T_XYZ_WING): return -1

    # look in rows first.
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 3: continue
            for c1 in range(c0+1, 9):
                U = Cands[r][c0] | Cands[r][c1]
                if not 2 <= len(Cands[r][c1]) <= 3 or len(U) != 3 or Cands[r][c0] == Cands[r][c1]: continue
                # Found a 2 cells of the triple in a row.
                BT = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # first scan the columns looking for a potential third cell to make the pattern
                rbz = (r//3)*3
                cb0 = (c0//3)*3; cb1 = (c1//3)*3
                if cb0 == cb1: continue  # need to be in separate boxes, else just looking for an exposed trip in a box again
                for r0 in sorted(set(range(9)) - {rbz, rbz+1, rbz+2}):
                    if len(Cands[r0][c0]) == 2 and len (U | Cands[r0][c0]) == 3:
                        if _bent_subset_elims(BT+[(r0, c0, Cands[r0][c0])], U | Cands[r0][c0], Cands, ElimCands, Step, Method): return 0
                    if len(Cands[r0][c1]) == 2 and len(U | Cands[r0][c1]) == 3:
                        if _bent_subset_elims(BT+[(r0, c1, Cands[r0][c1])], U | Cands[r0][c1], Cands, ElimCands, Step, Method): return 0
                # look in row box patterns
                rb0 = rbz + (r+1)%3; rb1 = rbz + (r+2)%3
                for cbx in {cb0, cb1}:  # use set to eliminate duplicates
                    for ra, ca in [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]:
                        if len(Cands[ra][ca]) == 2 and len(U | Cands[ra][ca]) == 3:
                            if _bent_subset_elims(BT+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, ElimCands, Step, Method):                                 return 0

    # bent triple not found scanning rows, try scanning cols, only necessary to look at col / box patterns, row/col patterns already covered
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 3: continue
            for r1 in range(r0+1, 9):
                U = Cands[r0][c] | Cands[r1][c]
                if not 2 <= len(Cands[r1][c]) <= 3 or len(U) != 3 or Cands[r0][c] == Cands[r1][c]: continue
                BT = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                rb0 = (r0//3)*3; rb1 = (r1//3)*3
                if rb0 == rb1: continue  # not interested in looking for an exposed trip in a box here.
                cbz = (c//3)*3; cb0 = cbz + (c+1)%3; cb1 = cbz + (c+2)%3
                for rbx in {rb0, rb1}:
                    for ra, ca in [(rbx, cb0), (rbx+1, cb0), (rbx+2, cb0), (rbx, cb1), (rbx+1, cb1), (rbx+2, cb1)]:
                        if len(Cands[ra][ca]) == 2 and len(U | Cands[ra][ca]) == 3:
                            if _bent_subset_elims(BT+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, ElimCands, Step, Method): return 0
    return -1

def tech_wxyz_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_WXYZ_WING: return -1
    return _tech_bent_exposed_quads(Grid, Step, Cands, ElimCands, Method = T_WXYZ_WING)

def tech_bent_exposed_quads(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_BENT_EXPOSED_QUAD: return -1
    return _tech_bent_exposed_quads(Grid, Step, Cands, ElimCands, Method = T_BENT_EXPOSED_QUAD)

# def tech_wxyz_wings()
def _tech_bent_exposed_quads(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # URC ==> unrestricted candidate.
    # BQ ==> BentQuad pattern.  list used to accumulate the cells that may form a BQ.
    # CIB ==> Cells in Box.  List of cells in box outside the intersection.
    # U ==> Union of candidates in cells being considered for the BQ.
#    if Method != T_UNDEF and (Method != T_XYZ_WING or Method != T_BENT_EXPOSED_QUAD): return -1

    # look in rows first.
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 4: continue
            for c1 in range(c0+1, 9):
                if not 2 <= len(Cands[r][c1]) <= 4 or len(Cands[r][c0] | Cands[r][c1]) > 4: continue
                BQ = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # 2 Possible candidates in the row, check for row/col BQ's search for two cells that fit the BQ
                # criteria first in c0, then c1.  Look in cols before looking in boxes.
                R = sorted(set(range(9)) - {r})
                for cx in [c0, c1]:  # scan each column
                    for i in len(R)-1:
                        if not 2 <= len(Cands[R[i]][cx]) <= 4 or len(Cands[r][c0] | Cands[r][c1] | Cands[R[i]][cx]) > 4: continue
                        for j in range(i+1, len(R)):
                            U = Cands[r][c0] | Cands[r][c1] | Cands[R[i]][cx] | Cands[R[j]][cx]
                            if not 2 <= len(Cands[R[j]][cx]) <= 4 or len(U) > 4: continue
                            BQ1 = BQ + [(R[i], cx, Cands[R[i]][cx]), (R[j], cx, Cands[R[j]][cx])]
                            if _bent_subset_elims(BQ1, U, Cands, ElimCands, Step, Method): return 0
                # BQ not found in row/col patterns, look at row box patterns
                cb0 = (c0//3)*3; cb1 = (c1//3)*3
                rbz = (r//3)*3; rb0 = rbz + (r+1)%3; rb1 = rbz + (r+2)%3
                for cbx in {cb0, cb1}:  # using a set removes dups.
                    CIB = [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]
                    for i in range(5):
                        ra, ca = CIB[i]
                        if not 2 <= len(Cands[ra][ca]) <= 4 or len(Cands[r][c0] | Cands[r][c1] | Cands[ra][ca]) > 4: continue
                        for j in range(i+1, 6):
                            rb, cb = CIB[j]
                            U = Cands[r][c0] | Cands[r][c1] | Cands[ra][ca] | Cands[rb][cb]
                            if not 2 <= len(Cands[ra][ca]) <= 4 or len(U) > 4: continue
                            BQ1 = BQ + [(ra, ca, Cands[ra][ca]), (rb, cb, Cands[rb][cb])]
                            if _bent_subset_elims(BQ1, U, Cands, ElimCands, Step, Method): return 0
                # BQ not found in row/box patterns with two cells in the row.  Scan for three cells in row pattern
                # first row / cols
                if c0 < 7 and c1 < 8:
                    for c2 in range (c1+1, 9):
                        U = Cands[r][c0] | Cands[r][c1] | Cands[r][c2]
                        if not 2 <= len(Cands[r][c2]) <= 4 or len(U) > 4: continue
                        BQ.append((r, c2, Cands[r][c2]))
                        # three possible cells in a row, first scan down the columns looking for the fourth cell, before
                        # scanning the boxes.
                        for r0 in sorted(set(range(9) - {r})):  # scan down the three cols in parallel for single cell.
                            if 2 <= len(Cands[r0][c0]) <=4 and len(U | Cands[r0][c0]) == 4:
                                if _bent_subset_elims(BQ+[(r0, c0, Cands[r0][c0])], U | Cands[r0][c0], Cands, ElimCands, Step, Method): return 0
                            if 2 <= len(Cands[r0][c1]) <=4 and len(U | Cands[r0][c1]) == 4:
                                if _bent_subset_elims(BQ+[(r0, c1, Cands[r0][c1])], U | Cands[r0][c1], Cands, ElimCands, Step, Method): return 0
                            if 2 <= len(Cands[r0][c2]) <=4 and len(U | Cands[r0][c2]) == 4:
                                if _bent_subset_elims(BQ+[(r0, c2, Cands[r0][c2])], U | Cands[r0][c2], Cands, ElimCands, Step, Method): return 0
                        #  look in row / boxes for patterns.
                        cb2 = (c2//3)*3
                        for cbx in {cb0, cb1, cb2}:  # use a set to remove dups
                            for ra, ca in [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]:
                                if 2 <= len(Cands[ra][ca]) <= 4 and len(U | Cands[ra][ca]) == 4:
                                    if _bent_subset_elims(BQ+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, ElimCands, Step, Method): return 0
    # bent quad not found by scanning rows, try scanning columns, here it would be a duplication of effort to look in row / col patterns
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 4: continue
            for r1 in range (r0+1, 9):
                if not 2 <= len(Cands[r1][c]) <= 4 or len(Cands[r0][c] | Cands[r1][c]) > 4: continue
                BQ = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                rb0 = (r0//3)*3; rb1 = (r1//3)*3
                cbz = (c//3)*3; cb0 = cbz + (c+1)%3; cb1 = cbz + (c+2)%3
                for rbx in {rb0, rb1}:
                    CIB = [(rbx, cb0), (rbx+1, cb0), (rbx+2, cb0), (rbx, cb1), (rbx+1, cb1), (rbx+2, cb1)]
                    for i in range(5):
                        ra, ca = CIB[i]
                        if not 2 <= len(Cands[ra][ca]) <= 4 or len(Cands[r0][c] | Cands[r1][c] | Cands[ra][ca]) > 4: continue
                        for j in range(i+1, 6):
                            rb, cb = CIB[j]
                            U = Cands[r0][c] | Cands[r1][c] | Cands[ra][ca] | Cands[rb][cb]
                            if not 2 <= len(Cands[ra][ca]) <= 4 or len(U) > 4: continue
                            BQ1 = BQ+[(ra, ca, Cands[ra][ca]), (rb, cb, Cands[rb][cb])]
                            if _bent_subset_elims(BQ1, U, Cands, ElimCands, Step, Method): return 0
                            # BQ not found in row/box patterns with two cells in the row.  Scan for three cells in row pattern
                if r0 < 7 and r1 < 8:
                    for r2 in range (r1+1, 9):
                        U = Cands[r0][c] | Cands[r1][c] | Cands[r2][c]
                        if not 2 <= len(Cands[r2][c]) <= 4 or len(U) > 4: continue
                        BQ.append((r2, c, Cands[r2][c]))
                        rb2 = (r2//3)*3
                        for rbx in {rb0, rb1, rb2}:
                            for ra, ca in [(rbx, cb0), (rbx+1, cb0), (rbx+2, cb0), (rbx, cb1), (rbx+1, cb1), (rbx+2, cb1)]:
                                if 2 <= len(Cands[ra][ca]) <= 4 and len(U | Cands[ra][ca]) == 4:
                                    if _bent_subset_elims(BQ+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, ElimCands, Step, Method): return 0
    return -1

def _bent_subset_elims(Cells, UCands, Cands, ElimCands, Step, Method):
    # Checks
    # 1.  only 1 URC
    # 2   ID intersecting cells
    # 3  elim URC from in
    #
    # The candidate that does not see all its same value cands in the pattern is the unrestricted candidate (URC)
    # and there can only be one URC in the bent subset pattern to make eliminations.

    NrCells = len(Cells)
    NrURC = 0
    URC = 0
    for Cand in UCands:
        for i in range(NrCells -1):
            ri, ci, Candsi = Cells[i]
            if Cand not in Candsi: continue
            for j in range(i+1, NrCells):
                rj, cj, Candsj = Cells[j]
                if Cand not in Candsj: continue
                if not cells_in_same_house(ri, ci, rj, cj):
                    NrURC += 1
                    if NrURC == 1: URC = Cand
                    if NrURC > 1: return False
            else: continue

    # NrURC == 1 and URC contains the un-restricted candidate
    URCCells = []
    NrCands = []
    for r0, c0, Cands0 in Cells:
        if URC in Cands0:
            URCCells.append((r0, c0))
        NrCands.append(len(Cands0))

    if NrCells == 3:
        if Method == T_Y_WING and NrCands[0] == NrCands[1] == NrCands[2] == 2: Step[P_TECH] = T_Y_WING
        elif Method == T_XYZ_WING: Step[P_TECH] = T_XYZ_WING
        else: return False
    else:  # NrCells == 4
        TwoCands = FourCands = 0
        for NrCand in NrCands:
            if NrCands == 2: TwoCands += 1
            elif NrCands == 4: FourCands += 1
        if Method == T_WXYZ_WING and TwoCands == 3 and FourCands == 1: Step[P_TECH] = T_WXYZ_WING
        elif Method == T_BENT_EXPOSED_QUAD: Step[P_TECH] = T_BENT_EXPOSED_QUAD
        else: return False

    # if NrURC == 1:  # Found a single URC.
    #     URCCells = []
    #     NrCands = []
    #     for r0, c0, Cands0 in Cells:
    #         if URC in Cands0: URCCells.append((r0, c0))
    #         NrCands.append(len(Cands0))

    for r0, c0 in cells_that_see_all_of(URCCells):
        if URC in Cands[r0][c0]:
            Cands[r0][c0].discard(URC)
            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, URC]])
            if ElimCands is not None:
                ElimCands[r0][c0].add(URC)
    if Step[P_OUTC]:
        # if NrCells == 3:
        #     if len(Cells[0][2]) == len(Cells[1][2]) == len(Cells[2][2]) == 2: Step[P_TECH] = T_Y_WING
        #     else: Step[P_TECH] = T_XYZ_WING
        # else:
        #     TwoCands = FourCands = 0
        #     for NrCand in NrCands:
        #         if NrCands == 2: TwoCands += 1
        #         elif NrCands == 4: FourCands += 1
        #     if TwoCands == 3 and FourCands == 1: Step[P_TECH] = T_WXYZ_WING
        #     else: Step[P_TECH] = T_BENT_EXPOSED_QUAD
        Step[P_OUTC].append([P_END, ])
        for r0, c0, Cands0 in Cells:
            if Step[P_COND]: Step[P_COND].append([P_CON, ])
            Step[P_COND].extend([[P_VAL, copy(Cands0)], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
        Step[P_COND].append([P_END, ])
        return True
    return False

# def _elim_bent_triple_cands(Ca, Cb, Cc, Rbc, Cbc, Rab, Cab, Rac, Cac, Cands, ElimCands, Step):
#     #  [Rbc][Cbc] are the coordinates in the intersection of the two houses.
#
#     for r0, c0 in cells_that_see_both(Rbc, Cbc, Rac, Cac):
#         if Cc in Cands[r0][c0]:
#             Cands[r0][c0].discard(Cc)
#             if Step[P_OUTC]:
#                 Step[P_OUTC].append([P_SEP, ])
#             Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cc]])
#             if ElimCands is not None:
#                 ElimCands[r0][c0].add(Cc)
#     if Step[P_OUTC]:
#         Step[P_TECH] = T_Y_WING
#         Step[P_OUTC].append([P_END, ])
#         Step[P_COND] = [[P_VAL, Cb, Cc], [P_OP, OP_EQ], [P_ROW, Rbc], [P_COL, Cbc], [P_CON, ],
#                         [P_VAL, Ca, Cb], [P_OP, OP_EQ], [P_ROW, Rab], [P_COL, Cab], [P_CON, ],
#                         [P_VAL, Ca, Cc], [P_OP, OP_EQ], [P_ROW, Rac], [P_COL, Cac], [P_END, ]]
#         return True
#     return False
