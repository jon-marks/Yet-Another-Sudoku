from globals import *
from solve_utils import *

class TREE:
    def __init__(self, Trunk = None):
        self.Odds = []
        self.Evens = []
        self.Trunk = Trunk

def tech_strong_linked_nets(Grid, Step, Cands, Methods):

    SLNodes = {}
    for Cand in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in list_all_cand_strong_links(Cand, Cands):
            Hash = str(Cand0)+str(r0)+str(c0)
            if Hash not in SLNodes:
                SLNodes[Hash] = TNODE(r0, c0, Cand0, Lk0)
            SLNodes[Hash].Children.append(TNODE(r1, c1, Cand1, Lk1))

    NodesConsidered = set()
    for Hash, Trunk in SLNodes.items():
        if Hash not in NodesConsidered:
            NodesConsidered.add(Hash)
            Tree = TREE(TNODE(Trunk.r, Trunk.c, Trunk.Cand))
            Tree.Evens = [(Trunk.r, Trunk.c, Trunk.Cand)]
            grow_sln(Tree, Tree.Trunk, Trunk.Children, NodesConsidered, SLNodes, 1)
            # How productive is this tree?
            Pattern = []
            lenEvens = len(Tree.Evens); lenOdds = len(Tree.Odds)
            if lenEvens < 2 or lenOdds < 2: continue  # must be at least two odd and two even nodes
            Elims = {}; Plcmts = []
            if T_STRONG_LINKED_NET_T1 in Methods:
                # 2 Even nodes see each other
                for i in range(lenEvens-1):
                    r0, c0, Cand0 = Tree.Evens[i]
                    for j in range(i+1, lenEvens):
                        r1, c1, Cand1 = Tree.Evens[j]
                        Lk = how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands)
                        if Lk:
                            if Lk & LK_STRG: Lk |= Lk_WKST
                            Pattern = [[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1]]
                            for r2, c2, Cand2 in Tree.Evens:
                                K = str(r2)+str(c2)
                                if K in Elims.keys(): Elims[K].append(Cand2)
                                else: Elims[K] = [Cand2]
                            Plcmts = Tree.Odds
                            Step.Method = T_STRONG_LINKED_NET_T1
                            break
                    if Elims: break
                if not Elims:
                    # 2 odd nodes see each other
                    for i in range(lenOdds-1):
                        r0, c0, Cand0 = Tree.Odds[i]
                        for j in range(i+1, lenOdds):
                            r1, c1, Cand1 = Tree.Odds[j]
                            Lk = how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands)
                            if Lk:
                                if Lk & LK_STRG: Lk |= Lk_WKST
                                Pattern = [[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1]]
                                for r2, c2, Cand2 in Tree.Odds:
                                    K = str(r2)+str(c2)
                                    if K in Elims.keys(): Elims[K].append(Cand2)
                                    else: Elims[K] = [Cand2]
                                Plcmts = Tree.Evens
                                Step.Method = T_STRONG_LINKED_NET_T1
                                break
                        if Elims: break
            if not Elims and T_STRONG_LINKED_NET_T2 in Methods:
                Links = []
                for r in range(9):
                    for c in range(9):
                        Links = []  # All cands in cell see even parity nodes
                        for Cand in Cands[r][c]:
                            if (r, c, Cand) in Tree.Evens: break
                            for re, ce, Cande in Tree.Evens:
                                Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                                if Lke:
                                    if Lke & LK_STRG: Lke |= LK_WKST
                                    Links.append([NL(r, c, Cand, Lke), NL(re, ce, Cande, LK_NONE)])
                                    break
                            else: break
                        if Links and len(Links) == len(Cands[r][c]):
                            for r2, c2, Cand2 in Tree.Evens:
                                K = str(r2)+str(c2)
                                if K in Elims.keys(): Elims[K].append(Cand2)
                                else: Elims[K] = [Cand2]
                            Plcmts = Tree.Odds
                        else:
                            Links = []  # All cands in cell see odd parity nodes
                            for Cand in Cands[r][c]:
                                if (r, c, Cand) in Tree.Odds: break
                                for ro, co, Cando in Tree.Odds:
                                    Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                                    if Lko:
                                        if Lko & LK_STRG: Lko |= LK_WKST
                                        Links.append([NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                        break
                                else: break
                            if Links and len(Links) == len(Cands[r][c]):
                                for r2, c2, Cand2 in Tree.Odds:
                                    K = str(r2)+str(c2)
                                    if K in Elims.keys(): Elims[K].append(Cand2)
                                    else: Elims[K] = [Cand2]
                                Plcmts = Tree.Evens
                        if Elims:
                            for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in Links:
                                if Pattern: Pattern.append([P_CON])
                                Pattern.extend([[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1]])
                                Step.Method = T_STRONG_LINKED_NET_T2
                            break
                    if Elims: break
            if not Elims and T_STRONG_LINKED_NET_T3 in Methods:
                # look for cells that are not part of the net that can see both an odd and even node.
                Pattern = []
                for r in range(9):
                    for c in range(9):
                        for Cand in sorted(Cands[r][c]):
                            Done = False
                            if (r, c, Cand) in [*Tree.Evens, *Tree.Odds]: continue
                            for re, ce, Cande in Tree.Evens:
                                Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                                if Lke:
                                    if Lke & LK_STRG: Lke |= LK_WKST
                                    for ro, co, Cando in Tree.Odds:
                                        Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                                        if Lko:
                                            if Lko & LK_STRG: Lko |= LK_WKST
                                            if Pattern:  Pattern.append([P_CON])
                                            Pattern.extend([[P_VAL, Cando], [P_ROW, re], [P_COL, ce], [P_OP, token_link(Lke & 0x000f)], [P_VAL, Cand], [P_ROW, r], [P_COL, c],
                                                            [P_OP, token_link(Lko & 0x000f)], [P_VAL, Cando], [P_ROW, ro], [P_COL, co]])
                                            K = str(r)+str(c)
                                            if K in Elims.keys():
                                                if Cand not in Elims[K]: Elims[K].append(Cand)
                                            else: Elims[K] = [Cand]
                                            Step.Method = T_STRONG_LINKED_NET_T3
                                            Done = True; break
                                if Done: break
            Step.Outcome = []
            for r, c, Cand in Plcmts:
                Grid[r][c] = Cand
                Cands[r][c].clear()
                discard_cand_from_peers(Cand, r, c, Cands)
                if Step.Outcome:  Step.Outcome.append([P_SEP])
                Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
            for K, Cands1 in Elims.items():
                r = int(K[0]); c = int(K[1])
                if Grid[r][c]: continue
                Elim = Cands[r][c] & set(Cands1)
                if Elim:
                    Cands[r][c] -= set(Cands1)
                    if Step.Outcome:  Step.Outcome.append([P_SEP])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elim]])
            if Step.Outcome:
                Step.Outcome.append([P_END])
                Step.Pattern = [[P_VAL, Tree.Trunk.Cand], [P_ROW, Tree.Trunk.r], [P_COL, Tree.Trunk.c]]
                Step.NrLks += 1
                climb_branch(Tree.Trunk, Step)
                if Pattern: Step.Pattern = [*Step.Pattern, [P_CON], *Pattern]
                Step.Pattern.append([P_END])
                return len(Plcmts)
    return -1

