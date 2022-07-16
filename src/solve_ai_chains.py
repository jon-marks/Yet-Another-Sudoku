
from globals import *
from solve_utils import *

def tech_ai_chains(Grid, Step, Cands, Methods):
    return ai_chains(Grid, Step, Cands, Methods, False)

def tech_gl_ai_chains(Grid, Step, Cands, Methods):
    return ai_chains(Grid, Step, Cands, Methods, True)

def ai_chains(Grid, Step, Cands, Methods, GrpLks = False):

    SLNodes = {}
    Forest = {}
    for Cand in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in list_all_cand_strong_links(Cand, Cands, GrpLks, True):
            Hash = str(Cand0)+str(r0)+str(c0)
            if Hash not in SLNodes:
                SLNodes[Hash] = TNODE(r0, c0, Cand0, Lk0)
                Forest[Hash] = ANODE(Hash)
            SLNodes[Hash].Children.append(TNODE(r1, c1, Cand1, Lk1))
            Forest[Hash].Children.append(ANODE(str(Cand1) + str(r1) + str(c1), Lk1))

    while Forest:
        Culls = set()
        State = STATE(SLNodes)
        for Hash, Tree in Forest.items():
            ai_chain_next_level(Tree, [], Cands, 1, Methods, State, GrpLks)
            if State.Tech != T_UNDEF:
                Step.Method = State.Tech
                if State.Tech == T_W_WING:
                    P = State.Pattern
                    Step.Pattern = [[P_OP, OP_PARO], [P_VAL, P[0].Cand], [P_OP, OP_SLK], [P_VAL, P[1].Cand], [P_OP, OP_PARC], [P_ROW, P[0].r], [P_COL, P[0].c],
                                    [P_OP, token_link(P[1].Lk & 0x000f)], [P_VAL, P[2].Cand], [P_ROW, P[2].r], [P_COL, P[2].c],
                                    [P_OP, OP_SLK], [P_VAL, P[3].Cand], [P_ROW, P[3].r], [P_COL, P[3].c], [P_OP, token_link(P[3].Lk & 0x000f)],
                                    [P_OP, OP_PARO], [P_VAL, P[4].Cand], [P_OP, OP_SLK], [P_VAL, P[5].Cand], [P_OP, OP_PARC], [P_ROW, P[5].r], [P_COL, P[5].c], [P_END]]
                else:
                    Step.NrLks = Step.NrGrpLks = 0
                    Step.Pattern = []; Step.Outcome = []
                    for r, c, Cand, Lk, in State.Pattern:
                        Step.NrLks += 1
                        if Step.Method & T_GRPLK:
                            if len(r) > 1: Step.NrGrpLks += 1
                            if len(c) > 1: Step.NrGrpLks += 1
                        Step.Pattern.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk & 0x000f)]])
                    Step.Pattern.append([P_END])
                if State.Tech in {T_DC_IBVC_AI_CHAIN, T_STRONG_AI_LOOP, T_GL_DC_IBVC_AI_CHAIN, T_GL_STRONG_AI_LOOP}:
                    n = 0
                    for r, c, Cand in State.Outcome:
                        n += 1
                        Grid[r][c] = Cand
                        Cands[r][c].clear()
                        discard_cand_from_peers(Cand, r, c, Cands)
                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                        Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
                    Step.Outcome.append([P_END, ])
                    return n
                else:  # Eliminations
                    for r, c, Cand in State.Outcome:
                        Cands[r][c].discard(Cand)
                        if Step.Outcome: Step.Outcome.append([P_SEP, ])
                        Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                    Step.Outcome.append([P_END, ])
                    return 0
            if not Tree.Children: Culls.add(Hash)
        for Hash in Culls: del Forest[Hash]
    return -1

