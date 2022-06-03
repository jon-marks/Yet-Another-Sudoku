from globals import *
from solve_utils import *

class NET:
    def __init__(self, Cands = None, NNode = None):
        self.Cands = Cands
        self.Odds = []
        self.Evens = []
        self.Tree = NNode
        self.OddEven = [[None for c in range(9)] for r in range(9)]

class NNODE:  # Net Node
    def __init__(self, r = -1, c = -1, Children = None):
        self.r = r; self.c = c
        self.Children = Children if Children else []

def tech_remote_pairs(Grid, Step, Cands, Methods):

    CellConsidered = [[False for c in range(9)] for r in range(9)]
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) == 2:
                if CellConsidered[r][c]: continue
                else: CellConsidered[r][c] = True
                Net = NET(Cands[r][c], NNODE(r, c))
                Net.OddEven[r][c] = Lvl = 0
                Net.Evens.append((r, c))
                next_net_level(Net, Net.Tree, True, True, True, CellConsidered, Cands, Lvl+1)
                if len(Net.Odds) > 1 and len(Net.Evens) > 1:  # possibility of remote pair eliminations
                    Elims = []
                    for r0 in range(9):
                        for c0 in range(9):
                            if Net.OddEven[r0][c0] is None and Cands[r0][c0] & Net.Cands:
                                for (rOdd, cOdd) in Net.Odds:
                                    if rOdd == r0 or cOdd == c0 or (rOdd//3 == r0//3 and cOdd//3 == c0//3):  # odd Net Node seen
                                        for (rEven, cEven) in Net.Evens:
                                            if rEven == r0 or cEven == c0 or (rEven//3 == r0//3 and cEven//3 == c0//3):  #
                                                Elims.append((r0, c0, Cands[r0][c0] & Net.Cands))
                                                break
                                        else: continue
                                        break
                    if Elims:
                        Step.Method = T_REMOTE_PAIR
                        Cands1 = sorted(Net.Cands)
                        Step.Pattern = [[P_OP, OP_PARO], [P_VAL, Cands1[0]], [P_OP, OP_SLK], [P_VAL, Cands1[1]], [P_OP, OP_PARC], [P_OP, OP_PARO], [P_ROW, Net.Tree.r], [P_COL, Net.Tree.c]]
                        Step.NrLks += 1
                        walk_subnet(Net.Tree, Step)
                        Step.Pattern.extend([[P_OP, OP_PARC], [P_END, ]])
                        for (r0, c0, ElimCands) in Elims:
                            Cands[r0][c0] -= ElimCands
                            if Step.Outcome: Step.Outcome.append([P_SEP, ])
                            Step.Outcome.extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, ElimCands]])
                        Step.Outcome.append([P_END, ])
                        return 0
    return -1

