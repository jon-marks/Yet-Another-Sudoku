
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
                Step.Pattern    = [[P_VAL, Grid[r][c]], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_END]]
                Step.Outcome    = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END]]
                return 1
    return -1

def tech_hidden_singles(Grid, Step, Cands, Methods):
    # For each empty cell in the grid, subtracting all the candidates from its
    # group (either row, col, blk_peers will yield the single if one exists,
    # either hidden or exposed.

    sCand = Step.Overrides.get('Cand')
    if sCand: CandList = [int(s) for s in sCand.split(",")]
    else: CandList = list(range(1, 10))
    sRow = Step.Overrides.get('Row')
    if sRow: RowList = [int(s)-1 for s in sRow.split(",")]
    elif sRow == '': RowList = []
    else: RowList = list(range(9))
    sCol = Step.Overrides.get('Col')
    if sCol: ColList = [int(s)-1 for s in sCol.split(",")]
    elif sCol == '': ColList = []
    else: ColList = list(range(9))
    sBox = Step.Overrides.get('Box')
    if sBox: BoxList = [int(s)-1 for s in sBox.split(",")]
    elif sBox == '': BoxList = []
    else: BoxList = list(range(9))

    n = c1 = r1 = Cand = 0  # hack to give variables function level scope.
    # scan rows
    for r in RowList:  # range(9):
        for Cand in CandList:  # range(1, 10):
            n = 0
            for c in range(9):
                if Cand in Cands[r][c]:
                    if n: break
                    else: n += 1; c1 = c
            else:
                if n:
                    Step.Method = T_HIDDEN_SINGLE
                    Grid[r][c1] = Cand
                    Step.Pattern = [[P_VAL, Cand], [P_OP, OP_CNT, 1], [P_ROW, r], [P_CON], [P_ROW, r], [P_COL, c1], [P_END]]
                    Step.Outcome = [[P_ROW, r], [P_COL, c1], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END]]
                    Cands[r][c1].clear()
                    discard_cand_from_peers(Cand, r, c1, Cands)
                    return 1
    # scan cols
    for c in ColList:  # range(9):
        for Cand in CandList:  # range(1, 10):
            n = 0
            for r in range(9):
                if Cand in Cands[r][c]:
                    if n: break
                    else: n += 1; r1 = r
            else:
                if n:
                    Step.Method = T_HIDDEN_SINGLE
                    Grid[r1][c] = Cand
                    Step.Pattern = [[P_VAL, Cand], [P_OP, OP_CNT, 1], [P_COL, c], [P_CON], [P_ROW, r1], [P_COL, c], [P_END]]
                    Step.Outcome = [[P_ROW, r1], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END]]
                    Cands[r1][c].clear()
                    discard_cand_from_peers(Cand, r1, c, Cands)
                    return 1
    #scan boxs
    for h in BoxList:  # range(9):
        br = (h//3)*3; bc = (h%3)*3
        for Cand in CandList:  # range(1, 10):
            n = 0
            for b in range(9):
                r = br + b//3; c = bc + b%3
                if Cand in Cands[r][c]:
                    if n: break
                    else: n += 1; r1 = r; c1 = c
            else:
                if n:
                    Step.Method = T_HIDDEN_SINGLE
                    Grid[r1][c1] = Cand
                    Step.Pattern = [[P_VAL, Cand], [P_OP, OP_CNT, 1], [P_BOX, h], [P_CON], [P_ROW, r1], [P_COL, c1], [P_END]]
                    Step.Outcome = [[P_ROW, r1], [P_COL, c1], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END]]
                    Cands[r1][c1].clear()
                    discard_cand_from_peers(Cand, r1, c1, Cands)
                    return 1
    return -1

