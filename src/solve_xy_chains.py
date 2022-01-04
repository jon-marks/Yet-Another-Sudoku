from copy import deepcopy

from globals import *
from solve_utils import *

REV = 0
FWD  = 1

class XYCUC:
    def __init__(self):
        self.XY  = []    # XY-chain or XY-loop being built
        self.OE  = []    # Other end of the XY-Chain/loop
        self.UC  = []    # list of used cells in the XY-Chain/loop
        self.EL  = []    # Ccells to eliminate if an XY Chain can be made.


def tech_remote_pairs(Grid, Step, Cands, Method = T_UNDEF):

    if Method != T_UNDEF and Method != T_REMOTE_PAIR: return -2

    class RPNE:  # Remote Pair node element
        def __init__(self, r = -1, c = -1, AltLk = -1, ConnNodes = None):
            self.r = r
            self.c = c
            self.AltLk = AltLk
            self.ConnNodes = [] if ConnNodes is None else ConnNodes

    class RPBVLE:  # Remote Pair Bi-Value Net lists element, BVList = [RPBVLE, ...]
        def __init__(self, RPCands = None, RPN = None):
            self.RPCands = set() if RPCands is None else RPCands
            self.RPNoList = [] if RPN is None else [RPN, ]
            self.RPNeList = []

    # build a list of bi-value cells.
    BVL0 = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2:
                for RPBVLElem in BVL0:
                    if Cands[r][c] == RPBVLElem.RPCands:
                        RPBVLElem.RPNoList.append(RPNE(r, c))
                        break
                else: BVL0.append(RPBVLE(Cands[r][c], RPNE(r, c)))

    for BVL in BVL0:
        if len(BVL.RPNoList) < 4: continue

        for i in range(len(BVL.RPNoList)-1):
            Ni = BVL.RPNoList[i]
            if Ni.AltLk >= 0: continue
            Ni.AltLk = 0
            for j in range(i+1, len(BVL.RPNoList)):
                Nj = BVL.RPNoList[j]
                if Nj.AltLk >= 0: continue
                if Ni.r == Nj.r or Ni.c == Nj.c or (Ni.r//3 == Nj.r//3 and Ni.c//3 == Nj.c//3):
                    Ni.AltLk = 0; Nj.AltLk = 1
                    Ni.ConnNodes.append(Nj)
                    BVL.RPNeList.append([Ni, Nj])
                    _next_net_node(BVL, Ni, REV)
                    _next_net_node(BVL, Nj, FWD)
            if BVL.RPNeList and len(BVL.RPNeList[-1]) > 3:
                if _remote_pair_elims(BVL, Cands, Step): return 0
    return -1

def _next_net_node(BVL, Ni, Dir = FWD):

    for Nj in BVL.RPNoList:
        if Nj.AltLk >= 0: continue
        if Ni.r == Nj.r or Ni.c == Nj.c or (Ni.r//3 == Nj.r//3 and Ni.c//3 == Nj.c//3):
            Nj.AltLk = (Ni.AltLk+1) & 0x01
            if Dir == FWD:
                Ni.ConnNodes.append(Nj)
                BVL.RPNeList[-1].append(Nj)
                _next_net_node(BVL, Nj, FWD)
            else:
                Nj.ConnNodes.append(Ni)
                BVL.RPNeList[-1].insert(0, Nj)
                _next_net_node(BVL, Nj, REV)

def _remote_pair_elims(BVL, Cands, Step):

    CandI = set()
    for r in range(9):
        for c in range(9):
            CandI = Cands[r][c] & BVL.RPCands
            if CandI:
                Found1Alt = -1
                for N in BVL.RPNeList[-1]:
                    if (r, c) != (N.r, N.c) and (r == N.r or c == N.c or (r//3 == N.r//3 and c//3 == N.c//3)):  # If CandI is not part of the net
                        if Found1Alt == -1: Found1Alt = N.AltLk
                        elif Found1Alt != N.AltLk:
                            #  Found CandI that can be eliminated.
                            Cands[r][c] -= CandI
                            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                            Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, CandI]])
    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Step[P_TECH] = T_REMOTE_PAIR
        Cand1, Cand2 = sorted(BVL.RPCands)
        Step[P_PTRN] = [[P_OP, OP_PARO], [P_VAL, Cand1], [P_OP, OP_SLK], [P_VAL, Cand2], [P_OP, OP_PARC], [P_OP, OP_PARO]]
        # N = BVL.RPNeList[-1][0]
        walk_subnets(BVL.RPNeList[-1][0], Step[P_PTRN])
        Step[P_PTRN].append([P_OP, OP_PARC])
        return True
    return False

def walk_subnets(N, Ptrn):

    while N:
        if Ptrn[-1] != [P_OP, OP_PARO] and Ptrn[-1] != [P_CON, ]: Ptrn.append([P_OP, OP_WSLK])
        Ptrn.extend([[P_ROW, N.r], [P_COL, N.c]])
        NrNodes = len(N.ConnNodes)
        if NrNodes == 0: break
        if NrNodes == 1: N = N.ConnNodes[0]; continue
        #  else:  NrNodes > 1
        Ptrn.extend([[P_OP, OP_WSLK], [P_OP, OP_PARO]])
        for N0 in N.ConnNodes:
            if Ptrn[-1] != [P_OP, OP_PARO]: Ptrn.append([P_CON, ])
            walk_subnets(N0, Ptrn)
        Ptrn.append([P_OP, OP_PARC])
        break

def tech_xy_chains(Grid, Step, Cands, Method = T_UNDEF):
    # 1. Build a list of BV cells.
    # 2. Search the BV list for 2 cells with common candidates not in the same house.
    # 3. If those common candidates result in an elimination, attempt to build an XY- chain out of
    #    the cells in the BV list.

    if Method != T_UNDEF and not (Method == T_XY_CHAIN or Method == T_Y_WING): return -2

    BVL, XYC0 = _find_xy_chain_starts(Cands)
    while XYC0:
        XYC1 = []
        for X in XYC0:
            # Find a BV cell to add to the XY chain being built and see if it can connect to the OE (other end)
            for BVC in BVL:
                for Cell in X.UC:
                    if Cell.r == BVC.r and Cell.c == BVC.c: break
                else:  # BVC is not in the UC list.
                    if X.XY[-1].Cand not in BVC.Cands: continue
                    LkT, LkH = how_ccells_linked(X.XY[-1].r, X.XY[-1].c, X.XY[-1].Cand, BVC.r, BVC.c, X.XY[-1].Cand, Cands)
                    if LkT == LK_NONE: continue
                    # BVC is linked to XY, connect it.
                    X1 = deepcopy(X)
                    X1.XY[-1] = NODE(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, LK_WEAK if LkT == LK_WEAK else LK_WKST)
                    X1.XY.extend([NODE(BVC.r, BVC.c, X1.XY[-1].Cand, LK_STRG), NODE(BVC.r, BVC.c, (BVC.Cands ^ {X1.XY[-1].Cand}).pop(), -1)])
                    # Does this newly added BVC connect to the OE.
                    LkT, LkH = how_ccells_linked(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, X1.OE[0].r, X1.OE[0].c, X1.OE[0].Cand, Cands)
                    if LkT == LK_NONE:
                        X1.UC.append(CELL(BVC.r, BVC.c))
                        XYC1.append(X1)
                    else:
                        X1.XY[-1] = NODE(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, LK_WEAK if LkT == LK_WEAK else LK_WKST)
                        X1.XY.extend(X.OE)
                        if _xy_chain_elims(X1, Cands, Step): return 0
        XYC0 = XYC1
    return -1

def tech_xy_loops(Grid, Step, Cands, Method = T_UNDEF):

    if Method != T_UNDEF and Method != T_XY_LOOP: return -2

    BVL, XYL0 = _find_xy_loop_starts(Cands)
    while XYL0:
        XYL1 = []
        for X in XYL0:
            for BVC in BVL:
                for Cell in X.UC:
                    if Cell.r == BVC.r and Cell.c == BVC.c: break
                else:  # BVC is not in the UC list
                    if X.XY[-1].Cand not in BVC.Cands: continue
                    LkT, LkH = how_ccells_linked(X.XY[-1].r, X.XY[-1].c, X.XY[-1].Cand, BVC.r, BVC.c, X.XY[-1].Cand, Cands)
                    if LkT == LK_NONE: continue
                    # BVC is linked to XY, connect it.
                    X1 = deepcopy(X)
                    X1.XY[-1] = NODE(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, LK_WEAK if LkT == LK_WEAK else LK_WKST)
                    X1.XY.extend([NODE(BVC.r, BVC.c, X1.XY[-1].Cand, LK_STRG), NODE(BVC.r, BVC.c, (BVC.Cands ^ {X1.XY[-1].Cand}).pop(), -1)])
                    # Does this newly added BVC connect to the OE.
                    LkT, LkH = how_ccells_linked(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, X1.OE[0].r, X1.OE[0].c, X1.OE[0].Cand, Cands)
                    if LkT == LK_NONE:
                        X1.UC.append(CELL(BVC.r, BVC.c))
                        XYL1.append(X1)
                    else:
                        X1.XY[-1] = NODE(X1.XY[-1].r, X1.XY[-1].c, X1.XY[-1].Cand, LK_WEAK if LkT == LK_WEAK else LK_WKST)
                        X1.XY.extend(X.OE)
                        if _xy_loop_elims(X1, Cands, Step): return 0
        XYL0 = XYL1
    return -1

def _find_xy_chain_starts(Cands):

    BVL = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2: BVL.append(BVCELL(r, c, Cands[r][c]))

    lenBVL = len(BVL)
    XYCStarts = []
    for i in range(lenBVL-1):
        for j in range(i+1, lenBVL):
            UC = []  # Used cells
            # EL = []  # Eliminated ccells
            for Cand in sorted(BVL[i].Cands & BVL[j].Cands):
                UC = [CELL(BVL[i].r, BVL[i].c), CELL(BVL[j].r, BVL[j].c)]
                EL = []  # Eliminated ccells
                for r0, c0 in cells_that_see_all_of([(BVL[i].r, BVL[i].c), (BVL[j].r, BVL[j].c)]):
                    if CELL(r0, c0) not in UC and Cand in Cands[r0][c0]: EL.append(CCELL(r0, c0, Cand))
                if EL:
                    X = XYCUC()
                    X.XY.extend([NODE(BVL[i].r, BVL[i].c, Cand, LK_STRG),
                                 NODE(BVL[i].r, BVL[i].c, (BVL[i].Cands ^ {Cand}).pop(), -1)])
                    X.OE.extend([NODE(BVL[j].r, BVL[j].c, (BVL[j].Cands ^ {Cand}).pop(), LK_STRG),
                                 NODE(BVL[j].r, BVL[j].c, Cand, LK_NONE)])
                    X.UC = UC
                    X.EL = EL
                    XYCStarts.append(deepcopy(X))
    return BVL, XYCStarts

def _find_xy_loop_starts(Cands):

    BVL = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2:  BVL.append(BVCELL(r, c, Cands[r][c]))

    lenBVL = len(BVL)
    XYLStarts = []
    for i in range(lenBVL-1):
        for j in range(i+1, lenBVL):
            UC = []
            for Cand in sorted(BVL[i].Cands & BVL[j].Cands):
                UC = [CELL(BVL[i].r, BVL[i].c), CELL(BVL[j].r, BVL[j].c)]
                LkT, LkH = how_ccells_linked(BVL[i].r, BVL[i].c, Cand, BVL[j].r, BVL[j].c, Cand, Cands)
                if LkT == LK_NONE: continue
                X = XYCUC()
                X.XY.extend([NODE(BVL[i].r, BVL[i].c, Cand, LK_STRG),
                             NODE(BVL[i].r, BVL[i].c, (BVL[i].Cands ^ {Cand}).pop(), -1)])
                X.OE.extend([NODE(BVL[j].r, BVL[j].c, (BVL[j].Cands ^ {Cand}).pop(), LK_STRG),
                             NODE(BVL[j].r, BVL[j].c, Cand, LK_WEAK if LkT == LK_WEAK else LK_WKST),
                             NODE(BVL[i].r, BVL[i].c, Cand, LK_NONE)])
                X.UC = UC
                XYLStarts.append(deepcopy(X))
    return BVL, XYLStarts

def _xy_chain_elims(X, Cands, Step):

    for Cc in X.EL:
        Cands[Cc.r][Cc.c].discard(Cc.Cand)
        if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
        Step[P_OUTC].extend([[P_ROW, Cc.r], [P_COL, Cc.c], [P_OP, OP_ELIM], [P_VAL, Cc.Cand]])
    Step[P_OUTC].append([P_END, ])
    Step[P_TECH] = T_Y_WING if len(X.XY) == 6 else T_XY_CHAIN
    Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + len(X.XY)//2 * LK_DIFF
    i = 0
    while 1:
        Step[P_PTRN].extend([[P_OP, OP_PARO], [P_VAL, X.XY[i].Cand], [P_OP, OP_SLK], [P_VAL, X.XY[i+1].Cand], [P_OP, OP_PARC],
                             [P_ROW, X.XY[i].r], [P_COL, X.XY[i].c]])
        if X.XY[i+1].Lk == LK_NONE: Step[P_PTRN].append([P_END, ]); break
        Step[P_PTRN].append([P_OP, OP_WLK if X.XY[i+1].Lk == LK_WEAK else OP_WSLK])
        i += 2
    return True

def _xy_loop_elims(X, Cands, Step):

    for i in range(len(X.XY)):
        if X.XY[i].Lk & LK_WEAK:  # captures both LK_WEAK and LK_WKST
            r = X.XY[i].r; c = X.XY[i].c; Cand = X.XY[i].Cand
            if r == X.XY[i+1].r:  # house is a row
                for c in sorted(set(range(9)) - {c, X.XY[i+1].c}):
                    if Cand in Cands[r][c]:
                        Cands[r][c].discard(Cand)
                        if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                        Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
            elif c == X.XY[i+1].c:  # house is a col
                for r in sorted(set(range(9))-{r, X.XY[i+1].r}):
                    if Cand in Cands[r][c]:
                        Cands[r][c].discard(Cand)
                        if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                        Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])

            if r//3  == X.XY[i+1].r//3 and c//3 == X.XY[i+1].c//3:  # house is a box, can also overlap with row or col.
            # else:  # house is a box
                for rb in range((r//3)*3, 3):
                    for cb in range((c//3)*3, 3):
                        if (rb == r and cb == c) or (rb == X.XY[i+1].r and cb == X.XY[i+1].c): continue
                        if Cand in Cands[rb][cb]:
                            Cands[rb][cb].discard(Cand)
                            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                            Step[P_OUTC].extend([[P_ROW, rb], [P_COL, cb], [P_OP, OP_ELIM], [P_VAL, Cand]])
    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Step[P_TECH] = T_XY_LOOP
        Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + len(X.XY)//2 * LK_DIFF
        i = 0
        while 1:
            Step[P_PTRN].extend([[P_OP, OP_PARO], [P_VAL, X.XY[i].Cand], [P_OP, OP_SLK], [P_VAL, X.XY[i+1].Cand], [P_OP, OP_PARC],
                                 [P_ROW, X.XY[i].r], [P_COL, X.XY[i].c]])
            Step[P_PTRN].append([P_OP, OP_WLK if X.XY[i+1].Lk == LK_WEAK else OP_WSLK])
            if X.XY[i+2].Lk == LK_NONE:
                Step[P_PTRN].extend([[P_VAL, X.XY[0].Cand], [P_ROW, X.XY[0].r], [P_COL, X.XY[0].c], [P_END, ]])
                break
            i += 2
        return True
    return False

