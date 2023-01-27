from copy import copy, deepcopy

from globals import *
from solve_utils import *

class SLNNODE:
    def __init__(self, SLNet = None, Ccell0 = None, Ccell1 = None, Children = None):
        self.SLNet = SLNet  # of type SLNET
        self.Ccell0 = Ccell0 if Ccell0 else ()   # (r, c, Cand) tuple
        self.Ccell1 = Ccell1 if Ccell1 else ()
        self.Children = Children if Children else []  # of type SLNNODE

class SLNET:
    def __init__(self, Trunk = None, Pol0 = None, Pol1 = None):
        self.Trunk = Trunk  # of type TNODE
        self.Pol0 = Pol0 if Pol0 else []
        self.Pol1 = Pol1 if Pol0 else []

class SLN_STATE:
    def __init__(self, SLNNodes = None, Chain = None, Tech = T_UNDEF, Pattern = None, Pattern1 = None, Elims = None, Plcmts = None):
        self.SLNNodes = SLNNodes if SLNNodes else []
        self.Chain = Chain
        self.Tech = Tech
        self.Pattern = Pattern if Pattern else []
        self.Pattern1 = Pattern1 if Pattern1 else []
        self.Elims = Elims if Elims else {}
        self.Plcmts = Plcmts if Plcmts else []

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
        if Hash in NodesConsidered: continue
        NodesConsidered.add(Hash)
        SLNet = SLNET(TNODE(Trunk.r, Trunk.c, Trunk.Cand, PAR_E))
        SLNet.Pol0 = [(Trunk.r, Trunk.c, Trunk.Cand)]
        grow_sln(SLNet, SLNet.Trunk, Trunk.Children, NodesConsidered, SLNodes, 1)

        Method, Elims, Plcmts, Pattern = sl_net_elims(SLNet, Methods, Cands)

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
            Step.Method = Method
            Step.NrLks = len(SLNet.Pol0) + len(SLNet.Pol1) - 1
            Step.Pattern = [[P_VAL, SLNet.Trunk.Cand], [P_ROW, SLNet.Trunk.r], [P_COL, SLNet.Trunk.c], [P_PAR, SLNet.Trunk.Lk]]
            climb_branch(SLNet.Trunk, Step.Pattern)
            if Pattern: Step.Pattern.extend([[P_CON], *Pattern])
            Step.Pattern.append([P_END])
            return len(Plcmts)
    return -1

