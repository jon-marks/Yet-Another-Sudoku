
from globals import *
from solve_utils import *

def tech_ai_chains(Grid, Step, Cands, Methods):
    return ai_chains(Grid, Step, Cands, Methods, False)

def tech_gl_ai_chains(Grid, Step, Cands, Methods):
    return ai_chains(Grid, Step, Cands, Methods, True)

def ai_chains(Grid, Step, Cands, Methods, GrpLks = False):

    Forest = []
    for Cand in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in list_all_cand_strong_links(Cand, Cands, GrpLks, True):
            Forest.append(TREE(r0, c0, Cand0, None, TNODE(r1, c1, Cand1, Lk1, [NL(r0, c0, Cand0, Lk0), NL(r1, c1, Cand1, Lk1)])))
            # All saplings planted.
    while Forest:
        Culls = set()  # trees to cull, use set to avoid dups.
        Status = STATUS()
        for Tree in Forest:
            find_next_ai_child_nodes(Tree.Branch, Cands, 1, Tree, Methods, Status, GrpLks)
            if Status.Tech != T_UNDEF: break
            if not Tree.Branch.Children:  Culls.add(Tree)
        if Status.Tech != T_UNDEF:
            Step.Method = Status.Tech
            if Status.Tech == T_W_WING:
                P = Status.Pattern
                Step.Pattern = [[P_OP, OP_PARO], [P_VAL, P[0].Cand], [P_OP, OP_SLK], [P_VAL, P[1].Cand], [P_OP, OP_PARC], [P_ROW, P[0].r], [P_COL, P[0].c],
                                [P_OP, token_link(P[1].Lk & 0x000f)], [P_VAL, P[2].Cand], [P_ROW, P[2].r], [P_COL, P[2].c],
                                [P_OP, OP_SLK], [P_VAL, P[3].Cand], [P_ROW, P[3].r], [P_COL, P[3].c], [P_OP, token_link(P[3].Lk & 0x000f)],
                                [P_OP, OP_PARO], [P_VAL, P[4].Cand], [P_OP, OP_SLK], [P_VAL, P[5].Cand], [P_OP, OP_PARC], [P_ROW, P[5].r], [P_COL, P[5].c], [P_END]]
            else:
                Step.NrLks = Step.NrGrpLks = 0
                Step.Pattern = []; Step.Outcome = []
                for r, c, Cand, Lk, in Status.Pattern:
                    Step.NrLks += 1
                    if Step.Method & T_GRPLK:
                        if len(r) > 1: Step.NrGrpLks += 1
                        if len(c) > 1: Step.NrGrpLks += 1
                    Step.Pattern.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk & 0x000f)]])
                Step.Pattern.append([P_END])
            if Status.Tech in {T_DC_IBVC_AI_CHAIN, T_STRONG_AI_LOOP, T_GL_DC_IBVC_AI_CHAIN, T_GL_STRONG_AI_LOOP}:
                n = 0
                for r, c, Cand in Status.Outcome:
                    n += 1
                    Grid[r][c] = Cand
                    Cands[r][c].clear()
                    discard_cand_from_peers(Cand, r, c, Cands)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand]])
                Step.Outcome.append([P_END, ])
                return n
            else:  # Eliminations
                for r, c, Cand in Status.Outcome:
                    Cands[r][c].discard(Cand)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                Step.Outcome.append([P_END, ])
                return 0
        for Tree in Culls: Forest.remove(Tree)
    return -1

