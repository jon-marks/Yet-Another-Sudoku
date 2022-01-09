
from copy import copy
from random import randint

from globals import *
from solve_utils import *  # discard_cand_from_peers, cell_val_has_no_conflicts, how_ccells_linked

def tech_exposed_singles(Grid, Step, Cands, Methods):

    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 1:
                Step.Method     = T_EXPOSED_SINGLE
                Grid[r][c]      = Cands[r][c].pop()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                Step.Pattern    = [[P_VAL, Grid[r][c]], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                return 1
    return -1

def tech_hidden_singles(Grid, Step, Cands, Methods):
    # For each empty cell in the grid, subtracting all the candidates from its
    # group (either row, col, blk_peers will yield the single if one exists,
    # either hidden or exposed.

    for r in range(9):
        for c in range(9):
            # Scan the row first.
            D = Cands[r][c].copy()
            for c1 in set(range(9))-{c}:
                D -= Cands[r][c1]
            if len(D) == 1:  # Hidden single found in row.
                Step.Method     = T_HIDDEN_SINGLE
                Grid[r][c]      = D.pop()
                Step.Pattern    = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_ROW, r],
                                   [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                return 1
            # Scan the col
            D = Cands[r][c].copy()
            for r1 in set(range(9))-{r}:
                D -= Cands[r1][c]
            if len(D) == 1:  # Hidden single found in col.
                Step.Method     = T_HIDDEN_SINGLE
                Grid[r][c]      = D.pop()
                Step.Pattern    = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_COL, c],
                                   [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
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
                Step.Method     = T_HIDDEN_SINGLE
                Grid[r][c]      = D.pop()
                Step.Pattern    = [[P_VAL, Grid[r][c]], [P_OP, OP_CNT, 1], [P_BOX, (br//3)*3+bc//3],
                                   [P_CON, ], [P_ROW, r], [P_COL, c], [P_END, ]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
                Cands[r][c].clear()
                discard_cand_from_peers(Grid[r][c], r, c, Cands)
                return 1
    return -1

def tech_locked_singles(Grid, Step, Cands, Methods):
    # For pointing in a block if a candidate value is confined to a row or col
    # then none of of the cells in that row or col outside the block can have
    # the candidate value.
    #
    # For claiming in a row or column if a candidate value is confined to a block
    # then none of the cells in the block can have the candidate value.

    # if (POINTING_LOCKED_SINGLE not in Method) \
    #         and (CLAIMING_LOCKED_SINGLE not in Method) \
    #         and (T_UNDEF not in Method): return -2

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
                        if (T_POINTING_LOCKED_SINGLE in Methods) or (T_UNDEF in Methods):
                            if Cand not in (Cands[or1][bc] | Cands[or1][bc1] | Cands[or1][bc2]
                                          | Cands[or2][bc] | Cands[or2][bc1] | Cands[or2][bc2]):
                            # Candidate is locked to the row and can be discarded
                            # from balance of row.
                                for c in C2:  # set(range(9)) - {bc, bc1, bc2}:
                                    if Cand in Cands[r0][c]:
                                        Cands[r0][c].discard(Cand)
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, c],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method  = T_POINTING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, Rx], [P_COL, bc, bc1, bc2],
                                                    [P_END, ]]
                                    return 0
                        # else check claiming
                        if (T_CLAIMING_LOCKED_SINGLE in Methods) or (T_UNDEF in Methods):
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
                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                            Step.Outcome.extend([[P_ROW, x], [P_COL, c],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1],
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
                        if (T_POINTING_LOCKED_SINGLE in Methods) or (T_UNDEF in Methods):
                            if Cand not in (Cands[br][oc1] | Cands[br1][oc1] | Cands[br2][oc1]
                                            | Cands[br][oc2] | Cands[br1][oc2] | Cands[br2][oc2]):
                                # Candidate is locked to the col, and can be discarded
                                # from the balance of the col.
                                for r in R2:  # set(range(9)) - {br, br1, br2}:
                                    if Cand in Cands[r][c0]:
                                        Cands[r][c0].discard(Cand)
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r], [P_COL, c0],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_POINTING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, br, br1, br2], [P_COL, Cx],
                                                    [P_END, ]]
                                    return 0
                        # else check claiming
                        if (T_CLAIMING_LOCKED_SINGLE in Methods) or (T_UNDEF in Methods):
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
                                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                            Step.Outcome.extend([[P_ROW, r], [P_COL, x],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0],
                                                    [P_SEP, ], [P_VAL, Cand], [P_OP, OP_ABS],
                                                    [P_ROW, R2], [P_COL, c0], [P_END, ]]
                                    return 0
    return -1

