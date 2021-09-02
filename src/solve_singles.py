
from copy import copy

from globals import *
from solve_utils import *

def tech_exposed_singles(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):

    if Method != T_UNDEF and Method != T_EXPOSED_SINGLE: return -1

    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 1:
                # This is an exposed single no need to subtract anything.
                Step[P_TECH] = T_EXPOSED_SINGLE
                Grid[r][c]   = Cands[r][c].pop()
                Step[P_PTRN] = [[P_VAL, Grid[r][c]], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c],
                                [P_END, ]]
                Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                if ElimCands: ElimCands[r][c].clear()
                return 1
    return -1


def tech_hidden_singles(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # For each empty cell in the grid, subtracting all the candidates from its
    # group (either row, col, blk_peers will yield the single if one exists,
    # either hidden or exposed.

    #  Returns >1:  Technique found a step, a locked single found.
    #           0:  Technique found a step, only candidates eliminated.
    #          <0:  Technique did not find a step

    if Method != T_UNDEF and Method != T_HIDDEN_SINGLE: return -1

    for r in range(9):
        for c in range(9):
            # Scan the row first.
            D = Cands[r][c].copy()
            for c1 in set(range(9))-{c}:
                D -= Cands[r][c1]
            if len(D) == 1:  # Hidden single found in row.
                Step[P_TECH] = T_HIDDEN_SINGLE
                Grid[r][c]   = D.pop()
                Step[P_PTRN] = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_ROW, r],
                                [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                # if ElimCands is None:
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                if ElimCands: ElimCands[r][c].clear()
                return 1
            # Scan the col
            D = Cands[r][c].copy()
            for r1 in set(range(9))-{r}:
                D -= Cands[r1][c]
            if len(D) == 1:  # Hidden single found in col.
                Step[P_TECH] = T_HIDDEN_SINGLE
                Grid[r][c]   = D.pop()
                Step[P_PTRN] = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_COL, c],
                                [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                # if ElimCands is None:
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                if ElimCands: ElimCands[r][c].clear()
                return 1
            # scan the block.
            D = Cands[r][c].copy()
            br = (r//3)*3
            bc = (c//3)*3
            for r1 in range(br, br+3):
                for c1 in range(bc, bc+3):
                    if (r1 != r) or (c1 != c):
                        D -= Cands[r1][c1]
            if len(D) == 1:  # Hidden single found in blk.
                Step[P_TECH] = T_HIDDEN_SINGLE
                Grid[r][c]   = D.pop()
                Step[P_PTRN] = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_BOX, (br//3)*3+bc//3],
                                [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                # if ElimCands is None:
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                if ElimCands: ElimCands[r][c].clear()
                return 1
    return -1

def tech_locked_singles(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # For pointing in a block if a candidate value is confined to a row or col
    # then none of of the cells in that row or col outside the block can have
    # the candidate value.
    #
    # For claiming in a row or column if a candidate value is confined to a block
    # then none of the cells in the block can have the candidate value.

    #  Returns >1:  Technique found a step, returns number of values placed/ccells solved.
    #           0:  Technique found a step, only candidates eliminated.
    #          -1:  Technique did not find a step

    if Method != T_UNDEF and Method != T_POINTING_LOCKED_SINGLE and Method != T_CLAIMING_LOCKED_SINGLE: return -1

    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            br1 = br+1; br2 = br+2
            bc1 = bc+1; bc2 = bc+2
            # scan the rows in the block first:
            for r0, or1, or2 in zip([br, br1, br2], [br1, br2, br], [br2, br, br1]):
                for Cand in Cands[r0][bc] | Cands[r0][bc1] | Cands[r0][bc2]:
                    C1 = []
                    if Cand in Cands[r0][bc]:
                        C1.append(bc)
                    if Cand in Cands[r0][bc1]:
                        C1.append(bc1)
                    if Cand in Cands[r0][bc2]:
                        C1.append(bc2)
                    if len(C1) >= 2:
                        # possibility of locking, check pointing first
                        Rx = sorted((or1, or2))
                        C2 = sorted(set(range(9)) - {bc, bc1, bc2})
                        if Method == T_UNDEF or Method == T_POINTING_LOCKED_SINGLE:
                            if Cand not in (Cands[or1][bc] | Cands[or1][bc1] | Cands[or1][bc2]
                                        | Cands[or2][bc] | Cands[or2][bc1] | Cands[or2][bc2]):
                            # Candidate is locked to the row and can be discarded
                            # from balance of row.
                                for c in C2:  # set(range(9)) - {bc, bc1, bc2}:
                                    if Cand in Cands[r0][c]:
                                        Cands[r0][c].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands:
                                            ElimCands[r0][c].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_POINTING_LOCKED_SINGLE
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, Rx], [P_COL, bc, bc1, bc2],
                                                    [P_END, ]]
                                    return 0
                        # else check claiming
                        if Method == T_UNDEF or Method == T_CLAIMING_LOCKED_SINGLE:
                            U = set()
                            for c in C2:  # set(range(9))-{bc, bc1, bc2}:
                                U |= Cands[r0][c]
                            if Cand not in U:
                                # Candidate is locked to the row, Candidate vals in the rest
                                # of the block can be discarded
                                for c in [bc, bc1, bc2]:
                                    for x in Rx:  # or1, or2]:
                                        if Cand in Cands[x][c]:
                                            Cands[x][c].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append([P_SEP, ])
                                            Step[P_OUTC].extend([[P_ROW, x], [P_COL, c],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands:
                                                ElimCands[x][c].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_CLAIMING_LOCKED_SINGLE
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, r0], [P_COL, C2], [P_END, ]]
                                    return 0
            # then scan the columns
            for c0, oc1, oc2 in zip([bc, bc1, bc2], [bc1, bc2, bc], [bc2, bc, bc1]):
                for Cand in Cands[br][c0] | Cands[br1][c0] | Cands[br2][c0]:
                    R1 = []
                    if Cand in Cands[br][c0]:
                        R1.append(br)
                    if Cand in Cands[br1][c0]:
                        R1.append(br1)
                    if Cand in Cands[br2][c0]:
                        R1.append(br2)
                    if len(R1) >=2:
                        # possibility of locking, check for pointing first
                        Cx = sorted((oc1, oc2))
                        R2 = sorted(set(range(9)) - {br, br1, br2})
                        if Method == T_UNDEF or Method == T_POINTING_LOCKED_SINGLE:
                            if Cand not in (Cands[br][oc1] | Cands[br1][oc1] | Cands[br2][oc1]
                                            | Cands[br][oc2] | Cands[br1][oc2] | Cands[br2][oc2]):
                                # Candidate is locked to the col, and can be discarded
                                # from the balance of the col.
                                for r in R2:  # set(range(9)) - {br, br1, br2}:
                                    if Cand in Cands[r][c0]:
                                        Cands[r][c0].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r], [P_COL, c0],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands:
                                            ElimCands[r][c0].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_POINTING_LOCKED_SINGLE
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, br, br1, br2], [P_COL, Cx],
                                                    [P_END, ]]
                                    return 0
                        # else check claiming
                        if Method == T_UNDEF or Method == T_CLAIMING_LOCKED_SINGLE:
                            U = set()
                            for r in R2:  # set(range(9)) - {br, br1, br2}:
                                U |= Cands[r][c0]
                            if Cand not in U:
                                # Candidate is locked to the col, Candidate vals in the rest
                                # of the block can be discarded
                                for r in [br, br1, br2]:
                                    for x in Cx:
                                        if Cand in Cands[r][x]:
                                            Cands[r][x].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append([P_SEP, ])
                                            Step[P_OUTC].extend([[P_ROW, r], [P_COL, x],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands:
                                                ElimCands[r][x].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_CLAIMING_LOCKED_SINGLE
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, R2], [P_COL, c0], [P_END, ]]
                                    return 0
    return -1

def tech_empty_rects(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # Covers the occurrence of 3 to 5 occurrences of the same candidate value
    # in a box that only describe a row and column in that box.  Occurrences of
    # less than three same candidate values are simply potential X-Chains and
    # are handled by the x chain algorithms.

    # look for boxes that contain 3 to 5 same candidate value that describe only
    # a single row (r) and column (c).  Then scan the column and the row outside
    # the box to find other cells with same value candidates (Cr and Cc).  If
    # any cell (Cb) that both Cr and Cc see also has a same value candidate then
    # we have found an Empty Rectangle.  If there is a strong link between Cb
    # and Cc, then the candidate can be eliminated from Cr.  Similarly if there
    # is/was a strong link between Cb and Cr, then Cc too can be eliminated.
    #

    if Method != T_UNDEF and Method != T_EMPTY_RECT: return -1

    # Look for a box that only has cands that describe a single row and col in
    # that box.
    for rb in [0, 3, 6]:
        for cb in [0, 3, 6]:
            for Cand in range(1, 10):
                n = 0
                R = [0, 0, 0]
                C = [0, 0, 0]
                BC = []
                rb1 = rb+1; rb2 = rb+2
                cb1 = cb+1; cb2 = cb+2
                for r in [rb, rb1, rb2]:
                    for c in [cb, cb1, cb2]:
                        if Cand in Cands[r][c]:
                            n += 1
                            R[r-rb] += 1
                            C[c-cb] += 1
                            BC.append((r, c))
                Rs = sorted(R); Cs = sorted(C)
                if n == 3 and (Rs == [0, 1, 2] or Cs == [0, 1, 2]) \
                        or n == 4 and ((Rs == [0, 1, 3] and Cs == [1, 1, 2])
                                       or (Rs == [1, 1, 2] and Cs == [0, 1, 3])
                                       or (Rs == [1, 1, 2] and Cs == [1, 1, 2])) \
                        or n == 5 and (Rs == Cs == [1, 1, 3]):
                    # ER pattern in box found.
                    r1 = c1 = -1
                    for i in [0, 1, 2]:
                        if R[i] > 1: r1 = i + rb
                        if C[i] > 1: c1 = i + cb
                    # The case when n = 3, R/C = [0, 1, 2] and C/R [1, 1, 1]
                    # If r1 =-1 assign it to the cell without candidate in the
                    # column containing 2 candidates.  Similarly for c1 = 0.
                    if r1 == -1:
                        for r in [rb, rb1, rb2]:
                            if Cand not in Cands[r][c1]:
                                r1 = r
                                break
                    if c1 == -1:
                        for c in [cb, cb1, cb2]:
                            if Cand not in Cands[r1][c]:
                                c1 = c
                                break
                    # Found a candidate describing a single row r and col c
                    # in a box.
                    # Scan the row outside the box for another candidate.
                    for c2 in sorted(set(range(9)) - {cb, cb1, cb2}):
                        if Cand not in Cands[r1][c2]: continue
                        # And scan the col outside the box for another candidate
                        for r2 in sorted(set(range(9)) - {rb, rb1, rb2}):
                            if Cand not in Cands[r2][c1]: continue
                            # Getting close, is there a candidate in (r2, c2)
                            if Cand not in Cands[r2][c2]: continue
                            # empty rect found, what can be eliminated?
                            Elim = []
                            if ccells_are_linked(r1, c2, Cand, r2, c2, Cand, Cands) & LK_STRG:
                                Elim.append((r2, c1))
                            if ccells_are_linked(r2, c1, Cand, r2, c2, Cand, Cands) & LK_STRG:
                                Elim.append((r1, c2))
                            if len(Elim):
                                Step[P_TECH] = T_EMPTY_RECT
                                for r3, c3 in Elim:
                                    Cands[r3][c3].discard(Cand)
                                    if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                                    Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c3],
                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    if ElimCands: ElimCands[r3][c3].add(Cand)
                                Step[P_OUTC].append([P_END, ])
                                Step[P_PTRN] = [[P_VAL, Cand], [P_OP, OP_CNT, n], [P_BOX, (rb//3)*3+cb//3]]
                                for r3, c3 in BC:
                                    Step[P_PTRN].extend([[P_CON, ], [P_ROW, r3], [P_COL, c3]])
                                Step[P_PTRN].append([P_END, ])
                                return 0
    return -1

# TODO Add Almost Locked Candidates.  Perhaps not, have not seen any examples in my searches
# to validate.