def tech_chained_strong_linked_nets(Grid, Step, Cands, Methods):

    SLNodes = {}
    for Cand in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in list_all_cand_strong_links(Cand, Cands):
            Hash = str(Cand0)+str(r0)+str(c0)
            if Hash not in SLNodes:
                SLNodes[Hash] = TNODE(r0, c0, Cand0, Lk0)
            SLNodes[Hash].Children.append(TNODE(r1, c1, Cand1, Lk1))

    Forest = []; SLNNodes = []
    NodesConsidered = set()
    for Hash, Trunk in SLNodes.items():
        if Hash in NodesConsidered: continue
        NodesConsidered.add(Hash)
        SLNet = SLNET(TNODE(Trunk.r, Trunk.c, Trunk.Cand, PAR_E))
        SLNet.Pol0 = [(Trunk.r, Trunk.c, Trunk.Cand)]
        grow_sln(SLNet, SLNet.Trunk, Trunk.Children, NodesConsidered, SLNodes, 1)
        # Build Forest of SLNet Pairs, each with switched polarity nodes, but same Tree/Net.
        # Uses a bit more memory but makes the chain of SLNet building much simpler.
        # Mirror image nets are seen as different nets.
        Forest.extend([SLNNODE(SLNet), SLNNODE(SLNET(SLNet.Trunk, SLNet.Pol1, SLNet.Pol0))])
        SLNNodes.extend([copy(Forest[-2]), copy(Forest[-1])])
    # Forest of SLNNode saplings planted

    State = SLN_STATE(SLNNodes)
    while Forest:
        Culls = set()
        for SLNNodes in Forest:
            sln_chain_next_level(SLNNodes, [SLNNodes], Cands, 1, Methods, State)
            if State.Tech != T_UNDEF:
                Step.Method = State.Tech
                Step.Pattern = []
                for SLNNode in State.Chain:
                    Step.NrLks += len(SLNNode.SLNet.Pol0) + len(SLNNode.SLNet.Pol1) - 1
                    if SLNNode.Ccell0:
                        r0, c0, Cand0, Pol0 = SLNNode.Ccell0; r1, c1, Cand1, Pol1 = SLNNode.Ccell1
                        Step.Pattern.extend([[P_OP, OP_LT], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, OP_WLK], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_OP, OP_GT]])
                        # Step.Pattern.extend([[P_OP, OP_LT], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_PAR, Pol0], [P_OP, OP_WLK], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_PAR, Pol1], [P_OP, OP_GT]])
                    Step.Pattern.extend([[P_OP, OP_SQBO], [P_VAL, SLNNode.SLNet.Trunk.Cand], [P_ROW, SLNNode.SLNet.Trunk.r], [P_COL, SLNNode.SLNet.Trunk.c], [P_PAR, SLNNode.SLNet.Trunk.Lk]])
                    climb_branch(SLNNode.SLNet.Trunk, Step.Pattern)
                    Step.Pattern.append([P_OP, OP_SQBC])
                if State.Pattern1: Step.Pattern.extend([[P_CON], *State.Pattern1])
                Step.Pattern.append([P_END])
                Step.Outcome = []
                for r, c, Cand in State.Plcmts:
                    Grid[r][c] = Cand
                    Cands[r][c].clear()
                    discard_cand_from_peers(Cand, r, c, Cands)
                    if Step.Outcome: Step.Outcome.append([P_SEP])
                    Step.Outcome.Extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
                for K, Cands1 in State.Elims.items():
                    r = int(K[0]); c = int(K[1])
                    if Grid[r][c]: continue
                    Elim = Cands[r][c] & set(Cands1)
                    if Elim:
                        Cands[r][c] -= set(Cands1)
                        if Step.Outcome:  Step.Outcome.append([P_SEP])
                        Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elim]])
                Step.Outcome.append([P_END])
                return len(State.Plcmts)
            if not SLNNodes.Children: Culls.add(SLNNodes)
        for X in Culls: Forest.remove(X)
    return -1

def sln_chain_next_level(SLNNode, Chain, Cands, Lvl, Methods, State):

    if SLNNode.Children:  # Not at leaves yet
        Prunes = set()
        for SLNNChild in SLNNode.Children:
            sln_chain_next_level(SLNNChild, [*Chain, SLNNChild], Cands, Lvl+1, Methods, State)
            if State.Tech != T_UNDEF: return
            if not SLNNChild.Children: Prunes.add(SLNNChild)
        for X in Prunes: SLNNode.Children.remove(X)
    else:  # at leaves.
        for SLNN1 in State.SLNNodes:
            for SLNNCh in Chain:  # Ensure SLNN1 or its mirror are not already in the chain
                if SLNN1.SLNet.Pol0 == SLNNCh.SLNet.Pol0 or SLNN1.SLNet.Pol0 == SLNNCh.SLNet.Pol1: break
            else:
                for r0, c0, Cand0 in SLNNode.SLNet.Pol1:
                    for r1, c1, Cand1 in SLNN1.SLNet.Pol0:
                        if ccells_see_each_other(r0, c0, Cand0, r1, c1, Cand1):  # They will only be weak links.
                            SLNN1 = deepcopy(SLNN1)
                            SLNN1.Ccell0 = (r0, c0, Cand0, PAR_O); SLNN1.Ccell1 = (r1, c1, Cand1, PAR_E)
                            #  a SLN that can be linked, what resolutions do the ends yield.
                            if resolve_sln_chain_patterns([*Chain, SLNN1], Cands, Methods, State): return
                            SLNNode.Children.append(SLNN1)

