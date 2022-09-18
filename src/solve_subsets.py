from copy import copy

from globals import *
from solve_utils import *

def tech_exposed_pairs(Grid, Step, Cands, Methods):
    # In any group (row, col or box), if any two cells have only the same two
    # candidates then we have found an exposed pair.  These candidates can be
    # eliminated from the balance of cells in that group.  If these two cell are
    # in the intersection of a box and a row or column, the we have a locked
    # exposed pair and the these candidates can be eliminated from the balance
    # of cells in the box and row/col.

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

    # Scan the rows first.
    for r in RowList:
        for c in range(8):
            if len(Cands[r][c]) != 2: continue
            for c1 in range(c+1, 9):
                if Cands[r][c] != Cands[r][c1]: continue
                # Found an exposed pair in the row. Could it perhaps
                # be a locked pair too?
                if (c//3) == (c1//3):  # both cells in same blk
                    # Yes, it is a locked pair too.
                    br = (r//3)*3; bc = (c//3)*3
                    for r2 in [br, br+1, br+2]:
                        if r2 == r: continue
                        for c2 in [bc, bc+1, bc+2]:
                            if Grid[r2][c2]: continue
                            Elims = Cands[r2][c2] & Cands[r][c]
                            if Elims:
                                Cands[r2][c2] -= Cands[r][c]
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, Elims]])
                if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_PAIR
                for c2 in set(range(9)) - {c, c1}:
                    if Grid[r][c2]: continue
                    Elims = Cands[r][c2] & Cands[r][c]
                    if Elims:
                        Cands[r][c2] -= Cands[r][c]
                        if Step.Outcome: Step.Outcome.append([P_SEP])
                        Step.Outcome.extend([[P_ROW, r], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, Elims]])
                if Step.Outcome:  # Candidates were eliminated
                    if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_PAIR
                    Step.Outcome.append([P_END])
                    Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c, c1], [P_END]]
                    return 0
    # then scan the cols.
    for c in ColList:
        for r in range(8):
            if len(Cands[r][c]) != 2: continue
            for r1 in range(r+1, 9):
                if Cands[r][c] != Cands[r1][c]: continue
                # Found an exposed pair in the col. Could it perhaps
                # be a locked pair too?
                if (r//3) == (r1//3):  # both cells in same blk
                    # Yes, it is a locked pair too.
                    br = (r//3)*3; bc = (c//3)*3
                    for c2 in [bc, bc+1, bc+2]:
                        if c2 == c: continue
                        for r2 in [br, br+1, br+2]:
                            if Grid[r2][c2]: continue
                            Elims = Cands[r2][c2] & Cands[r][c]
                            if Elims:
                                Cands[r2][c2] -= Cands[r][c]
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, Elims]])
                if Step.Outcome: Step.Method = T_LOCKED_EXPOSED_PAIR
                for r2 in set(range(9)) - {r, r1}:
                    if Grid[r2][c]: continue
                    Elims = Cands[r2][c] & Cands[r][c]
                    if Elims:
                        Cands[r2][c] -= Cands[r][c]
                        if Step.Outcome: Step.Outcome.append([P_SEP])
                        Step.Outcome.extend([[P_ROW, r2], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                if Step.Outcome:  # Candidates were eliminated
                    if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_PAIR
                    Step.Outcome.append([P_END])
                    Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r, r1], [P_COL, c], [P_END]]
                    return 0
    # and finally scan the blocks.
    for h in BoxList:  # range BoxList:
        br = (h//3)*3; bc = (h%3)*3
        for rc in range(8):
            r = br+(rc//3); c = bc+(rc%3)
            if len(Cands[r][c]) != 2: continue
            for rc1 in range(rc+1, 9):
                r1 = br+(rc1//3); c1 = bc+(rc1%3)
                if Cands[r][c] != Cands[r1][c1]: continue
                # Found an exposed pair in a box, discard matching
                # candidates from remaining cells in the box.
                for rc2 in set(range(9)) - {rc, rc1}:
                    r2 = br+(rc2//3); c2 = bc+(rc2%3)
                    if Grid[r2][c2]: continue
                    Elims = Cands[r2][c2] & Cands[r][c]
                    if Elims:
                        Cands[r2][c2] -= Cands[r][c]
                        if Step.Outcome: Step.Outcome.append([P_SEP])
                        Step.Outcome.extend([[P_ROW, r2], [P_COL, c2], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                if Step.Outcome:
                    Step.Method = T_EXPOSED_PAIR
                    Step.Outcome.append([P_END])
                    Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON], [P_ROW, r1], [P_COL, c1], [P_END]]
                    return 0
    return -1

def tech_hidden_pairs(Grid, Step, Cands, Methods):
    # A hidden pair is where two cells in a group share the same two candidates
    # (out of all their candidates), which are not found elsewhere in the group.
    # That is the candidates of those two cells are limited to the pair of
    # candidates they share.  All other candidates in those two cells can be
    # eliminated, thereby exposing the pair.  Algorithmically, select two cells
    # in a group and subtract the union of the candidates from the remaining
    # cells from the two selected cells.  If the same two remaining
    # candidates are in the selected cells, then a hidden pair has been found.

    for Cand0 in range(1, 9):
        for Cand1 in range(Cand0+1, 10):
            # scan row
            for r0 in range(9):
                n0 = 0; C = []
                for c0 in range(9):
                    if Grid[r0][c0]: continue
                    LenX = len(Cands[r0][c0] & {Cand0, Cand1})
                    if not LenX: continue
                    elif LenX == 1: break
                    if n0 > 1: break
                    C.append(c0); n0 += 1
                else:
                    if n0 != 2: continue
                    # found a hidden Pair in row
                    for c0 in C:
                        Elims = Cands[r0][c0] - {Cand0, Cand1}
                        if Elims:
                            Cands[r0][c0] = {Cand0, Cand1}
                            if Step.Outcome: Step.Outcome.append([P_SEP])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, Cand0, Cand1], [P_OP, OP_CNT, 2], [P_ROW, r0], [P_COL, C], [P_END]]
                        return 0
            # scan cols
            for c0 in range(9):
                n0 = 0; R = []
                for r0 in range(9):
                    if Grid[r0][c0]: continue
                    LenX = len(Cands[r0][c0] & {Cand0, Cand1})
                    if not LenX: continue
                    elif LenX == 1: break
                    if n0 > 1: break
                    R.append(r0); n0 += 1
                else:
                    if n0 != 2: continue
                    # found a hidden pair in col
                    for r0 in R:
                        Elims = Cands[r0][c0] - {Cand0, Cand1}
                        if Elims:
                            Cands[r0][c0] = {Cand0, Cand1}
                            if Step.Outcome: Step.Outcome.append([P_SEP])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, Cand0, Cand1], [P_OP, OP_CNT, 2], [P_ROW, R], [P_COL, c0], [P_END]]
                        return 0
            # scan boxes
            for h0 in range(9):
                br = (h0//3)*3; bc = (h0%3)*3
                n0 = 0; B = []
                for b0 in range(9):
                    r0 = br + b0//3; c0 = bc + b0%3
                    if Grid[r0][c0]: continue
                    LenX = len(Cands[r0][c0] & {Cand0, Cand1})
                    if not LenX: continue
                    elif LenX == 1: break
                    if n0 > 1: break
                    B.append((r0, c0)); n0 += 1
                else:
                    if n0 != 2: continue
                    # found a hidden pair in block
                    for r0, c0 in B:
                        Elims = Cands[r0][c0] - {Cand0, Cand1}
                        if Elims:
                            Cands[r0][c0] = {Cand0, Cand1}
                            if Step.Outcome: Step.Outcome.append([P_SEP])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                    if Step.Outcome:
                        Step.Outcome.append([P_END])
                        Step.Method = T_HIDDEN_PAIR
                        Step.Pattern = [[P_VAL, Cand0, Cand1], [P_OP, OP_CNT, 2], [P_BOX, h0]]
                        for r0, c0 in B:
                            Step.Pattern.extend([[P_CON], [P_ROW, r0], [P_COL, c0]])
                        Step.Pattern.append([P_END])
                        return 0
    return -1

def tech_exposed_triples(Grid, Step, Cands, Methods):
    # In any group (row, col or box) if any three empty cells have any
    # combination of only the same 3 candidates, then we have found an exposed
    # triple, and these three candidates can be eliminated from other cells.
    # Furthermore, if these three candidates are in the intersection of a box
    # and a row/col, this is a locked exposed triple and the candidates can be
    # eliminated from the other cells in that box too.

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

    # Scan the rows first
    for r in RowList:  # range(9):
        for c in range(7):
            if not 2 <= len(Cands[r][c]) <= 3: continue
            for c1 in range(c+1, 8):
                if not 2 <= len(Cands[r][c1]) <= 3: continue
                for c2 in range(c1+1, 9):
                    if not 2 <= len(Cands[r][c2]) <= 3: continue
                    D = Cands[r][c] | Cands[r][c1] | Cands[r][c2]
                    if len(D) == 3:
                        # An exposed triple is found, is it a locked triple?
                        if T_LOCKED_EXPOSED_TRIPLE in Methods:
                            bc = c//3
                            if bc == c1//3 == c2//3:
                                # Yes we have a locked exposed triple
                                br = (r//3)*3; bc *= 3
                                for r3 in range(br, br+3):
                                    if r3 == r: continue
                                    for c3 in range(bc, bc+3):
                                        if Grid[r3][c3]: continue
                                        Elims = Cands[r3][c3] & D
                                        if Elims:
                                            Cands[r3][c3] -= D
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, r3], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:  Step.Method = T_LOCKED_EXPOSED_TRIPLE
                        for c3 in range(9):
                            if c3 in [c, c1, c2]: continue
                            if Grid[r][c3]: continue
                            Elims = Cands[r][c3] & D
                            if Elims:
                                Cands[r][c3] -= D
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:
                            if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_TRIPLE
                            Step.Outcome.append([P_END])
                            Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c], [P_CON],
                                            [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c1], [P_CON],
                                            [P_VAL, sorted(Cands[r][c2])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c2], [P_END]]
                            return 0
    # scan the cols
    for c in ColList:  # range(9):
        for r in range(7):
            if not 2 <= len(Cands[r][c]) <= 3: continue
            for r1 in range(r+1, 8):
                if not 2 <= len(Cands[r1][c]) <= 3: continue
                for r2 in range(r1+1, 9):
                    if not 2 <= len(Cands[r2][c]) <= 3: continue
                    D = Cands[r][c] | Cands[r1][c] | Cands[r2][c]
                    if len(D) == 3:
                        # An exposed triple is found, is it a locked triple?
                        if T_LOCKED_EXPOSED_TRIPLE in Methods:
                            br = r//3
                            if br == r1//3 and br == r2//3:
                                # Yes we have a locked exposed triple
                                bc = (c//3)*3; br *= 3
                                for c3 in range(bc, bc+3):
                                    if c3 == c: continue
                                    for r3 in range(br, br+3):
                                        if Grid[r3][c3]: continue
                                        Elims = Cands[r3][c3] & D
                                        if Elims:
                                            Cands[r3][c3] -= D
                                            if Step.Outcome: Step.Outcome.append([P_SEP])
                                            Step.Outcome.extend([[P_ROW, r3], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:  Step.Method = T_LOCKED_EXPOSED_TRIPLE
                        # else: Step.Method = T_EXPOSED_TRIPLE
                        for r3 in range(9):
                            if r3 in [r, r1, r2]: continue
                            if Grid[r3][c]: continue
                            Elims = Cands[r3][c] & D
                            if Elims:
                                Cands[r3][c] -= D
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r3], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:  # Candidates were eliminated
                            if Step.Method == T_UNDEF: Step.Method = T_EXPOSED_TRIPLE
                            Step.Outcome.append([P_END])
                            Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c], [P_CON],
                                            [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ],
                                            [P_ROW, r1], [P_COL, c], [P_CON],
                                            [P_VAL, sorted(Cands[r2][c])], [P_OP, OP_EQ],
                                            [P_ROW, r2], [P_COL, c], [P_END]]
                            return 0
    # the scan the blocks.
    for h in BoxList:  # range BoxList:
        br = (h//3)*3; bc = (h%3)*3
        for rc in range(7):
            r = br+(rc//3); c = bc+(rc%3)
            if not 2 <= len(Cands[r][c]) <= 3: continue
            for rc1 in range(rc+1, 8):
                r1 = br+(rc1//3); c1 = bc+(rc1%3)
                if not 2 <= len(Cands[r1][c1]) <= 3: continue
                for rc2 in range(rc1+1, 9):
                    r2 = br+(rc2//3); c2 = bc+(rc2%3)
                    if not 2 <= len(Cands[r2][c2]) <= 3:
                        continue
                    D = Cands[r][c] | Cands[r1][c1] | Cands[r2][c2]
                    if len(D) == 3:
                        # An exposed triple is found
                        for rc3 in set(range(9)) - {rc, rc1, rc2}:
                            r3 = br+(rc3//3); c3 = bc+(rc3%3)
                            if Grid[r3][c3]: continue
                            Elims = Cands[r3][c3] & D
                            if Elims:
                                Cands[r3][c3] -= D
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r3], [P_COL, c3], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:
                            Step.Method = T_EXPOSED_TRIPLE
                            Step.Outcome.append([P_END])
                            Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c], [P_CON],
                                            [P_VAL, sorted(Cands[r1][c1])], [P_OP, OP_EQ],
                                            [P_ROW, r1], [P_COL, c1], [P_CON],
                                            [P_VAL, sorted(Cands[r2][c2])], [P_OP, OP_EQ],
                                            [P_ROW, r2], [P_COL, c2], [P_END]]
                            return 0
    return -1

def tech_hidden_triples(Grid, Step, Cands, Methods):
    # A hidden triple is where the union of three cells in a group contains the
    # same three candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those three cells that are not the
    # same three candidates, thereby exposing the hidden triple.

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

    for Cand0 in range(1, 8):
        for Cand1 in range(Cand0+1, 9):
            for Cand2 in range(Cand1+1, 10):
                # scan rows
                for r0 in RowList:  # range(9):
                    n0 = 0; C = []; U = set()
                    for c0 in range(9):
                        if Grid[r0][c0]: continue
                        X = Cands[r0][c0] & {Cand0, Cand1, Cand2}
                        if not X: continue
                        if len(X) == 1: break
                        if n0 > 2: break
                        C.append((c0, X)); U |= X; n0 += 1
                    else:
                        if n0 != 3 or len(U) != 3: continue
                        # hidden trip found in r0
                        for c0, X in C:
                            Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2}
                            if Elims:
                                Cands[r0][c0] = X
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:
                            Step.Outcome.append([P_END])
                            Step.Method = T_HIDDEN_TRIPLE
                            Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_ROW, r0], [P_COLX, C[0][0], C[1][0], C[2][0]], [P_END]]
                            return 0
                # scan cols
                for c0 in ColList:  # range(9):
                    n0 = 0; R = []; U = set()
                    for r0 in range(9):
                        if Grid[r0][c0]: continue
                        X = Cands[r0][c0] & {Cand0, Cand1, Cand2}
                        if not X: continue
                        if len(X) == 1: break
                        if n0 > 2: break
                        R.append((r0, X)); U |= X; n0 += 1
                    else:
                        if n0 != 3 or len(U) != 3: continue
                        # hidden trip found in r0
                        for r0, X in R:
                            Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2}
                            if Elims:
                                Cands[r0][c0] = X
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:
                            Step.Outcome.append([P_END])
                            Step.Method = T_HIDDEN_TRIPLE
                            Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_ROWX, R[0][0], R[1][0], R[2][0]], [P_COL, c0], [P_END]]
                            return 0
                # scan boxes
                for h0 in BoxList:  # range(9):
                    br = (h0//3)*3; bc = (h0%3)*3
                    n0 = 0; B = []; U = set()
                    for b0 in range(9):
                        r0 = br + b0//3; c0 = bc + b0%3
                        if Grid[r0][c0]: continue
                        X = Cands[r0][c0] & {Cand0, Cand1, Cand2}
                        if not X: continue
                        if len(X) == 1: break
                        if n0 > 2: break
                        B.append((b0, r0, c0, X)); U |= X; n0 += 1
                    else:
                        if n0 != 3 or len(U) != 3: continue
                        # found a hidden trip in block
                        for b0, r0, c0, X in B:
                            Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2}
                            if Elims:
                                Cands[r0][c0] = X
                                if Step.Outcome: Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                        if Step.Outcome:
                            Step.Outcome.append([P_END])
                            Step.Method = T_HIDDEN_TRIPLE
                            Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_BOX, h0], [P_POSX, B[0][0], B[1][0], B[2][0]], [P_END]]
                            return 0
    return -1