def next_net_level(Net, NNode, Row, Col, Box, CellConsidered, Cands, Lvl):

    if Row:
        for c in range(9):
            if c == NNode.c: continue
            if Cands[NNode.r][c] == Net.Cands and Net.OddEven[NNode.r][c] is None:
                CellConsidered[NNode.r][c] = True
                Net.OddEven[NNode.r][c] = Lvl
                if Lvl & 0x01: Net.Odds.append((NNode.r, c))
                else: Net.Evens.append((NNode.r, c))
                NNode.Children.append(NNODE(NNode.r, c))
                next_net_level(Net, NNode.Children[-1], False, True, True, CellConsidered, Cands, Lvl+1)
                break
    if Col:
        for r in range(9):
            if r == NNode.r: continue
            if Cands[r][NNode.c] == Net.Cands and Net.OddEven[r][NNode.c] is None:
                CellConsidered[r][NNode.c] = True
                Net.OddEven[r][NNode.c] = Lvl
                if Lvl & 0x01: Net.Odds.append((r, NNode.c))
                else: Net.Evens.append((r, NNode.c))
                NNode.Children.append(NNODE(r, NNode.c))
                next_net_level(Net, NNode.Children[-1], True, False, True, CellConsidered, Cands, Lvl+1)
                break
    if Box:
        for b in range(9):
            r = (NNode.r//3)*3 + b//3; c = (NNode.c//3)*3 + b%3
            if r == NNode.r or c == NNode.c: continue
            if Cands[r][c] == Net.Cands and Net.OddEven[r][c] is None:
                CellConsidered[r][c] = True
                Net.OddEven[r][c] = Lvl
                if Lvl & 0x01: Net.Odds.append((r, c))
                else: Net.Evens.append((r, c))
                NNode.Children.append(NNODE(r, c))
                next_net_level(Net, NNode.Children[-1], True, True, False, CellConsidered, Cands, Lvl+1)

def walk_subnet(NNode, Step):
    NrChildren = len(NNode.Children)
    if not NrChildren: return
    if NrChildren > 1: Step.Pattern.append([P_OP, OP_BRCO])
    First = True
    for Child in NNode.Children:
        if First:  First = False
        else: Step.Pattern.append([P_CON, ])
        Step.Pattern.extend([[P_OP, OP_WSLK], [P_ROW, Child.r], [P_COL, Child.c]])
        Step.NrLks += 1
        walk_subnet(Child, Step)
    if NrChildren > 1: Step.Pattern.append([P_OP, OP_BRCC])


def tech_xy_chains(Grid, Step, Cands, Methods):
    # By convention, Candsl lists are always ordered entering cand followed by leaving cand

    Forest = []
    for r in range(9):
        for c in range(9):
            if len(Cands[r][c]) != 2: continue
            Candsl = sorted(Cands[r][c])
            for r1, c1, Candsl1, Lk1 in list_bv_cells_linked_to(r, c, Candsl[1], Cands):
                if Lk1 & LK_STRG: Lk1 |= LK_WKST
                Forest.append(TREE(r, c, Candsl, None, TNODE(r1, c1, Candsl1, Lk1, [NL(r, c, Candsl, LK_NONE), NL(r1, c1, Candsl1, Lk1)])))
            for r1, c1, Candsl1, Lk1 in list_bv_cells_linked_to(r, c, Candsl[0], Cands):
                if Lk1 & LK_STRG: Lk1 |= LK_WKST
                Forest.append(TREE(r, c, [Candsl[1], Candsl[0]], None, TNODE(r1, c1, Candsl1, Lk1, [NL(r, c, [Candsl[1], Candsl[0]], LK_NONE), NL(r1, c1, Candsl1, Lk1)])))
    # all saplings planted.
    while Forest:
        Culls = set()
        Status = STATUS()
        for Tree in Forest:
            find_next_xy_child_nodes(Tree.Branch, Cands, 1, Tree, Methods, Status)
            if Status.Tech != T_UNDEF: break
            if not Tree.Branch.Children: Culls.add(Tree)
        if Status.Tech != T_UNDEF:
            Step.Method = Status.Tech
            Step.NrLks = Step.NrGrpLks = 0
            Step.Pattern = []; Step.Outcome = []
            for r, c, Candl, Lk in Status.Pattern:
                Step.Pattern.extend([[P_OP, OP_PARO], [P_VAL, Candl[0]], [P_OP, OP_SLK], [P_VAL, Candl[1]], [P_OP, OP_PARC], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk & 0x000f)]])
                Step.NrLks += 1
            Step.Pattern.append([P_END, ])
            if Status.Tech == T_DC_IBVC_XY_CHAIN:
                n = 0
                for r, c, Cand in Status.Outcome:
                    n += 1
                    Grid[r][c] = Cand
                    Cands[r][c].clear()
                    discard_cand_from_peers(Cand, r, c, Cands)
                    if Step.Outcome: Step.Outcme.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
                Step.Outcome.append([P_END, ])
                return n
            else:
                for r, c, Cand in Status.Outcome:
                    Cands[r][c].discard(Cand)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                Step.Outcome.append([P_END, ])
            return 0
        for Tree in Culls: Forest.remove(Tree)
    return -1