def resolve_sln_chain_patterns(Chain, Cands, Methods, State):

    State.Elims = {}; State.Pattern1 = []; State.Tech = T_UNDEF
    if T_CHAINED_STRONG_LINKED_NET_T1 in Methods:  # same candidate values
        Rpts = []
        for re0, ce0, Cande0 in Chain[0].SLNet.Pol0:
            for re1, ce1, Cande1 in Chain[-1].SLNet.Pol1:
                if Cande0 == Cande1:
                    for r, c in cells_that_see_all_of([(re0, ce0), (re1, ce1)]):
                        if Cande0 in Cands[r][c]:
                            if (Cande0, r, c) in Rpts: continue
                            Rpts.append((Cande0, r, c))
                            Lk0 = how_ccells_linked(re0, ce0, Cande0, r, c, Cande1, Cands)
                            if Lk0 & LK_STRG: Lk0 |= LK_WKST
                            Lk1 = how_ccells_linked(r, c, Cande0, re1, ce1, Cande1, Cands)
                            if Lk1 & LK_STRG: Lk1 |= LK_WKST
                            if State.Pattern1: State.Pattern1.append([P_CON])
                            State.Pattern1.extend([[P_VAL, Cande0], [P_ROW, re0], [P_COL, ce0], [P_OP, token_link(Lk0 & 0x000f)],
                                                   [P_VAL, Cande0], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk1 & 0x000f)],
                                                   [P_VAL, Cande0], [P_ROW, re1], [P_COL, ce1]])
                            K = str(r)+str(c)
                            if K in State.Elims.keys(): State.Elims[K].append(Cande0)
                            else: State.Elims[K] = [Cande0]
        if State.Elims:
            State.Chain = Chain
            State.Tech = T_CHAINED_STRONG_LINKED_NET_T1
            return True
    State.Elims = {}; State.Pattern1 = []; State.Tech = T_UNDEF
    if T_CHAINED_STRONG_LINKED_NET_T2 in Methods:  # different candidate values in same house
        Rpts = []
        for re0, ce0, Cande0 in Chain[0].SLNet.Pol0:
            for re1, ce1, Cande1 in Chain[-1].SLNet.Pol1:
                if Cande0 != Cande1 and cells_in_same_house(re0, ce0, re1, ce1):
                    if Cande0 in Cands[re1][ce1]:
                        if (Cande0, re1, ce1) in Rpts: continue
                        Rpts.append((Cande0, re1, ce1))
                        Lk0 = how_ccells_linked(re0, ce0, Cande0, re1, ce1, Cande0, Cands)
                        if Lk0 & LK_STRG: Lk0 |= LK_WKST
                        Lk1 = how_ccells_linked(re1, ce1, Cande0, re1, ce1, Cande1, Cands)
                        if Lk1 & LK_STRG: Lk1 |= LK_WKST
                        if State.Pattern1: State.Pattern1.append([P_CON])
                        State.Pattern1.extend([[P_VAL, Cande0], [P_ROW, re0], [P_COL, ce0], [P_OP, token_link(Lk0 & 0x000f)],
                                               [P_VAL, Cande0], [P_ROW, re1], [P_COL, ce1], [P_OP, token_link(Lk1 & 0x000f)],
                                               [P_VAL, Cande1], [P_ROW, re1], [P_COL, ce1]])
                        K = str(re1)+str(ce1)
                        if K in State.Elims.keys(): State.Elims[K].append(Cande0)
                        else: State.Elims[K] = [Cande0]
                    if Cande1 in Cands[re0][ce0]:
                        if (Cande1, re0, ce0) in Rpts: continue
                        Rpts.append((Cande1, re0, ce0))
                        Lk0 = how_ccells_linked(re1, ce1, Cande1, re0, ce0, Cande1, Cands)
                        if Lk0 & LK_STRG: Lk0 |= LK_WKST
                        Lk1 = how_ccells_linked(re0, ce0, Cande1, re0, ce0, Cande0, Cands)
                        if Lk1 & LK_STRG: Lk1 |= LK_WKST
                        if State.Pattern1: State.Pattern1.append([P_CON])
                        State.Pattern1.extend([[P_VAL, Cande1], [P_ROW, re1], [P_COL, ce1], [P_OP, token_link(Lk0 & 0x000f)],
                                               [P_VAL, Cande1], [P_ROW, re0], [P_COL, ce0], [P_OP, token_link(Lk1 & 0x000f)],
                                               [P_VAL, Cande0], [P_ROW, re0], [P_COL, ce0]])
                        K = str(re0)+str(ce0)
                        if K in State.Elims.keys(): State.Elims[K].append(Cande1)
                        else: State.Elims[K] = [Cande1]
        if State.Elims:
            State.Chain = Chain
            State.Tech = T_CHAINED_STRONG_LINKED_NET_T2
            return True
    State.Elims = {}; State.Pattern1 = []; State.Tech = T_UNDEF
    if T_CHAINED_STRONG_LINKED_NET_T3 in Methods:  # opposing candidates in Exposed pair
        for re0, ce0, Cande0 in Chain[0].SLNet.Pol0:
            for re1, ce1, Cande1 in Chain[-1].SLNet.Pol1:
                if Cande0 != Cande1 and cells_in_same_house(re0, ce0, re1, ce1):
                    if Cands[re0][ce0] == Cands[re1][ce1] and T_CHAINED_STRONG_LINKED_NET_T3 in Methods:  # opposing candidates in Exposed pair
                        if State.Pattern1: State.Pattern1.append([P_CON])
                        if re0 == re1: State.Pattern1.extend([[P_VAL, sorted(Cands[re0][ce0])], [P_OP, OP_EQ], [P_ROW, re0], [P_COL, ce0, ce1]])
                        elif ce0 == ce1: State.Pattern1.extend([[P_VAL, sorted(Cands[re0][ce0])], [P_OP, OP_EQ], [P_ROW, re0, re1], [P_COL, ce0]])
                        else: State.Pattern1.extend([[P_VAL, sorted(Cands[re0][ce0])], [P_OP, OP_EQ], [P_ROW, re0], [P_COL, ce0], [P_CON], [P_ROW, re1], [P_ROW, ce1]])
                        State.Plcmts.extend([(re0, ce0, Cande0), (re1, ce1, Cande1)])
                if State.Plcmts:
                    State.Chain = Chain
                    State.Tech = T_CHAINED_STRONG_LINKED_NET_T3
                    return True
    return False