def find_next_ai_child_nodes(Child, Cands, Lvl, Tree, Methods, Status, GrpLks = False):

    if Child.Children:
        OddPrunes = set()
        for GChild in Child.Children:
            EvenPrunes = set()
            for GGChild in GChild.Children:
                find_next_ai_child_nodes(GGChild, Cands, Lvl+1, Tree, Methods, Status, GrpLks)
                if Status.Tech != T_UNDEF: return  # don't waste any time when soln found.
                if not GGChild.Children: EvenPrunes.add(GGChild)
            for GGChild in EvenPrunes: GChild.Children.remove(GGChild)
            if not GChild.Children: OddPrunes.add(GChild)
        for GChild in OddPrunes: Child.Children.remove(GChild)
    else:  # at the leaves, attempt to add the next weak and strong links.
        for r1, c1, Cand1, Lk1 in list_ccells_linked_to(Child.r, Child.c, Child.Cand, Cands, LK_STWK, GrpLks):
            for (rx, cx, Candx, Lkx) in Child.Chain:
                if ccells_intersect(r1, c1, Cand1, rx, cx, Candx, GrpLks): break
            else:
                if Lk1 & LK_STRG: Lk1 = (Lk1 & 0x01f0) | LK_WKST
                else: Lk1 = (Lk1 &0x01f0) | LK_WEAK
                Node1 = TNODE(r1, c1, Cand1, Lk1, [*Child.Chain, NL(r1, c1, Cand1, Lk1)], Child)
                for r2, c2, Cand2, Lk2 in list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STRG, GrpLks):
                    if Lvl > 1 and (r2, c2, Cand2) == (Tree.r, Tree.c, Tree.Cand):
                        Status.Outcome = []
                        if GrpLks and T_GL_STRONG_AI_LOOP in Methods and len(r2) == len(c2) ==1:
                            Status.Outcome = [(list(r2)[0], list(c2)[0], Cand2)]
                            Status.Tech = T_GL_STRONG_AI_LOOP
                        elif ~GrpLks and T_STRONG_AI_LOOP in Methods:
                            Status.Outcome = [(r2, c2, Cand2)]
                            Status.Tech = T_STRONG_AI_LOOP
                        if Status.Outcome:
                            Status.Pattern = []
                            for i in range(len(Node1.Chain)-1):
                                Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Node1.Chain[i].Cand, Node1.Chain[i+1].Lk))
                            Status.Pattern.append(NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Node1.Chain[-1].Cand, Lk2))
                            return
                        # if Lvl > 1 and {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP} & set(Methods):
                        #     Status.Outcome = []
                        #     if GrpLks:
                        #     else:
                        #         Status.Outcome = [(r2, c2, Cand2)]
                        #         Status.Tech = T_STRONG_AI_LOOP
                        #     Status.Pattern = []
                        #     for i in range(len(Node1.Chain)-1):
                        #         Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Cand2, Node1.Chain[i+1].Lk))
                        #     Status.Pattern.append(NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Cand2, Lk2))
                        #     return
                    for rx, cx, Candx, Lkx in Child.Chain:
                        if ccells_intersect(r2, c2, Cand2, rx, cx, Candx, GrpLks): break
                    else:
                        Lk = how_ccells_linked(r2, c2, Cand2, Tree.r, Tree.c, Tree.Cand, Cands, GrpLks)
                        if Lk:  # Even AI-Loop found.
                            if {T_EVEN_AI_LOOP, T_GL_EVEN_AI_LOOP} & set(Methods):
                                if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
                                Status.Pattern = []
                                for i in range(len(Node1.Chain)-1):
                                    Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Node1.Chain[i].Cand, Node1.Chain[i+1].Lk))
                                Status.Pattern.extend([NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Node1.Chain[-1].Cand, Lk2), NL(r2, c2, Cand2, Lk)])
                                Status.Outcome = []
                                for i in range(1, len(Status.Pattern)-1, 2):
                                    if Status.Pattern[i].Lk & 0x000f == LK_WEAK:
                                        Status.Outcome.extend(link_elims(Status.Pattern[i].r, Status.Pattern[i].c, Status.Pattern[i].Cand,
                                                              Status.Pattern[i+1].r, Status.Pattern[i+1].c, Status.Pattern[i+1].Cand,
                                                              Cands, GrpLks))
                                if Status.Pattern[-1].Lk & 0x000f == LK_WEAK:
                                    Status.Outcome.extend(link_elims(Status.Pattern[-1].r, Status.Pattern[-1].c, Status.Pattern[-1].Cand,
                                                                     Status.Pattern[0].r, Status.Pattern[0].c, Status.Pattern[0].Cand,
                                                                     Cands, GrpLks))
                                if Status.Outcome:  # AI-Loop with Elimination found.
                                    Status.Tech = T_GL_EVEN_AI_LOOP if GrpLks else T_EVEN_AI_LOOP
                                    return
                        else:  # look for AI-Chains
                            Status.Outcome = []; Status.Tech = T_UNDEF
                            if Tree.Cand == Cand2:  # same value end candidates.
                                for r3, c3 in cells_that_see_all_of([(r2, c2), (Tree.r, Tree.c)], GrpLks):
                                    if Cand2 in Cands[r3][c3]: Status.Outcome.append((r3, c3, Cand2))
                                if Status.Outcome:
                                    if T_W_WING in Methods and ~GrpLks and Lvl == 2 and Node1.Chain[1].Lk & Lk2 & LK_CELL \
                                            and Cands[Tree.r][Tree.c] == Cands[r2][c2]: Status.Tech = T_W_WING
                                    elif {T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN} & set(Methods): Status.Tech = T_GL_SC_AI_CHAIN if GrpLks else T_SC_AI_CHAIN
                            elif cells_in_same_house(Tree.r, Tree.c, r2, c2, GrpLks):
                                if T_DC_IBVC_AI_CHAIN in Methods and ~GrpLks \
                                        and not(Tree.r == r2 and Tree.c == c2) \
                                        and Cands[Tree.r][Tree.c] == Cands[r2][c2]:
                                    Status.Tech = T_DC_IBVC_AI_CHAIN
                                    Status.Outcome = [(Tree.r, Tree.c, Tree.Cand), (r2, c2, Cand2)]
                                elif T_GL_DC_IBVC_AI_CHAIN in Methods and GrpLks \
                                        and not(Tree.r == r2 and Tree.c == c2) \
                                        and len(Tree.r) == len(Tree.c) == len(r2) == len(c2) == 1 \
                                        and Cands[list(Tree.r)[0]][list(Tree.c)[0]] == Cands[list(r2)[0]][list(c2)[0]]:
                                    Status.Tech = T_GL_DC_IBVC_AI_CHAIN
                                    Status.Outcome = [(list(Tree.r)[0], list(Tree.c)[0], Tree.Cand), (list(r2)[0], list(c2)[0], Cand2)]
                                elif T_DC_AI_CHAIN in Methods and ~GrpLks:
                                    Status.Tech = T_DC_AI_CHAIN
                                    if Tree.r == r2 and Tree.c == c2:  # same cell
                                        Status.Outcome = [(r2, c2, Cands[r2][c2] - {Tree.Cand, Cand2})]
                                    else:
                                        if Cand2 in Cands[Tree.r][Tree.c]: Status.Outcome.append((Tree.r, Tree.c, Cand2))
                                        if Tree.Cand in Cands[r2][c2]: Status.Outcome.append((r2, c2, Tree.Cand))
                                elif T_GL_DC_AI_CHAIN in Methods and GrpLks and \
                                        len(Tree.r) == len(Tree.c) == len(r2) == len(c2) == 1:
                                    Status.Tech = T_GL_DC_AI_CHAIN
                                    if Tree.r == r2 and Tree.c == c2:  # same cell
                                        Status.Outcome = [(list(r2)[0], list(c2)[0], Cands[list(r2)[0]][list(c2)[0]] - {Tree.Cand, Cand2})]
                                    else:
                                        if Cand2 in Cands[list(Tree.r)[0]][list(Tree.c)[0]]: Status.Outcome.append((list(Tree.r)[0], list(Tree.c)[0], Cand2))
                                        if Tree.Cand in Cands[list(r2)[0]][list(c2)[0]]: Status.Outcome.append((list(r2)[0], list(c2)[0], Tree.Cand))
                            if Status.Tech != T_UNDEF and Status.Outcome:
                                Status.Pattern = []
                                for i in range(len(Node1.Chain)-1):
                                    Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Node1.Chain[i].Cand, Node1.Chain[i+1].Lk))
                                Status.Pattern.extend([NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Node1.Chain[-1].Cand, Lk2), NL(r2, c2, Cand2, LK_NONE)])
                                return
                            else: Status.Tech = T_UNDEF; Status.Outcome = []
                        Node1.Children.append(TNODE(r2, c2, Cand2, Lk2, [*Node1.Chain, NL(r2, c2, Cand2, Lk2)], Node1))
                if Node1.Children: Child.Children.append(Node1)
        # Soln not found yet, has recursion bottomed out.
        if Lvl > RECURSE_LIM:
            Child.Children = []
            return

    # if Lvl > 1 and {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP} & set(Methods):
    #     Status.Outcome = []
    #     if (r2, c2, Cand2) == (Tree.r, Tree.c, Tree.Cand):
    #         if GrpLks:
    #             Status.Outcome = [(list(r1)[0], list(c1)[0], Cand1)]
    #             Status.Tech = T_GL_STRONG_AI_LOOP
    #         else:
    #             Status.Outcome = [(r2, c2, Cand1)]
    #             Status.Tech = T_STRONG_AI_LOOP
    #         Status.Pattern = []
    #         for i in range(len(Node1.Chain)-1):
    #             Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Cand2, Node1.Chain[i+1].Lk))
    #         Status.Pattern.append(NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Cand2, Lk2))
    #         return
    # for rx, cx, Candx, Lkx in Child.Chain:
    #     if ccells_intersect(r2, c2, Cand2, rx, cx, Candx, GrpLks): break
    # else:
    #     if {T_EVEN_AI_LOOP, T_GL_EVEN_AI_LOOP} & set(Methods):
    #         Lk = how_ccells_linked(r2, c2, Cand2, Tree.r, Tree.c, Tree.Cand, Cands, GrpLks)
    #         if Lk:  # Even AI-Loop found.
    #             if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
    #             Status.Pattern = []
    #             for i in range(len(Node1.Chain)-1):
    #                 Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Node1.Chain[i].Cand, Node1.Chain[i+1].Lk))
    #             Status.Pattern.extend([NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Node1.Chain[-1].Cand, Lk2), NL(r2, c2, Cand2, Lk)])
    #             Status.Outcome = []
    #             for i in range(len(Status.Pattern)-1):
    #                 if Status.Pattern[i].Lk & 0x0f == LK_WEAK:
    #                     for rx, cx in cells_that_see_all_of([(Status.Pattern[i].r, Status.Pattern[i].c), (Status.Pattern[i+1].r, Status.Pattern[i+1].c)], GrpLks):
    #                         if Cand1 in Cands[rx][cx]:  Status.Outcome.append((rx, cx, Cand1))
    #             if Status.Pattern[-1].Lk & 0x0f == LK_WEAK:
    #                 for rx, cx in cells_that_see_all_of([(Status.Pattern[-1].r, Status.Pattern[-1].c), (Status.Pattern[0].r, Status.Pattern[0].c)], GrpLks):
    #                     if Cand1 in Cands[rx][cx]:  Status.Outcome.append((rx, cx, Cand1))
    #             if Status.Outcome:  # AI-Loop with Elimination found.
    #                 Status.Tech = T_GL_EVEN_AI_LOOP if GrpLks else T_EVEN_AI_LOOP
    #                 return

    #
