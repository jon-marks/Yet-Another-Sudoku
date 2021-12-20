
from copy import copy

from globals import *
from solve_utils import *

def tech_y_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_Y_WING: return -2
    return _tech_bent_exposed_triples(Grid, Step, Cands, Method = T_Y_WING)

def tech_xyz_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_XYZ_WING: return -2
    return _tech_bent_exposed_triples(Grid, Step, Cands, Method = T_XYZ_WING)

def tech_wxyz_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_WXYZ_WING: return -2
    return _tech_bent_exposed_quads(Grid, Step, Cands, Method = T_WXYZ_WING)

def tech_bent_exposed_quads(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_BENT_EXPOSED_QUAD: return -2
    return _tech_bent_exposed_quads(Grid, Step, Cands, Method = T_BENT_EXPOSED_QUAD)



# def _w_wings(Grid, Step, Cands, AIC = 1, GrpLks = False):
#     # Defined by two bi-value cells with the same candidates that cannot
#     # directly "see each other, but are connected by a strong link on one of the
#     # candidates.  Any other cells with the other candidate value that both
#     # bi-value cells see, can eliminate the other candidate value.
#
#     # scan the grid looking for bi-value cells.
#     BVList = []
#     for r in range(9):
#         for c in range(9):
#             if len(Cands[r][c]) == 2:
#                 BVList.append([r, c, sorted(Cands[r][c])])
#     if len(BVList) > 1:
#         BVList = sorted(sorted(BVList, key = lambda a: a[2][1]), key = lambda a: a[2][0])
#         for i in range(len(BVList)-1):
#             r1, c1, BVCand1 = BVList[i]
#             for j in range(i+1, len(BVList)):
#                 r2, c2, BVCand2 = BVList[j]
#
#                 if BVCand1 != BVCand2 or cells_in_same_house(r1, c1, r2, c2): continue
#                 # Here we have a pair of identical bi-value cells that are not
#                 # in the same house (because list is sorted on cands, can break
#                 # when cands are no longer equal
#                 #
#                 # Attempt to build a chain on each of the values.  For all links
#                 # branching out of both BV cells, see if the other ends of the
#                 # link form a strong link.
#                 Cand1, Cand2 = BVCand1
#                 for Cand, Candx in zip([Cand1, Cand2], [Cand2, Cand1]):
#                     Nodes = are_ccells_weakly_linked(r1, c1, Cand, r2, c2, Cand, Cands, AIC = AIC, GrpLks = GrpLks)
#                     if not Nodes: continue
#                     # for r0, c0 in cells_that_see_both(r1, c1, r2, c2):
#                     for r0, c0 in cells_that_see_all_of([(r1, c1), (r2, c2)]):
#                         if Candx in Cands[r0][c0]:
#                             Cands[r0][c0].discard(Candx)
#                             if Step[P_OUTC]:
#                                 Step[P_OUTC].append([P_SEP, ])
#                             Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0],
#                                                  [P_OP, OP_ELIM], [P_VAL, Candx]])
#                     if Step[P_OUTC]:
#                         Lks = len(Nodes) - 1
#                         NrLks = NrGrpLks = 0
#                         Step[P_TECH] = T_W_WING if Lks <= 3 else T_KRAKEN_W_WING
#                         Step[P_OUTC].append([P_END, ])
#                         Chain = []
#                         for (r, c, Cand0, Lk) in Nodes:
#                             if isinstance(r, set) or isinstance(c, set): GrpLks += 1
#                             if Lk == -1:
#                                 Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c]])
#                             else:
#                                 NrLks += 1
#                                 Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
#                         Step[P_DIFF] = T[T_W_WING][T_DIFF] + (Lks - 3 - NrGrpLks) * KRAKEN_LK_DIFF + GrpLks * GRP_LK_DIFF
#                         Step[P_PTRN] = [[P_VAL, Cand1, Cand2], [P_OP, OP_EQ],
#                                         [P_ROW, r1], [P_COL, c1], [P_CON, ],
#                                         [P_ROW, r2], [P_COL, c2], [P_SEP, ]]
#                         Step[P_PTRN].extend(Chain)
#                         Step[P_PTRN].append([P_END, ])
#                         return 0
#     return -1

def _tech_bent_exposed_triples(Grid, Step, Cands, Method = T_UNDEF):
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
                    if len(Cands[r0][c0]) == 2 and len(U | Cands[r0][c0]) == 3:
                        if _bent_subset_elims(BT+[(r0, c0, Cands[r0][c0])], U | Cands[r0][c0], Cands, Step, Method): return 0
                    if len(Cands[r0][c1]) == 2 and len(U | Cands[r0][c1]) == 3:
                        if _bent_subset_elims(BT+[(r0, c1, Cands[r0][c1])], U | Cands[r0][c1], Cands, Step, Method): return 0
                # look in row box patterns
                rb0 = rbz + (r+1)%3; rb1 = rbz + (r+2)%3
                for cbx in {cb0, cb1}:  # use set to eliminate duplicates
                    for ra, ca in [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]:
                        if len(Cands[ra][ca]) == 2 and len(U | Cands[ra][ca]) == 3:
                            if _bent_subset_elims(BT+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, Step, Method): return 0

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
                            if _bent_subset_elims(BT+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, Step, Method): return 0
    return -1


def _tech_bent_exposed_quads(Grid, Step, Cands, Method = T_UNDEF):
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
                    for i in range(len(R)-1):
                        if not 2 <= len(Cands[R[i]][cx]) <= 4 or len(Cands[r][c0] | Cands[r][c1] | Cands[R[i]][cx]) > 4: continue
                        for j in range(i+1, len(R)):
                            U = Cands[r][c0] | Cands[r][c1] | Cands[R[i]][cx] | Cands[R[j]][cx]
                            if not 2 <= len(Cands[R[j]][cx]) <= 4 or len(U) > 4: continue
                            BQ1 = BQ + [(R[i], cx, Cands[R[i]][cx]), (R[j], cx, Cands[R[j]][cx])]
                            if _bent_subset_elims(BQ1, U, Cands, Step, Method): return 0
                # BQ not found in row/col patterns, look at row box patterns
                cb0 = (c0//3)*3; cb1 = (c1//3)*3
                rbz = (r//3)*3; rb0 = rbz + (r+1)%3; rb1 = rbz + (r+2)%3
                if cb0 != cb1:  # the 2 cells cannot be in the same box, else it is just an exposed quad in a box
                    for cbx in [cb0, cb1]:
                        CIB = [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]
                        for i in range(5):
                            ra, ca = CIB[i]
                            if not 2 <= len(Cands[ra][ca]) <= 4 or len(Cands[r][c0] | Cands[r][c1] | Cands[ra][ca]) > 4: continue
                            for j in range(i+1, 6):
                                rb, cb = CIB[j]
                                U = Cands[r][c0] | Cands[r][c1] | Cands[ra][ca] | Cands[rb][cb]
                                if not 2 <= len(Cands[rb][cb]) <= 4 or len(U) > 4: continue
                                BQ1 = BQ + [(ra, ca, Cands[ra][ca]), (rb, cb, Cands[rb][cb])]
                                if _bent_subset_elims(BQ1, U, Cands, Step, Method): return 0
                # BQ not found in row/box patterns with two cells in the row.  Scan for three cells in row pattern
                # first row / cols
                if c0 < 7 and c1 < 8:
                    for c2 in range(c1+1, 9):
                        U = Cands[r][c0] | Cands[r][c1] | Cands[r][c2]
                        if not 2 <= len(Cands[r][c2]) <= 4 or len(U) > 4: continue
                        # BQ.append((r, c2, Cands[r][c2]))
                        BQ1 = BQ + [(r, c2, Cands[r][c2])]
                        # three possible cells in a row, first scan down the columns looking for the fourth cell, before
                        # scanning the boxes.
                        for r0 in sorted(set(range(9)) - {r}):  # scan down the three cols in parallel for single cell.
                            if 2 <= len(Cands[r0][c0]) <=4 and len(U | Cands[r0][c0]) == 4:
                                if _bent_subset_elims(BQ1+[(r0, c0, Cands[r0][c0])], U | Cands[r0][c0], Cands, Step, Method): return 0
                            if 2 <= len(Cands[r0][c1]) <=4 and len(U | Cands[r0][c1]) == 4:
                                if _bent_subset_elims(BQ1+[(r0, c1, Cands[r0][c1])], U | Cands[r0][c1], Cands, Step, Method): return 0
                            if 2 <= len(Cands[r0][c2]) <=4 and len(U | Cands[r0][c2]) == 4:
                                if _bent_subset_elims(BQ1+[(r0, c2, Cands[r0][c2])], U | Cands[r0][c2], Cands, Step, Method): return 0
                        #  look in row / boxes for patterns.
                        cb2 = (c2//3)*3
                        if not (cb0 == cb1 == cb2):  # if the three cells are in the same box then we are just looking for an exposed quad in a box
                            for cbx in {cb0, cb1, cb2}:  # use a set to remove dups
                                for ra, ca in [(rb0, cbx), (rb0, cbx+1), (rb0, cbx+2), (rb1, cbx), (rb1, cbx+1), (rb1, cbx+2)]:
                                    if 2 <= len(Cands[ra][ca]) <= 4 and len(U | Cands[ra][ca]) == 4:
                                        if _bent_subset_elims(BQ1+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, Step, Method): return 0
    # bent quad not found by scanning rows, try scanning columns, here it would be a duplication of effort to look in row / col patterns
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 4: continue
            for r1 in range(r0+1, 9):
                if not 2 <= len(Cands[r1][c]) <= 4 or len(Cands[r0][c] | Cands[r1][c]) > 4: continue
                BQ = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                rb0 = (r0//3)*3; rb1 = (r1//3)*3
                cbz = (c//3)*3; cb0 = cbz + (c+1)%3; cb1 = cbz + (c+2)%3
                if rb0 != rb1:  # the 2 cells cannot be in the same box, else it is just an exposed quad in a box
                    for rbx in [rb0, rb1]:
                        CIB = [(rbx, cb0), (rbx+1, cb0), (rbx+2, cb0), (rbx, cb1), (rbx+1, cb1), (rbx+2, cb1)]
                        for i in range(5):
                            ra, ca = CIB[i]
                            if not 2 <= len(Cands[ra][ca]) <= 4 or len(Cands[r0][c] | Cands[r1][c] | Cands[ra][ca]) > 4: continue
                            for j in range(i+1, 6):
                                rb, cb = CIB[j]
                                U = Cands[r0][c] | Cands[r1][c] | Cands[ra][ca] | Cands[rb][cb]
                                if not 2 <= len(Cands[rb][cb]) <= 4 or len(U) > 4: continue
                                BQ1 = BQ+[(ra, ca, Cands[ra][ca]), (rb, cb, Cands[rb][cb])]
                                if _bent_subset_elims(BQ1, U, Cands, Step, Method): return 0
                                # BQ not found in row/box patterns with two cells in the row.  Scan for three cells in row pattern
                if r0 < 7 and r1 < 8:
                    for r2 in range(r1+1, 9):
                        U = Cands[r0][c] | Cands[r1][c] | Cands[r2][c]
                        if not 2 <= len(Cands[r2][c]) <= 4 or len(U) > 4: continue
                        BQ1 = BQ + [(r2, c, Cands[r2][c])]
                        rb2 = (r2//3)*3
                        if not (rb0 == rb1 == rb2):  # if the three cells are in the same box then we are just looking for an exposed quad in a box
                            for rbx in {rb0, rb1, rb2}:
                                for ra, ca in [(rbx, cb0), (rbx+1, cb0), (rbx+2, cb0), (rbx, cb1), (rbx+1, cb1), (rbx+2, cb1)]:
                                    if 2 <= len(Cands[ra][ca]) <= 4 and len(U | Cands[ra][ca]) == 4:
                                        if _bent_subset_elims(BQ1+[(ra, ca, Cands[ra][ca])], U | Cands[ra][ca], Cands, Step, Method): return 0
    return -1

def _bent_subset_elims(Cells, UCands, Cands, Step, Method):
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
                    if NrURC == 1:
                        URC = Cand
                        break
                    if NrURC > 1: return False
            else: continue
            break

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
            if NrCand == 2: TwoCands += 1
            elif NrCand == 4: FourCands += 1
        if Method == T_WXYZ_WING and TwoCands == 3 and FourCands == 1: Step[P_TECH] = T_WXYZ_WING
        elif Method == T_BENT_EXPOSED_QUAD: Step[P_TECH] = T_BENT_EXPOSED_QUAD
        else: return False

    for r0, c0 in cells_that_see_all_of(URCCells):
        if URC in Cands[r0][c0]:
            Cands[r0][c0].discard(URC)
            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, URC]])
    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        for r0, c0, Cands0 in Cells:
            if Step[P_PTRN]: Step[P_PTRN].append([P_CON, ])
            Step[P_PTRN].extend([[P_VAL, copy(Cands0)], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
        Step[P_PTRN].append([P_END, ])
        return True
    return False
