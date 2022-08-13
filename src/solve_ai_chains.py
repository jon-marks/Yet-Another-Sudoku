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
                if Step.Method == T_W_WING:
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
                if Step.Method in {T_AI_CHAIN_T2, T_AI_CHAIN_T3, T_GL_AI_CHAIN_T2, T_GL_AI_CHAIN_T3}:
                    for r0, c0, Cand0 in State.Pattern1:
                        Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_OP, OP_PRES], [P_ROW, r0], [P_COL, c0]])
                elif Step.Method in {T_AI_CHAIN_T3, T_GL_AI_CHAIN_T3}:
                    for r0, c0, Cand0 in State.Pattern1:
                        Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_OP, OP_EQ], [P_ROW, r0], [P_COL, c0]])
                elif Step.Method in {T_EVEN_AI_LOOP_T1, T_EVEN_AI_LOOP_T2, T_GL_EVEN_AI_LOOP_T1, T_GL_EVEN_AI_LOOP_T2}:  # T_AI_CHAIN_T3, T_STRONG_AI_LOOP, T_GL_AI_CHAIN_T3, T_GL_STRONG_AI_LOOP}:
                    for (r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1) in State.Pattern1:
                        Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)],
                                             [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1]])
                else:  # Step.Method in {T_W_WING, T_AI_CHAIN_T1, T_EVEN_AI_LOOP_T3, T_GL_AI_CHAIN_T1, T_GL_EVEN_AI_LOOP_T3}:
                    for (r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1), (r2, c2, Cand2, Lk2) in State.Pattern1:
                        Step.Pattern.extend([[P_CON], [P_VAL, Cand0], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk0 & 0x000f)],
                                             [P_VAL, Cand1], [P_ROW, r1], [P_COL, c1], [P_OP, token_link(Lk1 & 0x000f)],
                                             [P_VAL, Cand2], [P_ROW, r2], [P_COL, c2]])
                Step.Pattern.append([P_END])
                Step.Outcome = []
                for r, c, Cand in State.Plcmts:
                    Grid[r][c] = Cand
                    Cands[r][c].clear()
                    discard_cand_from_peers(Cand, r, c, Cands)
                    if Step.Outcome:  Step.Outcome.append([P_SEP])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
                for K, Cands1 in State.Elims.items():
                    r = int(K[0]); c = int(K[1])
                    if Grid[r][c]: continue
                    Elim = Cands[r][c] & set(Cands1)
                    if Elim:
                        Cands[r][c] -= set(Cands1)
                        if Step.Outcome:  Step.Outcome.append([P_SEP])
                        Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Elim]])
                if Step.Outcome:
                    Step.Outcome.append([P_END])
                    return len(State.Plcmts)
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

    if (Chain[0].r, Chain[0].c, Chain[0].Cand) != (Chain[-1].r, Chain[-1].c, Chain[-1].Cand): return False
    if GrpLks and T_GL_STRONG_AI_LOOP in Methods and len(Chain) > 4 and len(Chain[0].r) == len(Chain[0].c) == 1:
        Status.Plcmts = [(list(Chain[0].r)[0], list(Chain[0].c)[0], Chain[0].Cand)]
        Status.Tech = T_GL_STRONG_AI_LOOP
    elif ~GrpLks and T_STRONG_AI_LOOP in Methods and len(Chain) > 4:
        Status.Plcmts = [(Chain[0].r, Chain[0].c, Chain[0].Cand)]
        Status.Tech = T_STRONG_AI_LOOP
    else:
        Status.Plcmts= []
        Status.Tech = T_UNDEF
        return False
    Status.Pattern = [];  Status.Pattern1 = []
    for i in range(len(Chain)-1):
        Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
    Status.Pattern1.append([NL(Chain[1].r, Chain[1].c, Chain[1].Cand, LK_STRG), NL(Chain[0].r, Chain[0].c, Chain[0].Cand, LK_STRG), NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, LK_NONE)])
    return True

