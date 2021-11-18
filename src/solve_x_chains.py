
from globals import *
from solve_utils import *


def tech_three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_SKYSCRAPER, T_TWO_STRING_KITE, T_TURBOT_FISH}: return -2
    return _three_link_x_chains(Grid, Step, Cands, Method)

def tech_gl_three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_GL_SKYSCRAPER, T_GL_TWO_STRING_KITE, T_GL_TURBOT_FISH}: return -2
    return _three_link_x_chains(Grid, Step, Cands, Method, GrpLks = True)

def tech_other_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_X_CHAIN, T_EVEN_X_LOOP, T_STRONG_X_LOOP}: return -2
    return _x_chains(Grid, Step, Cands, Method)

def tech_gl_other_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method not in {T_UNDEF, T_GL_X_CHAIN, T_GL_EVEN_X_LOOP, T_GL_STRONG_X_LOOP}: return -2
    return _x_chains(Grid, Step, Cands, Method, GrpLks = True)

def _three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF, GrpLks = False):
    # Chains are found using trees.  X-Chains need to start with strong links.
    # There is an orchard for each candidate (XCuc[i]).  In each orchard,
    # each instance of the candidate is a potential tree trunk with up to three
    # strong link branches (row, col and box.
    #
    # The algorithm builds this two tier strong link level across all trees in all orchards
    # before recursing to the next level.  This approach, albeit a bit more
    # complex tends to find a solution (if there is one) quicker than building a tree in the
    # conventional way (one leaf at a time).  This is because the odds of finding a shorter
    # productive (elimination/assignment producing) chain is greater than than of finding a longer
    # productive chain.  There is no significant time difference for an unproductive search in
    # either approach

    ChLks = 0
    Status = STATUS()
    Lks, XCuc = _find_x_chain_starts(Cands, GrpLks)

    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        if XCuc[i]:
            XCuc[i] = _find_next_xc_nodes(Lks[i], XCuc[i], Cands, GrpLks, ChLks+1, Method, Status)
            if Status.Tech != T_UNDEF: return _x_chain_elims(Status, Grid, Cands, Step)
    return -1

def _x_chains(Grid, Step, Cands, Method, GrpLks = False):
    # Because complexity is related to chain length and the algorithm seeks to find patterns from
    # simplest to complex, all candidates at a certain chain length are explored before advancing
    # to a longer chain length  XCuc ==> X-Chain under construction structure.

    ChLks = 0
    #    Lvl = 0
    Status = STATUS()
    Lks, XCuc = _find_x_chain_starts(Cands, GrpLks)
    #    walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
    CandsXC = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    while CandsXC:
        #        Lvl += 1
        for i, Cand in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9]):
            if XCuc[i]:
                XCuc[i] = _find_next_xc_nodes(Lks[i], XCuc[i], Cands, GrpLks, ChLks+1, Method, Status)
                if Status.Tech != T_UNDEF: return _x_chain_elims(Status, Grid, Cands, Step)
            if not XCuc[i] and Cand in CandsXC: CandsXC.remove(Cand)
#        walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
    return -1

def _find_x_chain_starts(Cands, GrpLks = False):
    # Plants the trees in the candidate orchards, each tree can have upto three strong link branches
    # (row, col, box).

    # First build the list of strong links.
    Lks = [[], [], [], [], [], [], [], [], []]
    XCuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand in enumerate(range(1, 10)):
        Lks[i] = find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks)

        # Create a node for each end of the links
        NLks = len(Lks[i])
        UCS0 = []
        for j in range(NLks-1):
            ((r0, c0, Cand0), (r1, c1, Cand1)) = Lks[i][j]
            if (r0, c0, Cand0) in UCS0: continue
            UCS0.append((r0, c0, Cand0))
            N = TNODE(r0, c0, Cand0, LK_NONE, None, None, None)
            N.Children = [TNODE(r1, c1, Cand1, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None)]
            UCS1 = [(r1, c1, Cand1)]
            for k in range(j+1, NLks):
                # up to three slks possible (row, col, box and cell), scan for the rest of the SLks for them
                ((r2, c2, Cand2), (r3, c3, Cand3)) = Lks[i][k]
                if not ccells_match(r0, c0, Cand0, r2, c2, Cand2, GrpLks): continue  # only looking for branches off trunk (r0, c0, Cand0)
                if (r3, c3, Cand3) in UCS1: continue  # dup SLk, skip.
                UCS1.append((r3, c3, Cand3))
                N.Children.append(TNODE(r3, c3, Cand3, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None))
            XCuc[i].append(N)
    return Lks, XCuc

