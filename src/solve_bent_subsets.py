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
                if cb0 == cb1: continue  # pattern only wants one cell outside the intersection.
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
                    # 3rd possible cell found, look in cols for row / columns pattern for the 4th cell of the BEQ.
                    for r0 in range(9):
                        if r0 == r: continue
                        if 2 <= len(Cands[r0][c0]) <= 4 and len(U1 | Cands[r0][c0]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c0, Cands[r0][c0])], U1 | Cands[r0][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r0][c1]) <= 4 and len(U1 | Cands[r0][c1]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c1, Cands[r0][c1])], U1 | Cands[r0][c1], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r0][c2]) <= 4 and len(U1 | Cands[r0][c2]) == 4:
                            if bent_subset_elims(BQ1+[(r0, c2, Cands[r0][c2])], U1 | Cands[r0][c2], Cands, Step, Methods): return 0
                    # 4th not found in col, look in boxes
                    rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3})  # set to remove dup boxes to search.
                    if len(CB) == 1: continue  # pattern wants at least one cell outside the intersection
                    for cb in CB:
                        for b in range(9):
                            r3 = rb + b//3; c3 = cb +b%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                #  Cells 1 and 2 in the row, look for cells 3 and 4 in the cols
                for r1 in range(8):
                    if r1 == r: continue
                    if 2 <= len(Cands[r1][c0]) <= 4 and len(U | Cands[r1][c0]) <= 4:
                        BQ1 = BQ + [(r1, c0, Cands[r1][c0])]; U1 = U | Cands[r1][c0]
                        for r2 in range(r1+1, 9):
                            if r2 != r and 2 <= len(Cands[r2][c0]) <= 4 and len(U1 | Cands[r2][c0]) == 4:
                                if bent_subset_elims(BQ1+[(r2, c0, Cands[r2][c0])], U1 | Cands[r2][c0], Cands, Step, Methods): return 0
                    if 2 <= len(Cands[r1][c1]) <= 4 and len(U | Cands[r1][c1]) == 4:
                        BQ1 = BQ + [(r1, c1, Cands[r1][c1])]; U1 = U | Cands[r1][c1]
                        for r2 in range(r1+1, 9):
                            if r2 != r and 2 <= len(Cands[r2][c1]) <= 4 and len(U1 | Cands[r2][c1]) == 4:
                                if bent_subset_elims(BQ1+[(r2, c1, Cands[r2][c1])], U1 | Cands[r2][c1], Cands, Step, Methods): return 0
                # look for cells 3 and 4 in boxes
                rb = (r//3)*3; cb0 = (c0//3)*3; cb1 = (c1//3)*3
                if cb0 == cb1: continue  # pattern requires one cell outside of the in row / box intersection. (other possibilities checked in col/box intersections below.
                for b2 in range(8):
                    r2 = rb + b2//3; c2 = cb0 + b2%3
                    if r2 != r and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) <= 4:
                        BQ1 = BQ + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                        for b3 in range(b2+1, 9):
                            r3 = rb + b3//3; c3 = cb0 + b3%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                    c2 = cb1 + b2%3
                    if r2 != r and 2 <= len(Cands[r2][c2]) <= 4 and len(U | Cands[r2][c2]) <= 4:
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
                    # 3rd possible cell found, look in boxes for fourth
                    RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3}); cb = (c//3)*3  # use set to remove dups.
                    if len(RB) == 1: continue  # pattern wants at least one cell outside the intersection
                    for b in range(9):
                        for rb in RB:
                            r3 = rb + b//3; c3 = cb + b%3
                            if c3 != c and 2 <= len(Cands[r3][c3]) <= 4 and len(U1 | Cands[r3][c3]) == 4:
                                if bent_subset_elims(BQ1+[(r3, c3, Cands[r3][c3])], U1 | Cands[r3][c3], Cands, Step, Methods): return 0
                # Cells 1 and 2 in the col, look for cells 3 and 4 in boxes
                rb0 = (r0//3)*3; rb1 = (r1//3)*3; cb = (c//3)*3
                if rb0 == rb1: continue  # pattern wants at least one cell outside the intersection
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

def tech_bent_exposed_quints(Grid, Step, Cands, Methods):
    # URC ==> unrestricted candidate.
    # BQ ==> BentQuint pattern.  list used to accumulate the cells that may form a BQ.
    # CIB ==> Cells in Box.  List of cells in box outside the intersection.
    # U ==> Union of candidates in cells being considered for the BQ.

    # look for patterns starting with a row
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 5: continue
            for c1 in range(c0+1, 9):
                U = Cands[r][c0] | Cands[r][c1]
                if not 2 <= len(Cands[r][c1]) <= 5 or len(U) > 5: continue
                BQ = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # 2 possible cells in the row, if the second cell is not at the end of the row, look for a third row cell
                for c2 in range(c1+1, 9):
                    U1 = U | Cands[r][c2]
                    if not 2 <= len(Cands[r][c2]) <= 5 or len(U1) > 5: continue
                    BQ1 = BQ + [(r, c2, Cands[r][c2])]
                    # 3 possible cells in the row, if the 3rd cell is not at the end of the row, look for a fourth row cell
                    for c3 in range(c2+1, 9):
                        U2 = U1 | Cands[r][c3]
                        if not 2 <= len(Cands[r][c3]) <=5 or len(U2) > 5: continue
                        BQ2 = BQ1 + [(r, c3, Cands[r][c3])]
                        # 4th possible cell found, look in cols for row/col patterns for the 5th cell.
                        for r0 in range(9):
                            if r0 == r: continue
                            if 2 <= len(Cands[r0][c0]) <= 5 and len(U2 | Cands[r0][c0]) == 5:
                                if bent_subset_elims(BQ2 + [(r0, c0, Cands[r0][c0])], U2 | Cands[r0][c0], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r0][c1]) <= 5 and len(U2 | Cands[r0][c1]) == 5:
                                if bent_subset_elims(BQ2 + [(r0, c1, Cands[r0][c1])], U2 | Cands[r0][c1], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r0][c2]) <= 5 and len(U2 | Cands[r0][c2]) == 5:
                                if bent_subset_elims(BQ2 + [(r0, c2, Cands[r0][c2])], U2 | Cands[r0][c2], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r0][c3]) <= 5 and len(U2 | Cands[r0][c3]) == 5:
                                if bent_subset_elims(BQ2 + [(r0, c3, Cands[r0][c3])], U2 | Cands[r0][c3], Cands, Step, Methods): return 0
                        # 4th not found in col, look in boxes
                        rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3, (c3//3)*3})  # set to remove dup boxes to search.
                        for cb in CB:
                            for b in range(9):
                                r4 = rb + b//3; c4 = cb +b%3
                                if r4 != r and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                    if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
                    #  3 cells in the row, look for cells 4 and 5 in cols.
                    for r1 in range(8):
                        if r1 == r: continue
                        if 2 <= len(Cands[r1][c0]) <= 5 and len(U1 | Cands[r1][c0]) <= 5:
                            BQ2 = BQ1+[(r1, c0, Cands[r1][c0])]; U2 = U1 | Cands[r1][c0]
                            for r2 in range(r1+1, 9):
                                if r2 != r and 2 <= len(Cands[r2][c0]) <= 5 and len(U2 | Cands[r2][c0]) == 5:
                                    if bent_subset_elims(BQ2+[(r2, c0, Cands[r2][c0])], U2 | Cands[r2][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r1][c1]) <= 5 and len(U1 | Cands[r1][c1]) <= 5:
                            BQ2 = BQ1+[(r1, c1, Cands[r1][c1])]; U2 = U1 | Cands[r1][c1]
                            for r2 in range(r1+1, 9):
                                if r2 != r and 2 <= len(Cands[r2][c1]) <= 5 and len(U2 | Cands[r2][c1]) == 5:
                                    if bent_subset_elims(BQ2+[(r2, c1, Cands[r2][c1])], U2 | Cands[r2][c1], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r1][c2]) <= 5 and len(U1 | Cands[r1][c2]) <= 5:
                            BQ2 = BQ1+[(r1, c2, Cands[r1][c2])]; U2 = U1 | Cands[r1][c2]
                            for r2 in range(r1+1, 9):
                                if r2 != r and 2 <= len(Cands[r2][c2]) <= 5 and len(U2 | Cands[r2][c2]) == 5:
                                    if bent_subset_elims(BQ2+[(r2, c2, Cands[r2][c2])], U2 | Cands[r2][c2], Cands, Step, Methods): return 0
                    # Not found in cols, look for cell 4 and 5 in the boxes.
                    rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3})
                    if len(CB) == 1: continue  # pattern wants at least one cell outside the box
                    for cb in CB:
                        for b3 in range(8):
                            r3 = rb + b3//3; c3 = cb + b3%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 5 and len(U1 | Cands[r3][c3]) <= 5:
                                BQ2 = BQ1+[(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                for b4 in range(b3+1, 9):
                                    r4 = rb + b4//3; c4= cb + b4%3
                                    if r4 != r and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                        if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
                # Nothing found with 3 or more cells in a row, look in cols for the remaining 3 cells.
                for r2 in range(7):
                    if r2 == r: continue
                    if 2 <= len(Cands[r2][c0]) <= 5 and len(U | Cands[r2][c0]) <= 5:
                        BQ1 = BQ+[(r2, c0, Cands[r2][c0])]; U1 = U | Cands[r2][c0]
                        for r3 in range(r2+1, 8):
                            if r3 != r and 2 <= len(Cands[r3][c0]) <= 5 and len(U1 | Cands[r3][c0]) <= 5:
                                BQ2 = BQ1+[(r3, c0, Cands[r3][c0])]; U2 = U1 | Cands[r3][c0]
                                for r4 in range(r3+1, 9):
                                    if r4 != r and 2 <= len(Cands[r4][c0]) <= 5 and len(U2 | Cands[r4][c0]) == 5:
                                        if bent_subset_elims(BQ2+[(r4, c0, Cands[r4][c0])], U2 | Cands[r4][c0], Cands, Step, Methods): return 0
                    if 2 <= len(Cands[r2][c1]) <= 5 and len(U | Cands[r2][c1]) <= 5:
                        BQ1 = BQ+[(r2, c1, Cands[r2][c1])]; U1 = U | Cands[r2][c1]
                        for r3 in range(r2+1, 8):
                            if r3 != r and 2 <= len(Cands[r3][c1]) <= 5 and len(U1 | Cands[r3][c1]) <= 5:
                                BQ2 = BQ1+[(r3, c1, Cands[r3][c1])]; U2 = U1 | Cands[r3][c1]
                                for r4 in range(r3+1, 9):
                                    if r4 != r and 2 <= len(Cands[r4][c1]) <= 5 and len(U2 | Cands[r4][c1]) == 5:
                                        if bent_subset_elims(BQ2+[(r4, c1, Cands[r4][c1])], U2 | Cands[r4][c1], Cands, Step, Methods): return 0
                # Nothing found in 2 by row, 3 by col patterns, look in 2 by row, 3 by box patterns.
                rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3})
                if len(CB)== 1: continue  # pattern want at least one cell outside the box.
                for cb in CB:
                    for b2 in range(7):
                        r2 = rb + b2//3; c2 = cb + b2%3
                        if r2 != r and 2 <= len(Cands[r2][c2]) <= 5 and len(U | Cands[r2][c2]) <= 5:
                            BQ1 = BQ+[(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                            for b3 in range(b2+1, 8):
                                r3 = rb + b3//3; c3 = cb + b3%3
                                if r3 != r and 2 <= len(Cands[r3][c3]) <= 5 and len(U1 | Cands[r3][c3]) <= 5:
                                    BQ2 = BQ1+[(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                    for b4 in range(b3+1, 9):
                                        r4 = rb + b4//3; c4 = cb + b4%3
                                        if r4 != r and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                            if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
    # No bent quint patterns found in 2, 3 or 4 by row, and balance in cols or boxes, look for 1 in row, 4 in col patterns
    # scan cols by boxes, cols x rows already done above
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 5: continue
            for r1 in range(r0+1, 9):
                U = Cands[r0][c] | Cands[r1][c]
                if not 2 <= len(Cands[r1][c]) <= 5 or len(U) > 5: continue
                BQ = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                # 2 possible cells in the col, if the second cell is not at the end of the col, look for a third col cell
                for r2 in range(r1+1, 9):
                    U1 = U | Cands[r2][c]
                    if not 2 <= len(Cands[r2][c]) <= 5 or len(U1) > 5: continue
                    BQ1 = BQ + [(r2, c, Cands[r2][c])]
                    # 3 possible cells in the col, if the 3rd cell is not at the end of the col, look for a fourth col cell
                    for r3 in range(r2+1, 9):
                        U2 = U1 | Cands[r3][c]
                        if not 2 <= len(Cands[r3][c]) <=5 or len(U2) > 5: continue
                        BQ2 = BQ1 + [(r3, c, Cands[r3][c])]
                        # 4th possible cell found, look in box for 5th cell.
                        RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3, (r3//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                        for rb in RB:
                            for b in range(9):
                                r4 = rb + b//3; c4 = cb +b%3
                                if c4 != c and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                    if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
                    #  3 cells in the row, look for cells 4 and 5 in boxes.
                    RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                    if len(RB) == 1: continue  # pattern wants at least one cell outside the box
                    for rb in RB:
                        for b3 in range(8):
                            r3 = rb + b3//3; c3 = cb + b3%3
                            if c3 != c and 2 <= len(Cands[r3][c3]) <= 5 and len(U1 | Cands[r3][c3]) <= 5:
                                BQ2 = BQ1+[(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                for b4 in range(b3+1, 9):
                                    r4 = rb + b4//3; c4= cb + b4%3
                                    if c4 != c and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                        if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
                # Nothing found with 3 or more cells in a col, look in boxes for the remaining 3 cells.
                RB = list({(r0//3)*3, (r1//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                if len(RB)== 1: continue  # pattern want at least one cell outside the box.
                for rb in RB:
                    for b2 in range(7):
                        r2 = rb + b2//3; c2 = cb + b2%3
                        if c2 != c and 2 <= len(Cands[r2][c2]) <= 5 and len(U | Cands[r2][c2]) <= 5:
                            BQ1 = BQ+[(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                            for b3 in range(b2+1, 8):
                                r3 = rb + b3//3; c3 = cb + b3%3
                                if c3 != c and 2 <= len(Cands[r3][c3]) <= 5 and len(U1 | Cands[r3][c3]) <= 5:
                                    BQ2 = BQ1+[(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                    for b4 in range(b3+1, 9):
                                        r4 = rb + b4//3; c4 = cb + b4%3
                                        if c4 != c and 2 <= len(Cands[r4][c4]) <= 5 and len(U2 | Cands[r4][c4]) == 5:
                                            if bent_subset_elims(BQ2+[(r4, c4, Cands[r4][c4])], U2 | Cands[r4][c4], Cands, Step, Methods): return 0
    return -1

def tech_bent_exposed_sexts(Grid, Step, Cands, Methods):
    # URC ==> unrestricted candidate.
    # BS ==> BentQuint pattern.  list used to accumulate the cells that may form a BS.
    # CIB ==> Cells in Box.  List of cells in box outside the intersection.
    # U ==> Union of candidates in cells being considered for the BS.

    # look for patterns starting with a row
    for r in range(9):
        for c0 in range(8):
            if not 2 <= len(Cands[r][c0]) <= 6: continue
            for c1 in range(c0+1, 9):
                U = Cands[r][c0] | Cands[r][c1]
                if not 2 <= len(Cands[r][c1]) <= 6 or len(U) > 6: continue
                BS = [(r, c0, Cands[r][c0]), (r, c1, Cands[r][c1])]
                # 2 possible cells in the row, if the second cell is not at the end of the row, look for a third row cell
                for c2 in range(c1+1, 9):
                    U1 = U | Cands[r][c2]
                    if not 2 <= len(Cands[r][c2]) <= 6 or len(U1) > 6: continue
                    BS1 = BS + [(r, c2, Cands[r][c2])]
                    # 3 possible cells in the row, if the 3rd cell is not at the end of the row, look for a fourth row cell
                    for c3 in range(c2+1, 9):
                        U2 = U1 | Cands[r][c3]
                        if not 2 <= len(Cands[r][c3]) <=5 or len(U2) > 6: continue
                        BS2 = BS1 + [(r, c3, Cands[r][c3])]
                        # 4th possible cell found, if we are not at end of row, look for a 5th cell.
                        for c4 in range(c3+1, 9):
                            U3 = U2 | Cands[r][c4]
                            if not 2 < len(Cands[r][c4]) <= 6 or len(U2) > 6: continue
                            BS3 = BS2 + [(r, c4, Cands[r][c4])]
                            # 5 cells found in row look in in cols for row/col patterns for the 6th cell.
                            for r0 in range(9):
                                if r0 == r: continue
                                if 2 <= len(Cands[r0][c0]) <= 6 and len(U3 | Cands[r0][c0]) == 6:
                                    if bent_subset_elims(BS3 + [(r0, c0, Cands[r0][c0])], U3 | Cands[r0][c0], Cands, Step, Methods): return 0
                                if 2 <= len(Cands[r0][c1]) <= 6 and len(U3 | Cands[r0][c1]) == 6:
                                    if bent_subset_elims(BS3 + [(r0, c1, Cands[r0][c1])], U3 | Cands[r0][c1], Cands, Step, Methods): return 0
                                if 2 <= len(Cands[r0][c2]) <= 6 and len(U3 | Cands[r0][c2]) == 6:
                                    if bent_subset_elims(BS3 + [(r0, c2, Cands[r0][c2])], U3 | Cands[r0][c2], Cands, Step, Methods): return 0
                                if 2 <= len(Cands[r0][c3]) <= 6 and len(U3 | Cands[r0][c3]) == 6:
                                    if bent_subset_elims(BS3 + [(r0, c3, Cands[r0][c3])], U3 | Cands[r0][c3], Cands, Step, Methods): return 0
                                if 2 <= len(Cands[r0][c4]) <= 6 and len(U3 | Cands[r0][c4]) == 6:
                                    if bent_subset_elims(BS3 + [(r0, c4, Cands[r0][c4])], U3 | Cands[r0][c4], Cands, Step, Methods): return 0
                            # 6th not found in col, look in boxes
                            rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3, (c3//3)*3, (c4//3)*3})  # set to remove dup boxes to search.
                            for cb in CB:
                                for b in range(9):
                                    r5 = rb + b//3; c5 = cb +b%3
                                    if r5 != r and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                        if bent_subset_elims(BS3+[(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                        #  4 cells in the row, look for cells 5 and 6 in cols.
                        for r1 in range(8):
                            if r1 == r: continue
                            if 2 <= len(Cands[r1][c0]) <= 6 and len(U2 | Cands[r1][c0]) <= 6:
                                BS3 = BS2+[(r1, c0, Cands[r1][c0])]; U3 = U2 | Cands[r1][c0]
                                for r2 in range(r1+1, 9):
                                    if r2 != r and 2 <= len(Cands[r2][c0]) <= 6 and len(U3 | Cands[r2][c0]) == 6:
                                        if bent_subset_elims(BS3+[(r2, c0, Cands[r2][c0])], U3 | Cands[r2][c0], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r1][c1]) <= 6 and len(U2 | Cands[r1][c1]) <= 6:
                                BS3 = BS2+[(r1, c1, Cands[r1][c1])]; U3 = U2 | Cands[r1][c1]
                                for r2 in range(r1+1, 9):
                                    if r2 != r and 2 <= len(Cands[r2][c1]) <= 6 and len(U3 | Cands[r2][c1]) == 6:
                                        if bent_subset_elims(BS3+[(r2, c1, Cands[r2][c1])], U3 | Cands[r2][c1], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r1][c2]) <= 6 and len(U2 | Cands[r1][c2]) <= 6:
                                BS3 = BS2+[(r1, c2, Cands[r1][c2])]; U3 = U2 | Cands[r1][c2]
                                for r2 in range(r1+1, 9):
                                    if r2 != r and 2 <= len(Cands[r2][c2]) <= 5 and len(U3 | Cands[r2][c2]) == 6:
                                        if bent_subset_elims(BS3+[(r2, c2, Cands[r2][c2])], U3 | Cands[r2][c2], Cands, Step, Methods): return 0
                            if 2 <= len(Cands[r1][c3]) <= 6 and len(U2 | Cands[r1][c3]) <= 6:
                                BS3 = BS2+[(r1, c3, Cands[r1][c3])]; U3 = U2 | Cands[r1][c3]
                                for r2 in range(r1+1, 9):
                                    if r2 != r and 2 <= len(Cands[r2][c3]) <= 6 and len(U3 | Cands[r2][c3]) == 6:
                                        if bent_subset_elims(BS3+[(r2, c3, Cands[r2][c3])], U3 | Cands[r2][c3], Cands, Step, Methods): return 0
                        # Not found in cols, look for cell 4 and 5 in the boxes.
                        rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3, (c3//3)*3})
                        # if len(CB) == 1: continue  # pattern wants at least one cell outside the box
                        for cb in CB:
                            for b4 in range(8):
                                r4 = rb + b4//3; c4 = cb + b4%3
                                if r4 != r and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                    BS3 = BS2+[(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                    for b5 in range(b4+1, 9):
                                        r5 = rb + b5//3; c5= cb + b5%3
                                        if r5 != r and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                            if bent_subset_elims(BS3+[(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                    # Nothing found with 4 or more cells in a row, look 3 row cells and 3 col cells.
                    for r2 in range(7):
                        if r2 == r: continue
                        if 2 <= len(Cands[r2][c0]) <= 6 and len(U1 | Cands[r2][c0]) <= 6:
                            BS2 = BS1+[(r2, c0, Cands[r2][c0])]; U2 = U1 | Cands[r2][c0]
                            for r3 in range(r2+1, 8):
                                if r3 != r and 2 <= len(Cands[r3][c0]) <= 6 and len(U2 | Cands[r3][c0]) <= 6:
                                    BS3 = BS2+[(r3, c0, Cands[r3][c0])]; U3 = U2 | Cands[r3][c0]
                                    for r4 in range(r3+1, 9):
                                        if r4 != r and 2 <= len(Cands[r4][c0]) <= 6 and len(U3 | Cands[r4][c0]) == 6:
                                            if bent_subset_elims(BS3+[(r4, c0, Cands[r4][c0])], U3 | Cands[r4][c0], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r2][c1]) <= 6 and len(U1 | Cands[r2][c1]) <= 6:
                            BS2 = BS1+[(r2, c1, Cands[r2][c1])]; U2 = U1 | Cands[r2][c1]
                            for r3 in range(r2+1, 8):
                                if r3 != r and 2 <= len(Cands[r3][c1]) <= 6 and len(U2 | Cands[r3][c1]) <= 6:
                                    BS3 = BS2+[(r3, c1, Cands[r3][c1])]; U3 = U2 | Cands[r3][c1]
                                    for r4 in range(r3+1, 9):
                                        if r4 != r and 2 <= len(Cands[r4][c1]) <= 6 and len(U3 | Cands[r4][c1]) == 6:
                                            if bent_subset_elims(BS3+[(r4, c1, Cands[r4][c1])], U3 | Cands[r4][c1], Cands, Step, Methods): return 0
                        if 2 <= len(Cands[r2][c2]) <= 6 and len(U1 | Cands[r2][c2]) <= 6:
                            BS2 = BS1+[(r2, c2, Cands[r2][c2])]; U2 = U1 | Cands[r2][c2]
                            for r3 in range(r2+1, 8):
                                if r3 != r and 2 <= len(Cands[r3][c2]) <= 6 and len(U2 | Cands[r3][c2]) <= 6:
                                    BS3 = BS2+[(r3, c2, Cands[r3][c2])]; U3 = U2 | Cands[r3][c2]
                                    for r4 in range(r3+1, 9):
                                        if r4 != r and 2 <= len(Cands[r4][c2]) <= 6 and len(U3 | Cands[r4][c2]) == 6:
                                            if bent_subset_elims(BS3+[(r4, c2, Cands[r4][c2])], U3 | Cands[r4][c2], Cands, Step, Methods): return 0
                    # Nothing found in 3 by row, 3 by col patterns, look in 3 by row, 3 by box patterns.
                    rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3, (c2//3)*3})
                    if len(CB)== 1: continue  # pattern want at least one cell outside the box.
                    for cb in CB:
                        for b3 in range(7):
                            r3 = rb + b3//3; c3 = cb + b3%3
                            if r3 != r and 2 <= len(Cands[r3][c3]) <= 6 and len(U1 | Cands[r3][c3]) <= 6:
                                BS2 = BS1+[(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                for b4 in range(b3+1, 8):
                                    r4 = rb + b4//3; c4 = cb + b4%3
                                    if r4 != r and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                        BS3 = BS2+[(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                        for b5 in range(b4+1, 9):
                                            r5 = rb + b5//3; c5 = cb + b5%3
                                            if r5 != r and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                                if bent_subset_elims(BS3+[(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                # No 3 by row, look for 2 by row, 4 by col.
                for r2 in range(6):
                    if r2 == r: continue
                    if 2 <= len(Cands[r2][c0]) <=6 and len(U | Cands[r2][c0]) <=6:
                        BS1 = BS + [(r2, c0, Cands[r2][c0])]; U1 = U | Cands[r2][c0]
                        for r3 in range(r2+1, 7):
                            if r3 != r and 2 <= len(Cands[r3][c0]) <= 6 and len(U1 | Cands[r3][c0]) <= 6:
                                BS2 = BS1 + [(r3, c0, Cands[r3][c0])]; U2 = U1 | Cands[r3][c0]
                                for r4 in range(r3+1, 8):
                                    if r4 != r and 2 <= len(Cands[r4][c0]) <= 6 and len(U2 | Cands[r4][c0]) <= 6:
                                        BS3 = BS2 + [(r4, c0, Cands[r4][c0])]; U3 = U2 | Cands[r4][c0]
                                        for r5 in range(r4+1, 9):
                                            if r5 != r and 2 <= len(Cands[r5][c0]) <= 6 and len(U3 | Cands[r5][c0]) == 6:
                                                if bent_subset_elims(BS3 + [(r5, c0, Cands[r5][c0])], U3 | Cands[r5][c0], Cands, Step, Methods): return 0
                    if 2 <= len(Cands[r2][c1]) <= 6 and len(U | Cands[r2][c1]) <= 6:
                        BS1 = BS+[(r2, c1, Cands[r2][c1])]; U1 = U | Cands[r2][c1]
                        for r3 in range(r2+1, 7):
                            if r3 != r and 2 <= len(Cands[r3][c1]) <= 6 and len(U1 | Cands[r3][c1]) <= 6:
                                BS2 = BS1+[(r3, c1, Cands[r3][c1])]; U2 = U1 | Cands[r3][c1]
                                for r4 in range(r3+1, 8):
                                    if r4 != r and 2 <= len(Cands[r4][c1]) <= 6 and len(U2 | Cands[r4][c1]) <= 6:
                                        BS3 = BS2+[(r4, c1, Cands[r4][c1])]; U3 = U2 | Cands[r4][c1]
                                        for r5 in range(r4+1, 9):
                                            if r5 != r and 2 <= len(Cands[r5][c1]) <= 6 and len(U3 | Cands[r5][c1]) == 6:
                                                if bent_subset_elims(BS3+[(r5, c1, Cands[r5][c1])], U3 | Cands[r5][c1], Cands, Step, Methods): return 0
                # No 2 by row 4 by col, try 4 by box.
                rb = (r//3)*3; CB = list({(c0//3)*3, (c1//3)*3})
                if len(CB) == 1: continue  # pattern want at least one cell outside the box.
                for cb in CB:
                    for b2 in range(6):
                        r2 = rb + b2//3; c2 = cb + b2%3
                        if r2 != r and 2 <= len(Cands[r2][c2]) <=6 and len(U | Cands[r2][c2]) <= 6:
                            BS1 = BS + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                            for b3 in range(b2+1, 7):
                                r3 = rb + b3//3; c3 = cb + b3%3
                                if r3 != r and 2 <= len(Cands[r3][c3]) <= 6 and len(U1 | Cands[r3][c3]) <= 6:
                                    BS2 = BS1 + [(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                    for b4 in range(b3+1, 8):
                                        r4 = rb + b4//3; c4 = cb + b4%3
                                        if r4 != r and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                            BS3 = BS2 + [(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                            for b5 in range(b4+1, 9):
                                                r5 = rb + b5//3; c5 = cb + b5%3
                                                if r5 != r and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                                    if bent_subset_elims(BS3 + [(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
    # No bent sext patterns found in 2, 3 or 4 by row, and balance in cols or boxes, look for 1 in row, 4 in col patterns
    # scan cols by boxes, cols x rows already done above
    for c in range(9):
        for r0 in range(8):
            if not 2 <= len(Cands[r0][c]) <= 5: continue
            for r1 in range(r0+1, 9):
                U = Cands[r0][c] | Cands[r1][c]
                if not 2 <= len(Cands[r1][c]) <= 5 or len(U) > 5: continue
                BS = [(r0, c, Cands[r0][c]), (r1, c, Cands[r1][c])]
                # 2 possible cells in the col, if the second cell is not at the end of the col, look for a third col cell
                for r2 in range(r1+1, 9):
                    U1 = U | Cands[r2][c]
                    if not 2 <= len(Cands[r2][c]) <= 5 or len(U1) > 5: continue
                    BS1 = BS + [(r2, c, Cands[r2][c])]
                    # 3 possible cells in the col, if the 3rd cell is not at the end of the col, look for a fourth col cell
                    for r3 in range(r2+1, 9):
                        U2 = U1 | Cands[r3][c]
                        if not 2 <= len(Cands[r3][c]) <=5 or len(U2) > 5: continue
                        BS2 = BS1 + [(r3, c, Cands[r3][c])]
                        # 4th possible cell found, if not at end of col, look for 5th cell
                        for r4 in range(r3+1, 9):
                            U3 = U2 | Cands[r4][c]
                            if not 2 <= len(Cands[r4][c]) <= 6 or len(U3) > 6: continue
                            BS3 = BS2 + [(r4, c, Cands[r4][c])]
                            # 5th cell found look in boxes for 6th.
                            RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3, (r3//3)*3, (r4//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                            for rb in RB:
                                for b in range(9):
                                    r5 = rb + b//3; c5 = cb +b%3
                                    if c5 != c and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                        if bent_subset_elims(BS3 + [(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                        #  4 cells in the col, look for cells 5 and 6 in boxes.
                        RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3, (r3//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                        for rb in RB:
                            for b4 in range(8):
                                r4 = rb + b4//3; c4 = cb + b4%3
                                if c4 != c and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                    BS3 = BS2 + [(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                    for b5 in range(b4+1, 9):
                                        r5= rb + b5//3; c5= cb + b5%3
                                        if c5 != c and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                            if bent_subset_elims(BS3 + [(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                    # 3 cells in the col, look in boxes for remaining 3 cells.
                    RB = list({(r0//3)*3, (r1//3)*3, (r2//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                    if len(RB)== 1: continue  # pattern want at least one cell outside the box.
                    for rb in RB:
                        for b3 in range(7):
                            r3 = rb + b3//3; c3 = cb + b3%3
                            if c3 != c and 2 <= len(Cands[r3][c3]) <= 6 and len(U1 | Cands[r3][c3]) <= 6:
                                BS2 = BS1 + [(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                for b4 in range(b3+1, 8):
                                    r4 = rb + b4//3; c4 = cb + b4%3
                                    if c4 != c and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                        BS3 = BS2 + [(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                        for b5 in range(b4+1, 9):
                                            r5 = rb + b5//3; c5 = cb + b5%3
                                            if c5 != c and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                                if bent_subset_elims(BS3 + [(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
                # 2 cells in the col, look in boxes for remaining 4 cells.
                RB = list({(r0//3)*3, (r1//3)*3}); cb = (c//3)*3  # set to remove dup boxes to search.
                if len(RB)== 1: continue  # pattern want at least one cell outside the box.
                for rb in RB:
                    for b2 in range(6):
                        r2 = rb + b2//3; c2 = cb + b2%3
                        if c2 != c and 2 <= len(Cands[r2][c2]) <= 6 and len(U | Cands[r2][c2]) <= 6:
                            BS1 = BS + [(r2, c2, Cands[r2][c2])]; U1 = U | Cands[r2][c2]
                            for b3 in range(b2+1, 7):
                                r3 = rb + b3//3; c3 = cb + b3%3
                                if c3 != c and 2 <= len(Cands[r3][c3]) <= 6 and len(U1 | Cands[r3][c3]) <= 6:
                                    BS2 = BS1 + [(r3, c3, Cands[r3][c3])]; U2 = U1 | Cands[r3][c3]
                                    for b4 in range(b3+1, 8):
                                        r4 = rb + b4//3; c4 = cb + b4%3
                                        if c4 != c and 2 <= len(Cands[r4][c4]) <= 6 and len(U2 | Cands[r4][c4]) <= 6:
                                            BS3 = BS2 + [(r4, c4, Cands[r4][c4])]; U3 = U2 | Cands[r4][c4]
                                            for b5 in range(b4+1, 9):
                                                r5 = rb + b5//3; c5 = cb + b5%3
                                                if c5 != c and 2 <= len(Cands[r5][c5]) <= 6 and len(U3 | Cands[r5][c5]) == 6:
                                                    if bent_subset_elims(BS3 + [(r5, c5, Cands[r5][c5])], U3 | Cands[r5][c5], Cands, Step, Methods): return 0
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
    elif NrCells == 4:
        if T_BENT_EXPOSED_QUAD in Methods: Step.Method = T_BENT_EXPOSED_QUAD
        else: return False
    elif NrCells == 5:
        if T_BENT_EXPOSED_QUINT in Methods: Step.Method = T_BENT_EXPOSED_QUINT
        else: return False
    elif NrCells == 6:
        if T_BENT_EXPOSED_SEXT in Methods: Step.Method = T_BENT_EXPOSED_SEXT
        else: return False

    Elims = []
    for r0, c0 in cells_that_see_all_of(URCCells):
        if URC in Cands[r0][c0]:
            Cands[r0][c0].discard(URC)
            if Step.Outcome: Step.Outcome.append([P_SEP])
            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, URC]])
            Elims.append((r0, c0))
    if Step.Outcome:
        Step.Outcome.append([P_END])
        Step.Pattern = []
        for r0, c0, Cands0 in Cells:
            if Step.Pattern: Step.Pattern.append([P_CON])
            Step.Pattern.extend([[P_VAL, sorted(Cands0)], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
        Step.Pattern.append([P_SEP])   #  [[P_SEP], [P_OP, OP_PARO]])
        if len(Elims) == 1:
            r0, c0 = Elims[0]
            Step.Pattern.extend([[P_VAL, URC], [P_ROW, r0], [P_COL, c0]])
        else:
            Pat = []
            for r0, c0 in Elims:
                if Pat: Pat.append([P_CON])
                Pat.extend([[P_VAL, URC], [P_ROW, r0], [P_COL, c0]])
            Step.Pattern.extend([[P_OP, OP_PARO], *Pat, [P_OP, OP_PARC]])
        Step.Pattern.extend([[P_OP, OP_WLK], [P_OP, OP_URES], [P_VAL, URC], [P_OP, OP_PARO]])
        Pat = []
        for r0, c0 in URCCells:
            if Pat: Pat.append([P_CON])
            Pat.extend([[P_ROW, r0], [P_COL, c0]])
        Step.Pattern.extend(Pat)
        Step.Pattern.extend([[P_OP, OP_PARC], [P_END]])
        return True
    return False

def tech_grouped_bent_pair(Grid, Step, Cands, Methods):

    for r in range(9):
        f0 = (r//3)*3; F = sorted({0, 3, 6} - {f0})
        rb1, rb2 = sorted({f0, f0+1, f0+2} - {r})
        for c in range(9):
            if len(Cands[r][c]) != 2: continue
            Pair = Cands[r][c]  # Pair found
            t0 = (c//3)*3; T = sorted({0, 3, 6} - {t0})
            cb1, cb2 = sorted({t0, t0+1, t0+2} - {c})
            rb0 = cb0 = 0
            if T_GROUPED_BENT_PAIR_ER_HB in Methods:  # Exposed in row,
                for t in T:
                    if Pair <= Cands[r][t] | Cands[r][t+1] | Cands[r][t+2]:  # Almost pair found in rowbox:
                        n = 0
                        for rb, cb in [(rb1, t), (rb1, t+1), (rb1, t+2), (rb2, t), (rb2, t+1), (rb2, t+2)]:
                            if Pair & Cands[rb][cb]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = cb
                        else:
                            if n and Pair <= Cands[rb0][cb0]:  # == 1:  # Grouped bent pair found, how productive is it?
                                T1 = sorted({0, 3, 6}-{t})
                                for c1 in [T1[0], T1[0]+1, T1[0]+2, T1[1], T1[1]+1, T1[1]+2]:
                                    if c1 == c: continue
                                    Elims = Cands[r][c1] & Pair
                                    if Elims:
                                        Cands[r][c1] -= Pair
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                Elims = Cands[rb0][cb0]-Pair
                                if Elims:
                                    Cands[rb0][cb0] = copy(Pair)
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, rb0], [P_COL, cb0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                if Step.Outcome:
                                    Step.Method = T_GROUPED_BENT_PAIR_ER_HB
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, r], [P_COL, t, t+1, t+2], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_EC_HB in Methods:  # Exposed in col
                for f in F:
                    if Pair <= Cands[f][c] | Cands[f+1][c] | Cands[f+2][c]:  # Almost pair found in colbox
                        n = 0
                        for rb, cb in [(f, cb1), (f+1, cb1), (f+2, cb1), (f, cb2), (f+1, cb2), (f+2, cb2)]:
                            if Pair & Cands[rb][cb]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = cb
                        else:
                            if n and Pair <= Cands[rb0][cb0]:
                                F1 = sorted({0, 3, 6} - {f})
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
                                    Step.Method = T_GROUPED_BENT_PAIR_EC_HB
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, f, f+1, f+2], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_HR_EB in Methods:  # Hidden Row, Exposed Box
                for rb in [rb1, rb2]:
                    if Pair <= Cands[rb][t0] | Cands[rb][t0+1] | Cands[rb][t0+2]:  # Almost pair found in rowbox.
                        n = 0
                        for c1 in [T[0], T[0]+1, T[0]+2, T[1], T[1]+1, T[1]+2]:
                            if Pair & Cands[rb][c1]:
                                if n: break
                                n += 1; rb0 = rb; cb0 = c1
                        else:
                            if n and Pair <= Cands[rb0][cb0]:  # == 1:  # Grouped bent pair found, how productive is it?
                                F1 = sorted({f0, f0+1, f0+2} - {rb})
                                for rbx, cbx in [(F1[0], t0), (F1[0], t0+1), (F1[0], t0+2), (F1[1], t0), (F1[1], t0+1), (F1[1], t0+2)]:
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
                                    Step.Method = T_GROUPED_BENT_PAIR_HR_EB
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, rb0], [P_COL, t0, t0+1, t0+2], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
            if T_GROUPED_BENT_PAIR_HC_EB in Methods:  # Hidden Column, Exposed Box
                for cb in [cb1, cb2]:
                    if Pair <= Cands[f0][cb] | Cands[f0+1][cb] | Cands[f0+2][cb]:  # almost pair found in colbox
                        n = 0
                        for r1 in [F[0], F[0]+1, F[0]+2, F[1], F[1]+1, F[1]+2]:
                            if Pair & Cands[r1][cb]:
                                if n: break
                                n += 1; rb0 = r1; cb0 = cb
                        else:
                            if n and Pair <= Cands[rb0][cb0]:
                                T1 = sorted({t0, t0+1, t0+2} - {cb})
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
                                    Step.Method = T_GROUPED_BENT_PAIR_HC_EB
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Pair)], [P_ROW, f0, f0+1, f0+2], [P_COL, cb0], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Pair)], [P_OP, OP_PRES], [P_ROW, rb0], [P_COL, cb0], [P_END]]
                                    return 0
    return -1

def tech_grouped_bent_triple(Grid, Step, Cands, Methods):

    if T_GROUPED_BENT_TRIPLE_ER_HB in Methods:  # Exposed in row
        for r in range(9):
            f0 = (r//3)*3; rb1, rb2 = sorted({f0, f0+1, f0+2} - {r})
            for c0 in range(8):
                if not 2 <= len(Cands[r][c0]) <= 3: continue
                for c1 in range(c0+1, 9):
                    if not 2 <= len(Cands[r][c1]) <= 3: continue
                    Trip = Cands[r][c0] | Cands[r][c1]
                    if len(Trip) != 3: continue
                    for t in sorted({0, 3, 6} - {(c0//3)*3, (c1//3)*3}):
                        if Trip <= Cands[r][t] | Cands[r][t+1] | Cands[r][t+2]:  # row conditions satisfied, look in box
                            n = 0; HT = []
                            for rb, cb in [(rb1, t), (rb1, t+1), (rb1, t+2), (rb2, t), (rb2, t+1), (rb2, t+2)]:
                                if Trip & Cands[rb][cb]:
                                    if n > 1: break
                                    n += 1; HT.append((rb, cb))
                            else:
                                if n == 2:
                                    rb3, cb3 = HT[0]; rb4, cb4 = HT[1]
                                    if len(Trip & Cands[rb3][cb3]) and len(Trip & Cands[rb4][cb4]) and Trip <= (Cands[rb3][cb3] | Cands[rb4][cb4]):
                                        # ER pattern found, what can be eliminated.
                                        T1 = sorted({0, 3, 6} - {t})  # look in the row.
                                        for c2 in [T1[0], T1[0]+1, T1[0]+2, T1[1], T1[1]+1, T1[1]+2]:
                                            if c2 == c0 or c2 == c1: continue
                                            Elims = Cands[r][c2] & Trip
                                            if Elims:
                                                Cands[r][c2] -= Trip
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, r], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        #  look in the box
                                        Elims = Cands[rb3][cb3] - Trip
                                        if Elims:
                                            Cands[rb3][cb3] -= Elims
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, rb3], [P_COL, cb3], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        Elims = Cands[rb4][cb4] - Trip
                                        if Elims:
                                            Cands[rb4][cb4] -= Elims
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, rb4], [P_COL, cb4], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        if Step.Outcome:
                                            Step.Method = T_GROUPED_BENT_TRIPLE_ER_HB
                                            Step.Outcome.append([P_END])
                                            Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Trip)], [P_ROW, r], [P_COL, t, t+1, t+2], [P_CON],
                                                            [P_VAL, sorted(Cands[r][c0])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c0], [P_CON],
                                                            [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c1], [P_CON],
                                                            [P_VAL, sorted(Trip & Cands[rb3][cb3])], [P_OP, OP_PRES], [P_ROW, rb3], [P_COL, cb3], [P_CON],
                                                            [P_VAL, sorted(Trip & Cands[rb4][cb4])], [P_OP, OP_PRES], [P_ROW, rb4], [P_COL, cb4], [P_END]]
                                            return 0
    if T_GROUPED_BENT_TRIPLE_EC_HB in Methods:  # Exposed in col, hidden in box
        for c in range(9):
            t0 = (c//3)*3; cb1, cb2 = sorted({t0, t0+1, t0+2} - {c})
            for r0 in range(8):
                if not 2 <= len(Cands[r0][c]) <= 3: continue
                for r1 in range(r0+1, 9):
                    if not 2 <= len(Cands[r1][c]) <= 3: continue
                    Trip = Cands[r0][c] | Cands[r1][c]
                    if len(Trip) != 3: continue
                    for f in sorted({0, 3, 6} - {(r0//3)*3, (r1//3)*3}):
                        if Trip <= Cands[f][c] | Cands[f+1][c] | Cands[f+2][c]:  # col conditions satisfied, look in box
                            n = 0; HF = []
                            for rb, cb in [(f, cb1), (f+1, cb1), (f+2, cb1), (f, cb2), (f+1, cb2), (f+2, cb2)]:
                                if Trip & Cands[rb][cb]:
                                    if n > 1: break
                                    n += 1; HF.append((rb, cb))
                            else:
                                if n == 2:
                                    rb3, cb3 = HF[0]; rb4, cb4 = HF[1]
                                    if len(Trip & Cands[rb3][cb3]) and len(Trip & Cands[rb4][cb4]) and Trip <= (Cands[rb3][cb3] | Cands[rb4][cb4]):
                                        # ER pattern found, what can be eliminated.
                                        F1 = sorted({0, 3, 6} - {f})  # look in the row.
                                        for r2 in [F1[0], F1[0]+1, F1[0]+2, F1[1], F1[1]+1, F1[1]+2]:
                                            if r2 == r0 or r2 == r1: continue
                                            Elims = Cands[r2][c] & Trip
                                            if Elims:
                                                Cands[r2][c] -= Trip
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, r2], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        #  look in the box
                                        Elims = Cands[rb3][cb3] - Trip
                                        if Elims:
                                            Cands[rb3][cb3] -= Elims
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, rb3], [P_COL, cb3], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        Elims = Cands[rb4][cb4] - Trip
                                        if Elims:
                                            Cands[rb4][cb4] -= Elims
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, rb4], [P_COL, cb4], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                        if Step.Outcome:
                                            Step.Method = T_GROUPED_BENT_TRIPLE_EC_HB
                                            Step.Outcome.append([P_END])
                                            Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Trip)], [P_ROW, f,  f+1, f+2], [P_COL, c], [P_CON],
                                                            [P_VAL, sorted(Cands[r0][c])], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c], [P_CON],
                                                            [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c], [P_CON],
                                                            [P_VAL, sorted(Trip & Cands[rb3][cb3])], [P_OP, OP_PRES], [P_ROW, rb3], [P_COL, cb3], [P_CON],
                                                            [P_VAL, sorted(Trip & Cands[rb4][cb4])], [P_OP, OP_PRES], [P_ROW, rb4], [P_COL, cb4], [P_END]]
                                            return 0
    if {T_GROUPED_BENT_TRIPLE_HR_EB, T_GROUPED_BENT_TRIPLE_HC_EB} & set(Methods):  # exposed in box
        for f, t in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
            for h0 in range(8):
                rb0 = f + h0//3; cb0 = t + h0%3
                if not 2 <= len(Cands[rb0][cb0]) <= 3: continue
                for h1 in range(h0+1, 9):
                    rb1 = f + h1//3; cb1 = t + h1%3
                    if not 2 <= len(Cands[rb1][cb1]) <= 3: continue
                    Trip = Cands[rb0][cb0] | Cands[rb1][cb1]
                    if len(Trip) != 3: continue
                    if T_GROUPED_BENT_TRIPLE_HR_EB in Methods:
                        T = sorted({0, 3, 6}-{t})
                        for r in sorted({f, f+1, f+2} - {rb0, rb1}):
                            if Trip <= (Cands[r][t] | Cands[r][t+1] | Cands[r][t+2]):  # Box condition satisfied for row
                                n = 0; HR = []
                                for c in [T[0], T[0]+1, T[0]+2, T[1], T[1]+1, T[1]+2]:
                                    if Trip & Cands[r][c]:
                                        if n > 1: break
                                        n += 1; HR.append(c)
                                else:
                                    if n == 2:
                                        if len(Cands[r][HR[0]] & Trip) and len(Cands[r][HR[1]] & Trip) and Trip <= (Cands[r][HR[0]] | Cands[r][HR[1]]):
                                            # Hidden condition satisfied in row, what can be eliminated.
                                            R1 = sorted({f, f+1, f+2} - {r})  # look in the box
                                            for rb, cb in [(R1[0], t), (R1[0], t+1), (R1[0], t+2), (R1[1], t), (R1[1], t+1), (R1[1], t+2)]:
                                                if (rb, cb) == (rb0, cb0) or (rb, cb) == (rb1, cb1): continue
                                                Elims = Cands[rb][cb] & Trip
                                                if Elims:
                                                    Cands[rb][cb] -= Trip
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, rb], [P_COL, cb], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[r][HR[0]] - Trip
                                            if Elims:
                                                Cands[r][HR[0]] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, r], [P_COL, HR[0]], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[r][HR[1]] - Trip
                                            if Elims:
                                                Cands[r][HR[1]] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, r], [P_COL, HR[1]], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            if Step.Outcome:
                                                Step.Method = T_GROUPED_BENT_TRIPLE_HR_EB
                                                Step.Outcome.append([P_END])
                                                Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Trip)], [P_ROW, r], [P_COL, t, t+1, t+2], [P_CON],
                                                                [P_VAL, sorted(Cands[rb0][cb0])], [P_OP, OP_EQ], [P_ROW, rb0], [P_COL, cb0], [P_CON],
                                                                [P_VAL, sorted(Cands[rb1][cb1])], [P_OP, OP_EQ], [P_ROW, rb1], [P_COL, cb1], [P_CON],
                                                                [P_VAL, sorted(Trip & Cands[r][HR[0]])], [P_OP, OP_PRES], [P_ROW, r], [P_COL, HR[0]], [P_CON],
                                                                [P_VAL, sorted(Trip & Cands[r][HR[1]])], [P_OP, OP_PRES], [P_ROW, r], [P_COL, HR[1]], [P_END]]
                                                return 0
                    if T_GROUPED_BENT_TRIPLE_HC_EB in Methods:
                        F = sorted({0, 3, 6} - {f})
                        for c in sorted({t, t+1, t+2} - {cb0, cb1}):
                            if Trip <= (Cands[f][c] | Cands[f+1][c] | Cands[f+2][c]):  # box condition satisfied for col
                                n = 0; HC = []
                                for r in [F[0], F[0]+1, F[0]+2, F[1], F[1]+1, F[1]+2]:
                                    if Trip & Cands[r][c]:
                                        if n > 1: break
                                        n += 1; HC.append(r)
                                else:
                                    if n == 2:
                                        if len(Cands[HC[0]][c] & Trip) and len(Cands[HC[1]][c] & Trip) and Trip <= (Cands[HC[0]][c] | Cands[HC[1]][c]):
                                            # Hidden condition also satisfied in col, what can be eliminated
                                            C1 = sorted({t, t+1, t+2} - {c})
                                            for (rb, cb) in [(f, C1[0]), (f+1, C1[0]), (f+2, C1[0]), (f, C1[0]), (f+1, C1[0]), (f+2, C1[0])]:
                                                if (rb, cb) == (rb0, cb0) or (rb, cb) == (rb1, cb1): continue
                                                Elims = Cands[rb][cb] & Trip
                                                if Elims:
                                                    Cands[rb][cb] -= Trip
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, rb], [P_COL, cb], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[HC[0]][c] - Trip
                                            if Elims:
                                                Cands[HC[0]][c] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, HC[0]], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[HC[1]][c] - Trip
                                            if Elims:
                                                Cands[HC[1]][c] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, HC[1]], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            if Step.Outcome:
                                                Step.Method = T_GROUPED_BENT_TRIPLE_HC_EB
                                                Step.Outcome.append([P_END])
                                                Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Trip)], [P_ROW, f, f+1, f+2], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Cands[rb0][cb0])], [P_OP, OP_EQ], [P_ROW, rb0], [P_COL, cb0], [P_CON],
                                                                [P_VAL, sorted(Cands[rb1][cb1])], [P_OP, OP_EQ], [P_ROW, rb1], [P_COL, cb1], [P_CON],
                                                                [P_VAL, sorted(Trip & Cands[HC[0]][c])], [P_OP, OP_PRES], [P_ROW, HC[0]], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Trip & Cands[HC[1]][c])], [P_OP, OP_PRES], [P_ROW, HC[1]], [P_COL, c], [P_END]]
                                                return 0
    return -1

def tech_grouped_bent_quad(Grid, Step, Cands, Methods):

    if T_GROUPED_BENT_QUAD_ER_HB in Methods:  # Exposed in row, hidden in box
        for r in range(9):
            f0 = (r//3)*3; rb1, rb2 = sorted({f0, f0+1, f0+2} - {r})
            for c0 in range(7):
                if not 2 <= len(Cands[r][c0]) <= 4: continue
                for c1 in range(c0+1, 8):
                    if not 2 <= len(Cands[r][c1]) <= 4: continue
                    for c2 in range(c1+1, 9):
                        if not 2 <= len(Cands[r][c2]) <= 4: continue
                        Quad = Cands[r][c0] | Cands[r][c1] | Cands[r][c2]
                        if len(Quad) != 4: continue
                        for t in sorted({0, 3, 6} - {(c0//3)*3, (c1//3)*3, (c2//3)*3}):
                            if Quad <= Cands[r][t] | Cands[r][t+1] | Cands[r][t+2]:  # Exposed Quad condition satisfied in row
                                n = 0; HQ = []
                                for rb, cb in [(rb1, t), (rb1, t+1), (rb1, t+2), (rb2, t), (rb2, t+1), (rb2, t+2)]:
                                    if Quad & Cands[rb][cb]:
                                        if n > 2: break
                                        n += 1; HQ.append((rb, cb))
                                else:
                                    if n == 3:
                                        rb3, cb3 = HQ[0]; rb4, cb4 = HQ[1]; rb5, cb5 = HQ[2]
                                        if len(Quad & Cands[rb3][cb3]) and len(Quad & Cands[rb4][cb4]) and len(Quad & Cands[rb5][cb5]) and Quad <= (Cands[rb3][cb3] | Cands[rb4][cb4] | Cands[rb5][cb5]):
                                            # ER pattern found, what can be eliminated.
                                            T1 = sorted({0, 3, 6} - {t})  # look in the row.
                                            for c3 in [T1[0], T1[0]+1, T1[0]+2, T1[1], T1[1]+1, T1[1]+2]:
                                                if c3 == c0 or c3 == c1 or c3 == c2: continue
                                                Elims = Cands[r][c3] & Quad
                                                if Elims:
                                                    Cands[r][c3] -= Quad
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            #  look in the box
                                            Elims = Cands[rb3][cb3] - Quad
                                            if Elims:
                                                Cands[rb3][cb3] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb3], [P_COL, cb3], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[rb4][cb4] - Quad
                                            if Elims:
                                                Cands[rb4][cb4] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb4], [P_COL, cb4], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[rb5][cb5] - Quad
                                            if Elims:
                                                Cands[rb5][cb5] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb5], [P_COL, cb5], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            if Step.Outcome:
                                                Step.Method = T_GROUPED_BENT_QUAD_ER_EB
                                                Step.Outcome.append([P_END])
                                                Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Quad)], [P_ROW, r], [P_COL, t, t+1, t+2], [P_CON],
                                                                [P_VAL, sorted(Cands[r][c0])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c0], [P_CON],
                                                                [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c1], [P_CON],
                                                                [P_VAL, sorted(Cands[r][c2])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c2], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb3][cb3])], [P_OP, OP_PRES], [P_ROW, rb3], [P_COL, cb3], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb4][cb4])], [P_OP, OP_PRES], [P_ROW, rb4], [P_COL, cb4], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb5][cb5])], [P_OP, OP_PRES], [P_ROW, rb5], [P_COL, cb5], [P_END]]
                                                return 0
    if T_GROUPED_BENT_QUAD_EC_HB in Methods:  # Exposed in col, hidden in box
        for c in range(9):
            t0 = (c//3)*3; cb1 = t0+(c-t0+1)%3; cb2 = t0+(c-t0+2)%3
            for r0 in range(7):
                if not 2 <= len(Cands[r0][c]) <= 4: continue
                for r1 in range(r0+1, 8):
                    if not 2 <= len(Cands[r1][c]) <= 4: continue
                    for r2 in range(r1+1, 9):
                        if not 2 <= len(Cands[r2][c]) <= 4: continue
                        Quad = Cands[r0][c] | Cands[r1][c] | Cands[r2][c]
                        if len(Quad) != 4: continue
                        for f in sorted({0, 3, 6} - {(r0//3)*3, (r1//3)*3, (r2//3)*3}):
                            if Quad <= Cands[f][c] | Cands[f+1][c] | Cands[f+2][c]:  # Exposed Quad condition satisfied in col
                                n = 0; HQ = []
                                for rb, cb in [(f, cb1), (f+1, cb1), (f+2, cb1), (f, cb2), (f+1, cb2), (f+2, cb2)]:
                                    if Quad & Cands[rb][cb]:
                                        if n > 2: break
                                        n += 1; HQ.append((rb, cb))
                                else:
                                    if n == 3:
                                        rb3, cb3 = HQ[0]; rb4, cb4 = HQ[1]; rb5, cb5 = HQ[2]
                                        if len(Quad & Cands[rb3][cb3]) and len(Quad & Cands[rb4][cb4]) and len(Quad & Cands[rb5][cb5]) and Quad <= (Cands[rb3][cb3] | Cands[rb4][cb4] | Cands[rb5][cb5]):
                                            # ER pattern found, what can be eliminated.
                                            F1 = sorted({0, 3, 6} - {f})  # look in the row.
                                            for r3 in [F1[0], F1[0]+1, F1[0]+2, F1[1], F1[1]+1, F1[1]+2]:
                                                if r3 == r0 or r3 == r1 or r3 == r2: continue
                                                Elims = Cands[r3][c] & Quad
                                                if Elims:
                                                    Cands[r3][c] -= Quad
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r3], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            #  look in the box
                                            Elims = Cands[rb3][cb3] - Quad
                                            if Elims:
                                                Cands[rb3][cb3] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb3], [P_COL, cb3], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[rb4][cb4] - Quad
                                            if Elims:
                                                Cands[rb4][cb4] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb4], [P_COL, cb4], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            Elims = Cands[rb5][cb5] - Quad
                                            if Elims:
                                                Cands[rb5][cb5] -= Elims
                                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                                Step.Outcome.extend([[P_ROW, rb5], [P_COL, cb5], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                            if Step.Outcome:
                                                Step.Method = T_GROUPED_BENT_QUAD_EC_HB
                                                Step.Outcome.append([P_END])
                                                Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Quad)], [P_ROW, f, f+1, f+2], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Cands[r0][c])], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Cands[r2][c])], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb3][cb3])], [P_OP, OP_PRES], [P_ROW, rb3], [P_COL, cb3], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb4][cb4])], [P_OP, OP_PRES], [P_ROW, rb4], [P_COL, cb4], [P_CON],
                                                                [P_VAL, sorted(Quad & Cands[rb5][cb5])], [P_OP, OP_PRES], [P_ROW, rb5], [P_COL, cb5], [P_END]]
                                                return 0
    if {T_GROUPED_BENT_QUAD_HR_EB, T_GROUPED_BENT_QUAD_HC_EB} & set(Methods):  # exposed in box
        for f, t in [(0, 0), (0, 3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]:
            for h0 in range(7):
                rb0 = f + h0//3; cb0 = t + h0%3
                if not 2 <= len(Cands[rb0][cb0]) <= 4: continue
                for h1 in range(h0+1, 8):
                    rb1 = f + h1//3; cb1 = t + h1%3
                    if not 2 <= len(Cands[rb1][cb1]) <= 4: continue
                    for h2 in range(h1+1, 9):
                        rb2 = f + h2//3; cb2 = t + h2%3
                        if not 2 <= len(Cands[rb2][cb2]) <= 4: continue
                        Quad = Cands[rb0][cb0] | Cands[rb1][cb1] | Cands[rb2][cb2]
                        if len(Quad) != 4: continue
                        if T_GROUPED_BENT_QUAD_HR_EB in Methods:
                            T = sorted({0, 3, 6}-{t})
                            for r in sorted({f, f+1, f+2} - {rb0, rb1, rb2}):
                                if Quad <= (Cands[r][t] | Cands[r][t+1] | Cands[r][t+2]):  # Box condition satisfied for row
                                    n = 0; HR = []
                                    for c in [T[0], T[0]+1, T[0]+2, T[1], T[1]+1, T[1]+2]:
                                        if Quad & Cands[r][c]:
                                            if n > 2: break
                                            n += 1; HR.append(c)
                                    else:
                                        if n == 3:
                                            if len(Cands[r][HR[0]] & Quad) and len(Cands[r][HR[1]] & Quad) and len(Cands[r][HR[2]] & Quad) and Quad <= (Cands[r][HR[0]] | Cands[r][HR[1]] | Cands[r][HR[2]]):
                                                # Hidden condition satisfied in row, what can be eliminated.
                                                R1 = sorted({f, f+1, f+2}-{r})  # look in the box
                                                for rb, cb in [(R1[0], t), (R1[0], t+1), (R1[0], t+2), (R1[1], t), (R1[1], t+1), (R1[1], t+2)]:
                                                    if (rb, cb) == (rb0, cb0) or (rb, cb) == (rb1, cb1) or (rb, cb) == (rb2, cb2): continue
                                                    Elims = Cands[rb][cb] & Quad
                                                    if Elims:
                                                        Cands[rb][cb] -= Quad
                                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                                        Step.Outcome.extend([[P_ROW, rb], [P_COL, cb], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[r][HR[0]] - Quad
                                                if Elims:
                                                    Cands[r][HR[0]] -= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r], [P_COL, HR[0]], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[r][HR[1]] - Quad
                                                if Elims:
                                                    Cands[r][HR[1]] -= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r], [P_COL, HR[1]], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[r][HR[2]] - Quad
                                                if Elims:
                                                    Cands[r][HR[2]] -= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r], [P_COL, HR[2]], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                if Step.Outcome:
                                                    Step.Method = T_GROUPED_BENT_QUAD_HR_EB
                                                    Step.Outcome.append([P_END])
                                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Quad)], [P_ROW, r], [P_COL, t, t+1, t+2], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb0][cb0])], [P_OP, OP_EQ], [P_ROW, rb0], [P_COL, cb0], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb1][cb1])], [P_OP, OP_EQ], [P_ROW, rb1], [P_COL, cb1], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb2][cb2])], [P_OP, OP_EQ], [P_ROW, rb2], [P_COL, cb2], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[r][HR[0]])], [P_OP, OP_PRES], [P_ROW, r], [P_COL, HR[0]], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[r][HR[1]])], [P_OP, OP_PRES], [P_ROW, r], [P_COL, HR[1]], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[r][HR[2]])], [P_OP, OP_PRES], [P_ROW, r], [P_COL, HR[2]], [P_END]]
                                                    return 0
                        if T_GROUPED_BENT_QUAD_HC_EB in Methods:
                            F = sorted({0, 3, 6}-{f})
                            for c in sorted({t, t+1, t+2}-{cb0, cb1, cb2}):
                                if Quad <= (Cands[f][c] | Cands[f+1][c] | Cands[f+2][c]):  # box condition satisfied for col
                                    n = 0; HC = []
                                    for r in [F[0], F[0]+1, F[0]+2, F[1], F[1]+1, F[1]+2]:
                                        if Quad & Cands[r][c]:
                                            if n > 2: break
                                            n += 1; HC.append(r)
                                    else:
                                        if n == 3:
                                            if len(Cands[HC[0]][c] & Quad) and len(Cands[HC[1]][c] & Quad) and len(Cands[HC[2]][c] & Quad) and Quad <= (Cands[HC[0]][c] | Cands[HC[1]][c] | Cands[HC[2]][c]):
                                                # Hidden condition also satisfied in col, what can be eliminated
                                                C1 = sorted({t, t+1, t+2}-{c})
                                                for (rb, cb) in [(f, C1[0]), (f+1, C1[0]), (f+2, C1[0]), (f, C1[0]), (f+1, C1[0]), (f+2, C1[0])]:
                                                    if (rb, cb) == (rb0, cb0) or (rb, cb) == (rb1, cb1) or (rb, cb) == (rb2, cb2): continue
                                                    Elims = Cands[rb][cb] & Quad
                                                    if Elims:
                                                        Cands[rb][cb] -= Quad
                                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                                        Step.Outcome.extend([[P_ROW, rb], [P_COL, cb], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[HC[0]][c] - Quad
                                                if Elims:
                                                    Cands[HC[0]][c] -= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, HC[0]], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[HC[1]][c] - Quad
                                                if Elims:
                                                    Cands[HC[1]][c]-= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, HC[1]], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[HC[2]][c] - Quad
                                                if Elims:
                                                    Cands[HC[2]][c] -= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, HC[2]], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                if Step.Outcome:
                                                    Step.Method = T_GROUPED_BENT_QUAD_HC_EB
                                                    Step.Outcome.append([P_END])
                                                    Step.Pattern = [[P_OP, OP_U], [P_VAL, sorted(Quad)], [P_ROW, f, f+1, f+2], [P_COL, c], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb0][cb0])], [P_OP, OP_EQ], [P_ROW, rb0], [P_COL, cb0], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb1][cb1])], [P_OP, OP_EQ], [P_ROW, rb1], [P_COL, cb1], [P_CON],
                                                                    [P_VAL, sorted(Cands[rb2][cb2])], [P_OP, OP_EQ], [P_ROW, rb2], [P_COL, cb2], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[HC[0]][c])], [P_OP, OP_PRES], [P_ROW, HC[0]], [P_COL, c], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[HC[1]][c])], [P_OP, OP_PRES], [P_ROW, HC[1]], [P_COL, c], [P_CON],
                                                                    [P_VAL, sorted(Quad & Cands[HC[2]][c])], [P_OP, OP_PRES], [P_ROW, HC[2]], [P_COL, c], [P_END]]
                                                    return 0
    return -1

