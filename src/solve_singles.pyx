
include "globals.pxi"
from ctypedefs cimport *
from globals import *

from trc cimport *
from trc import *

from solve_singles cimport *
from solve_utils cimport discard_cand_from_peers_c, cell_val_has_no_conflicts_c, how_ccells_linked_c
# Tech, discard_cand_from_peers, cell_val_has_no_conflicts, how_ccells_linked

DEF ROW = 0
DEF COL = 1
DEF POINTING = 0
DEF CLAIMING = 1


cdef extern from "stdlib.h" nogil:
    int rand()

cdef extern from "string.h" nogil:
    void * memcpy(void *, void *, size_t)
    void * memset(void *, int, size_t)

cdef int tech_exposed_singles_c(int Grid[9][9], Step, bint Cands[9][9][9], Method):
    cdef int r, c, d, v, NrCands

    for r in range(9):
        for c in range(9):
            if Grid[r][c]: continue
            NrCands = 0; v = -1
            for d in range(9):
                if Cands[r][c][d]: NrCands += 1; v = d+1
                if NrCands > 1: break
            else:
                Step.Method     = T_EXPOSED_SINGLE
                Grid[r][c]      = v
                discard_cand_from_peers_c(v, r, c, Cands)
                Step.Pattern    = [[P_VAL, v], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, v], [P_END, ]]
                return 1
    return -1