def resolve_other_ai_chain_patterns(Chain, Cands, Methods, GrpLks, Status):

    Status.Tech = T_UNDEF
    if {T_EVEN_AI_LOOP_T1, T_EVEN_AI_LOOP_T2, T_EVEN_AI_LOOP_T3, T_GL_EVEN_AI_LOOP_T1, T_GL_EVEN_AI_LOOP_T2, T_GL_EVEN_AI_LOOP_T3} & set(Methods):  # Even AI-Loop found
        Lk = how_ccells_linked(Chain[0].r, Chain[0].c, Chain[0].Cand, Chain[-1].r, Chain[-1].c, Chain[-1].Cand, Cands, GrpLks)
        if Lk:
            if Lk & LK_STRG: Lk |= LK_WKST
            Status.Pattern = []; Status.Pattern1 = []; Status.Elims = {}; Status.Plcmts = []
            for i in range(len(Chain)-1):
                Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
            Status.Pattern.extend([NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, Lk)])
            Odds = []; Evens = []
            for i, (r, c, Cand, Lk) in enumerate(Chain):
                if i & 1: Odds.append((r, c, Cand))
                else: Evens.append((r, c, Cand))
            if {T_EVEN_AI_LOOP_T3, T_GL_EVEN_AI_LOOP_T3} & set(Methods):  # Highest likelihood of occurring: Type 3: Ccell(s) see both odd and even parity nodes.
                Status.Pattern1 = []; Status.Plcmts = []; Status.Elims = {}
                if GrpLks:
                    for r in range(9):
                        for c in range(9):
                            for Cand in sorted(Cands[r][c]):
                                CcellInChain = False
                                for rx, cx, Candx in [*Odds, *Evens]:
                                    if ccells_intersect({r}, {c}, Cand, rx, cx, Candx, GrpLks): CcellInChain = True; break
                                if CcellInChain: continue
                                Done = False
                                for re, ce, Cande in Evens:
                                    Lke = how_ccells_linked({r}, {c}, Cand, re, ce, Cande, Cands, GrpLks)
                                    if Lke:
                                        if Lke & LK_STRG: Lke |= LK_WKST
                                        for ro, co, Cando in Odds:
                                            Lko = how_ccells_linked({r}, {c}, Cand, ro, co, Cando, Cands, GrpLks)
                                            if Lko:
                                                if Lko & LK_STRG: Lko |= LK_WKST
                                                Status.Pattern1.append([NL(re, ce, Cande, Lke), NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                                K = str(r)+str(c)
                                                if K in Status.Elims.keys(): Status.Elims[K].append(Cand)
                                                else: Status.Elims[K] = [Cand]
                                                # Status.Tech = T_EVEN_AI_LOOP_T3
                                                # return
                else:  # not group links
                    for r in range(9):
                        for c in range(9):
                            for Cand in sorted(Cands[r][c]):
                                if (r, c, Cand) in [*Evens, *Odds]: continue
                                for re, ce, Cande in Evens:
                                    Lke = how_ccells_linked(r, c, Cand, re, ce, Cande, Cands, GrpLks)
                                    if Lke:
                                        if Lke & LK_STRG: Lke |= LK_WKST
                                        for ro, co, Cando in Odds:
                                            Lko = how_ccells_linked(r, c, Cand, ro, co, Cando, Cands, GrpLks)
                                            if Lko:
                                                if Lko & LK_STRG: Lko |= LK_WKST
                                                Status.Pattern1.append([NL(re, ce, Cande, Lke), NL(r, c, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                                K = str(r)+str(c)
                                                if K in Status.Elims.keys(): Status.Elims[K].append(Cand)
                                                else: Status.Elims[K] = [Cand]
                                                # Status.Tech = T_EVEN_AI_LOOP_T3
                                                # return
                if Status.Elims:
                    Status.Tech = T_GL_EVEN_AI_LOOP_T3 if GrpLks else T_EVEN_AI_LOOP_T3
                    return
            if {T_EVEN_AI_LOOP_T1, T_GL_EVEN_AI_LOOP_T1} & set(Methods):  # Type 1: two same parity nodes see each other.
                for i in range(0, len(Evens)-1):  # Look in even nodes
                    ri, ci, Candi = Evens[i]
                    for j in range(i+1, len(Evens)):
                        rj, cj, Candj = Evens[j]
                        Lk = how_ccells_linked(ri, ci, Candi, rj, cj, Candj, Cands, GrpLks)
                        if Lk:
                            if Lk & LK_STRG: Lk |= LK_WKST
                            Status.Pattern1 = [[NL(ri, ci, Candi, Lk), NL(rj, cj, Candj, LK_NONE)]]
                            if GrpLks:
                                for r2, c2, Cand2 in Evens:
                                    for r3 in r2:
                                        for c3 in c2:
                                            K = str(r3) + str(c3)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                for r3, c3, Cand3 in Odds:
                                    if len(r3) == len(c3) == 1: Status.Plcmts.append((r3, c3, Cand3))
                            else:
                                for r2, c2, Cand2 in Odds:
                                    K = str(r2)+str(c2)
                                    if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                    else: Status.Elims[K] = [Cand2]
                                Status.Plcmts = Odds
                            Step.Method = T_EVEN_AI_LOOP_T1
                            return
                for i in range(0, len(Odds)-1):  # and look in odd nodes.
                    ri, ci, Candi = Odds[i]
                    for j in range(i+1, len(Odds)):
                        rj, cj, Candj = Odds[j]
                        Lk = how_ccells_linked(ri, ci, Candi, rj, cj, Candj, Cands, GrpLks)
                        if Lk:
                            if Lk & LK_STRG: Lk |= LK_WKST
                            Status.Pattern1 = [[NL(ri, ci, Candi, Lk), NL(rj, cj, Candj, LK_NONE)]]
                            if GrpLks:
                                for r2, c2, Cand2 in Odds:
                                    for r3 in r2:
                                        for c3 in c2:
                                            K = str(r3) + str(c3)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                for r3, c3, Cand3 in Evens:
                                    if len(r3) == len(c3) == 1: Status.Plcmts.append((r3, c3, Cand3))
                            else:
                                for r2, c2, Cand2 in Evens:
                                    K = str(r2)+str(c2)
                                    if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                    else: Status.Elims[K] = [Cand2]
                                Status.Plcmts = Evens
                            Step.Method = T_EVEN_AI_LOOP_T1
                            return
            if {T_EVEN_AI_LOOP_T2, T_GL_EVEN_AI_LOOP_T2} & set(Methods):  # Type 2: All cands in a cell see same parity nodes
                if GrpLks:
                    for r in range(9):
                        for c in range(9):
                            CandInChain = False
                            for Cand in Cands[r][c]:  # Ensure none of the cands of that cell are in the chain.
                                for rx, cx, Candx, Lkx in Chain:
                                    if ccells_intersect({r}, {c}, Cand, rx, cx, Candx, GrpLks): CandInChain = True; break
                                if CandInChain: break
                            if CandInChain: continue
                            Status.Pattern1 = []
                            for Cand in sorted(Cands[r][c]):
                                for re, ce, Cande in Evens:  # Consider even parity nodes
                                    Lke = how_ccells_linked({r}, {c}, Cand, re, ce, Cande, Cands, GrpLks)
                                    if Lke:
                                        if Lke & LK_STRG: Lke |= LK_WKST
                                        Status.Pattern1.append([NL({r}, {c}, Cand, Lke), NL(re, ce, Cande, LK_NONE)])
                                        break
                                else: break
                            if Status.Pattern1 and len(Status.Pattern1) == len(Cands[r][c]):
                                for r2, c2, Cand2 in Evens:
                                    for r3 in r2:
                                        for c3 in c2:
                                            K = str(r3)+str(c3)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                    for r3, c3, Cand3 in Odds:
                                        if len(r3) == len(c3) == 1: Status.Plcmts.append((r3, c3, Cand3))
                                Status.Tech = T_GL_EVEN_AI_LOOP_T2
                                return
                            Status.Pattern1 = []
                            for Cand in sorted(Cands[r][c]):
                                for ro, co, Cando in Odds:
                                    Lko = how_ccells_linked({r}, {c}, Cand, ro, co, Cando, Cands, GrpLks)
                                    if Lko:
                                        if Lko & LK_STRG: Lko |= LK_WKST
                                        Status.Pattern1.append([NL({r}, {c}, Cand, Lko), NL(ro, co, Cando, LK_NONE)])
                                        break
                                else: break
                            if Status.Pattern1 and len(Status.Pattern1) == len(Cands[r][c]):
                                for r2, c2, Cand2 in Odds:
                                    for r3 in r2:
                                        for c3 in c2:
                                            K = str(r3)+str(c3)
                                            if K in Status.Elims.keys(): Status.Elims[K].append(Cand2)
                                            else: Status.Elims[K] = [Cand2]
                                    for r3, c3, Cand3 in Evens:
                                        if len(r3) == len(c3) == 1: Status.Plcmts.append((r3, c3, Cand3))
                                Status.Tech = T_GL_EVEN_AI_LOOP_T2
                                return
                else:  # Even AI-Loop SL Type 2 - no group links.
                    for r in range(9):
                        for c in range(9):
                            CandInChain = False
                            for Cand in sorted(Cands[r][c]):
                                if (r, c, Cand) in [*Odds, *Evens]: CandInChain = True; break
                            if CandInChain: continue
                            Status.Pattern1 = []
                            for Cand in sorted(Cands[r][c]):
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
                                Status.Tech = T_EVEN_AI_LOOP_T2
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
                                Status.Tech = T_EVEN_AI_LOOP_T2
                                return
    else:
        Status.Elims = {}; Status.Plcmts = []; Status.Pattern1 = []; Status.Tech = T_UNDEF
        # Check for Type 1 Chain Elims.  Ccell(s) see same Value chain ends.
        if Chain[0].Cand == Chain[-1].Cand:
            if GrpLks and T_GL_AI_CHAIN_T1 in Methods:
                for r, c in cells_that_see_all_of([(Chain[0].r, Chain[0].c), (Chain[-1].r, Chain[-1].c)], GrpLks):
                    if Chain[0].Cand in Cands[r][c]:
                        Lk0 = how_ccells_linked(Chain[0].r, Chain[0].c, Chain[0].Cand, {r}, {c}, Chain[0].Cand, Cands, GrpLks)
                        Lk1 = how_ccells_linked(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, {r}, {c}, Chain[-1].Cand, Cands, GrpLks)
                        if Lk0 & LK_STRG: Lk0 |= LK_WKST
                        if Lk1 & LK_STRG: Lk1 |= LK_WKST
                        Status.Pattern1.append([NL(Chain[0].r, Chain[0].c, Chain[0].Cand, Lk0), NL(r, c, Chain[0].Cand, Lk1), NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, LK_NONE)])
                        K = str(r) + str(c)
                        if K in Status.Elims.keys(): Status.Elims[K].append(Chain[0].Cand)
                        else: Status.Elims[K] = [Chain[0].Cand]
            elif (not GrpLks) and {T_W_WING, T_AI_CHAIN_T1} & set(Methods):
                for r, c in cells_that_see_all_of([(Chain[0].r, Chain[0].c), (Chain[-1].r, Chain[-1].c)], GrpLks):
                    if Chain[0].Cand in Cands[r][c]:
                        Lk0 = how_ccells_linked(Chain[0].r, Chain[0].c, Chain[0].Cand, r, c, Chain[0].Cand, Cands, GrpLks)
                        Lk1 = how_ccells_linked(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, r, c, Chain[-1].Cand, Cands, GrpLks)
                        if Lk0 & LK_STRG: Lk0 |= LK_WKST
                        if Lk1 & LK_STRG: Lk0 |= LK_WKST
                        Status.Pattern1 = [[NL(Chain[0].r, Chain[0].c, Chain[0].Cand, Lk0), NL(r, c, Chain[0].Cand, Lk1), NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, LK_NONE)]]
                        K = str(r) + str(c)
                        if K in Status.Elims.keys(): Status.Elims[K].append(Chain[0].Cand)
                        else: Status.Elims[K] = [Chain[0].Cand]
            if Status.Elims:
                if T_W_WING in Methods and ~GrpLks and len(Chain) == 6 and Chain[1].Lk & Chain[-1].Lk & LK_CELL \
                        and Cands[Chain[0].r][Chain[0].c] == Cands[Chain[-1].r][Chain[-1].c]: Status.Tech = T_W_WING
                elif {T_AI_CHAIN_T1, T_GL_AI_CHAIN_T1} & set(Methods): Status.Tech = T_GL_AI_CHAIN_T1 if GrpLks else T_AI_CHAIN_T1
        elif cells_in_same_house(Chain[0].r, Chain[0].c, Chain[-1].r, Chain[-1].c, GrpLks):  # Type 3: Opposing values & cells of an Exposed pair
            if T_AI_CHAIN_T3 in Methods and ~GrpLks \
                    and (Chain[0].r != Chain[-1].r or Chain[0].c != Chain[-1].c) \
                    and len(Cands[Chain[0].r][Chain[0].c]) == 2 \
                    and Cands[Chain[0].r][Chain[0].c] == Cands[Chain[-1].r][Chain[-1].c]:
                if Chain[0].r == Chain[-1].r: Status.Pattern1 = [(Chain[0].r, [Chain[0].c, Chain[-1].c], sorted(Cands[Chain[0].r][Chain[0].c]))]
                elif Chain[0].c == Chain[-1].c: Status.Pattern1 = [([Chain[0].r, Chain[-1].r], Chain[0].c, sorted(Cands[Chain[0].r][Chain[0].c]))]
                else: Status.Pattern1 = [(Chain[0].r, Chain[0].c, sorted(Cands[Chain[0].r][Chain[0].c])), (Chain[-1].r, Chain[-1].c, sorted(Cands[Chain[1].r][Chain[1].c]))]
                Status.Plcmts = [(Chain[0].r, Chain[0].c, Chain[0].Cand), (Chain[-1].r, Chain[-1].c, Chain[-1].Cand)]
                Status.Tech = T_AI_CHAIN_T3
            elif T_GL_AI_CHAIN_T3 in Methods and GrpLks \
                    and (Chain[0].r != Chain[-1].r or Chain[0].c != Chain[-1].c) \
                    and len(Chain[0].r) == len(Chain[-1].r) == len(Chain[0].c) == len(Chain[-1].c) == 1 \
                    and len(Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]]) == 2 \
                    and Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]] == Cands[list(Chain[-1].r)[0]][list(Chain[-1].c)[0]]:
                if Chain[0].r == Chain[-1].r: Status.Pattern1 = [(Chain[0].r, [Chain[0].c, Chain[-1].c], sorted(Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]]))]
                elif Chain[0].c == Chain[-1].c: Status.Pattern1 = [([Chain[0].r, Chain[-1].r], Chain[0].c, sorted(Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]]))]
                else: Status.Pattern1 = [(Chain[0].r, Chain[0].c, sorted(Cands[list(Chain[0].r)[0]][list(Chain[0].c)[0]])), (Chain[-1].r, Chain[-1].c, sorted(Cands[list(Chain[-1].r)[0]][list(Chain[-1].c)[0]]))]
                Status.Plcmts = [(list(Chain[0].r)[0], list(Chain[0].c)[0], Chain[0].Cand), (list(Chain[-1].r)[0], list(Chain[-1].c)[0], Chain[-1].Cand)]
                Status.Tech = T_GL_AI_CHAIN_T3
            elif T_AI_CHAIN_T2 in Methods and ~GrpLks:
                Status.Pattern1 = []; Status.Elims = {}
                if (Chain[0].r, Chain[0].c) == (Chain[-1].r, Chain[-1].c):  # same cell
                    Cands0 = Cands[Chain[0].r][Chain[0].c] - {Chain[0].Cand, Chain[-1].Cand}
                    if Cands0: Status.Elims[str(Chain[0].r)+str(Chain[0].c)] = [Cands0]; Status.Pattern1 = [(Chain[0].r, Chain[0].c, sorted(Cands0))]
                else:
                    if Chain[-1].Cand in Cands[Chain[0].r][Chain[0].c]: Status.Pattern1.append((Chain[0].r, Chain[0].c, Chain[-1].Cand)); Status.Elims[str(Chain[0].r) + str(Chain[0].c)] = [Chain[-1].Cand]
                    if Chain[0].Cand in Cands[Chain[-1].r][Chain[-1].c]: Status.Pattern1.append((Chain[-1].r, Chain[-1].c, Chain[0].Cand)); Status.Elims[str(Chain[-1].r) + str(Chain[-1].c)] = [Chain[0].Cand]
                if Status.Elims: Status.Tech = T_AI_CHAIN_T2
            elif T_GL_AI_CHAIN_T2 in Methods and GrpLks and len(Chain[0].r) == len(Chain[-1].r) == len(Chain[0].c) == len(Chain[-1].c) == 1:
                Status.Elims = {}; Status.Pattern1 = []
                r0 = list(Chain[0].r)[0]; c0 = list(Chain[0].c)[0]; r1 = list(Chain[-1].r)[0]; c1 = list(Chain[-1].c)[0]
                if (Chain[0].r, Chain[0].c) == (Chain[-1].r, Chain[-1].c):  # same cell
                    Cands0 = Cands[r0][c0]-{Chain[0].Cand, Chain[-1].Cand}
                    if Cands0: Status.Elims[str(r0)+str(c0)] = [Cands0]; Status.Pattern1 = [(r0, c0, sorted(Cands0))]
                else:
                    if Chain[-1].Cand in Cands[r0][c0]: Status.Pattern1 = [(Chain[0].r, Chain[0].c, Chain[-1].Cand)]; Status.Elims[str(r0)+str(c0)] = [Chain[-1].Cand]
                    if Chain[0].Cand in Cands[r1][c1]: Status.Pattern1 = [(Chain[-1].r, Chain[-1].c, Chain[0].Cand)]; Status.Elims[str(r1)+str(c1)] = [Chain[0].Cand]
                if Status.Elims: Status.Tech = T_GL_AI_CHAIN_T2
        if Status.Tech != T_UNDEF and (Status.Elims or Status.Plcmts):
            Status.Pattern = []
            for i in range(len(Chain)-1):
                Status.Pattern.append(NL(Chain[i].r, Chain[i].c, Chain[i].Cand, Chain[i+1].Lk))
            Status.Pattern.append(NL(Chain[-1].r, Chain[-1].c, Chain[-1].Cand, LK_NONE))
            return True
    return False