#
#
#
#     if T_W_WING in Methods and ~GrpLks and Lvl == 2 and Node1.Chain[1].Lk & Lk2 & LK_CELL \
#             and Cands[Tree.r][Tree.c] == Cands[r2][c2]: Status.Tech = T_W_WING
#     elif {T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN} & set(Methods): Status.Tech = T_GL_SC_AI_CHAIN if GrpLks else T_SC_AI_CHAIN
#     if Status.Tech != T_UNDEF:
#         for r3, c3 in cells_that_see_all_of([(r2, c2), (Tree.r, Tree.c)], GrpLks):
#             if Cand2 in Cands[r3][c3]: Status.Outcome.append((r3, c3, Cand2))
# elif cells_in_same_house(Tree.r, Tree.c, r2, c2, GrpLks):  # Tree.Cand != Cand2
#
#
#
#

#     if T_DC_AI_CHAIN in Methods and ~GrpLks: Status.Tech = T_DC_AI_CHAIN
#     elif T_GL_DC_AI_CHAIN in Methods and GrpLks and \
#             len(Tree.r) == len(Tree.c) == len(r2) == len(c2) == 1: Status.Tech = T_GL_DC_AI_CHAIN
#     if Status.Tech != T_UNDEF:
#         if Tree.r == r2 and Tree.c == c2:
#             Status.Outcome = [(r2, c2, Cands[r2][c2] - {Tree.Cand, Cand2})]
#         else:
#             if Cand2 in Cands[Tree.r][Tree.c]: Status.Outcome.append((Tree.r, Tree.c, Cand2))
#             if Tree.Cand in Cands[r2][c2]: Status.Outcome.append((r2, c2, Tree.Cand))
#     elif T_DC_IBVC_AI_CHAIN in Methods and ~GrpLks \
#             and not(Tree.r == r2 and Tree.c == c2) and cells_in_same_house(Tree.r, Tree.c, r2, c2) \
#             and Cands[Tree.r][Tree.c] == Cands[r2][c2]: Status.Tech = T_DC_IBVC_AI_CHAIN
#     elif T_GL_DC_IBVC_AI_CHAIN in Methods and GrpLks \
#             and not(Tree.r == r2 and Tree.c == c2) and cells_in_same_house(Tree.r, Tree.c, r2, c2) \
#             and Cands[Tree.r][Tree.c] == Cands[r2][c2] \
#             and len(Tree.r) == len(Tree.c) == len(r2) == len(c2) == 1 and cells_in_same_house(Tree.r, Tree.c, r2, c2, GrpLks):  Status.Tech = T_GL_DC_IBVC_AI_CHAIN
#     if Status.Tech != T_UNDEF:
#         if Cands[Tree.r][Tree.c] == Cands[r2][c2]:
#             Status.Outcome = [(Tree.r, Tree.c, Tree.Cand), (r2, c2, Cand2)]
# if Status.Tech != T_UNDEF and Status.Outcome:
#     Status.Pattern = []
#     for i in range(len(Node1.Chain)-1):
#         Status.Pattern.append(NL(Node1.Chain[i].r, Node1.Chain[i].c, Node1.Chain[i].Cand, Node1.Chain[i+1].Lk))
#     Status.Pattern.extend([NL(Node1.Chain[-1].r, Node1.Chain[-1].c, Node1.Chain[-1].Cand, Lk2), NL(r2, c2, Cand2, LK_NONE)])
#     return

