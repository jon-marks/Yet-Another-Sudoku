from copy import copy

from globals import *
from solve_utils import *

def tech_exposed_pairs(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # In any group (row, col or box), if any two cells have only the same two
    # candidates then we have found an exposed pair.  These candidates can be
    # eliminated from the balance of cells in that group.  If these two cell are
    # in the intersection of a box and a row or column, the we have a locked
    # exposed pair and the these candidates can be eliminated from the balance
    # of cells in the box and row/col.

    if Method != T_UNDEF and Method != T_EXPOSED_PAIR and Method != T_LOCKED_EXPOSED_PAIR: return -1

    # Scan the rows first.
    for r in range(9):
        for c in range(8):
            if len(Cands[r][c]) != 2:
                continue
            for c1 in range(c+1, 9):
                if Cands[r][c] != Cands[r][c1]:
                    continue
                # Found an exposed pair in the row. Could it perhaps
                # be a locked pair too?
                if Method == T_UNDEF or Method == T_LOCKED_EXPOSED_PAIR:
                    if (c//3) == (c1//3):  # both cells in same blk
                        # Yes, it is a locked pair too.
                        br = (r//3)*3
                        bc = (c//3)*3
                        for r2 in [br, br+1, br+2]:
                            for c2 in [bc, bc+1, bc+2]:
                                if len(Cands[r2][c2]) == 0:
                                    continue
                                if (r2 == r and c2 == c) or (r2 == r and c2 == c1):
                                    continue
                                for Cand in Cands[r][c]:
                                    if Cand in Cands[r2][c2]:
                                        Cands[r2][c2].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r2], [P_COL, c2],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r2][c2].add(Cand)
                if Step[P_OUTC]:
                    Step[P_TECH] = T_LOCKED_EXPOSED_PAIR
                else:
                    Step[P_TECH] = T_EXPOSED_PAIR
                for c2 in set(range(9)) - {c, c1}:
                    if len(Cands[r][c2]) == 0:
                        continue
                    for Cand in Cands[r][c]:
                        if Cand in Cands[r][c2]:
                            Cands[r][c2].discard(Cand)
                            if Step[P_OUTC]:
                                Step[P_OUTC].append([P_SEP, ])
                            Step[P_OUTC].extend([[P_ROW, r], [P_COL, c2],
                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                            if ElimCands is not None:
                                ElimCands[r][c2].add(Cand)
                if Step[P_OUTC]:  # Candidates were eliminated
                    Step[P_OUTC].append([P_END, ])
                    Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                    [P_ROW, r], [P_COL, c, c1], [P_END, ]]
                    return 0
    # then scan the cols.
    for c in range(9):
        for r in range(8):
            if len(Cands[r][c]) != 2:
                continue
            for r1 in range(r+1, 9):
                if Cands[r][c] != Cands[r1][c]:
                    continue
                # Found an exposed pair in the col. Could it perhaps
                # be a locked pair too?
                if Method == T_UNDEF or Method == T_LOCKED_EXPOSED_PAIR:
                    if (r//3) == (r1//3):  # both cells in same blk
                        # Yes, it is a locked pair too.
                        br = (r//3)*3
                        bc = (c//3)*3
                        for r2 in [br, br+1, br+2]:
                            for c2 in [bc, bc+1, bc+2]:
                                if len(Cands[r2][c2]) == 0:
                                    continue
                                if (r2 == r and c2 == c) or (r2 == r1 and c2 == c):
                                    continue
                                for Cand in Cands[r][c]:
                                    if Cand in Cands[r2][c2]:
                                        Cands[r2][c2].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append((P_SEP,))
                                        Step[P_OUTC].extend([[P_ROW, r2], [P_COL, c2],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r2][c2].add(Cand)
                if Step[P_OUTC]:
                    Step[P_TECH] = T_LOCKED_EXPOSED_PAIR
                else:
                    Step[P_TECH] = T_EXPOSED_PAIR
                for r2 in set(range(9)) - {r, r1}:
                    if len(Cands[r2][c]) == 0:
                        continue
                    if (r2 != r1) and (r2 != r):
                        for Cand in Cands[r][c]:
                            if Cand in Cands[r2][c]:
                                Cands[r2][c].discard(Cand)
                                if Step[P_OUTC]:
                                    Step[P_OUTC].append((P_SEP,))
                                Step[P_OUTC].extend([[P_ROW, r2], [P_COL, c],
                                                     [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if ElimCands is not None:
                                    ElimCands[r2][c].add(Cand)
                if Step[P_OUTC]:  # Candidates were eliminated
                    Step[P_OUTC].append([P_END, ])
                    Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                    [P_ROW, r, r1], [P_COL, c], [P_END, ]]
                    return 0
    # and finally scan the blocks.
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(8):
                r = br+(rc//3)
                c = bc+(rc%3)
                if len(Cands[r][c]) != 2:
                    continue
                for rc1 in range(rc+1, 9):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if Cands[r][c] != Cands[r1][c1]:
                        continue
                    # Found an exposed pair in a box, discard matching
                    # candidates from remaining cells in the box.
                    # Step[P_TECH] = T_EXPOSED_PAIR
                    for rc2 in set(range(9)) - {rc, rc1}:
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        if len(Cands[r2][c2]) == 0:
                            continue
                        for Cand in Cands[r][c]:
                            if Cand in Cands[r2][c2]:
                                Cands[r2][c2].discard(Cand)
                                if Step[P_OUTC]:
                                    Step[P_OUTC].append((P_SEP,))
                                Step[P_OUTC].extend([[P_ROW, r2], [P_COL, c2],
                                                     [P_OP, OP_ELIM], [P_VAL, Cand]])
                                if ElimCands is not None:
                                    ElimCands[r2][c2].add(Cand)
                    if Step[P_OUTC]:
                        Step[P_TECH] = T_EXPOSED_PAIR
                        Step[P_OUTC].append([P_END, ])
                        Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                        [P_ROW, r], [P_COL, c], [P_CON, ], [P_ROW, r1], [P_COL, c1],
                                        [P_END, ]]
                        return 0
    return -1

def tech_hidden_pairs(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # A hidden pair is where two cells in a group share the same two candidates
    # (out of all their candidates), which are not found elsewhere in the group.
    # That is the candidates of those two cells are limited to the pair of
    # candidates they share.  All other candidates in those two cells can be
    # eliminated, thereby exposing the pair.  Algorithmically, select two cells
    # in a group and subtract the union of the candidates from the remaining
    # cells from the two selected cells.  If there are the same two remaining
    # candidates in the selected cells, then a hidden pair has been found.

    if Method != T_UNDEF and Method != T_HIDDEN_PAIR: return -1

    # scan the rows first.
    for r in range(9):
        for c in range(8):
            if len(Cands[r][c]) < 2:
                continue
            for c1 in range(c+1, 9):
                if len(Cands[r][c1]) < 2:
                    continue
                D1 = copy(Cands[r][c])
                D2 = copy(Cands[r][c1])
                for c2 in set(range(9)) - {c, c1}:
                    D1 -= Cands[r][c2]
                    D2 -= Cands[r][c2]
                    if len(D1) < 2 or len(D2) < 2:
                        break
                else:
                    if D1 == D2:
                        # Found a hidden pair
                        # Step[P_TECH] = T_HIDDEN_PAIR
                        for c3 in [c, c1]:
                            for Cand in copy(Cands[r][c3]):
                                if Cand not in D1:
                                    Cands[r][c3].discard(Cand)
                                    if Step[P_OUTC]:
                                        Step[P_OUTC].append([P_SEP, ])
                                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c3],
                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    if ElimCands is not None:
                                        ElimCands[r][c3].add(Cand)
                        if Step[P_OUTC]:
                            D3 = sorted(D1)
                            Step[P_TECH] = T_HIDDEN_PAIR
                            Step[P_OUTC].append([P_END, ])
                            Step[P_PTRN] = [[P_VAL, D3], [P_OP, OP_CNT, 2], [P_ROW, r],
                                            [P_COL, c, c1], [P_END, ]]
                            return 0
    # then scan the cols
    for c in range(9):
        for r in range(8):
            if len(Cands[r][c]) < 2:
                continue
            for r1 in range(r+1, 9):
                if len(Cands[r1][c]) < 2:
                    continue
                D1 = copy(Cands[r][c])
                D2 = copy(Cands[r1][c])
                for r2 in set(range(9)) - {r, r1}:
                    D1 -= Cands[r2][c]
                    D2 -= Cands[r2][c]
                    if len(D1) < 2 or len(D2) < 2:
                        break
                else:
                    if D1 == D2:
                        # Found a hidden pair
                        for r3 in [r, r1]:
                            for Cand in copy(Cands[r3][c]):
                                if Cand not in D1:
                                    Cands[r3][c].discard(Cand)
                                    if Step[P_OUTC]:
                                        Step[P_OUTC].append([P_SEP, ])
                                    Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c],
                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    if ElimCands is not None:
                                        ElimCands[r3][c].add(Cand)
                        if Step[P_OUTC]:
                            D3 = sorted(D1)
                            Step[P_TECH] = T_HIDDEN_PAIR
                            Step[P_OUTC].append([P_END, ])
                            Step[P_PTRN] = [[P_VAL, D3], [P_OP, OP_CNT, 2],
                                            [P_ROW, r, r1], [P_COL, c], [P_END, ]]
                            return 0
    # then scan the blocks
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(8):
                r = br+(rc//3)
                c = bc+(rc%3)
                if len(Cands[r][c]) < 2:
                    continue
                for rc1 in range(rc+1, 9):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if len(Cands[r1][c1]) < 2:
                        continue
                    D1 = copy(Cands[r][c])
                    D2 = copy(Cands[r1][c1])
                    for rc2 in set(range(9)) - {rc, rc1}:
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        D1 -= Cands[r2][c2]
                        D2 -= Cands[r2][c2]
                        if len(D1) < 2 or len(D2) < 2:
                            break
                    else:
                        if D1 == D2:
                            # Found a hidden pair
                            # Step[P_TECH] = T_HIDDEN_PAIR
                            for r3, c3 in [(r, c), (r1, c1)]:
                                for Cand in copy(Cands[r3][c3]):
                                    if Cand not in D1:
                                        Cands[r3][c3].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c3],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r3][c3].add(Cand)
                            if Step[P_OUTC]:
                                D3 = sorted(D1)
                                Step[P_TECH] = T_HIDDEN_PAIR
                                Step[P_OUTC].append([P_END, ])
                                Step[P_PTRN] = [[P_VAL, D3], [P_OP, OP_CNT, 2], [P_BOX, (r//3)*3+c//3],
                                                [P_CON, ], [P_ROW, r], [P_COL, c],
                                                [P_CON, ], [P_ROW, r1], [P_COL, c1],
                                                [P_END, ]]
                                return 0
    return -1

def tech_exposed_triples(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # In any group (row, col or box) if any three empty cells have any
    # combination of only the same 3 candidates, then we have found an exposed
    # triple, and these three candidates can be eliminated from other cells.
    # Furthermore, if these three candidates are in the intersection of a box
    # and a row/col, this is a locked exposed triple and the candidates can be
    # eliminated from the other cells in that box too.

    if Method != T_UNDEF and Method != T_EXPOSED_TRIPLE and Method != T_LOCKED_EXPOSED_TRIPLE: return -1

    # Scan the rows first
    for r in range(9):
        for c in range(7):
            if not 2 <= len(Cands[r][c]) <= 3:
                continue
            for c1 in range(c+1, 8):
                if not 2 <= len(Cands[r][c1]) <= 3:
                    continue
                for c2 in range(c1+1, 9):
                    if not 2 <= len(Cands[r][c2]) <= 3:
                        continue
                    D = Cands[r][c] | Cands[r][c1] | Cands[r][c2]
                    if len(D) == 3:
                        # An exposed triple is found, is it a locked triple?
                        if Method == T_UNDEF or Method == T_LOCKED_EXPOSED_TRIPLE:
                            bc = c//3
                            if bc == c1//3 and bc == c2//3:
                                # Yes we have a locked exposed triple
                                br = (r//3)*3
                                bc *= 3
                                for r3 in [br, br+1, br+2]:
                                    for c3 in [bc, bc+1, bc+2]:
                                        if len(Cands[r3][c3]) == 0:
                                            continue
                                        if (r3 != r or c3 != c) \
                                                and (r3 != r or c3 != c1) \
                                                and (r3 != r or c3 != c2):
                                            for Cand in D:
                                                if Cand in Cands[r3][c3]:
                                                    Cands[r3][c3].discard(Cand)
                                                    if Step[P_OUTC]:
                                                        Step[P_OUTC].append((P_SEP,))
                                                    Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c3],
                                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                                    if ElimCands is not None:
                                                        ElimCands[r3][c3].add(Cand)
                        if Step[P_OUTC]:
                            Step[P_TECH] = T_LOCKED_EXPOSED_TRIPLE
                        else:
                            Step[P_TECH] = T_EXPOSED_TRIPLE
                        for c3 in set(range(9)) - {c, c1, c2}:
                            if len(Cands[r][c3]) == 0:
                                continue
                            for Cand in D:
                                if Cand in Cands[r][c3]:
                                    Cands[r][c3].discard(Cand)
                                    if Step[P_OUTC]:
                                        Step[P_OUTC].append((P_SEP,))
                                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c3],
                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    if ElimCands is not None:
                                        ElimCands[r][c3].add(Cand)
                        if Step[P_OUTC]:  # Candidates were eliminated
                            Step[P_OUTC].append([P_END, ])
                            Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c], [P_CON, ],
                                            [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c1], [P_CON, ],
                                            [P_VAL, sorted(Cands[r][c2])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c2], [P_END, ]]
                            return 0
    # then scan the cols
    for c in range(9):
        for r in range(7):
            if not 2 <= len(Cands[r][c]) <= 3:
                continue
            for r1 in range(r+1, 8):
                if not 2 <= len(Cands[r1][c]) <= 3:
                    continue
                for r2 in range(r1+1, 9):
                    if not 2 <= len(Cands[r2][c]) <= 3:
                        continue
                    D = Cands[r][c] | Cands[r1][c] | Cands[r2][c]
                    if len(D) == 3:
                        # An exposed triple is found, is it a locked triple?
                        if Method == T_UNDEF or Method == T_LOCKED_EXPOSED_TRIPLE:
                            br = r//3
                            if br == r1//3 and br == r2//3:
                                # Yes we have a locked exposed triple
                                br *= 3
                                bc = (c//3)*3
                                for r3 in [br, br+1, br+2]:
                                    for c3 in [bc, bc+1, bc+2]:
                                        if len(Cands[r3][c3]) == 0:
                                            continue
                                        if (r3 != r or c3 != c) \
                                                and (r3 != r1 or c3 != c) \
                                                and (r3 != r2 or c3 != c):
                                            for Cand in D:
                                                if Cand in Cands[r3][c3]:
                                                    Cands[r3][c3].discard(Cand)
                                                    if Step[P_OUTC]:
                                                        Step[P_OUTC].append((P_SEP,))
                                                    Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c3],
                                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                                    if ElimCands is not None:
                                                        ElimCands[r3][c3].add(Cand)
                        if Step[P_OUTC]:
                            Step[P_TECH] = T_LOCKED_EXPOSED_TRIPLE
                        else:
                            Step[P_TECH] = T_EXPOSED_TRIPLE
                        for r3 in set(range(9)) - {r, r1, r2}:
                            if len(Cands[r3][c]) == 0:
                                continue
                            for Cand in D:
                                if Cand in Cands[r3][c]:
                                    Cands[r3][c].discard(Cand)
                                    if Step[P_OUTC]:
                                        Step[P_OUTC].append((P_SEP,))
                                    Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c],
                                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                                    if ElimCands is not None:
                                        ElimCands[r3][c].add(Cand)
                        if Step[P_OUTC]:  # Candidates were eliminated
                            Step[P_OUTC].append([P_END, ])
                            Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                            [P_ROW, r], [P_COL, c], [P_CON, ],
                                            [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ],
                                            [P_ROW, r1], [P_COL, c], [P_CON, ],
                                            [P_VAL, sorted(Cands[r2][c])], [P_OP, OP_EQ],
                                            [P_ROW, r2], [P_COL, c], [P_END, ]]
                            return 0
    # the scan the blocks.
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(7):
                r = br+(rc//3)
                c = bc+(rc%3)
                if not 2 <= len(Cands[r][c]) <= 3:
                    continue
                for rc1 in range(rc+1, 8):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if not 2 <= len(Cands[r1][c1]) <= 3:
                        continue
                    for rc2 in range(rc1+1, 9):
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        if not 2 <= len(Cands[r2][c2]) <= 3:
                            continue
                        D = Cands[r][c] | Cands[r1][c1] | Cands[r2][c2]
                        if len(D) == 3:
                            # An exposed triple is found
                            for rc3 in set(range(9)) - {rc, rc1, rc2}:
                                r3 = br+(rc3//3)
                                c3 = bc+(rc3%3)
                                if len(Cands[r3][c3]) == 0:
                                    continue
                                for Cand in D:
                                    if Cand in Cands[r3][c3]:
                                        Cands[r3][c3].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append((P_SEP,))
                                        Step[P_OUTC].extend([[P_ROW, r3], [P_COL, c3],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r3][c3].add(Cand)
                            if Step[P_OUTC]:
                                Step[P_TECH] = T_EXPOSED_TRIPLE
                                Step[P_OUTC].append([P_END, ])
                                Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c], [P_CON, ],
                                                [P_VAL, sorted(Cands[r1][c1])], [P_OP, OP_EQ],
                                                [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                                [P_VAL, sorted(Cands[r2][c2])], [P_OP, OP_EQ],
                                                [P_ROW, r2], [P_COL, c2], [P_END, ]]
                                return 0
    return -1

def tech_hidden_triples(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # A hidden triple is where the union of three cells in a group contains the
    # same three candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those three cells that are not the
    # same three candidates, thereby exposing the hidden triple.

    if Method != T_UNDEF and Method != T_HIDDEN_TRIPLE: return -1

    # scan the rows first
    for r in range(9):
        for c in range(7):
            if len(Cands[r][c]) < 2:
                continue
            for c1 in range(c+1, 8):
                if len(Cands[r][c1]) < 2:
                    continue
                for c2 in range(c1+1, 9):
                    if len(Cands[r][c2]) < 2:
                        continue
                    D1 = copy(Cands[r][c])
                    D2 = copy(Cands[r][c1])
                    D3 = copy(Cands[r][c2])
                    for c3 in set(range(9)) - {c, c1, c2}:
                        D1 -= Cands[r][c3]
                        D2 -= Cands[r][c3]
                        D3 -= Cands[r][c3]
                        if len(D1) < 2 or len(D2) < 2 or len(D3) < 2:
                            break
                    else:
                        DT = sorted(D1 | D2 | D3)
                        if len(DT) == 3:
                            # found a hidden triple
                            # Step[P_TECH] = T_HIDDEN_TRIPLE
                            for c4 in [c, c1, c2]:
                                for Cand in copy(Cands[r][c4]):
                                    if Cand not in DT:
                                        Cands[r][c4].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r], [P_COL, c4],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r][c4].add(Cand)
                            if Step[P_OUTC]:
                                Step[P_TECH] = T_HIDDEN_TRIPLE
                                Step[P_OUTC].append([P_END, ])
                                for i, Cand in enumerate(DT):
                                    C = []
                                    if Cand in D1:
                                        C.append(c)
                                    if Cand in D2:
                                        C.append(c1)
                                    if Cand in D3:
                                        C.append(c2)
                                    if i:
                                        Step[P_PTRN].append([P_CON, ])
                                    Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(C)],
                                                         [P_ROW, r], [P_COL, C]])
                                Step[P_PTRN].append([P_END, ])
                                return 0
    # then scan the cols
    for c in range(9):
        for r in range(7):
            if len(Cands[r][c]) < 2:
                continue
            for r1 in range(r+1, 8):
                if len(Cands[r1][c]) < 2:
                    continue
                for r2 in range(r1+1, 9):
                    if len(Cands[r2][c]) < 2:
                        continue
                    D1 = copy(Cands[r][c])
                    D2 = copy(Cands[r1][c])
                    D3 = copy(Cands[r2][c])
                    for r3 in set(range(9)) - {r, r1, r2}:
                        D1 -= Cands[r3][c]
                        D2 -= Cands[r3][c]
                        D3 -= Cands[r3][c]
                        if len(D1) < 2 or len(D2) < 2 or len(D3) < 2:
                            break
                    else:
                        DT = sorted(D1 | D2 | D3)
                        if len(DT) == 3:
                            # found a hidden triple
                            # Step[P_TECH] = T_HIDDEN_TRIPLE
                            for r4 in [r, r1, r2]:
                                for Cand in copy(Cands[r4][c]):
                                    if Cand not in DT:
                                        Cands[r4][c].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append([P_SEP, ])
                                        Step[P_OUTC].extend([[P_ROW, r4], [P_COL, c],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r4][c].add(Cand)
                            if Step[P_OUTC]:
                                Step[P_OUTC].append([P_END, ])
                                Step[P_TECH] = T_HIDDEN_TRIPLE
                                for i, Cand in enumerate(DT):
                                    R = []
                                    if Cand in D1:
                                        R.append(r)
                                    if Cand in D2:
                                        R.append(r1)
                                    if Cand in D3:
                                        R.append(r2)
                                    if i:
                                        Step[P_PTRN].append([P_CON, ])
                                    Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(R)],
                                                         [P_ROW, R], [P_COL, c]])
                                Step[P_PTRN].append([P_END, ])
                                return 0
    # then scan the blocks
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(7):
                r = br+(rc//3)
                c = bc+(rc%3)
                if len(Cands[r][c]) < 2:
                    continue
                for rc1 in range(rc+1, 8):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if len(Cands[r1][c1]) < 2:
                        continue
                    for rc2 in range(rc1+1, 9):
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        if len(Cands[r2][c2]) < 2:
                            continue
                        D1 = copy(Cands[r][c])
                        D2 = copy(Cands[r1][c1])
                        D3 = copy(Cands[r2][c2])
                        for rc3 in set(range(9)) - {rc, rc1, rc2}:
                            r3 = br+(rc3//3)
                            c3 = bc+(rc3%3)
                            D1 -= Cands[r3][c3]
                            D2 -= Cands[r3][c3]
                            D3 -= Cands[r3][c3]
                            if len(D1) < 2 or len(D2) < 2 or len(D3) < 2:
                                break
                        else:
                            DT = sorted(D1 | D2 | D3)
                            if len(DT) == 3:
                                # found a hidden triple
                                for r4, c4 in [(r, c), (r1, c1), (r2, c2)]:
                                    for Cand in copy(Cands[r4][c4]):
                                        if Cand not in DT:
                                            Cands[r4][c4].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append([P_SEP, ])
                                            Step[P_OUTC].extend([[P_ROW, r4], [P_COL, c4],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands is not None:
                                                ElimCands[r4][c4].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_HIDDEN_TRIPLE
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = []
                                    for i, Cand in enumerate(DT):
                                        C = []
                                        if Cand in D1:
                                            C.append((r, c))
                                        if Cand in D2:
                                            C.append((r1, c1))
                                        if Cand in D3:
                                            C.append((r2, c2))
                                        if i:
                                            Step[P_PTRN].append([P_CON, ])
                                        Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(C)],
                                                             [P_BOX, (br//3)*3 + bc//3]])
                                        for (r4, c4) in C:
                                            Step[P_PTRN].extend([[P_CON, ], [P_ROW, r4], [P_COL, c4]])
                                    Step[P_PTRN].append([P_END, ])
                                    return 0
    return -1

def tech_exposed_quads(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # In any group (row, col or box) if any four empty cells have any
    # combination of only the same 4 candidates, then we have found an exposed
    # quad, and these four candidates can be eliminated from other cells in that
    # group.  It is not possible to have a locked exposed quad as four cells
    # is too large to fit in a col or row span.

    if Method != T_UNDEF and Method != T_EXPOSED_QUAD: return -1
    # Scan the rows first
    for r in range(9):
        for c in range(6):
            if not 2 <= len(Cands[r][c]) <= 4:
                continue
            for c1 in range(c+1, 7):
                if not 2 <= len(Cands[r][c1]) <= 4:
                    continue
                for c2 in range(c1+1, 8):
                    if not 2 <= len(Cands[r][c2]) <= 4:
                        continue
                    for c3 in range(c2+1, 9):
                        if not 2 <= len(Cands[r][c3]) <= 4:
                            continue
                        D = Cands[r][c] | Cands[r][c1] | Cands[r][c2] | Cands[r][c3]
                        if len(D) == 4:
                            # An exposed quad is found
                            for c4 in set(range(9)) - {c, c1, c2, c3}:
                                if len(Cands[r][c4]) == 0:
                                    continue
                                for Cand in D:
                                    if Cand in Cands[r][c4]:
                                        Cands[r][c4].discard(Cand)
                                        if Step[P_OUTC]: Step[P_OUTC].append((P_SEP,))
                                        Step[P_OUTC].extend([[P_ROW, r], [P_COL, c4],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None: ElimCands[r][c4].add(Cand)
                            if Step[P_OUTC]:  # Candidates were eliminated
                                Step[P_TECH] = T_EXPOSED_QUAD
                                Step[P_OUTC].append([P_END, ])
                                Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c], [P_CON, ],
                                                [P_VAL, sorted(Cands[r][c1])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c1], [P_CON, ],
                                                [P_VAL, sorted(Cands[r][c2])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c2], [P_CON, ],
                                                [P_VAL, sorted(Cands[r][c3])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c3], [P_END, ]]
                                return 0
    # then scan the cols
    for c in range(9):
        for r in range(6):
            if not 2 <= len(Cands[r][c]) <= 4:
                continue
            for r1 in range(r+1, 7):
                if not 2 <= len(Cands[r1][c]) <= 4:
                    continue
                for r2 in range(r1+1, 8):
                    if not 2 <= len(Cands[r2][c]) <= 4:
                        continue
                    for r3 in range(r2+1, 9):
                        if not 2 <= len(Cands[r3][c]) <= 4:
                            continue
                        D = Cands[r][c] | Cands[r1][c] | Cands[r2][c] | Cands[r3][c]
                        if len(D) == 4:
                            # An exposed quad is found
                            for r4 in set(range(9)) - {r, r1, r2, r3}:
                                if len(Cands[r4][c]) == 0:
                                    continue
                                for Cand in D:
                                    if Cand in Cands[r4][c]:
                                        Cands[r4][c].discard(Cand)
                                        if Step[P_OUTC]:
                                            Step[P_OUTC].append((P_SEP,))
                                        Step[P_OUTC].extend([[P_ROW, r4], [P_COL, c],
                                                             [P_OP, OP_ELIM], [P_VAL, Cand]])
                                        if ElimCands is not None:
                                            ElimCands[r4][c].add(Cand)
                            if Step[P_OUTC]:  # Candidates were eliminated
                                Step[P_TECH] = T_EXPOSED_QUAD
                                Step[P_OUTC].append([P_END, ])
                                Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                                [P_ROW, r], [P_COL, c], [P_CON, ],
                                                [P_VAL, sorted(Cands[r1][c])], [P_OP, OP_EQ],
                                                [P_ROW, r1], [P_COL, c], [P_CON, ],
                                                [P_VAL, sorted(Cands[r2][c])], [P_OP, OP_EQ],
                                                [P_ROW, r2], [P_COL, c], [P_CON, ],
                                                [P_VAL, sorted(Cands[r3][c])], [P_OP, OP_EQ],
                                                [P_ROW, r3], [P_COL, c], [P_END, ]]
                                return 0
    # the scan the blocks.
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(6):
                r = br+(rc//3)
                c = bc+(rc%3)
                if not 2 <= len(Cands[r][c]) <= 4:
                    continue
                for rc1 in range(rc+1, 7):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if not 2 <= len(Cands[r1][c1]) <= 4:
                        continue
                    for rc2 in range(rc1+1, 8):
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        if not 2 <= len(Cands[r2][c2]) <= 4:
                            continue
                        for rc3 in range(rc2+1, 9):
                            r3 = br+(rc3//3)
                            c3 = bc+(rc3%3)
                            if not 2 <= len(Cands[r3][c3]) <= 4:
                                continue
                            D = Cands[r][c] | Cands[r1][c1] | Cands[r2][c2] | Cands[r3][c3]
                            if len(D) == 4:
                                # An exposed quad is found
                                for rc4 in set(range(9)) - {rc, rc1, rc2, rc3}:
                                    r4 = br+(rc4//3)
                                    c4 = bc+(rc4%3)
                                    if len(Cands[r4][c4]) == 0:
                                        continue
                                    for Cand in D:
                                        if Cand in Cands[r4][c4]:
                                            Cands[r4][c4].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append((P_SEP,))
                                            Step[P_OUTC].extend([[P_ROW, r4], [P_COL, c4],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands is not None:
                                                ElimCands[r4][c4].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_EXPOSED_QUAD
                                    Step[P_OUTC].append([P_END, ])
                                    Step[P_PTRN] = [[P_VAL, sorted(Cands[r][c])], [P_OP, OP_EQ],
                                                    [P_ROW, r], [P_COL, c], [P_CON, ],
                                                    [P_VAL, sorted(Cands[r1][c1])], [P_OP, OP_EQ],
                                                    [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                                    [P_VAL, sorted(Cands[r2][c2])], [P_OP, OP_EQ],
                                                    [P_ROW, r2], [P_COL, c2], [P_CON, ],
                                                    [P_VAL, sorted(Cands[r3][c3])], [P_OP, OP_EQ],
                                                    [P_ROW, r3], [P_COL, c3], [P_END, ]]
                                    return 0
    return -1

def tech_hidden_quads(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # A hidden quad is where the union of four cells in a group contains the
    # same four candidates that are not found in any other cell in that group.
    # Here we can eliminate candidates from those four cells that are not the
    # same four candidates, thereby exposing the hidden quad.

    if Method != T_UNDEF and Method != T_HIDDEN_QUAD: return -1
    # scan the rows first
    for r in range(9):
        for c in range(6):
            if len(Cands[r][c]) < 2:
                continue
            for c1 in range(c+1, 7):
                if len(Cands[r][c1]) < 2:
                    continue
                for c2 in range(c1+1, 8):
                    if len(Cands[r][c2]) < 2:
                        continue
                    for c3 in range(c2+1, 9):
                        if len(Cands[r][c3]) < 2:
                            continue
                        D1 = copy(Cands[r][c])
                        D2 = copy(Cands[r][c1])
                        D3 = copy(Cands[r][c2])
                        D4 = copy(Cands[r][c3])
                        for c4 in set(range(9)) - {c, c1, c2, c3}:
                            D1 -= Cands[r][c4]
                            D2 -= Cands[r][c4]
                            D3 -= Cands[r][c4]
                            D4 -= Cands[r][c4]
                            if len(D1) < 2 or len(D2) < 2 or len(D3) < 2 or len(D4) < 2:
                                break
                        else:
                            DT = sorted(D1 | D2 | D3 | D4)
                            if len(DT) == 4:
                                # found a hidden quad
                                for c5 in [c, c1, c2, c3]:
                                    for Cand in copy(Cands[r][c5]):
                                        if Cand not in DT:
                                            Cands[r][c5].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append([P_SEP, ])
                                            Step[P_OUTC].extend([[P_ROW, r], [P_COL, c5],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands is not None:
                                                ElimCands[r][c5].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_HIDDEN_QUAD
                                    Step[P_OUTC].append([P_END, ])
                                    for i, Cand in enumerate(DT):
                                        C = []
                                        if Cand in D1:
                                            C.append(c)
                                        if Cand in D2:
                                            C.append(c1)
                                        if Cand in D3:
                                            C.append(c2)
                                        if Cand in D4:
                                            C.append(c3)
                                        if i:
                                            Step[P_PTRN].append([P_CON, ])
                                        Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(C)],
                                                             [P_ROW, r], [P_COL, C]])
                                    Step[P_PTRN].append([P_END, ])
                                    return 0
    # then scan the cols
    for c in range(9):
        for r in range(6):
            if len(Cands[r][c]) < 2:
                continue
            for r1 in range(r+1, 7):
                if len(Cands[r1][c]) < 2:
                    continue
                for r2 in range(r1+1, 8):
                    if len(Cands[r2][c]) < 2:
                        continue
                    for r3 in range(r2+1, 9):
                        if len(Cands[r3][c]) < 2:
                            continue
                        D1 = copy(Cands[r][c])
                        D2 = copy(Cands[r1][c])
                        D3 = copy(Cands[r2][c])
                        D4 = copy(Cands[r3][c])
                        for r4 in set(range(9))-{r, r1, r2, r3}:
                            D1 -= Cands[r4][c]
                            D2 -= Cands[r4][c]
                            D3 -= Cands[r4][c]
                            D4 -= Cands[r4][c]
                            if len(D1) < 2 or len(D2) < 2 or len(D3) < 2 or len(D4) < 2:
                                break
                        else:
                            DT = D1 | D2 | D3 | D4
                            if len(DT) == 4:
                                # found a hidden quad
                                # Step[P_TECH] = T_HIDDEN_QUAD
                                for r5 in [r, r1, r2, r3]:
                                    for Cand in copy(Cands[r5][c]):
                                        if Cand not in DT:
                                            Cands[r5][c].discard(Cand)
                                            if Step[P_OUTC]:
                                                Step[P_OUTC].append([P_SEP, ])
                                            Step[P_OUTC].extend([[P_ROW, r5], [P_COL, c],
                                                                 [P_OP, OP_ELIM], [P_VAL, Cand]])
                                            if ElimCands is not None:
                                                ElimCands[r5][c].add(Cand)
                                if Step[P_OUTC]:
                                    Step[P_TECH] = T_HIDDEN_QUAD
                                    Step[P_OUTC].append([P_END, ])
                                    for i, Cand in enumerate(DT):
                                        R = []
                                        if Cand in D1:
                                            R.append(r)
                                        if Cand in D2:
                                            R.append(r1)
                                        if Cand in D3:
                                            R.append(r2)
                                        if Cand in D4:
                                            R.append(r3)
                                        if i:
                                            Step[P_PTRN].append([P_CON, ])
                                        Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(R)],
                                                             [P_ROW, R], [P_COL, c]])
                                        Step[P_PTRN].append([P_END, ])
                                    return 0
    # then scan the blocks
    for br in [0, 3, 6]:
        for bc in [0, 3, 6]:
            for rc in range(6):
                r = br+(rc//3)
                c = bc+(rc%3)
                if len(Cands[r][c]) < 2:
                    continue
                for rc1 in range(rc+1, 7):
                    r1 = br+(rc1//3)
                    c1 = bc+(rc1%3)
                    if len(Cands[r1][c1]) < 2:
                        continue
                    for rc2 in range(rc1+1, 8):
                        r2 = br+(rc2//3)
                        c2 = bc+(rc2%3)
                        if len(Cands[r2][c2]) < 2:
                            continue
                        for rc3 in range(rc2+1, 9):
                            r3 = br+(rc3//3)
                            c3 = bc+(rc3%3)
                            if len(Cands[r3][c3]) < 2:
                                continue
                            D1 = copy(Cands[r][c])
                            D2 = copy(Cands[r1][c1])
                            D3 = copy(Cands[r2][c2])
                            D4 = copy(Cands[r3][c3])
                            for rc4 in set(range(9)) - {rc, rc1, rc2, rc3}:
                                r4 = br+(rc4//3)
                                c4 = bc+(rc4%3)
                                D1 -= Cands[r4][c4]
                                D2 -= Cands[r4][c4]
                                D3 -= Cands[r4][c4]
                                D4 -= Cands[r4][c4]
                                if len(D1) < 2 or len(D2) < 2 or len(D3) < 2 or len(D4) < 2:
                                    break
                            else:
                                DT = D1 | D2 | D3 | D4
                                if len(DT) == 4:
                                    # found a hidden quad
                                    # Step[P_TECH] = T_HIDDEN_QUAD
                                    for r5, c5 in [(r, c), (r1, c1), (r2, c2), (r3, c3)]:
                                        for Cand in copy(Cands[r5][c5]):
                                            if Cand not in DT:
                                                Cands[r5][c5].discard(Cand)
                                                if Step[P_OUTC]:
                                                    Step[P_OUTC].append([P_SEP, ])
                                                Step[P_OUTC].extend([[P_ROW, r5], [P_COL, c5],
                                                                     [P_OP, OP_ELIM], [P_VAL, Cand]])
                                                if ElimCands is not None:
                                                    ElimCands[r5][c5].add(Cand)
                                    if Step[P_OUTC]:
                                        Step[P_TECH] = T_HIDDEN_QUAD
                                        Step[P_OUTC].append([P_END, ])
                                        Step[P_PTRN] = []
                                        for i, Cand in enumerate(DT):
                                            C = []
                                            if Cand in D1:
                                                C.append((r, c))
                                            if Cand in D2:
                                                C.append((r1, c1))
                                            if Cand in D3:
                                                C.append((r2, c2))
                                            if Cand in D4:
                                                C.append((r3, c3))
                                            if i:
                                                Step[P_PTRN].append([P_CON, ])
                                            Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_CNT, len(C)],
                                                                 [P_BOX, (br//3)*3 + bc//3]])
                                            for (r5, c5) in C:
                                                Step[P_PTRN].extend([[P_CON, ], [P_ROW, r5], [P_COL, c5]])
                                        Step[P_PTRN].append([P_END, ])
                                        return 0
    return -1