def tech_bent_hidden_triple(Grid, Step, Cands, Methods):

    if T_BENT_HIDDEN_TRIPLE in Methods:
        for r0 in range(9):
            for Cand0 in range(1, 8):
                for Cand1 in range(Cand0+1, 9):
                    for Cand2 in range(Cand1+1, 10):
                        Trip = {Cand0, Cand1, Cand2}
                        for c0 in range(9):
                            if Trip <= Cands[r0][c0]:
                                t = (c0//3)*3; T = sorted({0, 3, 6} - {t})
                                n = 0; r2 = c2 = -1
                                for c1 in [T[0], T[0]+1, T[0]+2, T[1], T[1]+1, T[1]+2]:
                                    if len(Cands[r0][c1] & Trip):
                                        if n: break
                                        n += 1; c2 = c1
                                else:
                                    if n and len(Cands[r0][c2] & Trip) >= 2:  # row pattern found, find col.
                                        f = (r0//3)*3; F = sorted({0, 3, 6} - {f})
                                        n = 0
                                        for r1 in [F[0], F[0]+1, F[0]+2, F[1], F[1]+1, F[1]+2]:
                                            if len(Cands[r1][c0] & Trip):
                                                if n: break
                                                n += 1; r2 = r1
                                        else:
                                            if n and len((Cands[r0][c2] | Cands[r2][c0]) & Trip) == 3:  # Triple Fireworks pattern found, what can be eliminated
                                                Elims = Cands[r0][c0] - Trip
                                                if Elims:
                                                    Cands[r0][c0]-= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[r0][c2] - Trip
                                                if Elims:
                                                    Cands[r0][c2]-= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r0], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                Elims = Cands[r2][c0] - Trip
                                                if Elims:
                                                    Cands[r2][c0]-= Elims
                                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                                    Step.Outcome.extend([[P_ROW, r2], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Elims]])
                                                if Step.Outcome:
                                                    Step.Method = T_BENT_HIDDEN_TRIPLE
                                                    Step.Outcome.append([P_END])
                                                    Step.Pattern = [[P_VAL, sorted(Cands[r0][c2])], [P_ROW, r0], [P_COL, c2], [P_OP, OP_WLK],
                                                                    [P_VAL, sorted(Cands[r0][c0])], [P_ROW, r0], [P_COL, c0], [P_OP, OP_WLK],
                                                                    [P_VAL, sorted(Cands[r2][c0])], [P_ROW, r2], [P_COL, c0], [P_END]]
                                                    return 0
    return -1
