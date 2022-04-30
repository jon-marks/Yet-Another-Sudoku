
include "globals.pxi"
from globals import *
from trc cimport *
from trc import *

from solve_subsets cimport *
from solve_utils cimport *

cdef int tech_exposed_pairs_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # In any group (row, col or box), if any two cells have only the same two
    # candidates then we have found an exposed pair.  These candidates can be
    # eliminated from the balance of cells in that group.  If these two cell are
    # in the intersection of a box and a row or column, the we have a locked
    # exposed pair and the these candidates can be eliminated from the balance
    # of cells in the box and row/col.
    cdef int r0, c0, d, r1, c1, r2, c2, n, br, bc, or1, or2, oc1, oc2, t, rc0, rc1, rc2
    cdef int p[2]

    # TRCX(f"Cands: {trc_cands(Cands)}")
    # Scan the rows first.
    for r0 in range(9):
        for c0 in range(8):
            if Grid[r0][c0]: continue
            n = 0
            for d in range(9):
                # TRCX(f"Cell 1 Cands[{r0+1}][{c0+1}][{d+1}] = {Cands[r0][c0][d]}")
                if Cands[r0][c0][d]:
                    if n == 2: break
                    p[n] = d; n += 1
                    # TRCX(f"p: {p[0]},{p[1]}, n: {n}")
            else:
                # TRCX(f"Loop d: {d}, Else n:{n}")
                if n != 2: continue
                # Found a cell with only two candidates, continue scanning row for another
                # TRCX(f"First cell with only 2 cands: {p[0]+1}{p[1]+1}r{r0+1}c{c0+1}")
                for c1 in range(c0+1, 9):
                    if Grid[r0][c1]: continue
                    # TRCX(f"c1: {c1}, Looking for second cell with 2 cands")
                    n = 0
                    for d in range(9):
                        # TRCX(f"Cell 2 Cands[{r0+1}][{c1+1}][{d+1}] = {Cands[r0][c1][d]}")
                        if Cands[r0][c1][d]:
                            if n == 2: break
                            # TRCX(f"p: {p[0]+1},{p[1]+1}, n: {n}")
                            if d != p[n]: break
                            if d == p[n]: n += 1
                    else:
                        if n != 2: continue
                        # Found an exposed pair in a row, could it be a locked pair
                        # TRCX(f"Second cell with only 2 cands: {p[0]+1}{p[1]+1}r{r0+1}c{c1+1}")
                        if T_LOCKED_EXPOSED_PAIR in Methods:
                            if c0//3 == c1//3:
                                # yes, it is a locked pair too
                                br = (r0//3)*3; bc = (c0//3)*3
                                or1 = br + (r0+1)%3; or2 = br + (r0+2)%3
                                if or1 > or2: t = or1; or1 = or2; or2 = t
                                for c2 in range(bc, bc+3):
                                    if Cands[or1][c2][p[0]]:
                                        Cands[or1][c2][p[0]] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, or1], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                                    if Cands[or1][c2][p[1]]:
                                        Cands[or1][c2][p[1]] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, or1], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                                    if Cands[or2][c2][p[0]]:
                                        Cands[or2][c2][p[0]] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, or2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                                    if Cands[or2][c2][p[1]]:
                                        Cands[or2][c2][p[1]] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, or2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                        if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_PAIR
                        # else: Step.Method = T_EXPOSED_PAIR
                        # what can be eliminated along the row?
                        for c2 in range(9):
                            if c2 == c0 or c2 == c1: continue
                            if Cands[r0][c2][p[0]]:
                                Cands[r0][c2][p[0]] = False
                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                            if Cands[r0][c2][p[1]]:
                                Cands[r0][c2][p[1]] = False
                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                        if Step.Outcome:  # candidates are eliminated
                            if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_PAIR
                            Step.Outcome.append([P_END, ])
                            Step.Pattern = [[P_VAL, p[0]+1, p[1]+1], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0, c1], [P_END, ]]
                            return 0
    # then scan the cols.
    for c0 in range(9):
        for r0 in range(8):
            if Grid[r0][c0]: continue
            n = 0
            for d in range(9):
                # TRCX(f"Cell 1 Cands[{r0+1}][{c0+1}][{d+1}] = {Cands[r0][c0][d]}")
                if Cands[r0][c0][d]:
                    if n == 2: break
                    p[n] = d; n +=1
                    # TRCX(f"p: {p[0]},{p[1]}, n: {n}")
            else:
                if n != 2: continue
                # Found a cell with only 2 cands, continue to scan the col for another
                # TRCX(f"First cell with only 2 cands: {p[0]+1}{p[1]+1}r{r0+1}c{c0+1}")
                for r1 in range(r0+1, 9):
                    if Grid[r1][c0]: continue
                    n = 0
                    for d in range(9):
                        # TRCX(f"Cell 2 Cands[{r1+1}][{c0+1}][{d+1}] = {Cands[r1][c0][d]}")
                        if Cands [r1][c0][d]:
                            if n == 2: break
                            if d != p[n]: break
                            if d == p[n]: n += 1
                    else:
                        if n != 2: continue
                        # Found an exposed pair in a row, could it be a locked pair?
                        # TRCX(f"Second cell with only 2 cands: {p[0]+1}{p[1]+1}r{r1+1}c{c0+1}")
                        if T_LOCKED_EXPOSED_PAIR in Methods:
                            if r0//3 == r1//3:
                                # yes, it is a locked pair too.
                                br = (r0//3)*3; bc = (c0//3)*3
                                oc1 = bc + (c0+1)%3; oc2 = bc + (c0+2)%3
                                if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                                for r2 in range(br, br+3):
                                    if Cands[r2][oc1][p[0]]:
                                        Cands[r2][oc1][p[0]] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r2], [P_COL, oc1], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                                    if Cands[r2][oc1][p[1]]:
                                         Cands[r2][oc1][p[1]] = False
                                         if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                         Step.Outcome.extend([[P_ROW, r2], [P_COL, oc1], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                                    if Cands[r2][oc2][p[0]]:
                                         Cands[r2][oc2][p[0]] = False
                                         if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                         Step.Outcome.extend([[P_ROW, r2], [P_COL, oc2], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                                    if Cands[r2][oc2][p[1]]:
                                         Cands[r2][oc2][p[1]] = False
                                         if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                         Step.Outcome.extend([[P_ROW, r2], [P_COL, oc2], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                        if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_PAIR
                        # else: Step.Method = T_EXPOSED_PAIR
                        # what can be eliminated along the row?
                        for r2 in range(9):
                            if r2 == r0 or r2 == r1: continue
                            if Cands[r2][c0][p[0]]:
                                Cands[r2][c0][p[0]] = False
                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                Step.Outcome.extend([[P_ROW, r2], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                            if Cands[r2][c0][p[1]]:
                                Cands[r2][c0][p[1]] = False
                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                Step.Outcome.extend([[P_ROW, r2], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                        if Step.Outcome:  # candidates were eliminated
                            if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_PAIR
                            Step.Outcome.append([P_END, ])
                            Step.Pattern = [[P_VAL, p[0]+1, p[1]+1], [P_OP, OP_EQ], [P_ROW, r0, r1], [P_COL, c0], [P_END, ]]
                            return 0
    # and finally scan the blocks.
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for rc0 in range(8):
                r0 = br + (rc0//3); c0 = bc + (rc0%3)
                if Grid[r0][c0]: continue
                n = 0
                for d in range(9):
                    if Cands[r0][c0][d]:
                        if n == 2: break
                        p[n] = d; n += 1
                else:
                    if n != 2: continue
                    # Found a cell with only 2 cands, continue to scan box for another
                    for rc1 in range(rc0+1, 9):
                        r1 = br + (rc1//3); c1 = bc + (rc1%3)
                        if Grid[r1][c1]: continue
                        n = 0
                        for d in range(9):
                            if Cands[r1][c1][d]:
                                if n == 2: break
                                if d != p[n]: break
                                if d == p[n]: n += 1
                        else:
                            if n != 2: continue
                            # found an exposed pair in a box, discard matching cands from remaining cells in box
                            for rc2 in range(9):
                                r2 = br + (rc2//3); c2 = bc + (rc2%3)
                                if (r2 == r0 and c2 == c0) or (r2 == r1 and c2 == c1): continue
                                if Cands[r2][c2][p[0]]:
                                    Cands[r2][c2][p[0]] = False
                                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                    Step.Outcome.extend([[P_ROW, r2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[0]+1]])
                                if Cands[r2][c2][p[1]]:
                                    Cands[r2][c2][p[1]] = False
                                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                    Step.Outcome.extend([[P_ROW, r2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, p[1]+1]])
                            if Step.Outcome:  # candidates were eliminated
                                Step.Method = T_EXPOSED_PAIR
                                Step.Outcome.append([P_END, ])
                                Step.Pattern = [[P_VAL, p[0]+1, p[1]+1], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ], [P_ROW, r1], [P_COL, c1], [P_END, ]]
                                return 0
    return -1

cdef int tech_hidden_pairs_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # A hidden pair is where two cells in a group share the same two candidates
    # (out of all their candidates), which are not found elsewhere in the group.
    # That is the candidates of those two cells are limited to the pair of
    # candidates they share.  All other candidates in those two cells can be
    # eliminated, thereby exposing the pair.  Algorithmically, find two cands
    # in a cell and check if this pair of cands only occur twice in the group.
    cdef int r0, c0, r1, c1, d0, d1, d2, br, bc, b0, h0, n0
    cdef int p[2]

    for d0 in range(8):
        for d1 in range(d0+1, 9):
            # scan rows:
            for r0 in range(9):
                n0 = 0
                for c0 in range(9):
                    if Grid[r0][c0]: continue
                    if Cands[r0][c0][d0] != Cands[r0][c0][d1]: break
                    if Cands[r0][c0][d0] and Cands[r0][c0][d1]:
                        if n0 > 1: break
                        p[n0] = c0; n0 += 1
                else:
                    if n0 != 2: continue
                    # hidden pair found along r0
                    c0 = p[0]; c1 = p[1]
                    # TRCX(f"Hidden Pair: {d0+1}{d1+1}r{r0+1}c{c0+1}{c1+1}")
                    for d2 in range(9):
                        if d2 == d0 or d2 == d1: continue
                        if Cands[r0][c0][d2]:
                            Cands[r0][c0][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                        if Cands[r0][c1][d2]:
                            Cands[r0][c1][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END, ])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, d0+1, d1+1], [P_OP, OP_CNT, 2], [P_ROW, r0], [P_COL, c0, c1], [P_END, ]]
                        return 0
            #scan cols
            for c0 in range(9):
                n0 = 0
                for r0 in range(9):
                    if Grid[r0][c0]: continue
                    if Cands[r0][c0][d0] != Cands[r0][c0][d1]: break
                    if Cands[r0][c0][d0] and Cands[r0][c0][d1]:
                        if n0 > 1: break
                        p[n0] = r0; n0 += 1
                else:
                    if n0 != 2: continue
                    # hidden pair found along c0
                    r0 = p[0]; r1 = p[1]
                    for d2 in range(9):
                        if d2 == d0 or d2 == d1: continue
                        if Cands[r0][c0][d2]:
                            Cands[r0][c0][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                        if Cands[r1][c0][d2]:
                            Cands[r1][c0][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r1], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END, ])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, d0+1, d1+1], [P_OP, OP_CNT, 2], [P_ROW, r0, r1], [P_COL, c0], [P_END, ]]
                        return 0
            #scan blocks
            for h0 in range(9):
                br = (h0//3)*3; bc = (h0%3)*3
                n0 = 0
                for b0 in range(9):
                    r0 = br+(b0//3); c0 = bc+(b0%3)
                    if Grid[r0][c0]: continue
                    if Cands[r0][c0][d0] != Cands[r0][c0][d1]: break
                    if Cands[r0][c0][d0] and Cands[r0][c0][d1]:
                        if n0 > 1: break
                        p[n0] = b0; n0 += 1
                else:
                    if n0 != 2: continue
                    r0 = br+(p[0]//3); c0 = bc+(p[0]%3)
                    r1 = br+(p[1]//3); c1 = bc+(p[1]%3)
                    # A hidden pair in the block has been found
                    for d2 in range(9):
                        if d2 == d0 or d2 == d1: continue
                        if Cands[r0][c0][d2]:
                            Cands[r0][c0][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                        if Cands[r1][c1][d2]:
                            Cands[r1][c1][d2] = False
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r1], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, d2+1]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END, ])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, d0+1, d1+1], [P_OP, OP_CNT, 2], [P_BOX, h0], [P_CON, ], [P_ROW, r0], [P_COL, c0], [P_CON, ], [P_ROW, r1], [P_COL, c1], [P_END, ]]
                        return 0
    return -1

cdef int tech_exposed_triples_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # In any group (row, col or box) if any three empty cells have any
    # combination of only the same 3 candidates, then we have found an exposed
    # triple, and these three candidates can be eliminated from other cells.
    # Furthermore, if these three candidates are in the intersection of a box
    # and a row/col, this is a locked exposed triple and the candidates can be
    # eliminated from the other cells in that box too.
    cdef int r0, c0, b0, r1, c1, b1, r2, c2, b2, r3, c3, b3
    cdef int d, i, n, br, bc, or1, or2
    cdef int p0[3]
    cdef int p1[3]
    cdef int p2[3]
    cdef int u[3]

    # TRCX(f"Cands: {trc_cands(Cands)}")
    # Scan the rows first
    for r0 in range(9):
        for c0 in range(7):
            if Grid[r0][c0]: continue
            n = 0; p0[2] = -1
            for d in range(9):
                if Cands[r0][c0][d]:
                    if n >= 3: break
                    p0[n] = d; n += 1
            else:
                if not (2 <= n <= 3): continue
                # Found first cell with between 2 and 3 cands.
                # TRCX(f"Found 1 of 3: {p0[0]+1}{p0[1]+1}{p0[2]+1}r{r0+1}c{c0+1}")
                for c1 in range(c0+1, 8):
                    if Grid[r0][c1]: continue
                    n = 0; p1[2] = -1
                    for d in range(9):
                        if Cands[r0][c1][d]:
                            if n >= 3: break
                            p1[n] = d; n += 1
                    else:
                        if not (2 <= n <= 3): continue
                        # found second cell with between 2 and 3 cands.
                        # TRCX(f"Possible 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r0+1}c{c1+1}")
                        i = 0
                        for d in range(9):
                            if Cands[r0][c0][d] or Cands[r0][c1][d]: i += 1
                            if i > 3: break
                        if i > 3: continue
                        # first two cells can potentially be part of an exposed trip, look for the third cell
                        # TRCX(f"Found 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r0+1}c{c1+1}")
                        for c2 in range(c1+1, 9):
                            if Grid[r0][c2]: continue
                            n = 0; p2[2] = -1
                            for d in range(9):
                                if Cands[r0][c2][d]:
                                    if n >= 3: break
                                    p2[n] = d; n += 1
                            else:
                                if not (2 <= n <= 3): continue
                                # found third cell with between 2 and 3 cands
                                # TRCX(f"Possible 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r0+1}c{c2+1}")
                                i = 0
                                for d in range(9):
                                    if Cands[r0][c0][d] or Cands[r0][c1][d] or Cands[r0][c2][d]:
                                        if i >= 3: break
                                        u[i] = d; i += 1
                                else:
                                    if i != 3: continue
                                    # found an exposed triple, could it be a locked triple.
                                    # TRCX(f"Found 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r0+1}c{c2+1}")
                                    if T_LOCKED_EXPOSED_TRIPLE in Methods:
                                        bc = c0//3
                                        if bc == c1//3 == c2//3:
                                            # yes it is locked
                                            br = (r0//3)*3; bc *= 3
                                            or1 = br+(r0+1)%3; or2 = br+(r0+2)%3
                                            if or1 > or2: t = or1; or1 = or2; or2 = t
                                            for c3 in range(bc, bc+3):
                                                for i in range(3):
                                                    if Cands[or1][c3][u[i]]:
                                                        Cands[or1][c3][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, or1], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                                    if Cands[or2][c3][u[i]]:
                                                        Cands[or2][c3][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, or2], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                    if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_TRIPLE
                                    # else: Step.Method = T_EXPOSED_TRIPLE
                                    # What can be eliminated from the row?
                                    for c3 in range(9):
                                        if c3 == c0 or c3 == c1 or c3 == c2: continue
                                        for i in range(3):
                                            if Cands[r0][c3][u[i]]:
                                                Cands[r0][c3][u[i]] = False
                                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                    if Step.Outcome:  # cands are eliminated
                                        if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_TRIPLE
                                        Step.Outcome.append([P_END, ])
                                        P0 = []; P1 = []; P2 = []  # Python lists.
                                        for i in range(3):
                                            if p0[i] != -1: P0.append(p0[i]+1)
                                            if p1[i] != -1: P1.append(p1[i]+1)
                                            if p2[i] != -1: P2.append(p2[i]+1)
                                        Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                        [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c1], [P_CON, ],
                                                        [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c2], [P_END, ]]
                                        return 0
    # # then scan the cols
    for c0 in range(9):
        for r0 in range(7):
            if Grid[r0][c0]: continue
            n = 0; p0[2] = -1
            for d in range(9):
                if Cands[r0][c0][d]:
                    if n >= 3: break
                    p0[n] = d; n += 1
            else:
                if not (2 <= n <= 3): continue
                # found first cell with between 2 and 3 cands
                # TRCX(f"Found 1 of 3: {p0[0]+1}{p0[1]+1}{p0[2]+1}r{r0+1}c{c0+1}")
                for r1 in range(r0+1, 8):
                    if Grid[r1][c0]: continue
                    n = 0; p1[2] = -1
                    for d in range(9):
                        if Cands[r1][c0][d]:
                            if n >= 3: break
                            p1[n] = d; n += 1
                    else:
                        if not (2 <= n <= 3): continue
                        # found a second cell with between 2 and 3 cands
                        # TRCX(f"Possible 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r1+1}c{c0+1}")
                        i = 0
                        for d in range(9):
                            if Cands[r0][c0][d] or Cands[r1][c0][d]: i += 1
                            if i > 3: break
                        if i > 3: continue
                        # second cell has potential to form an exposed triple, look for third cell
                        # TRCX(f"Found 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r1+1}c{c0+1}")
                        for r2 in range(r1+1, 9):
                            if Grid[r2][c0]: continue
                            n = 0; p2[2] = -1
                            for d in range(9):
                                if Cands[r2][c0][d]:
                                    if n >= 3: break
                                    p2[n] = d; n += 1
                            else:
                                if not (2 <= n <= 3): continue
                                # found a third cell with between 2 and 3 cands.
                                # TRCX(f"Possible 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r2+1}c{c0+1}")
                                i = 0
                                for d in range(9):
                                    if Cands[r0][c0][d] or Cands[r1][c0][d] or Cands[r2][c0][d]:
                                        if i >= 3: break
                                        u[i] = d; i += 1
                                else:
                                    if i != 3: continue
                                    # found an exposed triple is it locked?
                                    # TRCX(f"Found 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r2+1}c{c0+1}")
                                    if T_LOCKED_EXPOSED_TRIPLE in Methods:
                                        br = r0//3
                                        if br == r1//3 == r2//3:
                                            # yes it is locked
                                            bc = (c0//3)*3; br *= 3
                                            oc1 = bc+(c0+1)%3; oc2 = bc+(c0+2)%3
                                            if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                                            for r3 in range(br, br+3):
                                                for i in range(3):
                                                    if Cands[r3][oc1][u[i]]:
                                                        Cands[r3][oc1][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, r3], [P_COL, oc1], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                                    if Cands[r3][oc2][u[i]]:
                                                        Cands[r3][oc2][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, r3], [P_COL, oc2], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                    if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_TRIPLE
                                    # else: Step.Method = T_EXPOSED_TRIPLE
                                    # What can be eliminated from the column
                                    for r3 in range(9):
                                        if r3 == r0 or r3 == r1 or r3 == r2: continue
                                        for i in range(3):
                                            if Cands[r3][c0][u[i]]:
                                                Cands[r3][c0][u[i]] = False
                                                if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                Step.Outcome.extend([[P_ROW, r3], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                    if Step.Outcome:
                                        if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_TRIPLE
                                        Step.Outcome.append([P_END, ])
                                        P0 = []; P1 = []; P2 = []  # Python lists
                                        for i in range(3):
                                            if p0[i] != -1: P0.append(p0[i]+1)
                                            if p1[i] != -1: P1.append(p1[i]+1)
                                            if p2[i] != -1: P2.append(p2[i]+1)
                                        Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                        [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c0], [P_CON, ],
                                                        [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c0], [P_END, ]]
                                        return 0
    # the scan the blocks.
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for b0 in range(7):
                r0 = br+(b0//3); c0 = bc+(b0%3)
                if Grid[r0][c0]: continue
                n = 0; p0[2] = -1
                for d in range(9):
                    if Cands[r0][c0][d]:
                        if n >= 3: break
                        p0[n] = d; n += 1
                else:
                    if not (2 <= n <= 3): continue
                    # found first cell with between 2 and 3 cands
                    # TRCX(f"Found 1 of 3: {p0[0]+1}{p0[1]+1}{p0[2]+1}r{r0+1}c{c0+1}")
                    for b1 in range(b0+1, 8):
                        r1 = br+(b1//3); c1 = bc+(b1%3)
                        if Grid[r1][c1]: continue
                        n = 0; p1[2] = -1
                        for d in range(9):
                            if Cands[r1][c1][d]:
                                if n >= 3: break
                                p1[n] = d; n += 1
                        else:
                            if not (2 <= n <= 3): continue
                            # found a second cell with between 2 and 3 candidates
                            # TRCX(f"Possible 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r1+1}c{c1+1}")
                            i = 0
                            for d in range(9):
                                if Cands[r0][c0][d] or Cands[r1][c1][d]: i += 1
                                if i > 3: break
                            if i > 3: continue
                            # second cell has potential to form an exposed triple, look for third cell
                            # TRCX(f"Found 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r1+1}c{c1+1}")
                            for b2 in range(b1+1, 9):
                                r2 = br+(b2//3); c2 = bc+(b2%3)
                                if Grid[r2][c2]: continue
                                n = 0; p2[2] = -1
                                for d in range(9):
                                    if Cands[r2][c2][d]:
                                        if n >= 3: break
                                        p2[n] = d; n += 1
                                else:
                                    if not (2 <= n <= 3): continue
                                    # found third cell with between 2 and 3 candidates
                                    # TRCX(f"Possible 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r2+1}c{c2+1}")
                                    i = 0
                                    for d in range(9):
                                        if Cands[r0][c0][d] or Cands[r1][c1][d] or Cands[r2][c2][d]:
                                            if i >= 3: break
                                            u[i] = d; i += 1
                                    else:
                                        if i != 3: continue
                                        # found a triple, what can be eliminated
                                        # TRCX(f"Found 3 of 3: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r2+1}c{c2+1}")
                                        for b3 in range(9):
                                            if b3 == b0 or b3 == b1 or b3 == b2: continue
                                            r3 = br+(b3//3); c3 = bc+(b3%3)
                                            for i in range(3):
                                                if Cands[r3][c3][u[i]]:
                                                    Cands[r3][c3][u[i]] = False
                                                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                    Step.Outcome.extend([[P_ROW, r3], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                    if Step.Outcome:
                                        Step.Outcome.append([P_END, ])
                                        Step.Method = T_EXPOSED_TRIPLE
                                        P0 = []; P1 = []; P2 = []  # Python lists
                                        for i in range(3):
                                            if p0[i] != -1: P0.append(p0[i]+1)
                                            if p1[i] != -1: P1.append(p1[i]+1)
                                            if p2[i] != -1: P2.append(p2[i]+1)
                                        Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                        [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                                        [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c2], [P_END, ]]
                                        return 0
    return -1

cdef int tech_hidden_triples_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # A hidden triple is where the union of three cells in a group contains the
    # same three candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those three cells that are not the
    # same three candidates, thereby exposing the hidden triple.
    cdef int r0, c0, b0, d0, d1, d2, d3
    cdef int br, bc, n0, i
    cdef int p[3]
    cdef int r[3]
    cdef int c[3]
    cdef int u0, u1, u2

    for d0 in range(7):
        for d1 in range(d0+1, 8):
            for d2 in range(d1+1, 9):
                # Scan rows
                for r0 in range(9):
                    # TRCX(f"Scanning row: {r0+1}")
                    n0 = u0 = u1 = u2 = 0
                    for c0 in range(9):
                        if Grid[r0][c0]: continue
                        # TRCX(f"{d0+1}{d1+1}{d2+1} in r{r0+1}c{c0+1}")
                        i = 0
                        if Cands[r0][c0][d0]:
                            i += 1; u0 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u0 > 3: break
                        if Cands[r0][c0][d1]:
                            i += 1; u1 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u1 > 3: break
                        if Cands[r0][c0][d2]:
                            i += 1; u2 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u2 > 3: break
                        if not i: continue
                        if i == 1: break
                        if n0 >= 3: break
                        p[n0] = c0; n0 += 1
                    else:
                        if n0 == 3 and u0 and u1 and u2:
                            # hidden trip found along r0
                            for d3 in range(9):
                                if d3 == d0 or d3 == d1 or d3 == d2: continue
                                for i in range(3):
                                    if Cands[r0][p[i]][d3]:
                                        Cands[r0][p[i]][d3] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, p[i]], [P_OP, OP_ELIM], [P_VAL, d3+1]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END, ])
                                Step.Method = T_HIDDEN_TRIPLE
                                V = [[], [], []]
                                for i in range(3):
                                    if Cands[r0][p[i]][d0]: V[i].append(d0+1)
                                    if Cands[r0][p[i]][d1]: V[i].append(d1+1)
                                    if Cands[r0][p[i]][d2]: V[i].append(d2+1)
                                Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[0]], [P_CON, ],
                                                [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[1]], [P_CON, ],
                                                [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[2]], [P_END, ]]
                                return 0
                # Scan cols
                for c0 in range(9):
                    # TRCX(f"Scanning col: {c0+1}")
                    n0 = u0 = u1 = u2 = 0
                    for r0 in range(9):
                        if Grid[r0][c0]: continue
                        # TRCX(f"{d0+1}{d1+1}{d2+1} in r{r0+1}c{c0+1}")
                        i = 0
                        if Cands[r0][c0][d0]:
                            i += 1; u0 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u0 > 3: break
                        if Cands[r0][c0][d1]:
                            i += 1; u1 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u1 > 3: break
                        if Cands[r0][c0][d2]:
                            i += 1; u2 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u2 > 3: break
                        if not i: continue
                        if i == 1: break
                        if n0 >= 3: break
                        p[n0] = r0; n0 += 1
                    else:
                        if n0 == 3 and u0 and u1 and u2:
                            # hidden trip found along c0
                            for d3 in range(9):
                                if d3 == d0 or d3 == d1 or d3 == d2: continue
                                for i in range(3):
                                    if Cands[p[i]][c0][d3]:
                                        Cands[p[i]][c0][d3] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, p[i]], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d3+1]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END, ])
                                Step.Method = T_HIDDEN_TRIPLE
                                V = [[], [], []]
                                for i in range(3):
                                    if Cands[p[i]][c0][d0]: V[i].append(d0+1)
                                    if Cands[p[i]][c0][d1]: V[i].append(d1+1)
                                    if Cands[p[i]][c0][d2]: V[i].append(d2+1)
                                Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, p[0]], [P_COL, c0], [P_CON, ],
                                                [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, p[1]], [P_COL, c0], [P_CON, ],
                                                [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, p[2]], [P_COL, c0], [P_END, ]]
                                return 0
                for h0 in range(9):
                    br = (h0//3)*3; bc = (h0%3)*3
                    n0 = u0 = u1 = u2 = 0
                    for b0 in range(9):
                        r0 = br+(b0//3); c0 = bc+(b0%3)
                        # TRCX(f"Scanning box: {b0}")
                        if Grid[r0][c0]: continue
                        # TRCX(f"{d0+1}{d1+1}{d2+1} in r{r0+1}c{c0+1}")
                        i = 0
                        if Cands[r0][c0][d0]:
                            i += 1; u0 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u0 > 3: break
                        if Cands[r0][c0][d1]:
                            i += 1; u1 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u1 > 3: break
                        if Cands[r0][c0][d2]:
                            i += 1; u2 += 1
                            # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2}, i: {i}")
                            if u2 > 3: break
                        if not i: continue
                        if i == 1: break
                        if n0 >= 3: break
                        p[n0] = b0; n0 += 1
                    else:
                        if n0 == 3 and u0 and u1 and u2:
                            # hidden trip found in box h0
                            for i in range(3):
                                r[i] = br + (p[i]//3); c[i] = bc + (p[i]%3)
                            for d3 in range(9):
                                if d3 == d0 or d3 == d1 or d3 == d2: continue
                                for i in range(3):
                                    if Cands[r[i]][c[i]][d3]:
                                        Cands[r[i]][c[i]][d3] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r[i]], [P_COL, c[i]], [P_OP, OP_ELIM], [P_VAL, d3+1]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END, ])
                                Step.Method = T_HIDDEN_TRIPLE
                                V = [[], [], []]
                                for i in range(3):
                                    if Cands[r[i]][c[i]][d0]: V[i].append(d0+1)
                                    if Cands[r[i]][c[i]][d1]: V[i].append(d1+1)
                                    if Cands[r[i]][c[i]][d2]: V[i].append(d2+1)
                                Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, r[0]], [P_COL, c[0]], [P_CON, ],
                                                [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, r[1]], [P_COL, c[1]], [P_CON, ],
                                                [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, r[2]], [P_COL, c[2]], [P_END, ]]
                                return 0
    return -1

cdef int tech_exposed_quads_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # In any group (row, col or box) if any four empty cells have any
    # combination of only the same 4 candidates, then we have found an exposed
    # quad, and these four candidates can be eliminated from other cells in that
    # group.  It is not possible to have a locked exposed quad as four cells
    # is too large to fit in a col or row span.

    cdef int r0, c0, b0, r1, c1, b1, r2, c2, b2, r3, c3, b3, r4, c4, b4
    cdef int d, i, n, br, bc
    cdef int p0[4]
    cdef int p1[4]
    cdef int p2[4]
    cdef int p3[4]
    cdef int u[4]

    # Scan the rows first
    for r0 in range(9):
        for c0 in range(6):
            if Grid[r0][c0]: continue
            n = 0; p0[2] = p0[3] = -1
            for d in range(9):
                if Cands[r0][c0][d]:
                    if n >= 4: break
                    p0[n] = d; n += 1
            else:
                if not (2 <= n <= 4): continue
                # Found first cell with between 2 and 4 cands.
                # TRCX(f"Found 1 of 4: {p0[0]+1}{p0[1]+1}{p0[2]+1}r{r0+1}c{c0+1}")
                for c1 in range(c0+1, 7):
                    if Grid[r0][c1]: continue
                    n = 0; p1[2] = p1[3] = -1
                    for d in range(9):
                        if Cands[r0][c1][d]:
                            if n >= 4: break
                            p1[n] = d; n += 1
                    else:
                        if not (2 <= n <= 4): continue
                        # found second cell with between 2 and 4 cands.
                        # TRCX(f"Possible 2 of 4: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r0+1}c{c1+1}")
                        i = 0
                        for d in range(9):
                            if Cands[r0][c0][d] or Cands[r0][c1][d]: i += 1
                            if i > 4: break
                        if i > 4: continue
                        # first two cells can potentially be part of an exposed quad, look for the third cell
                        # TRCX(f"Found 2 of 3: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r0+1}c{c1+1}")
                        for c2 in range(c1+1, 8):
                            if Grid[r0][c2]: continue
                            n = 0; p2[2] = p2[3] = -1
                            for d in range(9):
                                if Cands[r0][c2][d]:
                                    if n >= 4: break
                                    p2[n] = d; n += 1
                            else:
                                if not (2 <= n <= 4): continue
                                # found third cell with between 2 and 4 cands
                                # TRCX(f"Possible 3 of 4: {p2[0]+1}{p2[1]+1}{p2[2]+1}r{r0+1}c{c2+1}")
                                i = 0
                                for d in range(9):
                                    if Cands[r0][c0][d] or Cands[r0][c1][d] or Cands[r0][c2][d]: i += 1
                                    if i >= 4: break
                                if i > 4: continue
                                # first three cells can potentially be part of an exposed quad, look for the fourth cell
                                for c3 in range(c2+1, 9):
                                    if Grid[r0][c3]: continue
                                    n = 0; p3[2] = p3[3] = -1
                                    for d in range(9):
                                        if Cands[r0][c3][d]:
                                            if n >= 4: break
                                            p3[n] = d; n += 1
                                    else:
                                        if not (2 <= n <= 4): continue
                                        # found a fourth cell with between 2 and 4 cands
                                        i = 0
                                        for d in range(9):
                                            if Cands[r0][c0][d] or Cands[r0][c1][d] or Cands[r0][c2][d] or Cands[r0][c3][d]:
                                                if i >= 4: break
                                                u[i] = d; i += 1
                                        else:
                                            if i != 4: continue
                                            # found an exposed quad, what can be eliminated?
                                            for c4 in range(9):
                                                if c4 == c0 or c4 == c1 or c4 == c2 or c4 == c3: continue
                                                for i in range(4):
                                                    if Cands[r0][c4][u[i]]:
                                                        Cands[r0][c4][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, c4], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                            if Step.Outcome:  # cands are eliminated
                                                Step.Outcome.append([P_END, ])
                                                Step.Method = T_EXPOSED_QUAD
                                                P0 = []; P1 = []; P2 = []; P3 = []  # Python lists.
                                                for i in range(4):
                                                    if p0[i] != -1: P0.append(p0[i]+1)
                                                    if p1[i] != -1: P1.append(p1[i]+1)
                                                    if p2[i] != -1: P2.append(p2[i]+1)
                                                    if p3[i] != -1: P3.append(p3[i]+1)
                                                Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                                [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c1], [P_CON, ],
                                                                [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c2], [P_CON, ],
                                                                [P_VAL, P3], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c3], [P_END, ]]
                                                return 0
    # then scan the cols
    for c0 in range(9):
        for r0 in range(6):
            if Grid[r0][c0]: continue
            n = 0; p0[2] = p0[3] = -1
            for d in range(9):
                if Cands[r0][c0][d]:
                    if n >= 4: break
                    p0[n] = d; n += 1
            else:
                if not (2 <= n <= 4): continue
                # found first cell with between 2 and 4 cands
                # TRCX(f"Found 1 of 4: {p0[0]+1}{p0[1]+1}{p0[2]+1}{p0[3]+1}r{r0+1}c{c0+1}")
                for r1 in range(r0+1, 7):
                    if Grid[r1][c0]: continue
                    n = 0; p1[2] = p1[3] = -1
                    for d in range(9):
                        if Cands[r1][c0][d]:
                            if n >= 4: break
                            p1[n] = d; n += 1
                    else:
                        if not (2 <= n <= 4): continue
                        # found a second cell with between 2 and 3 cands
                        # TRCX(f"Possible 2 of 4: {p1[0]+1}{p1[1]+1}{p1[2]+1}{p1[3]+1}r{r1+1}c{c0+1}")
                        i = 0
                        for d in range(9):
                            if Cands[r0][c0][d] or Cands[r1][c0][d]: i += 1
                            if i > 4: break
                        if i > 4: continue
                        # second cell has potential to form an exposed quad look for third cell
                        # TRCX(f"Found 2 of 4: {p1[0]+1}{p1[1]+1}{p1[2]+1}r{r1+1}c{c0+1}")
                        for r2 in range(r1+1, 8):
                            if Grid[r2][c0]: continue
                            n = 0; p2[2] = p2[3] = -1
                            for d in range(9):
                                if Cands[r2][c0][d]:
                                    if n >= 4: break
                                    p2[n] = d; n += 1
                            else:
                                if not (2 <= n <= 4): continue
                                # found a third cell with between 2 and 4 cands.
                                # TRCX(f"Possible 3 of 4: {p2[0]+1}{p2[1]+1}{p2[2]+1}{p2[3]+1}r{r2+1}c{c0+1}")
                                i = 0
                                for d in range(9):
                                    if Cands[r0][c0][d] or Cands[r1][c0][d] or Cands[r2][c0][d]: i += 1
                                    if i >= 4: break
                                if i < 4: continue
                                # these three cells have the potential to be part of the exposed quad, look for the fourth cell
                                # TRCX(f"Found 3 of 4: {p2[0]+1}{p2[1]+1}{p2[2]+1}{p2[3]+1}r{r1+1}c{c0+1}")
                                for r3 in range(r2+1, 9):
                                    if Grid[r3][c0]: continue
                                    n = 0; p3[2] = p3[3] = -1
                                    for d in range(9):
                                        if Cands[r3][c0][d]:
                                            if n >= 4: break
                                            p3[n] = d; n += 1
                                    else:
                                        if not (2 <= n <= 4): continue
                                        # found a fourth cell between 2 and 4 cands
                                        # TRCX(f"Possible 4 of 4: {p3[0]+1}{p3[1]+1}{p3[2]+1}{p3[3]+1}r{r3+1}c{c0+1}")
                                        i = 0
                                        for d in range(9):
                                            if Cands[r0][c0][d] or Cands[r1][c0][d] or Cands[r2][c0][d] or Cands[r3][c0][d]:
                                                if i >= 4: break
                                                u[i] = d; i += 1
                                        else:
                                            if i != 4: continue
                                            # found an exposed quad, what can be eliminated?
                                            # TRCX(f"Found 4 of 4: {p3[0]+1}{p3[1]+1}{p3[2]+1}{p3[3]+1}r{r3+1}c{c0+1}")
                                            for r4 in range(9):
                                                if r4 == r0 or r4 == r1 or r4 == r2 or r4 == r3: continue
                                                for i in range(4):
                                                    if Cands[r4][c0][u[i]]:
                                                        Cands[r4][c0][u[i]] = False
                                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                        Step.Outcome.extend([[P_ROW, r4], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                            if Step.Outcome:
                                                Step.Outcome.append([P_END, ])
                                                Step.Method = T_EXPOSED_QUAD
                                                P0 = []; P1 = []; P2 = []; P3 = []  # Python lists
                                                for i in range(4):
                                                    if p0[i] != -1: P0.append(p0[i]+1)
                                                    if p1[i] != -1: P1.append(p1[i]+1)
                                                    if p2[i] != -1: P2.append(p2[i]+1)
                                                    if p3[i] != -1: P3.append(p3[i]+1)
                                                Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                                [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c0], [P_CON, ],
                                                                [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c0], [P_CON, ],
                                                                [P_VAL, P3], [P_OP, OP_EQ], [P_ROW, r3], [P_COL, c0], [P_END, ]]
                                                return 0
    # the scan the blocks.
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for b0 in range(6):
                r0 = br+(b0//3); c0 = bc+(b0%3)
                if Grid[r0][c0]: continue
                n = 0; p0[2] =p0[3] = -1
                for d in range(9):
                    if Cands[r0][c0][d]:
                        if n >= 4: break
                        p0[n] = d; n += 1
                else:
                    if not (2 <= n <= 4): continue
                    # found first cell with between 2 and 4 cands
                    # TRCX(f"Found 1 of 4: {p0[0]+1}{p0[1]+1}{p0[2]+1}{p0[3]+1}r{r0+1}c{c0+1}")
                    for b1 in range(b0+1, 7):
                        r1 = br+(b1//3); c1 = bc+(b1%3)
                        if Grid[r1][c1]: continue
                        n = 0; p1[2] = p1[3] = -1
                        for d in range(9):
                            if Cands[r1][c1][d]:
                                if n >= 4: break
                                p1[n] = d; n += 1
                        else:
                            if not (2 <= n <= 4): continue
                            # found a second cell with between 2 and 4 candidates
                            # TRCX(f"Possible 2 of 4: {p1[0]+1}{p1[1]+1}{p1[2]+1}{p1[3]+1}r{r1+1}c{c1+1}")
                            i = 0
                            for d in range(9):
                                if Cands[r0][c0][d] or Cands[r1][c1][d]: i += 1
                                if i > 4: break
                            if i > 4: continue
                            # second cell has potential to form an exposed quad, look for third cell
                            # TRCX(f"Found 2 of 4: {p1[0]+1}{p1[1]+1}{p1[2]+1}{p1[3]+1}r{r1+1}c{c1+1}")
                            for b2 in range(b1+1, 8):
                                r2 = br+(b2//3); c2 = bc+(b2%3)
                                if Grid[r2][c2]: continue
                                n = 0; p2[2] = p2[3] = -1
                                for d in range(9):
                                    if Cands[r2][c2][d]:
                                        if n >= 4: break
                                        p2[n] = d; n += 1
                                else:
                                    if not (2 <= n <= 4): continue
                                    # found third cell with between 2 and 3 candidates
                                    # TRCX(f"Possible 3 of 4: {p2[0]+1}{p2[1]+1}{p2[2]+1}{p2[3]+1}r{r2+1}c{c2+1}")
                                    i = 0
                                    for d in range(9):
                                        if Cands[r0][c0][d] or Cands[r1][c1][d] or Cands[r2][c2][d]: i += 1
                                        if i >= 4: break
                                    if i > 4: continue
                                    # first three cells have the potential to form an exposed quad, look for fourth cell
                                    # TRCX(f"Found 3 of 4: {p2[0]+1}{p2[1]+1}{p2[2]+1}{p2[3]+1}r{r2+1}c{c2+1}")
                                    for b3 in range(b2+1, 9):
                                        r3 = br+(b3//3); c3 = bc+(b3%3)
                                        if Grid[r3][c3]: continue
                                        n = 0; p3[2] = p3[3] = -1
                                        for d in range(9):
                                            if Cands[r3][c3][d]:
                                                if n >= 4: break
                                                p3[n] = d; n += 1
                                        else:
                                            if not (2 <= n <= 4): continue
                                            # found a fourth cell with between 2 and 4 candidates
                                            # TRCX(f"Possible 4 of 4: {p3[0]+1}{p3[1]+1}{p3[2]+1}{p3[3]+1}r{r2+1}c{c2+1}")
                                            i = 0
                                            for d in range(9):
                                                if Cands[r0][c0][d] or Cands[r1][c1][d] or Cands[r2][c2][d] or Cands[r3][c3][d]:
                                                    if i >= 4: break
                                                    u[i] = d; i += 1
                                            else:
                                                if i != 4: continue
                                                # found an exposed quad in a box
                                                # TRCX(f"Found 4 of 4: {p3[0]+1}{p3[1]+1}{p3[2]+1}{p3[3]+1}r{r2+1}c{c2+1}")
                                                for b4 in range(9):
                                                    if b4 == b0 or b4 == b1 or b4 == b2 or b4 == b3: continue
                                                    r4 = br+(b4//3); c4 = bc+(b4%3)
                                                    for i in range(4):
                                                        if Cands[r4][c4][u[i]]:
                                                            Cands[r4][c4][u[i]] = False
                                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                                            Step.Outcome.extend([[P_ROW, r4], [P_COL, c4], [P_OP, OP_ELIM], [P_VAL, u[i]+1]])
                                            if Step.Outcome:
                                                Step.Outcome.append([P_END, ])
                                                Step.Method = T_EXPOSED_QUAD
                                                P0 = []; P1 = []; P2 = []; P3 = [] # Python lists
                                                for i in range(4):
                                                    if p0[i] != -1: P0.append(p0[i]+1)
                                                    if p1[i] != -1: P1.append(p1[i]+1)
                                                    if p2[i] != -1: P2.append(p2[i]+1)
                                                    if p3[i] != -1: P3.append(p3[i]+1)
                                                Step.Pattern = [[P_VAL, P0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0], [P_CON, ],
                                                                [P_VAL, P1], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                                                [P_VAL, P2], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c2], [P_CON, ],
                                                                [P_VAL, P3], [P_OP, OP_EQ], [P_ROW, r3], [P_COL, c3], [P_END, ]]
                                                return 0
    return -1

cdef int tech_hidden_quads_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # A hidden quad is where the union of four cells in a group contains the
    # same four candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those four cells that are not the
    # same four candidates, thereby exposing the hidden quad.
    cdef int r0, c0, b0, d0, d1, d2, d3, d4
    cdef int br, bc, n0, i
    cdef int p[4]
    cdef int r[4]
    cdef int c[4]
    cdef int u0, u1, u2, u3

    for d0 in range(6):
        for d1 in range(d0+1, 7):
            for d2 in range(d1+1, 8):
                for d3 in range(d2+1, 9):
                    # Scan rows
                    for r0 in range(9):
                        n0 = u0 = u1 = u2 = u3 = 0
                        for c0 in range(9):
                            if Grid[r0][c0]: continue
                            # TRCX(f"Cands: {d0+1}{d1+1}{d2+1}{d3+1}, r{r0+1}c{c0+1}")
                            i = 0
                            if Cands[r0][c0][d0]:
                                i += 1; u0 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u0 > 4: break
                            if Cands[r0][c0][d1]:
                                i += 1; u1 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u1 > 4: break
                            if Cands[r0][c0][d2]:
                                i += 1; u2 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u2 > 4: break
                            if Cands[r0][c0][d3]:
                                i += 1; u3 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d3+1}]: {Cands[r0][c0][d3]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u3 > 4: break
                            if not i: continue
                            if i == 1: break
                            if n0 >= 4: break
                            p[n0] = c0; n0 += 1
                        else:
                            if n0 == 4 and u0 and u1 and u2 and u3:
                                # hidden quad found along r0, are there any eliminations
                                for d4 in range(9):
                                    if d4 == d0 or d4 == d1 or d4 == d2 or d4 == d3: continue
                                    for i in range(4):
                                        if Cands[r0][p[i]][d4]:
                                            Cands[r0][p[i]][d4] = False
                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                            Step.Outcome.extend([[P_ROW, r0], [P_COL, p[i]], [P_OP, OP_ELIM], [P_VAL, d4+1]])
                                if Step.Outcome:
                                    Step.Outcome.append([P_END, ])
                                    Step.Method = T_HIDDEN_QUAD
                                    V = [[], [], [], []]
                                    for i in range(4):
                                        if Cands[r0][p[i]][d0]: V[i].append(d0+1)
                                        if Cands[r0][p[i]][d1]: V[i].append(d1+1)
                                        if Cands[r0][p[i]][d2]: V[i].append(d2+1)
                                        if Cands[r0][p[i]][d3]: V[i].append(d3+1)
                                    Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[0]], [P_CON, ],
                                                    [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[1]], [P_CON, ],
                                                    [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[2]], [P_CON, ],
                                                    [P_VAL, V[3]], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, p[3]], [P_END, ]]
                                    return 0
                    # Scan Cols
                    for c0 in range(9):
                        n0 = u0 = u1 = u2 = u3 = 0
                        for r0 in range(9):
                            if Grid[r0][c0]: continue
                            # TRCX(f"Cands: {d0+1}{d1+1}{d2+1}{d3+1}, r{r0+1}c{c0+1}")
                            i = 0
                            if Cands[r0][c0][d0]:
                                i += 1; u0 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u0 > 4: break
                            if Cands[r0][c0][d1]:
                                i += 1; u1 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u1 > 4: break
                            if Cands[r0][c0][d2]:
                                i += 1; u2 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u2 > 4: break
                            if Cands[r0][c0][d3]:
                                i += 1; u3 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d3+1}]: {Cands[r0][c0][d3]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u3 > 4: break
                            if not i: continue
                            if i == 1: break
                            if n0 >= 4: break
                            p[n0] = r0; n0 += 1
                        else:
                            if n0 == 4 and u0 and u1 and u2 and u3:
                                # hidden trip found along c0
                                for d4 in range(9):
                                    if d4 == d0 or d4 == d1 or d4 == d2 or d4 == d3: continue
                                    for i in range(4):
                                        if Cands[p[i]][c0][d4]:
                                            Cands[p[i]][c0][d4] = False
                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                            Step.Outcome.extend([[P_ROW, p[i]], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, d4+1]])
                                if Step.Outcome:
                                    Step.Outcome.append([P_END, ])
                                    Step.Method = T_HIDDEN_QUAD
                                    V = [[], [], [], []]
                                    for i in range(4):
                                        if Cands[p[i]][c0][d0]: V[i].append(d0+1)
                                        if Cands[p[i]][c0][d1]: V[i].append(d1+1)
                                        if Cands[p[i]][c0][d2]: V[i].append(d2+1)
                                        if Cands[p[i]][c0][d3]: V[i].append(d3+1)
                                    Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, p[0]], [P_COL, c0], [P_CON, ],
                                                    [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, p[1]], [P_COL, c0], [P_CON, ],
                                                    [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, p[2]], [P_COL, c0], [P_CON, ],
                                                    [P_VAL, V[3]], [P_OP, OP_EQ], [P_ROW, p[3]], [P_COL, c0], [P_END, ]]
                                    return 0
                    for h0 in range(9):
                        br = (h0//3)*3; bc = (h0%3)*3
                        n0 = u0 = u1 = u2 = u3 = 0
                        for b0 in range(9):
                            r0 = br+(b0//3); c0 = bc+(b0%3)
                            if Grid[r0][c0]: continue
                            # TRCX(f"Cands: {d0+1}{d1+1}{d2+1}{d3+1}, r{r0+1}c{c0+1}")
                            i = 0
                            if Cands[r0][c0][d0]:
                                i += 1; u0 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d0+1}]: {Cands[r0][c0][d0]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u0 > 4: break
                            if Cands[r0][c0][d1]:
                                i += 1; u1 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d1+1}]: {Cands[r0][c0][d1]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u1 > 4: break
                            if Cands[r0][c0][d2]:
                                i += 1; u2 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d2+1}]: {Cands[r0][c0][d2]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u2 > 4: break
                            if Cands[r0][c0][d3]:
                                i += 1; u3 += 1
                                # TRCX(f"Cands[{r0+1}][{c0+1}][{d3+1}]: {Cands[r0][c0][d3]}, n0: {n0}, u: {u0},{u1},{u2},{u3}, i: {i}")
                                if u3 > 4: break
                            if not i: continue
                            if i == 1: break
                            if n0 >= 4: break
                            p[n0] = b0; n0 += 1
                        else:
                            if n0 == 4 and u0 and u1 and u2 and u3:
                                # hidden quad found in box h0
                                # TRCX_cands(Cands)
                                # TRCX(f"Hidden Quad found in box: {h0+1}")
                                for i in range(4):
                                    r[i] = br+(p[i]//3); c[i] = bc+(p[i]%3)
                                    # TRCX(f"p[{i+1}]: {p[i]+1}, r[{i+1}]: {r[i]+1}, c[{i+1}]: {c[i]+1}")
                                for d4 in range(9):
                                    if d4 == d0 or d4 == d1 or d4 == d2 or d4 == d3: continue
                                    for i in range(4):
                                        if Cands[r[i]][c[i]][d4]:
                                            Cands[r[i]][c[i]][d4] = False
                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                            Step.Outcome.extend([[P_ROW, r[i]], [P_COL, c[i]], [P_OP, OP_ELIM], [P_VAL, d4+1]])
                                if Step.Outcome:
                                    Step.Outcome.append([P_END, ])
                                    Step.Method = T_HIDDEN_QUAD
                                    V = [[], [], [], []]
                                    for i in range(4):
                                        if Cands[r[i]][c[i]][d0]: V[i].append(d0+1)
                                        if Cands[r[i]][c[i]][d1]: V[i].append(d1+1)
                                        if Cands[r[i]][c[i]][d2]: V[i].append(d2+1)
                                        if Cands[r[i]][c[i]][d3]: V[i].append(d3+1)
                                    Step.Pattern = [[P_VAL, V[0]], [P_OP, OP_EQ], [P_ROW, r[0]], [P_COL, c[0]], [P_CON, ],
                                                    [P_VAL, V[1]], [P_OP, OP_EQ], [P_ROW, r[1]], [P_COL, c[1]], [P_CON, ],
                                                    [P_VAL, V[2]], [P_OP, OP_EQ], [P_ROW, r[2]], [P_COL, c[2]], [P_CON, ],
                                                    [P_VAL, V[3]], [P_OP, OP_EQ], [P_ROW, r[3]], [P_COL, c[3]], [P_END, ]]
                                    return 0
    return -1
