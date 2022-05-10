
from copy import copy

from globals import *
from solve_utils import *

# def tech_y_wings(Grid, Step, Cands, Method = T_UNDEF):
#     if Method != T_UNDEF and Method != T_Y_WING: return -2
#     return _tech_bent_exposed_triples(Grid, Step, Cands, Method = T_Y_WING)
#
# def tech_xyz_wings(Grid, Step, Cands, Method = T_UNDEF):
#     if Method != T_UNDEF and Method != T_XYZ_WING: return -2
#     return _tech_bent_exposed_triples(Grid, Step, Cands, Method = T_XYZ_WING)
#
# def tech_wxyz_wings(Grid, Step, Cands, Method = T_UNDEF):
#     if Method != T_UNDEF and Method != T_WXYZ_WING: return -2
#     return _tech_bent_exposed_quads(Grid, Step, Cands, Method = T_WXYZ_WING)
#
# def tech_bent_exposed_quads(Grid, Step, Cands, Method = T_UNDEF):
#     if Method != T_UNDEF and Method != T_BENT_EXPOSED_QUAD: return -2
#     return _tech_bent_exposed_quads(Grid, Step, Cands, Method = T_BENT_EXPOSED_QUAD)

# W-Wings are treated as the AI_chains that they are, see solve_ai_chains.py