cdef int tech_hidden_singles_c(int Grid[9][9], Step, bint Cands[9][9][9], Method):
    # For each empty cell in the grid, subtracting all the candidates from its
    # group (either row, col, blk_peers will yield the single if one exists,
    # either hidden or exposed.

    # The search order for hidden singles differs from the interpreted implementation
    # here all rows are scanned before columns, before boxes for all candidate, seeking
    # a unique candidate.
    # In the interpreted code for each cell, it's row, column and box are scanned looking
    # for a unique candidate.

    cdef int r, c, d, b, br, bc, NrCand, r1, c1, b1

    for r in range(9):  # Scan each row
        for d in range(9):  # for each candidate
            NrCand = 0; c1 = -1
            for c in range(9):  # scan the cells in the row counting the cand value
                if Grid[r][c] == d+1: break
                if Grid[r][c]: continue
                # TRCX(f"Cands[{r}][{c}][{d}]: {Cands[r][c][d]}, NrCand: {NrCand}")
                if Cands[r][c][d]:
                    if NrCand > 0: break
                    NrCand += 1; c1 = c
            else:
                Step.Method  = T_HIDDEN_SINGLE
                Grid[r][c1]  = d+1
                memset(<void *>&Cands[r][c1][0], False, 36)  # 9 x 4bytes = 36
                discard_cand_from_peers_c(d+1, r, c1, Cands)
                Step.Pattern = [[P_VAL, d+1], [P_OP, OP_CNT, 1], [P_ROW, r],
                                [P_CON, ], [P_ROW, r], [P_COL, c1], [P_END, ]]
                Step.Outcome = [[P_ROW, r], [P_COL, c1], [P_OP, OP_ASNV], [P_VAL, d+1], [P_END, ]]
                return 1
    for c in range(9):  # scan each col
        for d in range(9):
            NrCand = 0; r1 = -1
            for r in range(9):
                if Grid[r][c] == d+1: break
                if Grid[r][c]: continue
                if Cands[r][c][d]:
                    if NrCand > 0: break
                    NrCand += 1; r1 = r
            else:
                Step.Method = T_HIDDEN_SINGLE
                Grid[r1][c] = d+1
                memset(<void *>&Cands[r1][c][0], False, 36)  # 9 x 4bytes = 36
                discard_cand_from_peers_c(d+1, r1, c, Cands)
                Step.Pattern = [[P_VAL, d+1], [P_OP, OP_CNT, 1], [P_COL, c],
                                [P_CON, ], [P_ROW, r1], [P_COL, c], [P_END, ]]
                Step.Outcome = [[P_ROW, r1], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, d+1], [P_END, ]]
                return 1
    for b in range(9):        # scan the blocks.
        br = (b//3)*3; bc = (b%3)*3
        for d in range(9):
            NrCand = 0
            # scan the cells in blocks/box.
            for b1 in range(9):
                r = br + b1//3; c = bc + b1%3
            # for r, c in [(br, bc), (br, bc+1), (br, bc+2), (br+1, bc), (br+1, bc+1), (br+1, bc+2), (br+2, bc), (br+2, bc+1), (br+2, bc+2)]:
                if Grid[r][c] == d+1: break
                if Grid[r][c]: continue
                if Cands[r][c][d]:
                    if NrCand > 0: break
                    NrCand += 1; r1 = r; c1 = c
            else:
                Step.Method = T_HIDDEN_SINGLE
                Grid[r1][c1] = d+1
                memset(<void *>&Cands[r1][c1][0], False, 36)  # 9 x 4bytes = 36
                discard_cand_from_peers_c(d+1, r1, c1, Cands)
                Step.Pattern = [[P_VAL, d+1], [P_OP, OP_CNT, 1], [P_BOX, b+1],
                                [P_CON, ], [P_ROW, r1], [P_COL, c1], [P_END, ]]
                Step.Outcome = [[P_ROW, r1], [P_COL, c1], [P_OP, OP_ASNV], [P_VAL, d+1], [P_END, ]]
                return 1
    return -1

cdef int tech_locked_singles_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # For pointing in a block if a candidate value is confined to a row or col
    # then none of of the cells in that row or col outside the block can have
    # the candidate value.
    #
    # For claiming in a row or column if a candidate value is confined to a block
    # then none of the cells in the block can have the candidate value.

    cdef int br, bc, r0, c0, r1, c1, or1, or2, oc1, oc2, t, Cand
    cdef int Ox[6]
    cdef COORD Orc[6]
    cdef bint Pointing = False, Claiming = False

    for Meth in Methods:
        if Meth == T_POINTING_LOCKED_SINGLE: Pointing = True
        if Meth == T_CLAIMING_LOCKED_SINGLE: Claiming = True
        if Meth == -1: break
    # TRCX(f"Pointing: {Pointing}, Claiming: {Claiming}")
    # TRCX(f"Cands: {trc_cands(Cands)}")
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            # scan the rows in the block
            for r0 in range(br, br+3):
                for Cand in range(9):
                    # TRCX(f"br:{br}, bc:{bc}, r0:{r0}, Cand:{Cand+1}")
                    if ((Cands[r0][bc][Cand] & Cands[r0][bc+1][Cand] & Cands[r0][bc+2][Cand])
                            or (Cands[r0][bc][Cand] & Cands[r0][bc+1][Cand])
                            or (Cands[r0][bc][Cand] & Cands[r0][bc+2][Cand])
                            or (Cands[r0][bc+1][Cand] & Cands[r0][bc+2][Cand])):  # 2 or 3 same val cands in a block row
                        # TRCX(f"{Cand+1}, occurs 2 or 3 times in r{r0+1}c{bc+1}{bc+2}{bc+3}")
                        if Pointing:
                            or1 = br + (r0+1)%3; or2 = br + (r0+2)%3
                            if or1 > or2: t = or1; or1 = or2; or2 = t
                            # TRCX(f"Pointing:  Checking for absence of cands in r{or1+1}{or2+1}c{bc+1}{bc+2}{bc+3}")
                            if not (Cands[or1][bc][Cand] | Cands[or1][bc+1][Cand] | Cands[or1][bc+2][Cand]
                                    | Cands[or2][bc][Cand] | Cands[or2][bc+1][Cand] | Cands[or2][bc+2][Cand]):  # not present in other box cells
                                oc1 = (bc+3)%9; oc2 = (bc+6)%9
                                # TRCX(f"No other cands in the box, checking for cands along the balance of the row: {oc1}, and {oc2}")
                                if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                                Ox = [oc1, oc1+1, oc1+2, oc2, oc2+1, oc2+2]
                                for c0 in Ox:
                                    if Cands[r0][c0][Cand]:
                                        # TRCX(f"Cand: {Cand+1}r{r0}c{c0} can be eliminated")
                                        Cands[r0][c0][Cand] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
                                if Step.Outcome:
                                    Step.Method = T_POINTING_LOCKED_SINGLE
                                    C1 = []  # C1 Python var.

                                    for c0 in range(bc, bc+3):
                                        if Cands[r0][c0][Cand]: C1.append(c0)
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand+1], [P_ROW, r0], [P_COL, C1], [P_SEP, ],
                                                    [P_VAL, Cand+1], [P_OP, OP_ABS], [P_ROW, or1, or2], [P_COL, bc, bc+1, bc+2],
                                                    [P_END]]
                                    # TRCX(f"Step Pattern: {Step.Pattern}")
                                    # TRCX(f"Step Outcome: {Step.Outcome}")
                                    return 0
                        if Claiming:
                            oc1 = (bc+3)%9; oc2 = (bc+6)%9
                            if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                            # TRCX(f"Claiming:  Checking for absence of cands in r{r0+1}c{oc1+1}{oc1+2}{oc1+3}{oc2+1}{oc2+2}{oc2+3}")
                            if not (Cands[r0][oc1][Cand] | Cands[r0][oc1+1][Cand] | Cands[r0][oc1+2][Cand]
                                    | Cands[r0][oc2][Cand] | Cands[r0][oc2+1][Cand] | Cands[r0][oc2+2][Cand]):  # not present along the balance of row
                                # TRCX(f"No other cands present: {Cand+1}!-r{r0+1}c{oc1+1}{oc1+2}{oc1+3}{oc2+1}{oc2+2}{oc2+3}")
                                or1 = br+(r0+1)%3; or2 = br+(r0+2)%3
                                if or1 > or2: t = or1; or1 = or2; or2 = t
                                # TRCX(f"Any cands in r{or1+1}{or2+1}c{bc+1}{bc+2}{bc+3} can be eliminated")
                                Orc[0].r = Orc[1].r = Orc[2].r = or1; Orc[3].r = Orc[4].r = Orc[5].r = or2
                                Orc[0].c = Orc[3].c = bc; Orc[1].c = Orc[4].c = bc+1; Orc[2].c = Orc[5].c = bc+2
                                for t in range(6):
                                    r1 = Orc[t].r; c1 = Orc[t].c
                                    # TRCX(f"Cands[{r1+1}][{c1+1}][{Cand+1}]: {Cands[r1][c1][Cand]}")
                                    if Cands[r1][c1][Cand]:
                                        Cands[r1][c1][Cand] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r1], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    C1 = []  # C1 Python var.
                                    for c0 in range(bc, bc+3):
                                        if Cands[r0][c0][Cand]: C1.append(c0)
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand+1], [P_ROW, r0], [P_COL, C1], [P_SEP, ],
                                                    [P_VAL, Cand+1], [P_OP, OP_ABS], [P_ROW, r0], [P_COL, oc1, oc1+1, oc1+2, oc2, oc2+1, oc2+2],
                                                    [P_END]]
                                    return 0
            # scan the cols in the block
            # TRCX("got here")
            for c0 in range(bc, bc+3):
                for Cand in range(9):
                    if ((Cands[br][c0][Cand] & Cands[br+1][c0][Cand] & Cands[br+2][c0][Cand])
                            or (Cands[br][c0][Cand] & Cands[br+1][c0][Cand])
                            or (Cands[br][c0][Cand] & Cands[br+2][c0][Cand])
                            or (Cands[br+1][c0][Cand] & Cands[br+2][c0][Cand])): # 2 or 3 same val cands in a block col.
                        if Pointing:
                            oc1 = bc + (c0+1)%3; oc2 = bc + (c0+2)%3
                            if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                            # TRCX("got here")
                            if not (Cands[br][oc1][Cand] | Cands[br+1][oc1][Cand] | Cands[br+2][oc1][Cand]
                                    | Cands[br][oc2][Cand] | Cands[br+1][oc2][Cand] | Cands[br+2][oc2][Cand]):  # not present in other box cells
                                # TRCX("got here")
                                or1 = (br+3)%9; or2 = (br+6)%9
                                if or1 > or2: t = or1; or1 = or2; or2 = t
                                Ox = [or1, or1+1, or1+2, or2, or2+1, or2+2]
                                for r0 in Ox:
                                    if Cands[r0][c0][Cand]:
                                        Cands[r0][c0][Cand] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
                                if Step.Outcome:
                                    Step.Method = T_POINTING_LOCKED_SINGLE
                                    R1 = []  # C1 Python var.
                                    for r0 in range(br, br+3):
                                        if Cands[r0][c0][Cand]: R1.append(r0)
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand+1], [P_ROW, R1], [P_COL, c0], [P_SEP, ],
                                                    [P_VAL, Cand+1], [P_OP, OP_ABS], [P_ROW, or1, or2], [P_COL, bc, bc+1, bc+2],
                                                    [P_END]]
                                    return 0
                        if Claiming:
                            # TRCX(f"2 or 3 of Cand{Cand+1} in r{br}{br+1}{br+2}c{c0}")
                            or1 = (br+3)%9; or2 = (br+6)%9
                            if or1 > or2: t = or1; or1 = or2; or2 = t
                            if not (Cands[or1][c0][Cand] | Cands[or1+1][c0][Cand] | Cands[or1+2][c0][Cand]
                                    | Cands[or2][c0][Cand] | Cands[or2+1][c0][Cand] | Cands[or2+2][c0][Cand]):  # not present along the balance of row
                                # TRCX(f"No cands present Col: {Cand+1}!-r{or1}{or1+1}{or1+2}c{c0}")
                                oc1 = bc+(c0+1)%3; oc2 = bc+(c0+2)%3
                                if oc1 > oc2: t = oc1; oc1 = oc2; oc2 = t
                                Orc[0].r = Orc[3].r = br; Orc[1].r = Orc[4].r = br+1; Orc[2].r = Orc[5].r = br+2
                                Orc[0].c = Orc[1].c = Orc[2].c = oc1; Orc[3].c = Orc[4].c = Orc[5].c = oc2
                                for t in range(6):
                                    r1 = Orc[t].r; c1 = Orc[t].c
                                    if Cands[r1][c1][Cand]:
                                        Cands[r1][c1][Cand] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r1], [P_COL, c1], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    R1 = []  # C1 Python var.
                                    for r0 in range(bc, bc+3):
                                        if Cands[r0][c0][Cand]: R1.append(r0)
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand+1], [P_ROW, R1], [P_COL, c0], [P_SEP, ],
                                                    [P_VAL, Cand+1], [P_OP, OP_ABS], [P_ROW, or1, or1+1, or1+2, or2, or2+1, or2+2], [P_COL, c0],
                                                    [P_END]]
                                    return 0
    return -1

