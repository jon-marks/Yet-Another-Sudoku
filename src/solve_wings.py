

from globals import *
from solve_utils import *



def tech_y_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # Find a cell with 2 cands.  This is cell BC which cands Cb, Cc.
    # Then look, NS, then EW then in the box for AB.  If AB is found, then look
    # in the other "directions" for AC.

    if Method != T_UNDEF and Method != T_Y_WING: return -1
    for r0 in range(9):
        for c0 in range(9):
            if len(Cands[r0][c0]) == 2:
                #  Found a possible BC, with cands Cb and Cc.  look for AB.
                for Cb in Cands[r0][c0]:
                    # Look along the column (north to south) for AB from BC
                    for r1 in sorted(set(range(9)) - {r0}):
                        if len(Cands[r1][c0]) == 2 and Cb in Cands[r1][c0]:
                            # Found a possible AB with cands Ca and Cb, scan the
                            # remaining directions (EW, box) for AC.
                            Ca = (Cands[r1][c0] - {Cb}).pop()
                            Cc = (Cands[r0][c0] - {Cb}).pop()
                            # Look West to east.
                            for c1 in sorted(set(range(9)) - {c0}):
                                if Cands[r1][c1] == {Ca, Cc}:
                                    # found an Y-Wing
                                    if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, r1, c0, r1, c1,
                                                             Cands, ElimCands, Step):
                                        return 0
                            # Else look in the box.
                            # but first make sure r1 is not in the same box as r0
                            rb = r1//3
                            if rb != r0//3:
                                rb *= 3
                                cb = (c0//3)*3
                                for rb1 in sorted({rb, rb+1, rb+2} - {r0}):
                                    for cb1 in sorted({cb, cb+1, cb+2} - {c0}):
                                        if Cands[rb1][cb1] == {Ca, Cc}:
                                            # found an Y-Wing
                                            if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, r1, c0, rb1, cb1,
                                                                     Cands, ElimCands, Step):
                                                return 0
                    # Look for AB in the row (east to west) from BC
                    for c1 in sorted(set(range(9)) - {c0}):
                        if len(Cands[r0][c1]) == 2 and Cb in Cands[r0][c1]:
                            # found a possible AB with cands Ca and Cb, scan the
                            # remaining directions (NS, box) for AC
                            Ca = (Cands[r0][c1] - {Cb}).pop()
                            Cc = (Cands[r0][c0] - {Cb}).pop()
                            # Look north to south.
                            for r1 in sorted(set(range(9)) - {r0}):
                                if Cands[r1][c1] == {Ca, Cc}:
                                    # found an Y-Wing
                                    if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, r0, c1, r1, c1,
                                                             Cands, ElimCands, Step):
                                        return 0
                            # Else look in the box but first make sure c1 is not
                            # in the same box as c0
                            cb = c1//3
                            if cb != c0//3:
                                cb *= 3
                                rb = (r0//3)*3
                                for cb1 in sorted({cb, cb+1, cb+2} - {c0}):
                                    for rb1 in sorted({rb, rb+1, rb+2} - {r0}):
                                        if Cands[rb1][cb1] == {Ca, Cc}:
                                            # found an Y-wing
                                            if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, r0, c1, rb1, cb1,
                                                                     Cands, ElimCands, Step):
                                                return 0
                    # look in the box for AB from BC
                    rb = (r0//3)*3
                    cb = (c0//3)*3
                    for rb1 in [rb, rb+1, rb+2]:
                        for cb1 in [cb, cb+1, cb+2]:
                            if rb1 != r0 or cb1 != c0:
                                if len(Cands[rb1][cb1]) == 2 and Cb in Cands[rb1][cb1]:
                                    # found a possible AB, scan the remaining directions
                                    # NS or EW for AC.
                                    Ca = (Cands[rb1][cb1] -{Cb}).pop()
                                    Cc = (Cands[r0][c0] - {Cb}).pop()
                                    # look NS for AC if BC and AB  are not in the same column.
                                    if c0 != cb1:
                                        for r1 in sorted(set(range(9)) - {rb1}):
                                            if Cands[r1][cb1] == {Ca, Cc}:
                                                # found an Y-Wing.
                                                if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, rb1, cb1, r1, cb1,
                                                                         Cands, ElimCands, Step):
                                                    return 0
                                    # look EW for AC if BC and AB are not in the same raw.
                                    if r0 != rb1:
                                        for c1 in sorted(set(range(9)) - {cb1}):
                                            if Cands[rb1][c1] == {Ca, Cc}:
                                                # found an Y-Wing.
                                                if _elim_cands_in_y_wing(Ca, Cb, Cc, r0, c0, rb1, cb1, rb1, c1,
                                                                         Cands, ElimCands, Step):
                                                    return 0
    return -1

def tech_w_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_W_WING: return -1
    return _tech_w_wings(Grid, Step, Cands, ElimCands, AIC = 1)

def tech_kraken_w_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_W_WING: return -1
    return _tech_w_wings(Grid, Step, Cands, ElimCands, AIC = 2)

def _tech_w_wings(Grid, Step, Cands, ElimCands = None, AIC = 1):
    # Defined by two bi-value cells with the same candidates that cannot
    # directly "see each other, but are connected by a strong link on one of the
    # candidates.  Any other cells with the other candidate value that both
    # bi-value cells see, can eliminate the other candidate value.

    # scan the grid looking for bi-value cells.
    BVList = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2:
                BVList.append([r, c, sorted(Cands[r][c])])
    if AIC: AIC = 2
    else: AIC = 1
    if len(BVList) > 1:
        BVList = sorted(sorted(BVList, key = lambda a: a[2][1]), key = lambda a: a[2][0])
        for i in range(len(BVList)-1):
            r1, c1, BVCand1 = BVList[i]
            for j in range(i+1, len(BVList)):
                r2, c2, BVCand2 = BVList[j]

                if BVCand1 != BVCand2 or cells_in_same_house(r1, c1, r2, c2): continue
                # Here we have a pair of identical bi-value cells that are not
                # in the same house (because list is sorted on cands, can break
                # when cands are no longer equal
                #
                # Attempt to build a chain on each of the values.  For all links
                # branching out of both BV cells, see if the other ends of the
                # link form a strong link.
                Cand1, Cand2 = BVCand1
                for Cand, Candx in zip([Cand1, Cand2], [Cand2, Cand1]):
                    Nodes = are_ccells_weakly_linked(r1, c1, Cand, r2, c2, Cand, Cands, AIC = AIC)
                    if not Nodes: continue
                    for r0, c0 in cells_seen_by_both(r1, c1, r2, c2):
                        if Candx in Cands[r0][c0]:
                            Cands[r0][c0].discard(Candx)
                            if Step[P_OUTC]:
                                Step[P_OUTC].append([P_SEP, ])
                            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0],
                                                 [P_OP, OP_ELIM], [P_VAL, Candx]])
                            if ElimCands is not None:
                                ElimCands[r0][c0].add(Candx)
                    if Step[P_OUTC]:
                        Lks = len(Nodes) - 1
                        Step[P_TECH] = T_W_WING if Lks <= 3 else T_W_WING_AIC
                        Step[P_DIFF] = T[T_W_WING][T_DIFF] + (Lks - 3) * AIC_LK_DIFF
                        Step[P_OUTC].append([P_END, ])
                        Chain = []
                        for (r, c, Cand0, Lk) in Nodes:
                            if Lk == -1:
                                Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c]])
                            else:
                                Chain.extend([[P_VAL, Cand0], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
                        Step[P_COND] = [[P_VAL, Cand1, Cand2], [P_OP, OP_EQ],
                                        [P_ROW, r1], [P_COL, c1], [P_CON, ],
                                        [P_ROW, r2], [P_COL, c2], [P_SEP, ]]
                        Step[P_COND].extend(Chain)
                        Step[P_COND].append([P_END, ])
                        return 0
    return -1

def tech_xyz_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):

    if Method != T_UNDEF and Method != T_XYZ_WING: return -1

    return -1

def tech_wxyz_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):

    if Method != T_UNDEF and Method != T_XYZ_WING: return -1

    return -1


def _elim_cands_in_y_wing(Ca, Cb, Cc, Rbc, Cbc, Rab, Cab, Rac, Cac, Cands, ElimCands, Step):

    for r0, c0 in cells_seen_by_both(Rbc, Cbc, Rac, Cac):
        if Cc in Cands[r0][c0]:
            Cands[r0][c0].discard(Cc)
            if Step[P_OUTC]:
                Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cc]])
            if ElimCands is not None:
                ElimCands[r0][c0].add(Cc)
    if Step[P_OUTC]:
        Step[P_TECH] = T_Y_WING
        Step[P_OUTC].append([P_END, ])
        Step[P_COND] = [[P_VAL, Cb, Cc], [P_OP, OP_EQ], [P_ROW, Rbc], [P_COL, Cbc], [P_CON, ],
                        [P_VAL, Ca, Cb], [P_OP, OP_EQ], [P_ROW, Rab], [P_COL, Cab], [P_CON, ],
                        [P_VAL, Ca, Cc], [P_OP, OP_EQ], [P_ROW, Rac], [P_COL, Cac], [P_END, ]]
        return True
    return False
