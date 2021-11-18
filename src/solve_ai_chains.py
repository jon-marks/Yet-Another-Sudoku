
from globals import *
from solve_utils import *

def tech_w_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_W_WING}: return -2
    return _ai_chains(Grid, Step, Cands, T_W_WING)

def tech_gl_w_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_GL_W_WING}: return -2
    return _ai_chains(Grid, Step, Cands, T_GL_W_WING, GrpLks = True)

def tech_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_SC_AI_CHAIN, T_DC_AI_CHAIN, T_EVEN_AI_LOOP, T_STRONG_AI_LOOP}: return -2
    return _ai_chains(Grid, Step, Cands, Method)

def tech_gl_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_GL_SC_AI_CHAIN, T_GL_DC_AI_CHAIN, T_GL_EVEN_AI_LOOP, T_GL_STRONG_AI_LOOP}: return -2
    return _ai_chains(Grid, Step, Cands, Method, GrpLks = True)


def _ai_chains(Grid, Step, Cands, Method, GrpLks = False):
    # Chains are found using trees.  AI-Chains need to start with strong links.
    # There is an orchard for each candidate (AIC[i]).  In each orchard,
    # each instance of the candidate is a potential tree trunk with up to four strong link branches.
    #
    # The algorithm builds this two tier strong link level across all trees in all orchards before
    # recursing to the next level.  This approach, albeit a bit more
    # complex tends to find a solution (if there is one) quicker than building a tree in the
    # conventional way (one leaf at a time).  This is because the odds of finding a shorter
    # productive (elimination/assignment producing) chain is greater than than of finding a longer
    # productive chain.  There is no significant time difference for an unproductive search in
    # either approach
    #
    # The chains being built are the paths from first branch off trunk to the leaf.  At each level,
    # for each new leaf (node or sub-branch) checks are performed to find a productive loop and/or
    # prune stubs or unproductive chain/loop patterns:
    # * If no child (sub-branch) links are found for a particular branch (node), this is a stub and
    #   is pruned.
    # * If the chain intersects itself (ccell match, not cell match) at any location other than the
    #   start of the chain, the chain is not valid and that node can be pruned.
    # * If the chain intersects its start, and forms an even-loop or strong loop pattern, check for
    #   eliminations/assignments making the loop productive.
    # * If an unproductive loop (even or strong) is encountered, this is treated as a stub and is
    #   pruned.
    # * If the loop is productive, return out the recursive stack with the pattern and outcome
    #   parameters.
    # * if the chain leaf is a strong link to it's branch (odd length AIC) and together with the
    #   starting link can see ccells to eliminate (either same candidate, or different candidate in
    #   same house); return up recursive stack with pattern and outcome parameters.
    #
    # An unproductive search occurs when all the trees for each candidate have been pruned back to
    # their trunks and the algorithm is stumped :-).

    ChLks = 0
#    Lvl = 0
    Status = STATUS()
    SLks, AIC = _find_ai_chain_starts(Cands, GrpLks)
#    walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
    CandsAIC = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    while CandsAIC:
#        Lvl += 1
        for i, Cand in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9]):
            if AIC[i]:
                AIC[i] = _find_next_aic_nodes(SLks, AIC[i], Cands, GrpLks, ChLks+1, Method, Status)
                if Status.Tech != T_UNDEF: return _ai_chain_elims(Status, Grid, Cands, Step)
            if not AIC[i] and Cand in CandsAIC: CandsAIC.remove(Cand)
#        walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
    return -1

def _find_ai_chain_starts(Cands, GrpLks = False):
    # Plants the trees in the candidate orchards, each tree can have upto four strong link branches
    # (row, col, box, and cell).

    SLks = [[], [], [], [], [], [], [], [], []]
    AICuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand in enumerate(range(1, 10)):
        SLks[i] = find_all_strong_cand_links(Cand, Cands, GrpLks)
        NSLks = len(SLks[i])
        UCS0 = []
        for j in range(NSLks):
            ((r0, c0, Cand0), (r1, c1, Cand1)) = SLks[i][j]
            if (r0, c0, Cand0) in UCS0: continue
            UCS0.append((r0, c0, Cand0))
            N = TNODE(r0, c0, Cand0, LK_NONE, None, None, None)
            N.Children = [TNODE(r1, c1, Cand1, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None)]
            UCS1 = [(r1, c1, Cand1)]
            for k in range(j+1, NSLks):
                # up to four slks possible (row, col, box and cell), scan the rest of the SLks for them
                ((r2, c2, Cand2), (r3, c3, Cand3)) = SLks[i][k]
                if not ccells_match(r0, c0, Cand0, r2, c2, Cand2, GrpLks): continue  # only looking for branches off trunk (r0, c0, Cand0)
                if (r3, c3, Cand3) in UCS1: continue  # dup SLk, skip.
                UCS1.append((r3, c3, Cand3))
                N.Children.append(TNODE(r3, c3, Cand3, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None))
            AICuc[i].append(N)
    return SLks, AICuc