def tech_locked_singles(Grid, Step, Cands, Methods):
    # For pointing in a block if a candidate value is confined to a row or col
    # then none of the cells in that row or col outside the block can have
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
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r0], [P_COL, c],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method  = T_POINTING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1], [P_CON], [P_OP, OP_ABS], [P_BOX, (r0//3)*3 + C1[0]%3 + 1], [P_END]]
                                    return 0
                        # else check claiming
                        if (T_CLAIMING_LOCKED_SINGLE in Methods) or (T_UNDEF in Methods):
                            U = set()
                            for c in C2:  # set(range(9))-{bc, bc1, bc2}:
                                U |= Cands[r0][c]
                            if Cand not in U:
                                # Candidate is locked to the block, Candidate vals in the rest
                                # of the block can be discarded
                                for c in [bc, bc1, bc2]:
                                    for x in Rx:  # or1, or2]:
                                        if Cand in Cands[x][c]:
                                            Cands[x][c].discard(Cand)
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, x], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, r0], [P_COL, C1], [P_CON], [P_OP, OP_ABS], [P_ROW, r0], [P_END]]
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
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_POINTING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0], [P_CON], [P_OP, OP_ABS], [P_BOX, (R1[0]//3)*3 + c0%3 + 1], [P_END]]
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
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, r], [P_COL, x], [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if Step.Outcome:
                                    Step.Method = T_CLAIMING_LOCKED_SINGLE
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_VAL, Cand], [P_ROW, R1], [P_COL, c0], [P_CON], [P_OP, OP_ABS], [P_COL, c0], [P_END]]
                                    return 0
    return -1

def tech_empty_rects(Grid, Step, Cands, Methods):
    # Covers the occurrence of 3 to 5 occurrences of the same candidate value
    # in a box that only describe a row and column in that box.  Occurrences of
    # less than three same candidate values are simply potential X-Chains and
    # are handled by the x chain algorithms.

    # Look for boxes that contain 3 to 5 same candidate value that describe only
    # a single row (r) and column (c).  Then scan the column and the row outside
    # the box to find other cells with same value candidates (Cr and Cc).  If
    # any cell (Cb) that both Cr and Cc see also has a same value candidate then
    # we have found an Empty Rectangle.  If a strong link between Cb
    # and Cc exists, then the candidate can be eliminated from Cr.  Similarly, if
    # a strong link between Cb and Cr exists, then Cc too can be eliminated.
    #

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
                    # An empty rectangle pattern found, scan row and col for other candidates
                    # scan the row and col outside the box for additional candidates
                    or1 = (rb+3)%9; or2 = (rb+6)%9
                    oc1 = (cb+3)%9; oc2 = (cb+6)%9
                    for c in [oc1, oc1+1, oc1+2, oc2, oc2+1, oc2+2]:
                        if Cand not in Cands[row][c]: continue
                        for r in [or1, or1+1, or1+2, or2, or2+1, or2+2]:
                            if Cand not in Cands[r][col]: continue
                            # found a cand along the row and col, does the opposing cell have a Cand
                            if Cand in Cands[r][c]:
                                Elim = []
                                Lk = how_ccells_linked(r, c, Cand, row, c, Cand, Cands)
                                if Lk & LK_STRG: Elim.append((r, c, row, c, r, col))
                                Lk = how_ccells_linked(r, c, Cand, r, col, Cand, Cands)
                                if Lk & LK_STRG: Elim.append((r, c, r, col, row, c))
                                if len(Elim):
                                    Step.Method = T_EMPTY_RECT
                                    Step.Pattern = [[P_VAL, Cand], [P_OP, OP_CNT, len(BC)], [P_BOX, (rb//3)*3+cb//3], [P_CON], [P_ROW, row], [P_CON], [P_COL, col]]
                                    for r1, c1, r2, c2, r3, c3 in Elim:
                                        Cands[r3][c3].discard(Cand)
                                        Step.Pattern.extend([[P_CON], [P_VAL, Cand], [P_ROW, r1], [P_COL, c1], [P_OP, OP_EQ], [P_VAL, Cand], [P_ROW, r2], [P_COL, c2]])
                                        if Step.Outcome: Step.Outcome.append([P_SEP])
                                        Step.Outcome.extend([[P_ROW, r3], [P_COL, c3],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    Step.Pattern.append([P_END])
                                    Step.Outcome.append([P_END])
                                    return 0
    return -1

def tech_brute_force(Grid, Step, Cands, Methods):

    # Note Grid must have at least one hole in it, else code will hang here.
    # Randomly find an empty cell
    while 1:
        rr = randint(0, 80)
        r = rr//9; c = rr%9
        if not Grid[r][c]: break

    Grid[r][c] = Step.Soln[r][c]
    Step.Method = T_BRUTE_FORCE
    Step.Pattern = [[P_ROW, r], [P_COL, c], [P_OP, OP_EQ], [P_VAL, Grid[r][c]], [P_END]]
    Step.Outcome = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Grid[r][c]], [P_END]]
    Cands[r][c].clear()
    discard_cand_from_peers(Grid[r][c], r, c, Cands)
    return 1

