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
                if len(Net.Odds) < 2 or len(Net.Evens) < 2: continue
                Pattern = []; Elims = {}
                if T_REMOTE_PAIR_T3 in Methods:  # Ccell see both an odd and even node. # perhaps has a higher likelihood of occurring than Type 2.
                    for r0 in range(9):
                        for c0 in range(9):
                            if Net.OddEven[r0][c0]: continue
                            Cand0 = sorted(Cands[r0][c0] & Net.Cands)
                            if Cand0:
                                Done = False
                                for re, ce in Net.Evens:
                                    Lke = how_ccells_linked(r0, c0, Cand0[0], re, ce, Cand0[0], Cands)
                                    if Lke:
                                        if Lke & LK_STRG: Lke |= LK_WKST
                                        for ro, co in Net.Odds:
                                            Lko = how_ccells_linked(r0, c0, Cand0[0], ro, co, Cand0[0], Cands)
                                            if Lko:
                                                if Lko & LK_STRG: Lko |= LK_WKST
                                                Pattern.append([[P_CON], [P_VAL, Cand0], [P_ROW, re], [P_COL, ce], [P_OP, token_link(Lke & 0x000f)],
                                                                [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lke & 0x000f)],
                                                                [P_VAL, Cand0], [P_ROW, ro], [P_COL, co]])
                                                K = str(r0)+str(c0)
                                                for Cand in Cand0:
                                                    if K in Elims.keys():
                                                        if Cand not in Elims[K]: Elims[K].append(Cand)
                                                    else: Elims[K] = [Cand]
                                                Done = True; break
                                    if Done: break
                    if Elims:
                        Step.Method = T_REMOTE_PAIR_T3
                        Cands1 = sorted(Net.Cands)
                        Step.Pattern = [[P_OP, OP_PARO], [P_VAL, Cands1[0]], [P_OP, OP_SLK], [P_VAL, Cands1[1]], [P_OP, OP_PARC], [P_OP, OP_PARO], [P_ROW, Net.Tree.r], [P_COL, Net.Tree.c]]
                        Step.NrLks += 1
                        walk_subnet(Net.Tree, Step)
                        Step.Pattern.append([P_OP, OP_PARC])
                        for Patt in Pattern:  Step.Pattern.extend(Patt)
                        Step.Pattern.append([P_END])
                        for K, Cands1 in Elims.items():
                            r = int(K[0]); c = int(K[1])
                            if Grid[r][c]: continue
                            Elim = Cands[r][c] & set(Cands1)
                            if Elim:
                                Cands[r][c] -= set(Cands1)
                                if Step.Outcome:  Step.Outcome.append([P_SEP])
                                Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elim]])
                        if Step.Outcome: Step.Outcome.append([P_END])
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
        Status = STATE()
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
            if Step.Method in {T_XY_CHAIN_T1, T_EVEN_XY_LOOP_T3}:
                for (r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1), (r2, c2, Cand2, Lk2) in Status.Pattern1:
                    Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)],
                                         [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_OP, token_link(Lk1 &0x000f)],
                                         [P_VAL, Cand2], [P_ROW, r2], [P_COL, c2]])
            elif Step.Method in {T_XY_CHAIN_T2, T_XY_CHAIN_T3}:
                for r0, c0, Cand0 in Status.Pattern1:
                    Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_OP, OP_PRES], [P_ROW, r0], [P_COL, c0]])
            elif Step.Method in {T_EVEN_XY_LOOP_T2}:
                for (r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1) in Status.Pattern1:
                    Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1]])
            Step.Pattern.append([P_END])
            Step.Outcome = []
            for r, c, Cand in Status.Plcmts:
                Grid[r][c] = Cand
                Cands[r][c].clear()
                discard_cand_from_peers(Cand, r, c, Cands)
                if Step.Outcome:  Step.Outcome.append([P_SEP])
                Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
            for K, Cands1 in Status.Elims.items():
                r = int(K[0]); c = int(K[1])
                if Grid[r][c]: continue
                Elim = Cands[r][c] & set(Cands1)
                if Elim:
                    Cands[r][c] -= set(Cands1)
                    if Step.Outcome:  Step.Outcome.append([P_SEP])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elim]])
            if Step.Outcome:
                Step.Outcome.append([P_END])
                return len(Status.Plcmts)
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
            for rx, cx, Candlx, Lkx in Child.Chain:  # Make sure found NL is not already in the chain.
                if rx == r1 and cx == c1: break
            else:
                if {T_EVEN_XY_LOOP_T2, T_EVEN_XY_LOOP_T3} & set(Methods):
                    Lk = how_ccells_linked(r1, c1, Candsl1[1], Child.Chain[0].r, Child.Chain[0].c, Child.Chain[0].Cand[0], Cands)
                    if Lk:  # XY-Loop found
                        if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
                        Status.Pattern = []
                        for i in range(len(Child.Chain)-1):
                            Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                        Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, Lk)])
                        Odds = []; Evens = []
                        for r, c, Cand, Lk in Child.Chain:
                            Evens.append((r, c, Cand[0])); Odds.append((r, c, Cand[1]))
                        if T_EVEN_XY_LOOP_T3 in Methods:  # Type 3: Ccell(s) see odd and even nodes - most likely outcome first for this pattern
                            Status.Pattern1 = []; Status.Plcmts = []; Status.Elims = {}
                            for r in range(9):
                                for c in range(9):
                                    for Cand in sorted(Cands[r][c]):
                                        Done = False
                                        if (r, c, Cand) in [*Evens, *Odds]: continue
                                        for re, ce, Cande in Evens:
                                            Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                                            if Lke:
                                                if Lke & LK_STRG: Lke |= LK_WKST
                                                for ro, co, Cando in Odds:
                                                    Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                                                    if Lko:
                                                        if Lko & LK_STRG: Lko |= LK_WKST
                                                        Status.Pattern1.append([NL(re, ce, Cande, Lke), NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                                        K = str(r) + str(c)
                                                        if K in Status.Elims.keys(): Status.Elims[K].append(Cand)
                                                        else: Status.Elims[K] = [Cand]
                                                        Status.Tech = T_EVEN_XY_LOOP_T3
                                                        Done = True; break
                                            if Done: break
                            if Status.Elims: return
                        if not Status.Elims and T_EVEN_XY_LOOP_T2 in Methods:  # All cands in cell see same parity nodes
                            # Status.Plcmts = []; Status.Elims = {}
                            for r in range(9):
                                for c in range(9):
                                    CandInChain = False
                                    for Cand in Cands[r][c]:
                                        if Cand in [*Evens, *Odds]: CandInChain = True; break
                                    if CandInChain: continue

                                    Status.Pattern1 = []
                                    for Cand in sorted(Cands[r][c]):  # All cands in a cell see even parity nodes
                                        for re, ce, Cande in Evens:
                                            Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                                            if Lke:
                                                if Lke & LK_STRG: Lke |= LK_WKST
                                                Status.Pattern1.append([NL(r, c, Cand, Lke), NL(re, ce, Cande, LK_NONE)])
                                                break
                                        else: break
                                    if Status.Pattern1 and len(Status.Pattern1) == len(Cands[r][c]):
                                        for r2, c2, Cand2 in Evens:
                                            K = str(r2)+str(c2)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                        Status.Plcmts = Odds
                                        Status.Tech = T_EVEN_XY_LOOP_T2
                                        return
                                    Status.Pattern1 = []
                                    for Cand in sorted(Cands[r][c]):  # All cands in a cell see odd parity nodes
                                        for ro, co, Cando in Odds:
                                            Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                                            if Lko:
                                                if Lko & LK_STRG: Lko |= LK_WKST
                                                Status.Pattern1.append([NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                                break
                                        else: break
                                    if Status.Pattern1 and len(Status.Pattern1) == len(Cands[r][c]):
                                        for r2, c2, Cand2 in Odds:
                                            K = str(r2)+str(c2)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                        Status.Plcmts = Evens
                                        Status.Tech = T_EVEN_XY_LOOP_T2
                                        return
                else:  # look for XY-Chains
                    # Status.Pattern = []
                    if T_XY_CHAIN_T1 in Methods and Child.Chain[0].Cand[0] == Candsl1[1]:  # same end candidate value.
                        Cand = Candsl1[1]; r2 = Child.Chain[0].r; c2 = Child.Chain[0].c
                        Status.Pattern1 = []; Status.Elims = {}
                        for r, c in cells_that_see_all_of([(r1, c1), (r2, c2)]):
                            if Cand in Cands[r][c]:
                                Lk1 = how_ccells_linked(r1, c1, Cand, r, c, Cand, Cands)
                                Lk2 = how_ccells_linked(r, c, Cand, r2, c2, Cand, Cands)
                                if Lk1 and Lk2:
                                    if Lk1 & LK_STRG: Lk1 |= LK_WKST
                                    if Lk2 & LK_STRG: Lk2 |= LK_WKST
                                    Status.Pattern1.append([NL(r1, c1, Cand, Lk1), NL(r, c, Cand, Lk2), NL(r1, c1, Cand, LK_NONE)])
                                    K = str(r)+str(c)
                                    if K in Status.Elims.keys(): Status.Elims[K].append(Cand)
                                    else: Status.Elims[K] = [Cand]
                        if Status.Elims:
                            Status.Tech = T_XY_CHAIN_T1
                            Status.Pattern = []
                            for i in range(len(Child.Chain)-1):
                                Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                            Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, LK_NONE)])
                            return
                    if cells_in_same_house(r1, c1, Child.Chain[0].r, Child.Chain[0].c):
                        if T_XY_CHAIN_T3 in Methods and Child.Chain[0].Cand == Candsl1:
                            r0 = Child.Chain[0].r; c0 = Child.Chain[0].c; Cand0 = Child.Chain[0].Cand[0]; Cand1 = Candsl[1]
                            Status.Pattern1.append((r0, c0, Cand1)); Status.Plcmts.append((r0, c0, Cand0))
                            Status.Pattern1.append((r1, c1, Cand0)); Status.Plcmts.append((r1, c1, Cand1))
                            Status.Elims = {}
                            Status.Tech  = T_XY_CHAIN_T3
                            Status.Pattern = []
                            for i in range(len(Child.Chain)-1):
                                Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                            Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, LK_NONE)])
                            return
                        if T_XY_CHAIN_T2 in Methods:
                            r0 = Child.Chain[0].r; c0 = Child.Chain[0].c; Cand0 = Child.Chain[0].Cand[0]; Cand1 = Candsl[1]
                            Status.Elims = {}
                            if (r0, c0) == (r1, c1):  # in same cell
                                Status.elims[str(r0) + str(c0)] = [Cands[r0][c0] - {Cand0, Cand1}]
                                Status.Pattern1 = [(r0, c0, sorted(Cands[r0][c0] - {Cand0, Cand1}))]
                            else:
                                if Cand1 in Cands[r0][c0]: Status.Pattern1.append((r0, c0, Cand1)); Status.Elims[str(r0)+str(c0)] = [Cand1]
                                if Cand0 in Cands[r1][c1]: Status.Pattern1.append((r1, c1, Cand0)); Status.Elims[Str(r1)+str(c1)] = [Cand0]
                            if Status.Elims:
                                Status.Tech = T_XY_CHAIN_T2
                                Status.Pattern = []
                                for i in range(len(Child.Chain)-1):
                                    Status.Pattern.append(NL(Child.Chain[i].r, Child.Chain[i].c, Child.Chain[i].Cand, Child.Chain[i+1].Lk))
                                Status.Pattern.extend([NL(Child.Chain[-1].r, Child.Chain[-1].c, Child.Chain[-1].Cand, Lk1), NL(r1, c1, Candsl1, LK_NONE)])
                                return
                # No possible eliminations, grow branches.
                Child.Children.append(TNODE(r1, c1, Candsl1, Lk1, [*Child.Chain, NL(r1, c1, Candsl1, Lk1)]))