def tech_bent_exposed_triples(Grid, Step, Cands, Methods):
    # a bent (exposed) triple can only be either a Y-Wing or a XYZ-Wing.
    # Note that in a bent triple, the pincers (URC) cells can only have 2 pincers
    # for the pattern to be valid.  If there are three candidates in either/both
    # pincer cells, then there is more than one URC in the pattern invalidating it
    # as a bent triple.

    # The row column search is only applicable to Y wings (each of the three cells
    # only has 2 cands) and each cell is in a separate box.  If the there is a
    # common chute then it will be found in the line/box searches.


    # look for row -> box/col patterns.
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 3: continue
            for c1 in range(c0+1, 9):
                U = Cands[r][c0] | Cands[r][c1]
                if not 2 <= len(Cands[r][c1]) <= 3 or len(U) != 3 or Cands[r][c0] == Cands[r][c1]: continue
                # Found 2 cells of the triple in a row.
                BT = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # first scan the columns looking for a potential third cell to make the pattern
                for r0 in range(9):
                    if r0 == r: continue
                    if len(Cands[r0][c0]) == 2 and len(U | Cands[r0][c0]) == 3:
                        if bent_subset_elims(BT+[(r0, c0, Cands[r0][c0])], U | Cands[r0][c0], Cands, Step, Methods): return 0
                    if len(Cands[r0][c1]) == 2 and len(U | Cands[r0][c1]) == 3:
                        if bent_subset_elims(BT+[(r0, c1, Cands[r0][c1])], U | Cands[r0][c1], Cands, Step, Methods): return 0
                #  Then scan boxes looking for potential third cell.
                rb = (r//3)*3; cb0 = (c0//3)*3; cb1 = (c1//3)*3
                if cb0 == cb1: continue  # pattern only wants one cell outside of the intersection.
                for b in range(9):
                    r2 = rb + b//3; c2 = cb0 + b%3; c3 = cb1 + b%3
                    if r2 != r and c2 != c0 and len(Cands[r2][c2]) == 2 and len(U | Cands[r2][c2]) == 3:
                        if bent_subset_elims(BT+[(r2, c2, Cands[r2][c2])], U | Cands[r2][c2], Cands, Step, Methods): return 0
                    if r2 != r and c3 != c0 and len(Cands[r2][c3]) == 2 and len(U | Cands[r2][c3]) == 3:
                        if bent_subset_elims(BT+[(r2, c3, Cands[r2][c3])], U | Cands[r2][c3], Cands, Step, Methods): return 0

    # not found - look for col -> row/box bent triple not found scanning rows, try scanning cols, only necessary to look at col / box patterns, row/col patterns already covered
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 3: continue
            for r1 in range(r0+1, 9):
                U = Cands[r0][c] | Cands[r1][c]
                if not 2 <= len(Cands[r1][c]) <= 3 or len(U) != 3 or Cands[r0][c] == Cands[r1][c]: continue
                # Found two cells of the triple in a col.
                BT = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                # already looked for col/row (same as row/col) patterns, only need to look for col/box patterns
                rb0 = (r0//3)*3; rb1 = (r1//3)*3; cb = (c//3)*3
                for b in range(9):
                    r2 = rb0 + b//3; r3 = rb1 + b//3; c2 = cb + b%3
                    if r2 != r0 and c2 != c and len(Cands[r2][c2]) == 2 and len(U | Cands[r2][c2]) == 3:
                        if bent_subset_elims(BT+[(r2, c2, Cands[r2][c2])], U | Cands[r2][c2], Cands, Step, Methods): return 0
                    if r3 != r0 and c2 != c and len(Cands[r3][c2]) == 2 and len(U | Cands[r3][c2]) == 3:
                        if bent_subset_elims(BT+[(r3, c2, Cands[r3][c2])], U | Cands[r3][c2], Cands, Step, Methods): return 0
    return -1


def tech_bent_exposed_quads(Grid, Step, Cands, Methods):
    # URC ==> unrestricted candidate.
    # BQ ==> BentQuad pattern.  list used to accumulate the cells that may form a BQ.
    # CIB ==> Cells in Box.  List of cells in box outside the intersection.
    # U ==> Union of candidates in cells being considered for the BQ.

    # look for patterns starting with a row
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 4: continue
            for c1 in range(c0+1, 9):
                U = Cands[r][c0] | Cands[r][c1]
                if not 2 <= len(Cands[r][c1]) <= 4 or len(U) > 4: continue
                BQ = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # 2 possible cells in the row, if the second cell is not at the end of the row, look for a third row cell
                for c2 in range(c1+1, 9):
                    U1 = U | Cands[r][c2]
                    if not 2 <= len(Cands[r][c2]) <= 4 or len(U1) > 4: continue
                    BQ1 = BQ + [(r, c2, Cands[r][c2])]
                    # 3rd possible cell found, look in cols look for row / columns pattern for the 4th cell of the BEQ.
                    for r0 in range(9):
                        if r0 == r: continue
                        if 2 <= len(Cands[r0][c0]) <= 4 and len(U1 | Cands[r0][c0]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c0, Cands[r0][c0])], U1 | Cands[r0][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r0][c1]) <= 4 and len(U1 | Cands[r0][c1]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c1, Cands[r0][c1])], U1 | Cands[r0][c1], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r0][c2]) <= 4 and len(U1 | Cands[r0][c2]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c2, Cands[r0][c2])], U1 | Cands[r0][c2], Cands, Step, Methods): return 0
                    # 4th not found in col, look in boxes
                    rb = (r//3)*3; CB = sorted({c0//3, c1//3, c2//3})  # set to remove dup boxes to search.
                    if len(CB) == 1: continue  # pattern wants at least one cell outside the intersection
                    for b in range(9):
                        for cb in CB:
                            r3 = rb + b//3; c3 = cb*3 +b%3
                            if r3 != r and c3 != c0 and c3 != c1 and c3 != c2 and len(Cands[r3][c3]) == 2 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                #  Cells 1 and 2 in the row, look for cells 3 and 4 in the cols
                for r1 in range(8):
                    if r1 != r and 2 <= len(Cands[r1][c0]) <= 4 and len(U | Cands[r1][c0]) == 4:
                        BQ1 = BQ + [(r1, c0, Cands[r1][c0])]; U1 = U | Cands[r1][c0]
                        for r2 in range(r1+1, 9):
                            if r2 != r and 2 <= len(Cands[r2][c0]) <= 4 and len(U1 | Cands[r2][c0]) == 4:
                                if bent_subset_elims(BQ1+[(r2, c0, Cands[r2][c0])], U1 | Cands[r2][c0], Cands, Step, Methods): return 0
                    if r1 != r and 2 <= len(Cands[r1][c1]) <= 4 and len(U | Cands[r1][c1]) == 4:
                        BQ1 = BQ + [(r1, c1, Cands[r1][c1])]; U1 = U | Cands[r1][c1]
                        for r2 in range(r1+1, 9):
                            if r2 != r and 2 <= len(Cands[r2][c1]) <= 4 and len(U1 | Cands[r2][c1]) == 4:
                                if bent_subset_elims(BQ1+[(r2, c1, Cands[r2][c1])], U1 | Cands[r2][c1], Cands, Step, Methods): return 0
                # look for cells 3 and 4 in boxes
                rb = (r//3)*3; cb0 = (c0//3)*3; cb1 = (c1//3)*3
                if cb0 == cb1: continue  # pattern requires one cell outside of the in row / box intersection. (other possibilities checked in col/box intersections below.
                for b2 in range(8):
                    r2 = rb + b2//3; c2 = cb0 + b2%3
                    if r2 != r and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) == 4:
                        BQ1 = BQ + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                        for b3 in range(b2+1, 9):
                            r3 = rb + b3//3; c3 = cb0 + b3%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                    c2 = cb1 + b2%3
                    if r2 != r and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) == 4:
                        BQ1 = BQ + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                        for b3 in range(b2+1, 9):
                            r3 = rb + b3//3; c3 = cb1 + b3%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
    # bent quad not found by scanning rows, try scanning columns, here it would be a duplication of effort to look in row / col patterns
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 4: continue
            for r1 in range(r0+1, 9):
                U = Cands[r0][c] | Cands[r1][c]
                if not 2 <= len(Cands[r1][c]) <= 4 or len(U) > 4: continue
                BQ = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                # 2 possible cells in the col, if the second cell is not at the end of the column look for a third cell in the col
                for r2 in range(r1+1, 9):
                    U1 = U | Cands[r2][c]
                    if not 2 <= len(Cands[r2][c]) <= 4 or len(U1) > 4: continue
                    BQ1 = BQ + [(r2, c, Cands[r2][c])]
                    # 3rd possible cell found, look in rows for col/row patterns
                    for c0 in range(9):
                        if c0 == c: continue
                        if 2 <= len(Cands[r0][c0]) <= 4 and len(U1 | Cands[r0][c0]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c0, Cands[r0][c0])], U1 | Cands[r0][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r1][c0]) <= 4 and len(U1 | Cands[r1][c0]) == 4:
                            if bent_subset_elims(BQ1+[(r1, c0, Cands[r1][c0])], U1 | Cands[r1][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r2][c0]) <= 4 and len(U1 | Cands[r2][c0]) == 4:
                            if bent_subset_elims(BQ1+[(r2, c0, Cands[r2][c0])], U1 | Cands[r2][c0], Cands, Step, Methods): return 0
                    # 4th not found in col, look in boxes
                    cb = (c//3)*3; RB = sorted({r0//3, r1//3, r2//3})  # use set to remove dups.
                    if len(RB) == 1: continue  # pattern wants at least one cell outside the intersection
                    for b in range(9):
                        for rb in RB:
                            r3 = rb*3 + b//3; c3 = cb + b%3
                            if r3 != r0 and r3 != r1 and r3 != r2 and c3 != c and len(Cands[r3][c3]) == 2 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                # Cells 1 and 2 in the col, look for cells 3 and 4 in the row
                for c1 in range(8):
                    if c1 != c and 2 <= len(Cands[r0][c1]) <= 4 and len(U | Cands[r0][c1]) == 4:
                        BQ1 = BQ + [(r0, c1, Cands[r0][c1])]; U1 = U | Cands[r0][c1]
                        for c2 in range(c1+1, 9):
                            if c2 != c and 2 <= len(Cands[r0][c2]) <= 4 and len(U1 | Cands[r0][c2]) == 4:
                                if bent_subset_elims(BQ1+[(r0, c2, Cands[r0][c2])], U1 | Cands[r0][c2], Cands, Step, Methods): return 0
                    if c1 != c and 2 <= len(Cands[r1][c1]) <= 4 and len(U | Cands[r1][c1]) == 4:
                        BQ1 = BQ+[(r1, c1, Cands[r1][c1])]; U1 = U | Cands[r1][c1]
                        for c2 in range(c1+1, 9):
                            if c2 != c and 2 <= len(Cands[r1][c2]) <= 4 and len(U1 | Cands[r1][c2]) == 4:
                                if bent_subset_elims(BQ1+[(r1, c2, Cands[r1][c2])], U1 | Cands[r1][c2], Cands, Step, Methods): return 0
                # look for cells 3 and 4 in boxes
                rb0 = (r0//3)*3; rb1 = (r1//3)*3; cb = (c//3)*3
                if rb0 == rb1: continue  # pattern wants at least one cell outside of the intersect
                for b2 in range(8):
                    r2 = rb0 + b2//3; c2 = cb + b2%3
                    if c2 != c and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) == 4:
                        BQ1 = BQ + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                        for b3 in range(b2+1, 9):
                            r3 = rb0 + b3//3; c3 = cb + b3%3
                            if c3 != c and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                    r2 = rb1 + b2//3
                    if c2 != c and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) == 4:
                        BQ1 = BQ+[(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                        for b3 in range(b2+1, 9):
                            r3 = rb1 + b3//3; c3 = cb + b3%3
                            if c3 != c and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
    return -1

def bent_subset_elims(Cells, UCands, Cands, Step, Methods):
    # Checks
    # 1.  only 1 URC
    # 2   ID intersecting cells
    # 3  elim URC from in
    #
    # The candidate that does not see all its same value cands in the pattern is the unrestricted candidate (URC)
    # and there can only be one URC in the bent subset pattern to make eliminations.

    # # Ensure all cands have multiple occurances in the pattern
    # i = 0
    # for (r, c, Candc) in Cells:
    #     for Cand in UCands:
    #         if Cand in Candc: i += 1
    #     if i < 2: return false

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
        if T_Y_WING in Methods and NrCands[0] == NrCands[1] == NrCands[2] == 2: Step.Method = T_Y_WING
        elif T_XYZ_WING in Methods: Step.Method = T_XYZ_WING
        else: return False
    else:  # NrCells == 4
        TwoCands = FourCands = 0
        for NrCand in NrCands:
            if NrCand == 2: TwoCands += 1
            elif NrCand == 4: FourCands += 1
        if T_WXYZ_WING in Methods and TwoCands == 3 and FourCands == 1: Step.Method = T_WXYZ_WING
        elif T_BENT_EXPOSED_QUAD in Methods: Step.Method = T_BENT_EXPOSED_QUAD
        else: return False

    for r0, c0 in cells_that_see_all_of(URCCells):
        if URC in Cands[r0][c0]:
            Cands[r0][c0].discard(URC)
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, URC]])
    if Step.Outcome:
        Step.Outcome.append([P_END, ])
        for r0, c0, Cands0 in Cells:
            if Step.Pattern: Step.Pattern.append([P_CON, ])
            Step.Pattern.extend([[P_VAL, copy(Cands0)], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
        Step.Pattern.append([P_END, ])
        return True
    return False