def find_next_xy_child_nodes(Child, Cands, Lvl, Tree, Methods, Status):

    if Child.Children:
        Prunes = set()
        for GChild in Child.Children:
            find_next_xy_child_nodes(GChild, Cands, Lvl+1, Tree, Methods, Status)
            if Status.Tech != T_UNDEF: return  # chain found, return with haste
            if not GChild.Children: Prunes.add(GChild)
        for GChild in Prunes: Child.Children.remove(GChild)
    else:  # at the leaves
        for r1, c1, Candsl1, Lk1 in list_bv_cells_linked_to(Child.r, Child.c, Child.Cand[1], Cands):
            for rx, cx, Candlx, Lkx in Child.Chain:
                if rx == r1 and cx == c1: break
            else:
                Lk = how_ccells_linked(r1, c1, Candsl1[1], Child.Chain[0].r, Child.Chain[0].c, Child.Chain[0].Cand[0], Cands)
                if Lk:  # XY-Loop found
                    if T_XY_LOOP in Methods:
                        if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
                        Status.Pattern = []
                        for i in range(len(Child.Chain)-1):
                            Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                        Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, Lk)])
                        Status.Outcome = []
                        for i in range(len(Status.Pattern)-1):
                            if Status.Pattern[i].Lk & 0x000f == LK_WEAK:
                                Status.Outcome.extend(link_elims(Status.Pattern[i].r, Status.Pattern[i].c, Status.Pattern[i].Cand[1],
                                                                 Status.Pattern[i+1].r, Status.Pattern[i+1].c, Status.Pattern[i+1].Cand[0],
                                                                 Cands, False))
                        if Lk & 0x000f == LK_WEAK:
                            Status.Outcome.extend(link_elims(Status.Pattern[-1].r, Status.Pattern[-1].c, Status.Pattern[-1].Cand[1],
                                                             Status.Pattern[0].r, Status.Pattern[0].c, Status.Pattern[0].Cand[0],
                                                             Cands, False))
                        if Status.Outcome:
                            Status.Tech = T_XY_LOOP
                            return
                #
                # if Lvl > 1:
                #     if T_XY_LOOP in Methods:
                #         Lk = how_ccells_linked(r1, c1, Candsl1[1], Child.Chain[0].r, Child.Chain[0].c, Child.Chain[0].Cand[0], Cands)
                #         if Lk:  # XY-Loop found
                #             if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
                #             Status.Pattern = []
                #             for i in range(len(Child.Chain)-1):
                #                 Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                #             Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, Lk)])
                #             Status.Outcome = []
                #             for i in range(len(Status.Pattern)-1):
                #                 if Status.Pattern[i] & 0x000f == LK_WEAK:
                #                     Status.Outcome.extend(link_elims(Status.Pattern[i].r, Status.Pattern[i].c, Status.Pattern[i].Cand[1],
                #                             Status.Pattern[i+1].r, Status.Pattern[i+1].c, Status.Pattern[i+1].Cand[0],
                #                             Cands, GrpLks))
                #             if Status.Pattern[-1].Lk & 0x000f == LK_WEAK:
                #                 Status.Outcome.extend(link_elims(Status.Pattern[-1].r, Status.Pattern[-1].c, Status.Pattern[-1].Cand[1],
                #                         Status.Pattern[0].r, Status.Pattern[0].c, Status.Pattern[0].Cand[0],
                #                         Cands, GrpLks))
                #             if Status.Outcome:
                #                 Status.Tech = T_XY_LOOP
                #                 return
                else:  # look for XY-Chains
                    Status.Outcome = []; Status.Tech = T_UNDEF
                    if Child.Chain[0].Cand[0] == Candsl1[1]:  # same end value.
                        for r2, c2 in cells_that_see_all_of([(r1, c1), (Child.Chain[0].r, Child.Chain[0].c)]):
                            if Candsl1[1] in Cands[r2][c2]:  Status.Outcome.append((r2, c2, Candsl1[1]))
                        if Status.Outcome and T_SC_XY_CHAIN in Methods: Status.Tech = T_SC_XY_CHAIN
                    elif cells_in_same_house(r1, c1, Child.Chain[0].r, Child.Chain[0].c, False):  # different end value candidates in same house.
                        if T_DC_IBVC_XY_CHAIN in Methods \
                                and not(r1 == Child.Chain[0].r and c1 == Child.Chain[0].c) \
                                and Cands[r1][c1] == Cands[Child.Chain[0].r][Child.Chain[0].c]: Status.Tech = T_DC_IBVC_XY_CHAIN
                        if Status.Tech != T_UNDEF:
                            Status.Outcome = [(Child.Chain[0].r, Child.Chain[0].c, Child.Chain[0].Cand[0]), (r1, c1, Candsl1[1])]
                        elif T_DC_XY_CHAIN in Methods and not(r1== Child.Chain[0].r and c1 == Child.Chain[0].c):
                            if Candsl1[1] in Cands[Child.Chain[0].r][Child.Chain[0].c]: Status.Outcome.append((Child.Chain[0].r, Child.Chain[0].c, Candsl1[1]))
                            if Child.Chain[0].Cand[0] in Cands[r1][c1]: Status.Outcome.append((r1, c1, Child.Chain))
                    if Status.Tech != T_UNDEF and Status.Outcome:
                        Status.Pattern = []
                        for i in range(len(Child.Chain)-1):
                            Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                        if Lk1 & LK_STRG: Lk1 = (Lk1 & 0x01f0) | LK_WKST
                        Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, LK_NONE)])
                        return
                    else: Status.Tech = T_UNDEF; Status.Outcome = []
                    # if T_SC_XY_CHAIN in Methods and Child.Chain[0].Cand[0] == Candsl1[1]:  # same candidate chain ends
                    #     for rx, cx in cells_that_see_all_of([(r1, c1), (Child.Chain[0].r, Child.Chain[0].c)]):
                    #         if Candsl1[1] in Cands[rx][cx]: Status.Outcome.append((rx, cx, Candsl1[1]))
                    #     if Status.Outcome: Status.Tech = T_SC_XY_CHAIN
                    # elif T_DC_IBVC_XY_CHAIN in Methods and (Child.Chain[0].r == r1 or Child.Chain[0].c == c1 or (Child.Chain[0].r//3 == r1//3 and Child.Chain[0].c//3 == c1//3)) \
                    #         and len(Cands[r1][c1]) == 2 and Cands[Child.Chain[0].r][Child.Chain[0].c] == Cands[r1][c1]:  # Identical BV cells in same house
                    #     Status.Outcome = [(Child.Chain[0].r, Child.Chain[0].c, Child.Chain[0].Cand[0]), (r1, c1, Candsl1[1])]
                    #     if Status.Outcome: Status.Tech = T_DC_IBVC_XY_CHAIN
                    # if Status.Outcome:
                    #     Status.Pattern = []
                    #     for i in range(len(Child.Chain)-1):
                    #         Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                    #     if Lk1 & LK_STRG: Lk1 = (Lk1 & 0x01f0) | LK_WKST
                    #     Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, LK_NONE)])
                    #     return
                # No possible eliminations, grow branches.
                Child.Children.append(TNODE(r1, c1, Candsl1, Lk1, [*Child.Chain, NL(r1, c1, Candsl1, Lk1)]))