def _find_next_xc_nodes(SLks, Children, Cands, GrpLks, ChLks, Method, Status):
    # Note: Pruning is achieved by not copying a child branch from the Children list to the Kids list.

    Kids = []
    for C in Children:
        if C.Children:  # Continue to recurse down the children.
            C.Children = _find_next_xc_nodes(SLks, C.Children, Cands, GrpLks, ChLks+1, Method, Status)
            if Status.Tech != T_UNDEF: return C
        else:  # at a leaf of the tree, try to grow some branches
            # i = -1
            Ch0 = [*C.Chain, *[(C.r, C.c, C.Cand, LK_NONE)]]
            for ((r0, c0, Cand0), (r1, c1, Cand1)) in SLks:
                pos = is_in_chain(r0, c0, Cand0, Ch0, GrpLks)  # LK_NONE as link to starting strong link has not been determined yet.
                if pos >= 0: continue
                # The ending strong link may only intersect the starting link of the chain being built.
                Ch1 = [*Ch0, *[(r0, c0, Cand0, LK_STRG)]]
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
                    if Method not in {T_STRONG_X_LOOP, T_GL_STRONG_X_LOOP}: continue
                    if GrpLks:  # The common ccell can only be a scalar, not grouped, with group no unique cell asgnmt can be made, therefore grouped is simply invalid intersecting ccells in the chain
                        ra, ca, Canda, Lka = Ch1[0]
                        if not (len(ra) == len(ca) == len(r1) == len(c1) == 1): continue
                        Status.Outcome = [(list(r1)[0], list(c1)[0], Cand1)]
                    else:
                        Status.Outcome = [(r1, c1, Cand1)]
                    Status.Tech = T_GL_STRONG_X_LOOP if GrpLks else T_STRONG_X_LOOP
                    Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
                    return C
                ra, ca, Canda, Lka = Ch1[0]
                if Method in {T_UNDEF, T_EVEN_X_LOOP, T_GL_EVEN_X_LOOP}:  # no intersection, check for an EVEN_AI_LOOP
                    LkT, LkH = how_ccells_linked(ra, ca, Canda, r1, c1, Cand1, Cands, GrpLks)
                    if LkT != LK_NONE:  # found EVEN_X_LOOP pattern, scan for eliminations
                        if LkT != LK_WEAK: LkT = LK_WKST
                        # Ch2 = [*Ch1[:-1], *[(r1, c1, Cand1, LkT), (ra, ca, Canda, LK_NONE)]]
                        Ch2 = [*Ch1, *[(r1, c1, Cand1, LkT), (ra, ca, Canda, LK_NONE)]]
                        EL = []
                        for i in range(len(Ch2)-1):
                            r2, c2, Cand2, Lk2 = Ch2[i]
                            if Lk2 != LK_STRG:
                                r3, c3, Cand3, Lk3 = Ch2[i+1]
                                for r4, c4 in cells_that_see_all_of([(r2, c2), (r3, c3)], GrpLks):  # cells_that_see_all_of handles both scalars and groups
                                    if Canda in Cands[r4][c4]: EL.append((r4, c4, Canda))
                        if EL:
                            Status.Tech = T_GL_EVEN_X_LOOP if GrpLks else T_EVEN_X_LOOP
                            Status.Pattern = Ch2
                            Status.Outcome = EL
                            return C
                if Method in {T_UNDEF, T_GL_X_CHAIN, T_GL_SKYSCRAPER, T_GL_TWO_STRING_KITE, T_GL_TURBOT_FISH, T_X_CHAIN, T_SKYSCRAPER, T_TWO_STRING_KITE, T_TURBOT_FISH}:  # Strongly ended chain, same candidates check for eliminations
                    if Canda == Cand1:  # same candidate value ending ccells
                        EL = []
                        for r2, c2 in cells_that_see_all_of([(r1, c1), (ra, ca)], GrpLks):
                            if Cand1 in Cands[r2][c2]: EL.append((r2, c2, Cand1))
                        if EL:
                            # if there is a three link chain: (ie 3 link patterns)
                            #   len(Ch1) == 3, node 0 = (ra, ca), node 1 = (C.r, C.c), node 2 = (r0, c0), node 3 = (r1, c1)
                            if len(Ch1) == 3:
                                Lh0 = link_house(ra, ca, C.r, C.c, GrpLks)
                                Lh1 = link_house(C.r, C.c, r0, c0, GrpLks)
                                Lh2 = link_house(r0, c0, r1, c1, GrpLks)
                                if Lh0 & LK_LINE == Lh1 & LK_LINE == Lh2 & LK_LINE == LK_LINE: s = T_SKYSCRAPER
                                elif Lh0 & LK_LINE == Lh2 & LK_LINE == LK_LINE and Lh1 == LK_BOX: s = T_TWO_STRING_KITE
                                else: s = T_TURBOT_FISH
                            else: s = T_X_CHAIN
                            if GrpLks: s |= T_GRPLK
                            if Method in {T_UNDEF, s}:
                                Status.Tech = s
                                Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
                                Status.Outcome = EL
                                return C
                # Algorithm ends up here when the strong link is part of the valid chain and there was no complete AI-Chain pattern identified and resolved.
                C.Children.append(TNODE(r0, c0, Cand0, LkT, Ch0, C))
                C.Children[-1].Children.append(TNODE(r1, c1, Cand1, LK_STRG, Ch1, C.Children[-1]))
        if C.Children: Kids.append(C)
    return Kids

def _x_chain_elims(S, Grid, Cands, Step):
    Step[P_TECH] = S.Tech
    NLks = NGrpLks = 0
    for r, c, Cand, Lk, in S.Pattern:
        NLks += 1
        if not isinstance(r, int) and len(r) > 1: NGrpLks += 1
        if not isinstance(c, int) and len(c) > 1: NGrpLks += 1
        if Lk == LK_NONE: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_END, ]])
        else: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
    Step[P_DIFF] = T[Step[P_TECH]][T_DIFF]+(NLks-NGrpLks)*KRAKEN_LK_DIFF+NGrpLks*GRP_LK_DIFF
    if S.Tech in {T_STRONG_X_LOOP, T_GL_STRONG_X_LOOP}:
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