def _find_next_aic_nodes(SLks, Children, Cands, GrpLks, ChLks, Method, Status):
    # Note: Pruning is achieved by not copying a child branch from the Children list to the Kids list.

    Kids = []
    for C in Children:
        if C.Children:  # Continue to recurse down the children.
            C.Children = _find_next_aic_nodes(SLks, C.Children, Cands, GrpLks, ChLks+1, Method, Status)
            if Status.Tech != T_UNDEF: return C
        else:  # at a leaf of the tree, try to grow some branches
            Lks1 = []
            # look for Ccells in the same cell first (other candidates in same cell)
            if GrpLks:
                if len(C.r) == len(C.c) == 1:
                    ra = list(C.r)[0]; ca = list(C.c)[0]
                    for Candx in sorted(Cands[ra][ca] - {C.Cand}):
                        for ((r0, c0, Cand0), (r1, c1, Cand1)) in SLks[Candx-1]:
                            if Cand0 == Cand1 and C.r == r0 and C.c == c0: Lks1.append(((r0, c0, Cand0), (r1, c1, Cand1)))
            else:
                for Candx in sorted(Cands[C.r][C.c] - {C.Cand}):
                    for ((r0, c0, Cand0), (r1, c1, Cand1)) in SLks[Candx-1]:
                        if Cand0 == Cand1 and C.r == r0 and C.c == c0: Lks1.append(((r0, c0, Cand0), (r1, c1, Cand1)))
            Ch0 = [*C.Chain, *[(C.r, C.c, C.Cand, LK_NONE)]]
            for ((r0, c0, Cand0), (r1, c1, Cand1)) in [*SLks[C.Cand-1], *Lks1]:
                pos = is_in_chain(r0, c0, Cand0, Ch0, GrpLks)  # LK_NONE as link to starting strong link has not been determined yet.
                if pos >= 0: continue
                # The ending strong link may only intersect the starting link of the chain being built.
                Ch1 = [*C.Chain, *[(C.r, C.c, C.Cand, LK_NONE), (r0, c0, Cand0, LK_STRG)]]
                pos = is_in_chain(r1, c1, Cand1, Ch1, GrpLks)
                if pos > 0: continue
                # if the starting strong link connects to the chain, add it to the list of children.
                LkT, LkH = how_ccells_linked(C.r, C.c, C.Cand, r0, c0, Cand0, Cands, GrpLks)
                if LkT == LK_NONE: continue
                if LkT != LK_WEAK: LkT = LK_WKST
                # C.Lk = LkT
                Ch0[-1] = (C.r, C.c, C.Cand, LkT)
                Ch1[-2] = (C.r, C.c, C.Cand, LkT)
                if pos == 0:  # a possible Strong AI Loop found. (impossible to form if #links <5)
                    if Method not in {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP}: continue
                    if GrpLks:  # The common ccell can only be a scalar, not grouped, with group no unique cell asgnmt can be made, therefore grouped is simply invalid intersecting ccells in the chain
                        ra, ca, Canda, Lka = Ch1[0]
                        if not (len(ra) == len(ca) == len(r1) == len(c1) == 1): continue
                        Status.Outcome = [(list(r1)[0], list(c1)[0], Cand1)]
                    else:
                        Status.Outcome = [(r1, c1, Cand1)]
                    Status.Tech = T_GL_STRONG_AI_LOOP if GrpLks else T_STRONG_AI_LOOP
                    Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
                    return C
                ra, ca, Canda, Lka = Ch1[0]
                if Method in {T_UNDEF, T_EVEN_AI_LOOP, T_GL_EVEN_AI_LOOP}:  # no intersection, check for an EVEN_AI_LOOP
                    LkT, LkH = how_ccells_linked(ra, ca, Canda, r1, c1, Cand1, Cands, GrpLks)
                    if LkT != LK_NONE:  # found EVEN_AI_LOOP pattern, scan for eliminations. In weak links, if in same cell then other cands, else if house, then other same value ccels not part of base set.
                        if LkT != LK_WEAK: LkT = LK_WKST
                        Ch2 = [*Ch1, *[(r1, c1, Cand1, LkT), (ra, ca, Canda, LK_NONE)]]
                        EL = []
                        for i in range(len(Ch2)-1):
                            r2, c2, Cand2, Lk2 = Ch2[i]
                            if Lk2 != LK_STRG:
                                r3, c3, Cand3, Lk3 = Ch2[i+1]
                                if Cand2 != Cand3:  # Cands are in the same cell, and if grplinks the cells must be scalars.
                                    if GrpLks: r4 = list(r2)[0]; c4 = list(c2)[0]
                                    else: r4 = r2; c4 = c2
                                    for Cand4 in sorted(Cands[r4][c4] - {Cand2, Cand3}):
                                        EL.append((r4, c4, Cand4))
                                else:  # same cands in a house
                                    for r4, c4 in cells_that_see_all_of([(r2, c2), (r3, c3)], GrpLks):  # cells_that_see_all_of handles both scalars and groups
                                        if Cand2 in Cands[r4][c4]:
                                            EL.append((r4, c4, Cand2))
                        if EL:
                            Status.Tech = T_GL_EVEN_AI_LOOP if GrpLks else T_EVEN_AI_LOOP
                            Status.Pattern = Ch2
                            Status.Outcome = EL
                            return C
                if Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN, T_W_WING, T_GL_W_WING}:  # Strongly ended chain, same candidates check for eliminations
                    if Canda == Cand1:  # same candidate value ending ccells
                        EL = []
                        for r2, c2 in cells_that_see_all_of([(r1, c1), (ra, ca)], GrpLks):
                            if Cand1 in Cands[r2][c2]: EL.append((r2, c2, Cand1))
                        if EL:
                            Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
                            # does this chain match the criteria for a W-Wing. a ==> node 0, b ==> node 1, 2 ==> node -2, 1==> node -1
                            rb, cb, Candb, Lkb = Status.Pattern[1]; r2, c2, Cand2, Lk2 = Status.Pattern[-2]
                            if Canda != Candb and Candb == Cand2:
                                NLks = len(Status.Pattern) - 1
                                if NLks < 5 and Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN}: Status.Tech = T_SC_AI_CHAIN
                                elif NLks == 5 and Method in {T_UNDEF, T_W_WING, T_GL_W_WING}: Status.Tech = T_W_WING
                                else: continue
                            elif Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN}: Status.Tech = T_SC_AI_CHAIN
                            else: continue
                            if GrpLks: Status.Tech |= T_GRPLK
                            Status.Outcome = EL
                            return C
                if Method in {T_UNDEF, T_DC_AI_CHAIN, T_GL_DC_AI_CHAIN}:  # different value candidates
                    if Canda != Cand1:  # Different candidate value ending ccells
                        EL = []
                        if GrpLks:
                            if len(ra) == len(ca) == len(r1) == len(c1) == 1:  # only scalar end ccells, eliminations not possible if grouped
                                ras = list(ra)[0]; cas = list(ca)[0]; r1s = list(r1)[0]; c1s = list(c1)[0]
                                if ras == r1s and cas == c1s:
                                    if len(Cands[r1s][c1s]) > 2: EL.append((r1s, c1s, Cands[r1s][c1s] - {Cand1 | Canda}))
                                elif cells_in_same_house(ras, cas, r1s, c1s):
                                    if Cand1 in Cands[ras][cas]: EL.append((ras, cas, Cand1))
                                    if Canda in Cands[r1s][c1s]: EL.append((r1s, c1s, Canda))
                        else:
                            if ra == r1 and ca == c1:
                                if len(Cands[r1][c1]) >2: EL.append((r1, c1, Cands[r1][c1] - {Cand1 | Canda}))
                            elif cells_in_same_house(ra, ca, r1, c1):
                                if Cand1 in Cands[ra][ca]: EL.append((ra, ca, Cand1))
                                if Canda in Cands[r1][c1]: EL.append((r1, c1, Canda))
                        if EL:
                            Status.Tech = T_GL_DC_AI_CHAIN if GrpLks else T_DC_AI_CHAIN
                            Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
                            # Status.Pattern = [*C.Chain, *[(C.r, C.c, C.Cand, LK_STRG), (r, c, Cand, LK_NONE)]]
                            Status.Outcome = EL
                            return C
                # Algorithm ends up here when the strong link is part of the valid chain and there was no complete AI-Chain pattern identified and resolved.
                if Method in {T_W_WING, T_GL_W_WING} and len(C.Chain) >= 4: continue
                C.Children.append(TNODE(r0, c0, Cand0, LkT, Ch0, C))
                C.Children[-1].Children.append(TNODE(r1, c1, Cand1, LK_STRG, Ch1, C.Children[-1]))
        if C.Children: Kids.append(C)
    return Kids



def _ai_chain_elims(S, Grid, Cands, Step):

    Step[P_TECH] = S.Tech
    NLks = NGrpLks = 0
    for r, c, Cand, Lk, in S.Pattern:
        NLks += 1
        if not isinstance(r, int) and len(r) > 1: NGrpLks += 1
        if not isinstance(c, int) and len(c) > 1: NGrpLks += 1
        if Lk == LK_NONE: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_END, ]])
        else: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
    Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NLks - NGrpLks) * KRAKEN_LK_DIFF + NGrpLks * GRP_LK_DIFF
    if S.Tech in {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP}:
        r, c, Cand = S.Outcome[0]
        Grid[r][c] = Cand
        Cands[r][c].clear()
        discard_cand_from_peers(Cand, r, c, Cands)
        Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END, ]]
        return 1
    else:  # Eliminations
        for r, c, Cand in S.Outcome:
            Cands[r][c].discard(Cand)
            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
        Step[P_OUTC].append([P_END, ])
        return 0