cdef int tech_empty_rects_c(int Grid[9][9], Step, bint Cands[9][9][9], Method):
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
    cdef int    Cand, row, col, r, c, rb, cb, or1, or2, oc1, oc2, i, n, n1, m, m1
    cdef int    LKH, LKT
    cdef COORD  BC[5]
    cdef COORD  Elim[2]
    cdef int    Rx[6]
    cdef int    Cx[6]

    # TRCX("Got here")
    # TRCX(f"Cands: {trc_cands(Cands)}")
    for Cand in range(9):
        for row in range(9):
            rb = (row//3)*3
            for col in range(9):
                cb = (col//3)*3
                # TRCX(f"Looking in row: {row} and Col: {col}")
                n = 0
                for i in range(9):
                    r = rb+i//3; c = cb+i%3
                    if Cands[r][c][Cand]:
                        if r == row and c == col: BC[n].r = r; BC[n].c = c; n += 1
                        elif r == row or c == col: BC[n].r = r; BC[n].c = c; n += 1
                        else: break
                else:
                    if n < 3: continue
                    # TRCX(f"Empty rectangle block pattern found Cand:{Cand+1}, row:{row+1}, col:{col+1}")
                    # An empty rectangle pattern found, scan row and col for other candidates
                    # scan the row and col outside the box for additional candidates
                    or1 = (rb+3)%9; or2 = (rb+6)%9
                    oc1 = (cb+3)%9; oc2 = (cb+6)%9
                    Rx = [or1, or1+1, or1+2, or2, or2+1, or2+2]
                    Cx = [oc1, oc1+1, oc1+2, oc2, oc2+1, oc2+2]
                    for c in Cx:
                        if not Cands[row][c][Cand]: continue
                        for r in Rx:
                            if not Cands[r][col][Cand]: continue
                            # TRCX(f"Other Cands found: {Cand+1}r{row+1}c{c+1} and {Cand+1}r{r+1}c{col+1}")
                            # found a cand along the row and col, does the opposing cell have a Cand
                            if Cands[r][c][Cand]:
                                # TRCX(f"Opposing Candidate found {Cand+1}r{r+1}c{c+1}")
                                m = 0
                                LkT, LkH = how_ccells_linked_c(r, c, Cand, row, c, Cand, Cands)
                                # TRCX(f"LkT:{LkT} between {Cand+1}r{r+1}c{c+1} and {Cand+1}r{row+1}c{c+1}")
                                if LkT & LK_STRG_C: Elim[m].r = r; Elim[m].c = col; m += 1
                                LkT, LkH = how_ccells_linked_c(r, c, Cand, r, col, Cand, Cands)
                                # TRCX(f"LkT:{LkT} between {Cand+1}r{r+1}c{c+1} and {Cand+1}r{r+1}c{col+1}")
                                if LkT & LK_STRG_C:  Elim[m].r = row; Elim[m].c = c; m += 1
                                if m:
                                    Step.Method = T_EMPTY_RECT
                                    for m1 in range(m):
                                        Cands[Elim[m1].r][Elim[m1].c][Cand] = False
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, Elim[m1].r], [P_COL, Elim[m1].c], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand+1], [P_OP, OP_CNT, len(BC)], [P_BOX, (rb//3)*3+cb//3]]
                                    for n1 in range(n):
                                        Step.Pattern.extend([[P_CON, ], [P_ROW, BC[n1].r], [P_COL, BC[n1].c]])
                                    Step.Pattern.append([P_END, ])
                                    return 0
    return -1

cdef int tech_brute_force_c(int Grid[9][9], Step, bint Cands[9][9][9], Method):

    cdef int r, c, rr
    cdef int G[9][9]

    # Randomly find an empty cell
    while 1:
        rr = rand()
        r = (rr%81)//9; c = rr%9
        if not Grid[r][c]: break

    memcpy(<void *>G, <void *>Grid, sizeof (int[9][9]))
    if solve_puzzle_backtrack(G, 0):
        Step.Method     = T_BRUTE_FORCE
        Grid[r][c]      = G[r][c]
        Step.Pattern    = [[P_ROW, r], [P_COL, c], [P_OP, OP_EQ], [P_VAL, Grid[r][c]], [P_END, ]]
        Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
        memset(<void *>&Cands[r][c][0], False, 9* sizeof(int))
        discard_cand_from_peers_c(Grid[r][c], r, c, Cands)
        return 1
    else:
        return 0

cdef bint solve_puzzle_backtrack(int [9][9]Grid, int Cell):
    #  Recursive backtracking function to find a Sudoku puzzle. If the
    #  puzzle is not a valid sudoku either the first solution found will be
    #  in grid, or returns False if no solution found.
    #  Grid: In:  A Sudoku puzzle (can process invalid puzzles too)
    #        Recursive call:  Partially solved puzzle
    #        Out:  The solved puzzle.
    #  cell: In: Optional: - must be 0 if not called recursively
    #        Recursive call: The current cell position
    #  Returns:  True: a solution found - does not imply a valid puzzle
    #            False: no solution found - implies invalid puzzle
    cdef int r, c, v
    #  Find the next hole in the puzzle.
    while Cell < 81:
        r = Cell//9
        c = Cell%9
        if Grid[r][c] != 0:
            Cell += 1
        else:
            break
    else:
        #        Soln[0] = [[Grid[r1][c1] for c1 in range(9)] for r1 in range(9)]
        return True  # All cells successfully filled

    for v in range(1, 10):
        if cell_val_has_no_conflicts_c(v, Grid, r, c):
            Grid[r][c] = v
            if solve_puzzle_backtrack(Grid, Cell+1):
                return True
    Grid[r][c] = 0
    return False


# TODO Add Almost Locked Candidates.  Perhaps not, have not seen any examples in my searches
# to validate.