def tech_exposed_quads(Grid, Step, Cands, Methods):
    # In any group (row, col or box) if any four empty cells have any
    # combination of only the same 4 candidates, then we have found an exposed
    # quad, and these four candidates can be eliminated from other cells in that
    # group.  It is impossible to have a locked exposed quad as four cells
    # is too large to fit in a col or row span.

    # Scan rows
    for r in range(9):
        for c in range(6):
            if not 2 <= len(Cands[r][c]) <= 4: continue
            for c1 in range(c+1, 7):
                if not 2 <= len(Cands[r][c1]) <= 4: continue
                for c2 in range(c1+1, 8):
                    if not 2 <= len(Cands[r][c2]) <= 4: continue
                    for c3 in range(c2+1, 9):
                        if not 2 <= len(Cands[r][c3]) <= 4: continue
                        D = Cands[r][c] | Cands[r][c1] | Cands[r][c2] | Cands[r][c3]
                        if len(D) == 4:
                            # An exposed quad is found
                            for c4 in set(range(9)) - {c, c1, c2, c3}:
                                if Grid[r][c4]: continue
                                Elims = Cands[r][c4] & D
                                if Elims:
                                    Cands[r][c4] -= D
                                    if Step.Outcome: Step.Outcome.append((P_SEP,))
                                    Step.Outcome.extend([[P_ROW, r], [P_COL, c4], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                            if Step.Outcome:  # Candidates were eliminated
                                Step.Method = T_EXPOSED_QUAD
                                Step.Outcome.append([P_END])
                                Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c1], [P_CON],
                                                [P_VAL, sorted(Cands[r][c2])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c2], [P_CON],
                                                [P_VAL, sorted(Cands[r][c3])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c3], [P_END]]
                                return 0
    # then scan the cols
    for c in range(9):
        for r in range(6):
            if not 2 <= len(Cands[r][c]) <= 4: continue
            for r1 in range(r+1, 7):
                if not 2 <= len(Cands[r1][c]) <= 4: continue
                for r2 in range(r1+1, 8):
                    if not 2 <= len(Cands[r2][c]) <= 4: continue
                    for r3 in range(r2+1, 9):
                        if not 2 <= len(Cands[r3][c]) <= 4: continue
                        D = Cands[r][c] | Cands[r1][c] | Cands[r2][c] | Cands[r3][c]
                        if len(D) == 4:
                            # An exposed quad is found
                            for r4 in set(range(9)) - {r, r1, r2, r3}:
                                if Grid[r4][c]: continue
                                Elims = Cands[r4][c] & D
                                if Elims:
                                    Cands[r4][c] -= D
                                    if Step.Outcome: Step.Outcome.append((P_SEP,))
                                    Step.Outcome.extend([[P_ROW, r4], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                            if Step.Outcome:  # Candidates were eliminated
                                Step.Method = T_EXPOSED_QUAD
                                Step.Outcome.append([P_END])
                                Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c], [P_CON],
                                                [P_VAL, sorted(Cands[r2][c])], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c], [P_CON],
                                                [P_VAL, sorted(Cands[r3][c])], [P_OP, OP_EQ], [P_ROW, r3], [P_COL, c], [P_END]]
                                return 0
    # the scan the blocks.
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            for rc in range(6):
                r = br+(rc//3); c = bc+(rc%3)
                if not 2 <= len(Cands[r][c]) <= 4: continue
                for rc1 in range(rc+1, 7):
                    r1 = br+(rc1//3); c1 = bc+(rc1%3)
                    if not 2 <= len(Cands[r1][c1]) <= 4: continue
                    for rc2 in range(rc1+1, 8):
                        r2 = br+(rc2//3); c2 = bc+(rc2%3)
                        if not 2 <= len(Cands[r2][c2]) <= 4: continue
                        for rc3 in range(rc2+1, 9):
                            r3 = br+(rc3//3); c3 = bc+(rc3%3)
                            if not 2 <= len(Cands[r3][c3]) <= 4: continue
                            D = Cands[r][c] | Cands[r1][c1] | Cands[r2][c2] | Cands[r3][c3]
                            if len(D) == 4:
                                # An exposed quad is found
                                for rc4 in set(range(9)) - {rc, rc1, rc2, rc3}:
                                    r4 = br+(rc4//3); c4 = bc+(rc4%3)
                                    if Grid[r4][c4]: continue
                                    Elims = Cands[r4][c4] & D
                                    if Elims:
                                        Cands[r4][c4] -= D
                                        if Step.Outcome: Step.Outcome.append((P_SEP,))
                                        Step.Outcome.extend([[P_ROW, r4], [P_COL, c4], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                                if Step.Outcome:
                                    Step.Method = T_EXPOSED_QUAD
                                    Step.Outcome.append([P_END])
                                    Step.Pattern = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ], [P_ROW, r], [P_COL, c], [P_CON],
                                                    [P_VAL, sorted(Cands[r1][c1])], [P_OP, OP_EQ], [P_ROW, r1], [P_COL, c1], [P_CON],
                                                    [P_VAL, sorted(Cands[r2][c2])], [P_OP, OP_EQ], [P_ROW, r2], [P_COL, c2], [P_CON],
                                                    [P_VAL, sorted(Cands[r3][c3])], [P_OP, OP_EQ], [P_ROW, r3], [P_COL, c3], [P_END]]
                                    return 0
    return -1

def tech_hidden_quads(Grid, Step, Cands, Method = T_UNDEF):
    # A hidden quad is where the union of four cells in a group contains the
    # same four candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those four cells that are not the
    #  four candidates, thereby exposing the hidden quad.

    for Cand0 in range(1, 7):
        for Cand1 in range(Cand0+1, 8):
            for Cand2 in range(Cand1+1, 9):
                for Cand3 in range(Cand2+1, 10):
                    # Scan rows
                    for r0 in range(9):
                        n0 = 0; C = []; U = set()
                        for c0 in range(9):
                            if Grid[r0][c0]: continue
                            X = Cands[r0][c0] & {Cand0, Cand1, Cand2, Cand3}
                            if not X: continue
                            if len(X) == 1: break
                            if n0 > 3: break
                            C.append((c0, X)); U |= X; n0 += 1
                        else:
                            if n0 != 4 or len(U) != 4: continue
                            # hidden quad found
                            for c0, X in C:
                                Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2, Cand3}
                                if Elims:
                                    Cands[r0][c0] = X
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END])
                                Step.Method = T_HIDDEN_QUAD
                                Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_ROW, r0], [P_COLX, C[0][0], C[1][0], C[2][0], C[3][0]], [P_END]]
                                return 0
                    # Scan cols
                    for c0 in range(9):
                        n0 = 0; R = []; U = set()
                        for r0 in range(9):
                            if Grid[r0][c0]: continue
                            X = Cands[r0][c0] & {Cand0, Cand1, Cand2, Cand3}
                            if not X: continue
                            if len(X) == 1: break
                            if n0 > 3: break
                            R.append((r0, X)); U |= X; n0 += 1
                        else:
                            if n0 != 4 or len(U) != 4: continue
                            # hidden trip found in r0
                            for r0, X in R:
                                Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2, Cand3}
                                if Elims:
                                    Cands[r0][c0] = X
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END])
                                Step.Method = T_HIDDEN_QUAD
                                Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_ROWX, R[0][0], R[1][0], R[2][0], R[3][0]], [P_COL, c0], [P_END]]
                                return 0
                    # scan boxes
                    for h0 in range(9):
                        br = (h0//3)*3; bc = (h0%3)*3
                        n0 = 0; B = []; U = set()
                        for b0 in range(9):
                            r0 = br + b0//3; c0 = bc + b0%3
                            if Grid[r0][c0]: continue
                            X = Cands[r0][c0] & {Cand0, Cand1, Cand2, Cand3}
                            if not X: continue
                            if len(X) == 1: break
                            if n0 > 3: break
                            B.append((b0, r0, c0, X)); U |= X; n0 += 1
                        else:
                            if n0 != 4 or len(U) != 4: continue
                            # found a hidden quad in block
                            for b0, r0, c0, X in B:
                                Elims = Cands[r0][c0] - {Cand0, Cand1, Cand2, Cand3}
                                if Elims:
                                    Cands[r0][c0] = X
                                    if Step.Outcome: Step.Outcome.append([P_SEP])
                                    Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, sorted(Elims)]])
                            if Step.Outcome:
                                Step.Outcome.append([P_END])
                                Step.Method = T_HIDDEN_QUAD
                                Step.Pattern = [[P_VAL, sorted(U)], [P_OP, OP_ABS], [P_BOX, h0], [P_POSX, B[0][0], B[1][0], B[2][0], B[3][0]], [P_END]]
                                return 0
    return -1