def ai_chain_next_level(ANode, Chain, Cands, Lvl, Methods, State, GrpLks):

    SLN = State.SLNodes[ANode.Hash]
    Chain1 = [*Chain, NL(SLN.r, SLN.c, SLN.Cand, ANode.Lk)]
    PrunesC = set()
    for ANChild in ANode.Children:
        SLNC = State.SLNodes[ANChild.Hash]
        PrunesGC = set()
        Chain2 = [*Chain1, NL(SLNC.r, SLNC.c, SLNC.Cand, ANChild.Lk)]
        if ANChild.Children:  # not at the leaves yet.
            for ANGChild in ANChild.Children:
                ai_chain_next_level(ANGChild, Chain2, Cands, Lvl+1, Methods, State, GrpLks)
                if State.Tech != T_UNDEF: return
                if not ANGChild.Children: PrunesGC.add(ANGChild)
            for X in PrunesGC:
                for i in range(len(ANChild.Children)):
                    if ANChild.Children[i].Hash == X.Hash: del ANChild.Children[i]; break
        else:  # at the leaves
            for r1, c1, Cand1, Lk1 in list_ccells_linked_to(SLNC.r, SLNC.c, SLNC.Cand, Cands, LK_STWK, GrpLks, True):
                Hash = str(Cand1)+str(r1)+str(c1)
                if Hash not in State.SLNodes: continue
                for rx, cx, Candx, Lkx in Chain1:
                    if ccells_intersect(r1, c1, Cand1, rx, cx, Candx, GrpLks): break
                else:
                    if Lk1 & LK_STRG: Lk1 |= LK_WKST
                    Chain3 = [*Chain2, NL(r1, c1, Cand1, Lk1)]
                    SLNGC = State.SLNodes[Hash]
                    ANGChild = ANODE(Hash, Lk1)
                    for SLNGGC in SLNGC.Children:
                        if resolve_strong_ai_loops([*Chain3, NL(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, SLNGGC.Lk)], Cands, Methods, GrpLks, State): return
                        for rx, cx, Candx, Lkx in Chain3:
                            if ccells_intersect(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, rx, cx, Candx, GrpLks): break
                        else:
                            if resolve_other_ai_chain_patterns([*Chain3, NL(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, SLNGGC.Lk)], Cands, Methods, GrpLks, State): return
                            if Lvl <= AIC_RECURSE_LIM: ANGChild.Children.append(ANODE(str(SLNGGC.Cand) + str(SLNGGC.r) + str(SLNGGC.c), SLNGGC.Lk))
                    if ANGChild.Children:  ANChild.Children.append(ANGChild)
        if not ANChild.Children or Lvl > AIC_RECURSE_LIM:  PrunesC.add(ANChild)
    for X in PrunesC:
        for i in range(len(ANode.Children)):
            if ANode.Children[i].Hash == X.Hash: del ANode.Children[i]; break

def resolve_strong_ai_loops(Chain, Cands, Methods, GrpLks, Status):

    Status.Tech = T_UNDEF
    if {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP} & set(Methods) and len(Chain) > 4 and (Chain[0].r, Chain[0].c, Chain[0].Cand) == (Chain[-1].r, Chain[-1].c, Chain[-1].Cand):
        Status.Outcome = []
        if GrpLks and T_GL_STRONG_AI_LOOP in Methods and len(Chain[0].r) == len(Chain[0].c) == 1:
            Status.Outcome = [(list(Chain[0].r)[0], list(Chain[0].c)[0], Chain[0].Cand)]
            Status.Tech = T_GL_STRONG_AI_LOOP
        elif ~GrpLks and T_STRONG_AI_LOOP in Methods:
            Status.Outcome = [(Chain[0].r, Chain[0].c, Chain[0].Cand)]
            Status.Tech = T_STRONG_AI_LOOP
        if Status.Outcome:
            Status.Pattern = []
            for i in range(len(Chain)-1):
                Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
            return True
    return False