#
#
#
#
#
#
#
# # # TODO merge W_WINGS into ai_chains.
# # def tech_w_wings(Grid, Step, Cands, Method):
# #     if Method not in {T_UNDEF, T_W_WING}: return -2
# #     return _ai_chains(Grid, Step, Cands, T_W_WING)
# #
# # def tech_gl_w_wings(Grid, Step, Cands, Method = T_UNDEF):
# #     if Method not in {T_UNDEF, T_GL_W_WING}: return -2
# #     return _ai_chains(Grid, Step, Cands, T_GL_W_WING, GrpLks = True)
# #
# # def tech_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
# #     if Method not in {T_UNDEF, T_SC_AI_CHAIN, T_DC_AI_CHAIN, T_EVEN_AI_LOOP, T_STRONG_AI_LOOP}: return -2
# #     return _ai_chains(Grid, Step, Cands, Method)
# #
# # def tech_gl_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
# #     if Method not in {T_UNDEF, T_GL_SC_AI_CHAIN, T_GL_DC_AI_CHAIN, T_GL_EVEN_AI_LOOP, T_GL_STRONG_AI_LOOP}: return -2
# #     return _ai_chains(Grid, Step, Cands, Method, GrpLks = True)
# #
#
# def _ai_chains(Grid, Step, Cands, Method, GrpLks = False):
#     # Chains are found using trees.  AI-Chains need to start with strong links.
#     # There is an orchard for each candidate (AIC[i]).  In each orchard,
#     # each instance of the candidate is a potential tree trunk with up to four strong link branches.
#     #
#     # The algorithm builds this two tier strong link level across all trees in all orchards before
#     # recursing to the next level.  This approach, albeit a bit more
#     # complex tends to find a solution (if there is one) quicker than building a tree in the
#     # conventional way (one leaf at a time).  This is because the odds of finding a shorter
#     # productive (elimination/assignment producing) chain is greater than than of finding a longer
#     # productive chain.  There is no significant time difference for an unproductive search in
#     # either approach
#     #
#     # The chains being built are the paths from first branch off trunk to the leaf.  At each level,
#     # for each new leaf (node or sub-branch) checks are performed to find a productive loop and/or
#     # prune stubs or unproductive chain/loop patterns:
#     # * If no child (sub-branch) links are found for a particular branch (node), this is a stub and
#     #   is pruned.
#     # * If the chain intersects itself (ccell match, not cell match) at any location other than the
#     #   start of the chain, the chain is not valid and that node can be pruned.
#     # * If the chain intersects its start, and forms an even-loop or strong loop pattern, check for
#     #   eliminations/assignments making the loop productive.
#     # * If an unproductive loop (even or strong) is encountered, this is treated as a stub and is
#     #   pruned.
#     # * If the loop is productive, return out the recursive stack with the pattern and outcome
#     #   parameters.
#     # * if the chain leaf is a strong link to it's branch (odd length AIC) and together with the
#     #   starting link can see ccells to eliminate (either same candidate, or different candidate in
#     #   same house); return up recursive stack with pattern and outcome parameters.
#     #
#     # An unproductive search occurs when all the trees for each candidate have been pruned back to
#     # their trunks and the algorithm is stumped :-).
#
#     ChLks = 0
# #    Lvl = 0
#     Status = STATUS()
#     SLks, AIC = _find_ai_chain_starts(Cands, GrpLks)
# #    walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
#     CandsAIC = [1, 2, 3, 4, 5, 6, 7, 8, 9]
#     while CandsAIC:
# #        Lvl += 1
#         for i, Cand in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9]):
#             if AIC[i]:
#                 AIC[i] = _find_next_aic_nodes(SLks, AIC[i], Cands, GrpLks, ChLks+1, Method, Status)
#                 if Status.Tech != T_UNDEF: return _ai_chain_elims(Status, Grid, Cands, Step)
#             if not AIC[i] and Cand in CandsAIC: CandsAIC.remove(Cand)
# #        walk_ai_trees(AIC, f"scratch/tree{Lvl}.txt")
#     return -1
#
# def _find_ai_chain_starts(Cands, GrpLks = False):
#     # Plants the trees in the candidate orchards, each tree can have upto four strong link branches
#     # (row, col, box, and cell).
#
#     SLks = [[], [], [], [], [], [], [], [], []]
#     AICuc = [[], [], [], [], [], [], [], [], []]
#     for i, Cand in enumerate(range(1, 10)):
#         SLks[i] = find_all_strong_cand_links(Cand, Cands, GrpLks)
#         NSLks = len(SLks[i])
#         UCS0 = []
#         for j in range(NSLks):
#             ((r0, c0, Cand0), (r1, c1, Cand1)) = SLks[i][j]
#             if (r0, c0, Cand0) in UCS0: continue
#             UCS0.append((r0, c0, Cand0))
#             N = TNODE(r0, c0, Cand0, LK_NONE, None, None, None)
#             N.Children = [TNODE(r1, c1, Cand1, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None)]
#             UCS1 = [(r1, c1, Cand1)]
#             for k in range(j+1, NSLks):
#                 # up to four slks possible (row, col, box and cell), scan the rest of the SLks for them
#                 ((r2, c2, Cand2), (r3, c3, Cand3)) = SLks[i][k]
#                 if r0 != r2 or c0 != c2 or Cand0 != Cand2: continue  # only looking for branches off trunk (r0, c0, Cand0)
#                 # if not ccells_match(r0, c0, Cand0, r2, c2, Cand2, GrpLks): continue
#                 if (r3, c3, Cand3) in UCS1: continue  # dup SLk, skip.
#                 UCS1.append((r3, c3, Cand3))
#                 N.Children.append(TNODE(r3, c3, Cand3, LK_STRG, [(r0, c0, Cand0, LK_STRG)], N, None))
#             AICuc[i].append(N)
#     return SLks, AICuc
#
#
# def _find_next_aic_nodes(SLks, Children, Cands, GrpLks, ChLks, Method, Status):
#     # Note: Pruning is achieved by not copying a child branch from the Children list to the Kids list.
#
#     Kids = []
#     for C in Children:
#         if C.Children:  # Continue to recurse down the children.
#             C.Children = _find_next_aic_nodes(SLks, C.Children, Cands, GrpLks, ChLks+1, Method, Status)
#             if Status.Tech != T_UNDEF: return C
#         else:  # at a leaf of the tree, try to grow some branches
#             Lks1 = []
#             # look for Ccells in the same cell first (other candidates in same cell)
#             if GrpLks:
#                 if len(C.r) == len(C.c) == 1:
#                     ra = list(C.r)[0]; ca = list(C.c)[0]
#                     for Candx in sorted(Cands[ra][ca] - {C.Cand}):
#                         for ((r0, c0, Cand0), (r1, c1, Cand1)) in SLks[Candx-1]:
#                             if Cand0 == Cand1 and C.r == r0 and C.c == c0: Lks1.append(((r0, c0, Cand0), (r1, c1, Cand1)))
#             else:
#                 for Candx in sorted(Cands[C.r][C.c] - {C.Cand}):
#                     for ((r0, c0, Cand0), (r1, c1, Cand1)) in SLks[Candx-1]:
#                         if Cand0 == Cand1 and C.r == r0 and C.c == c0: Lks1.append(((r0, c0, Cand0), (r1, c1, Cand1)))
#             Ch0 = [*C.Chain, *[(C.r, C.c, C.Cand, LK_NONE)]]
#             for ((r0, c0, Cand0), (r1, c1, Cand1)) in [*SLks[C.Cand-1], *Lks1]:
#                 pos = is_in_chain(r0, c0, Cand0, Ch0, GrpLks)  # LK_NONE as link to starting strong link has not been determined yet.
#                 if pos >= 0: continue
#                 # The ending strong link may only intersect the starting link of the chain being built.
#                 Ch1 = [*C.Chain, *[(C.r, C.c, C.Cand, LK_NONE), (r0, c0, Cand0, LK_STRG)]]
#                 pos = is_in_chain(r1, c1, Cand1, Ch1, GrpLks)
#                 if pos > 0: continue
#                 # if the starting strong link connects to the chain, add it to the list of children.
#                 LkT, LkH = how_ccells_linked(C.r, C.c, C.Cand, r0, c0, Cand0, Cands, GrpLks)
#                 if LkT == LK_NONE: continue
#                 if LkT != LK_WEAK: LkT = LK_WKST
#                 # C.Lk = LkT
#                 Ch0[-1] = (C.r, C.c, C.Cand, LkT)
#                 Ch1[-2] = (C.r, C.c, C.Cand, LkT)
#                 if pos == 0:  # a possible Strong AI Loop found. (impossible to form if #links <5)
#                     if Method not in {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP}: continue
#                     if GrpLks:  # The common ccell can only be a scalar, not grouped, with group no unique cell asgnmt can be made, therefore grouped is simply invalid intersecting ccells in the chain
#                         ra, ca, Canda, Lka = Ch1[0]
#                         if not (len(ra) == len(ca) == len(r1) == len(c1) == 1): continue
#                         Status.Outcome = [(list(r1)[0], list(c1)[0], Cand1)]
#                     else:
#                         Status.Outcome = [(r1, c1, Cand1)]
#                     Status.Tech = T_GL_STRONG_AI_LOOP if GrpLks else T_STRONG_AI_LOOP
#                     Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
#                     return C
#                 ra, ca, Canda, Lka = Ch1[0]
#                 if Method in {T_UNDEF, T_EVEN_AI_LOOP, T_GL_EVEN_AI_LOOP}:  # no intersection, check for an EVEN_AI_LOOP
#                     LkT, LkH = how_ccells_linked(ra, ca, Canda, r1, c1, Cand1, Cands, GrpLks)
#                     if LkT != LK_NONE:  # found EVEN_AI_LOOP pattern, scan for eliminations. In weak links, if in same cell then other cands, else if house, then other same value ccels not part of base set.
#                         if LkT != LK_WEAK: LkT = LK_WKST
#                         Ch2 = [*Ch1, *[(r1, c1, Cand1, LkT), (ra, ca, Canda, LK_NONE)]]
#                         EL = []
#                         for i in range(len(Ch2)-1):
#                             r2, c2, Cand2, Lk2 = Ch2[i]
#                             if Lk2 != LK_STRG:
#                                 r3, c3, Cand3, Lk3 = Ch2[i+1]
#                                 if Cand2 != Cand3:  # Cands are in the same cell, and if grplinks the cells must be scalars.
#                                     if GrpLks: r4 = list(r2)[0]; c4 = list(c2)[0]
#                                     else: r4 = r2; c4 = c2
#                                     for Cand4 in sorted(Cands[r4][c4] - {Cand2, Cand3}):
#                                         EL.append((r4, c4, Cand4))
#                                 else:  # same cands in a house
#                                     for r4, c4 in cells_that_see_all_of([(r2, c2), (r3, c3)], GrpLks):  # cells_that_see_all_of handles both scalars and groups
#                                         if Cand2 in Cands[r4][c4]:
#                                             EL.append((r4, c4, Cand2))
#                         if EL:
#                             Status.Tech = T_GL_EVEN_AI_LOOP if GrpLks else T_EVEN_AI_LOOP
#                             Status.Pattern = Ch2
#                             Status.Outcome = EL
#                             return C
#                 if Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN, T_W_WING, T_GL_W_WING}:  # Strongly ended chain, same candidates check for eliminations
#                     if Canda == Cand1:  # same candidate value ending ccells
#                         EL = []
#                         for r2, c2 in cells_that_see_all_of([(r1, c1), (ra, ca)], GrpLks):
#                             if Cand1 in Cands[r2][c2]: EL.append((r2, c2, Cand1))
#                         if EL:
#                             Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
#                             # does this chain match the criteria for a W-Wing. a ==> node 0, b ==> node 1, 2 ==> node -2, 1==> node -1
#                             rb, cb, Candb, Lkb = Status.Pattern[1]; r2, c2, Cand2, Lk2 = Status.Pattern[-2]
#                             if Canda != Candb and Candb == Cand2:
#                                 NLks = len(Status.Pattern) - 1
#                                 if NLks < 5 and Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN}: Status.Tech = T_SC_AI_CHAIN
#                                 elif NLks == 5 and Method in {T_UNDEF, T_W_WING, T_GL_W_WING}: Status.Tech = T_W_WING
#                                 else: continue
#                             elif Method in {T_UNDEF, T_SC_AI_CHAIN, T_GL_SC_AI_CHAIN}: Status.Tech = T_SC_AI_CHAIN
#                             else: continue
#                             if GrpLks: Status.Tech |= T_GRPLK
#                             Status.Outcome = EL
#                             return C
#                 if Method in {T_UNDEF, T_DC_AI_CHAIN, T_GL_DC_AI_CHAIN}:  # different value candidates
#                     if Canda != Cand1:  # Different candidate value ending ccells
#                         EL = []
#                         if GrpLks:
#                             if len(ra) == len(ca) == len(r1) == len(c1) == 1:  # only scalar end ccells, eliminations not possible if grouped
#                                 ras = list(ra)[0]; cas = list(ca)[0]; r1s = list(r1)[0]; c1s = list(c1)[0]
#                                 if ras == r1s and cas == c1s:
#                                     if len(Cands[r1s][c1s]) > 2: EL.append((r1s, c1s, Cands[r1s][c1s] - {Cand1 | Canda}))
#                                 elif cells_in_same_house(ras, cas, r1s, c1s):
#                                     if Cand1 in Cands[ras][cas]: EL.append((ras, cas, Cand1))
#                                     if Canda in Cands[r1s][c1s]: EL.append((r1s, c1s, Canda))
#                         else:
#                             if ra == r1 and ca == c1:
#                                 if len(Cands[r1][c1]) >2: EL.append((r1, c1, Cands[r1][c1] - {Cand1 | Canda}))
#                             elif cells_in_same_house(ra, ca, r1, c1):
#                                 if Cand1 in Cands[ra][ca]: EL.append((ra, ca, Cand1))
#                                 if Canda in Cands[r1][c1]: EL.append((r1, c1, Canda))
#                         if EL:
#                             Status.Tech = T_GL_DC_AI_CHAIN if GrpLks else T_DC_AI_CHAIN
#                             Status.Pattern = [*Ch1, *[(r1, c1, Cand1, LK_NONE)]]
#                             # Status.Pattern = [*C.Chain, *[(C.r, C.c, C.Cand, LK_STRG), (r, c, Cand, LK_NONE)]]
#                             Status.Outcome = EL
#                             return C
#                 # Algorithm ends up here when the strong link is part of the valid chain and there was no complete AI-Chain pattern identified and resolved.
#                 if Method in {T_W_WING, T_GL_W_WING} and len(C.Chain) >= 4: continue
#                 C.Children.append(TNODE(r0, c0, Cand0, LkT, Ch0, C))
#                 C.Children[-1].Children.append(TNODE(r1, c1, Cand1, LK_STRG, Ch1, C.Children[-1]))
#         if C.Children: Kids.append(C)
#     return Kids
#
#
#
# def _ai_chain_elims(S, Grid, Cands, Step):
#
#     Step[P_TECH] = S.Tech
#     NLks = NGrpLks = 0
#     for r, c, Cand, Lk, in S.Pattern:
#         NLks += 1
#         if not isinstance(r, int) and len(r) > 1: NGrpLks += 1
#         if not isinstance(c, int) and len(c) > 1: NGrpLks += 1
#         if Lk == LK_NONE: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_END, ]])
#         else: Step[P_PTRN].extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
#     Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NLks - NGrpLks) * LK_DIFF + NGrpLks * GRP_LK_DIFF
#     if S.Tech in {T_STRONG_AI_LOOP, T_GL_STRONG_AI_LOOP}:
#         r, c, Cand = S.Outcome[0]
#         Grid[r][c] = Cand
#         Cands[r][c].clear()
#         discard_cand_from_peers(Cand, r, c, Cands)
#         Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END, ]]
#         return 1
#     else:  # Eliminations
#         for r, c, Cand in S.Outcome:
#             Cands[r][c].discard(Cand)
#             if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
#             Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
#         Step[P_OUTC].append([P_END, ])
#         return 0