def tech_empty_rects(Grid, Step, Cands, Methods):
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

    # if (T_EMPTY_RECT not in Method) and (T_UNDEF not in Method): return -2

    # Look for a box that only has cands that describe a single row and col in
    # that box.

    for Cand in range(1, 10):
        for row in range(9):
            rb = (row//3)*3
            for col in range(9):
                cb = (col//3)*3
                BC = []
                for i in range(9):
                    r = rb+i//3; c = cb+i%3
                    if Cand in Cands[r][c]:
                        if r == row and c == col: BC.append((r, c))
                        elif r == row or c == col: BC.append((r, c))
                        else: break
                else:
                    if len(BC) < 3: continue
                    # An empty rectangle pattern found, scan row and col for other condidates
                    # scan the row and col outside the box for additional candiates
                    or1 = (rb+3)%9; or2 = (rb+6)%9
                    oc1 = (cb+3)%9; oc2 = (cb+6)%9
                    Rx = [or1, or1+1, or1+2, or2, or2+1, or2+2]
                    Cx = [oc1, oc1+1, oc1+2, oc2, oc2+1, oc2+2]
                    for c in Cx:
                        if Cand not in Cands[row][c]: continue
                        for r in Rx:
                            if Cand not in Cands[r][col]: continue
                            # found a cand along the row and col, does the opposing cell have a Cand
                            if Cand in Cands[r][c]:
                                Elim = []
                                LkT, LkH = how_ccells_linked(r, c, Cand, row, c, Cand, Cands)
                                if LkT & LK_STRG: Elim.append((r, col))
                                LkT, LkH = how_ccells_linked(r, c, Cand, r, col, Cand, Cands)
                                if LkT & LK_STRG: Elim.append((row, c))
                                if len(Elim):
                                    Step.Method = T_EMPTY_RECT
                                    for r3, c3 in Elim:
                                        Cands[r3][c3].discard(Cand)
                                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                                        Step.Outcome.extend([[P_ROW, r3], [P_COL, c3],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    Step.Outcome.append([P_END, ])
                                    Step.Pattern = [[P_VAL, Cand], [P_OP, OP_CNT, len(BC)], [P_BOX, (rb//3)*3+cb//3]]
                                    for r3, c3 in BC:
                                        Step.Pattern.extend([[P_CON, ], [P_ROW, r3], [P_COL, c3]])
                                    Step.Pattern.append([P_END, ])
                                    return 0
    return -1

def tech_brute_force(Grid, Step, Cands, Methods):

    # Randomly find an empty cell
    while 1:
        rr = randint(0, 80)
        r = rr//9; c = rr%9
        if not Grid[r][c]: break

    G = [[Grid[r1][c1] for c1 in range(9)] for r1 in range(9)]
    if _solve_puzzle_backtrack(G):
        Step.Method     = T_BRUTE_FORCE
        Grid[r][c]      = G[r][c]
        Step.Pattern    = [[P_ROW, r], [P_COL, c], [P_OP, OP_EQ], [P_VAL, Grid[r][c]], [P_END, ]]
        Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END, ]]
        Cands[r][c].clear()
        discard_cand_from_peers(Grid[r][c], r, c, Cands)
        return 1
    else:
        return 0

def _solve_puzzle_backtrack(Grid, Cell = 0):
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

    for v in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        if cell_val_has_no_conflicts(v, Grid, r, c):
            Grid[r][c] = v
            if _solve_puzzle_backtrack(Grid, Cell+1):
                return True
    Grid[r][c] = 0
    return False


# TODO Add Almost Locked Candidates.  Perhaps not, have not seen any examples in my searches
# to validate.