def climb_branch(TNode, Step):

    nChildren = len(TNode.Children)
    if nChildren == 0: return
    if nChildren >= 1: Step.Pattern.append([P_OP, OP_SLK])
    if nChildren > 1: Step.Pattern.append([P_OP, OP_BRCO])
    First = True
    for Child in TNode.Children:
        if First: First = False
        else: Step.Pattern.append([P_CON])
        Step.Pattern.extend([[P_VAL, Child.Cand], [P_ROW, Child.r], [P_COL, Child.c]])
        Step.NrLks +=1
        climb_branch(Child, Step)
    if nChildren > 1: Step.Pattern.append([P_OP, OP_BRCC])

def grow_sln(Tree, TNode, SLNChildren, NodesConsidered, SLNodes, Lvl):

    for SLNC in SLNChildren:
        Hash = str(SLNC.Cand) + str(SLNC.r) + str(SLNC.c)
        if Hash in NodesConsidered: continue
        NodesConsidered.add(Hash)
        if Hash not in SLNodes.keys(): continue
        if Lvl & 0x01: Tree.Odds.append((SLNC.r, SLNC.c, SLNC.Cand))
        else:  Tree.Evens.append((SLNC.r, SLNC.c, SLNC.Cand))
        TNode.Children.append(TNODE(SLNC.r, SLNC.c, SLNC.Cand))
        grow_sln(Tree, TNode.Children[-1], SLNodes[Hash].Children, NodesConsidered, SLNodes, Lvl+1)
