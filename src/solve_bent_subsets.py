from copy import copy

from globals import *
from solve_utils import *

def tech_bent_exposed_triples(Grid, Step, Cands, Methods):
    # A bent exposed triple (BET) can only be a Y-Wing or a XYZ-Wing, comprising
    # a pivot and two pincers.

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
    # 1.  Check for only 1 URC
    # 2   ID intersecting cells
    # 3   Elim cells outside the pattern that see the URC

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
            Step.Pattern.extend([[P_VAL, sorted(Cands0)], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
        Step.Pattern.append([P_END, ])
        return True
    return False

def tech_grouped_bent_pair(Grid, Step, Cands, Methods):

    F1 = []; T1 = []
    # Exposed row, hidden box.
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) != 2: continue
            Pair = Cands[r][c]  # Pair found
            t0 = (c//3)*3; T = [0, 3, 6]; T.remove(t0)  # ; ta, tb = T
            f0 = (r//3)*3; F = [0, 3, 6]; F.remove(f0)  # ; fa, fb = F
            rb1 = f0+(r-f0+1)%3; rb2 = f0+(r-f0+2)%3
            cb1 = t0+(c-t0+1)%3; cb2 = t0+(c-t0+2)%3
            rb0 = cb0 = 0
            if T_GROUPED_BENT_PAIR_ER in Methods:  # Check out exposed in row, hidden in box.
                for t1 in T:
                    if Pair <= Cands[r][t1] | Cands[r][t1+1] | Cands[r][t1+2]:  # Almost pair found in rowbox:
                        n = 0
                        for rb, cb in [(rb1, t1), (rb1, t1+1), (rb1, t1+2), (rb2, t1), (rb2, t1+1), (rb2, t1+2)]:
                            if Cands[rb][cb] and Pair & Cands[rb][cb]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = cb; T1 = [0, 3, 6]; T1.remove(t1)
                        else:
                            if n and Pair <= Cands[rb0][cb0]:  # == 1:  # Grouped bent pair found, how productive is it?
                                for c1 in [T1[0], T1[0]+1, T1[0]+2, T1[1], T1[1]+1, T1[1]+2]:
                                    if c1 == c: continue
                                    Elims = Cands[r][c1] & Pair
                                    if Elims:
                                        Cands[r][c1] -= Pair
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                Elims = Cands[rb0][cb0] - Pair
                                if Elims:
                                    Cands[rb0][cb0] = copy(Pair)
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, rb0], [P_COL, cb0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                if Step.Outcome:
                                    Step.Method = T_GROUPED_BENT_PAIR_ER
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, r], [P_COL, t1, t1+1, t1+2], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_EC in Methods:  # Check out pair exposed in col, hidden in box.
                for f1 in F:
                    if Pair <= Cands[f1][c] | Cands[f1+1][c] | Cands[f1+2][c]:  # Almost pair found in colbox
                        n = 0
                        for rb, cb in [(f1, cb1), (f1+1, cb1), (f1+2, cb1), (f1, cb2), (f1+1, cb2), (f1+2, cb2)]:
                            if Cands[rb][cb] and Pair & Cands[rb][cb]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = cb; F1 = [0, 3, 6]; F1.remove(f1)
                        else:  # Grouped bent pair found, how productive is it?
                            if n and Pair <= Cands[rb0][cb0]:
                                for r1 in [F1[0], F1[0]+1, F1[0]+2, F1[1], F1[1]+1, F1[1]+2]:
                                    if r1 == r: continue
                                    Elims = Cands[r1][c] & Pair
                                    if Elims:
                                        Cands[r1][c] -= Pair
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r1], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                Elims = Cands[rb0][cb0] - Pair
                                if Elims:
                                    Cands[rb0][cb0] = copy(Pair)
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, rb0], [P_COL, cb0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                if Step.Outcome:
                                    Step.Method = T_GROUPED_BENT_PAIR_EC
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, f1, f1+1, f1+2], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_HR in Methods:  # Check out pair exposed in box, hidden in row.
                for rb in [rb1, rb2]:
                    if Pair <= Cands[rb][t0] | Cands[rb][t0+1] | Cands[rb][t0+2]:  # Almost pair found in rowbox.
                        n = 0
                        for c1 in [T[0], T[0]+1, T[0]+2, T[1], T[1]+1, T[1]+2]:
                            if Cands[rb][c1] and Pair & Cands[rb][c1]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = c1; F1 = [f0, f0+1, f0+2]; F1.remove(rb)
                        else:
                            if n and Pair <= Cands[rb0][cb0]:  # == 1:  # Grouped bent pair found, how productive is it?
                                for rbx, cbx in [(F1[0], t0), (F1[0], t0+1), (F1[0], t0+2), (F1[1], t0), (F1[1], t0+1), (F1[1], t0+2)]:
                                    if rbx == r and cbx == c: continue
                                    Elims = Cands[rbx][cbx] & Pair
                                    if Elims:
                                        Cands[rbx][cbx] -= Pair
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, rbx], [P_COL, cbx], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                Elims = Cands[rb0][cb0]  - Pair
                                if Elims:
                                    Cands[rb0][cb0] = copy(Pair)
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, rb0], [P_COL, cb0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                if Step.Outcome:
                                    Step.Method = T_GROUPED_BENT_PAIR_HR
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, rb0], [P_COL, t0, t0+1, t0+2], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_HC in Methods:  # Check out pair in exposed box, hidden in col
                for cb in [cb1, cb2]:
                    if Pair <= Cands[f0][cb] | Cands[f0+1][cb] | Cands[f0+2][cb]:  # almost pair found in colbox
                        n = 0
                        for r1 in [F[0], F[0]+1, F[0]+2, F[1], F[1]+1, F[1]+2]:
                            if Cands[r1][cb] and Pair & Cands[r1][cb]:
                                if n: break
                                n += 1; rb0 = r1; cb0 = cb; T1 = [t0, t0+1, t0+2]; T1.remove(cb)
                        else:
                            if n and Pair <= Cands[rb0][cb0]:
                                for rbx, cbx in [(f0, T1[0]), (f0+1, T1[0]), (f0+2, T1[0]), (f0, T1[1]), (f0+1, T1[1]), (f0+2, T1[1])]:
                                    if rbx == r and cbx == c: continue
                                    Elims = Cands[rbx][cbx] & Pair
                                    if Elims:
                                        Cands[rbx][cbx] -= Pair
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, rbx], [P_COL, cbx], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                Elims = Cands[rb0][cb0] - Pair
                                if Elims:
                                    Cands[rb0][cb0] = copy(Pair)
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, rb0], [P_COL, cb0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                if Step.Outcome:
                                    Step.Method = T_GROUPED_BENT_PAIR_HC
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, f0, f0+1, f0+2], [P_COL, cb0], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
    return -1

def tech_grouped_bent_triple(Grid, Step, Cands, Methods):
    return -1

def tech_grouped_bent_quad(Grid, Step, Cands, Methods):
    return -1

def tech_bent_hidden_triple(Grid, Step, Cands, Methods):
    return -1