def resolve_other_ai_chain_patterns(Chain, Cands, Methods, GrpLks, Status):

    Status.Tech = T_UNDEF
    Lk = how_ccells_linked(Chain[0].r, Chain[0].c, Chain[0].Cand, Chain[-1].r, Chain[-1].c, Chain[-1].Cand, Cands, GrpLks)
    if {T_EVEN_AI_LOOP, T_GL_EVEN_AI_LOOP} & set(Methods) and Lk:  # Even AI-Loop found
        if Lk & LK_STRG: Lk |= LK_WKST
        Status.Pattern = []; Status.Outcome = []
        # Search for ccells that are not part of the chain and can see both an odd and even chain node.
        if GrpLks:
            for r in range(9):
                for c in range(9):
                    for Cand in Cands[r][c]:
                        Odd = Even = False
                        for i, (rn, cn, Candn, Lkn) in enumerate(Chain):
                            if ccells_intersect({r}, {c}, Cand, rn, cn, Candn, GrpLks): break
                            if ccells_see_each_other({r}, {c}, Cand, rn, cn, Candn, GrpLks):
                                if i & 0x01: Odd = True
                                else: Even = True
                                if Odd and Even: Status.Outcome.append((r, c, Cand)); break
        else:
            for r in range(9):
                for c in range(9):
                    for Cand in Cands[r][c]:
                        Odd = Even = False
                        for i, (rn, cn, Candn, Lkn) in enumerate(Chain):
                            if (r, c, Cand) == (rn, cn, Candn): break
                            if ccells_see_each_other(r, c, Cand, rn, cn, Candn, GrpLks):
                                if i & 0x01: Odd = True
                                else: Even = True
                                if Odd and Even: Status.Outcome.append((r, c, Cand)); break
        if Status.Outcome:
            for i in range(len(Chain)-1):
                Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
            Status.Pattern.append(NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, Lk))
            Status.Tech = T_GL_EVEN_AI_LOOP if GrpLks else T_EVEN_AI_LOOP
            return True
    else:
        Status.Outcome = []; Status.Tech = T_UNDEF
        if Chain[0].Cand == Chain[-1].Cand:  # chain starts and ends with same candidate values
            for r, c in cells_that_see_all_of([(Chain[0].r, Chain[0].c), (Chain[-1].r, Chain[-1].c)], GrpLks):
                if Chain[0].Cand in Cands[r][c]: Status.Outcome.append((r, c, Chain[0].Cand))
            if Status.Outcome:
                if T_W_WING in Methods and ~GrpLks and len(Chain) == 6 and Chain[1].Lk & Chain[-1].Lk & LK_CELL \
                        and Cands[Chain[0].r][Chain[0].c] == Cands[Chain[-1].r][Chain[-1].c]: Status.Tech = T_W_WING
                elif {T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN} & set(Methods): Status.Tech = T_GL_SC_AI_CHAIN if GrpLks else T_SC_AI_CHAIN
        elif cells_in_same_house(Chain[0].r, Chain[0].c, Chain[-1].r, Chain[-1].c, GrpLks):
            if T_DC_IBVC_AI_CHAIN in Methods and ~GrpLks \
                    and (Chain[0].r != Chain[-1].r or Chain[0].c != Chain[-1].c) \
                    and len(Cands[Chain[0].r][Chain[0].c]) == 2 \
                    and Cands[Chain[0].r][Chain[0].c] == Cands[Chain[-1].r][Chain[-1].c]:
                Status.Tech = T_DC_IBVC_AI_CHAIN
                Status.Outcome = [(Chain[0].r, Chain[0].c, Chain[0].Cand), (Chain[-1].r, Chain[-1].c, Chain[-1].Cand)]
            elif T_GL_DC_IBVC_AI_CHAIN in Methods and GrpLks \
                    and (Chain[0].r != Chain[-1].r or Chain[0].c != Chain[-1].c) \
                    and len(Chain[0].r) == len(Chain[-1].r) == len(Chain[0].c) == len(Chain[-1].c) == 1 \
                    and len(Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]]) == 2 \
                    and Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]] == Cands[list(Chain[-1].r)[0]][list(Chain[-1].c)[0]]:
                Status.Tech = T_GL_DC_IBVC_AI_CHAIN
                Status.Outcome = [(list(Chain[0].r)[0], list(Chain[0].c)[0], Chain[0].Cand), (list(Chain[-1].r)[0], list(Chain[-1].c)[0], Chain[-1].Cand)]
            elif T_DC_AI_CHAIN in Methods and ~GrpLks:
                if (Chain[0].r, Chain[0].c) == (Chain[-1].r, Chain[-1].c):  # same cell
                    Cands0 = Cands[Chain[0].r][Chain[0].c] - {Chain[0].Cand, Chain[-1].Cand}
                    if Cands0: Status.Outcome = [(Chain[0].r, Chain[0].c, Cands0)]
                else:
                    if Chain[-1].Cand in Cands[Chain[0].r][Chain[0].c]: Status.Outcome.append((Chain[0].r, Chain[0].c, Chain[-1].Cand))
                    if Chain[0].Cand in Cands[Chain[-1].r][Chain[-1].c]: Status.Outcome.append((Chain[-1].r, Chain[-1].c, Chain[0].Cand))
                if Status.Outcome: Status.Tech = T_DC_AI_CHAIN
            elif T_GL_DC_AI_CHAIN in Methods and GrpLks and len(Chain[0].r) == len(Chain[-1].r) == len(Chain[0].c) == len(Chain[-1].c) == 1:
                if (Chain[0].r, Chain[0].c) == (Chain[-1].r, Chain[-1].c):  # same cell
                    Cands0 = Cands[list(Chain[-1].r)[0]][list(Chain[-1].c)[0]]-{Chain[0].Cand, Chain[-1].Cand}
                    if Cands0: Status.Outcome = [(list(Chain[0].r)[0], list(Chain[0].c)[0], Cands0)]
                else:
                    if Chain[-1].Cand in Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]]: Status.Outcome.append((list(Chain[0].r)[0], list(Chain[0].c)[0], Chain[-1].Cand))
                    if Chain[0].Cand in Cands[list(Chain[-1].r)[0]][list(Chain[-1].c)[0]]: Status.Outcome.append((list(Chain[-1].r)[0], list(Chain[-1].c)[0], Chain[0].Cand))
                if Status.Outcome: Status.Tech = T_GL_DC_AI_CHAIN
        if Status.Tech != T_UNDEF and Status.Outcome:
            Status.Pattern = []
            for i in range(len(Chain)-1):
                Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
            Status.Pattern.append(NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, LK_NONE))
            return True
    return False