def sl_net_elims(Tree, Methods, Cands):

    if len(Tree.Pol0) < 2 or len(Tree.Pol1) < 2: return -1, {}, [], []
    if T_STRONG_LINKED_NET_T1 in Methods:  # Type 1
        # 2 Even nodes see each other
        for i, (r0, c0, Cand0) in enumerate(Tree.Pol0[:-1]):
            for r1, c1, Cand1 in Tree.Pol0[i+1:]:
                Lk = how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands)
                if Lk:
                    if Lk & LK_STRG: Lk |= Lk_WKST
                    Pattern = [[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_PAR, PAR_E], [P_OP, token_link(Lk & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_PAR, PAR_E]]
                    Elims = {}
                    for r2, c2, Cand2 in Tree.Pol0:
                        K = str(r2)+str(c2)
                        if K in Elims.keys(): Elims[K].append(Cand2)
                        else: Elims[K] = [Cand2]
                    return T_STRONG_LINKED_NET_T1, Elims, Tree.Pol1, Pattern
        # 2 odd nodes see each other
        for i, (r0, c0, Cand0) in enumerate(Tree.Pol1[:-1]):
            for r1, c1, Cand1 in Tree.Pol1[i+1:]:
                Lk = how_ccells_linked(r0, c0, Cand0, r1, c1, Cand1, Cands)
                if Lk:
                    if Lk & LK_STRG: Lk |= Lk_WKST
                    Pattern = [[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_PAR, PAR_O], [P_OP, token_link(Lk & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_PAR, PAR_O]]
                    Elims = {}
                    for r2, c2, Cand2 in Tree.Pol1:
                        K = str(r2)+str(c2)
                        if K in Elims.keys(): Elims[K].append(Cand2)
                        else: Elims[K] = [Cand2]
                    return T_STRONG_LINKED_NET_T1, Elims, Tree.Pol0, Pattern
    if T_STRONG_LINKED_NET_T2 in Methods:  # Type 2
        Links = []; Pol = -1
        for r in range(9):
            for c in range(9):
                Links = []; Elims = {}; Plcmts = []  # All cands in cell see polarity 0 nodes
                for Cand in Cands[r][c]:
                    if (r, c, Cand) in Tree.Pol0: break
                    for re, ce, Cande in Tree.Pol0:
                        Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                        if Lke:
                            if Lke & LK_STRG: Lke |= LK_WKST
                            Links.append([NL(r, c, Cand, Lke), NL(re, ce, Cande, LK_NONE)])
                            break
                    else: break
                if Links and len(Links) == len(Cands[r][c]):
                    Pol = PAR_E
                    for r2, c2, Cand2 in Tree.Pol0:
                        K = str(r2)+str(c2)
                        if K in Elims.keys(): Elims[K].append(Cand2)
                        else: Elims[K] = [Cand2]
                    Plcmts = Tree.Pol1
                else:
                    Links = []  # All cands in cell see polarity 1 nodes
                    for Cand in Cands[r][c]:
                        if (r, c, Cand) in Tree.Pol1: break
                        for ro, co, Cando in Tree.Pol1:
                            Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                            if Lko:
                                if Lko & LK_STRG: Lko |= LK_WKST
                                Links.append([NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                break
                        else: break
                    if Links and len(Links) == len(Cands[r][c]):
                        Pol = PAR_O
                        for r2, c2, Cand2 in Tree.Pol1:
                            K = str(r2)+str(c2)
                            if K in Elims.keys(): Elims[K].append(Cand2)
                            else: Elims[K] = [Cand2]
                        Plcmts = Tree.Pol0
                if Elims:
                    Pattern = []
                    for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in Links:
                        if Pattern: Pattern.append([P_CON])
                        Pattern.extend([[P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)], [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_PAR, Pol]])
                    return T_STRONG_LINKED_NET_T2, Elims, Plcmts, Pattern
    if T_STRONG_LINKED_NET_T3 in Methods:
        # look for non-net cells that see both an odd and even nodes
        Pattern = []; Elims = {}
        for r in range(9):
            for c in range(9):
                for Cand in sorted(Cands[r][c]):
                    Done = False
                    if (r, c, Cand) in [*Tree.Pol0, *Tree.Pol1]: continue
                    for re, ce, Cande in Tree.Pol0:
                        Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands)
                        if Lke:
                            if Lke & LK_STRG: Lke |= LK_WKST
                            for ro, co, Cando in Tree.Pol1:
                                Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands)
                                if Lko:
                                    if Lko & LK_STRG: Lko |= LK_WKST
                                    if Pattern:  Pattern.append([P_CON])
                                    Pattern.extend([[P_VAL, Cando], [P_ROW, re], [P_COL, ce], [P_PAR, PAR_E], [P_OP, token_link(Lke & 0x000f)], [P_VAL, Cand], [P_ROW, r], [P_COL, c],
                                                    [P_OP, token_link(Lko & 0x000f)], [P_VAL, Cando], [P_ROW, ro], [P_COL, co], [P_PAR, PAR_O]])
                                    K = str(r)+str(c)
                                    if K in Elims.keys():
                                        if Cand not in Elims[K]: Elims[K].append(Cand)
                                    else: Elims[K] = [Cand]
                                    Done = True; break
                        if Done: break
        if Elims: return T_STRONG_LINKED_NET_T3, Elims, [], Pattern
    return T_UNDEF, {}, [], []

def climb_branch(TNode, Pattern):

    nChildren = len(TNode.Children)
    if nChildren == 0: return
    if nChildren >= 1: Pattern.append([P_OP, OP_SLK])
    if nChildren > 1: Pattern.append([P_OP, OP_BRCO])
    First = True
    for Child in TNode.Children:
        if First: First = False
        else: Pattern.append([P_CON])
        Pattern.extend([[P_VAL, Child.Cand], [P_ROW, Child.r], [P_COL, Child.c], [P_PAR, Child.Lk]])
        climb_branch(Child, Pattern)
    if nChildren > 1: Pattern.append([P_OP, OP_BRCC])

def grow_sln(Tree, TNode, SLNChildren, NodesConsidered, SLNodes, Lvl):

    for SLNC in SLNChildren:
        Hash = str(SLNC.Cand) + str(SLNC.r) + str(SLNC.c)
        if Hash in NodesConsidered: continue
        NodesConsidered.add(Hash)
        if Hash not in SLNodes.keys(): continue
        if Lvl & 0x01:
            Tree.Pol1.append((SLNC.r, SLNC.c, SLNC.Cand))
            TNode.Children.append(TNODE(SLNC.r, SLNC.c, SLNC.Cand, PAR_O))
        else:
            Tree.Pol0.append((SLNC.r, SLNC.c, SLNC.Cand))
            TNode.Children.append(TNODE(SLNC.r, SLNC.c, SLNC.Cand, PAR_E))
        grow_sln(Tree, TNode.Children[-1], SLNodes[Hash].Children, NodesConsidered, SLNodes, Lvl+1)
