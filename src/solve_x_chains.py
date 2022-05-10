from globals import *
from solve_utils import *


def tech_x_chains(Grid, Step, Cands, Methods):
    return x_chains(Grid, Step, Cands, Methods, False)

def tech_gl_x_chains(Grid, Step, Cands, Methods):
    return x_chains(Grid, Step, Cands, Methods, True)

def x_chains(Grid, Step, Cands, Methods, GrpLks = False):

    Forest = []
    for Cand in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in find_strong_cand_links_btwn_cells(Cand, Cands, GrpLks):
            Forest.append(TREE(r0, c0, Cand0, None, TNODE(r1, c1, Cand1, Lk1, [NL(r0, c0, Cand0, Lk0), NL(r1, c1, Cand1, Lk1)])))
    # All saplings planted.
    while Forest:
        Culls = set()  # trees to cull, use set to avoid dups.
        Status = STATUS()
        for Tree in Forest:
            find_next_x_child_nodes(Tree.Branch, Cands, 1, Tree, Methods, Status, GrpLks)
            if Status.Tech != T_UNDEF: break
            if not Tree.Branch.Children:  Culls.add(Tree)
        if Status.Tech != T_UNDEF:
            Step.Method = Status.Tech
            Step.NrLks = Step.NrGrpLks = 0
            Step.Pattern = []; Step.Outcome = []
            for r, c, Cand, Lk, in Status.Pattern:
                Step.NrLks += 1
                if Step.Method & T_GRPLK:
                    if len(r) > 1: Step.NrGrpLks += 1
                    if len(c) > 1: Step.NrGrpLks += 1
                Step.Pattern.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk & 0x000f)]])
            if Status.Tech in {T_STRONG_X_LOOP, T_GL_STRONG_X_LOOP}:
                r, c, Cand = Status.Outcome[0]
                Grid[r][c] = Cand
                Cands[r][c].clear()
                discard_cand_from_peers(Cand, r, c, Cands)
                Step.Outcome = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END, ]]
                return 1
            else:  # Eliminations
                for r, c, Cand in Status.Outcome:
                    Cands[r][c].discard(Cand)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                Step.Outcome.append([P_END, ])
                return 0
        for Tree in Culls: Forest.remove(Tree)
    return -1

def find_next_x_child_nodes(Child, Cands, Lvl, Tree, Methods, Status, GrpLks = False):

    if Child.Children:
        OddPrunes = set()
        for GChild in Child.Children:
            EvenPrunes = set()
            for GGChild in GChild.Children:
                find_next_x_child_nodes(GGChild, Cands, Lvl+1, Tree, Methods, Status, GrpLks)
                if Status.Tech != T_UNDEF: return  # don't waste any time when soln found.
                if not GGChild.Children: EvenPrunes.add(GGChild)
            for GGChild in EvenPrunes: GChild.Children.remove(GGChild)
            if not GChild.Children: OddPrunes.add(GChild)
        for GChild in OddPrunes: Child.Children.remove(GChild)
    else:  # at the leaves, attempt to add the next weak and strong links.
        for r1, c1, Cand1, Lk1 in list_ccells_linked_to(Child.r, Child.c, Child.Cand, Cands, LK_STWK, GrpLks, False):
            for (rx, cx, Candx, Lkx) in Child.Chain:
                if ccells_intersect(r1, c1, Cand1, rx, cx, Candx): break
            else:
                if Lk1 & LK_STRG: Lk1 = (Lk1 & 0x01f0) | LK_WKST
                else: Lk1 = (Lk1 &0x01f0) | LK_WEAK
                Node1 = TNODE(r1, c1, Cand1, Lk1, [*Child.Chain, NL(r1, c1, Cand1, Lk1)], Child)
                for r2, c2, Cand2, Lk2 in list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STRG, GrpLks, False):
                    if Lvl > 1 and (T_STRONG_X_LOOP in Methods or T_GL_STRONG_X_LOOP in Methods):
                        if (r2, c2, Cand2) == (Tree.r, Tree.c, Tree.Cand):
                            if GrpLks:
                                Status.Outcome = [(list(r1)[0], list(c1)[0], Cand1)]
                                Status.Tech = T_GL_STRONG_X_LOOP
                            else:
                                Status.Outcome = [(r2, c2, Cand1)]
                                Status.Tech = T_STRONG_X_LOOP
                            Ch = [*Node1.Chain, NL(r2, c2, Cand2, Lk2)]
                            Ch.reverse()
                            Status.Pattern = Ch[:-1]
                            return
                    for rx, cx, Candx, Lkx in Child.Chain:
                        if ccells_intersect(r2, c2, Cand2, rx, cx, Candx): break
                    else:
                        Elims = []
                        if Lvl > 1 and (T_EVEN_X_LOOP in Methods or T_GL_EVEN_X_LOOP in Methods):
                            Lk = how_ccells_linked(r2, c2, Cand2, Tree.r, Tree.c, Tree.Cand, Cands, GrpLks)
                            if Lk:  # Even X-Loop found.
                                if Lk & LK_STRG: Lk = (Lk & 0x01f0) | LK_WKST
                                Ch = [*Node1.Chain, NL(r2, c2, Cand2, Lk2)]
                                Ch.reverse()
                                (r0, c0, Cand0, Lk0) = Ch.pop()
                                Ch.append(NL(r0, c0, Cand0, Lk))
                                for i in range(len(Ch)-1):
                                    if Ch[i].Lk & 0x0f == LK_WEAK:
                                        for r3, c3 in cells_that_see_all_of([(Ch[i].r, Ch[i].c), (Ch[i+1].r, Ch[i+1].c)], GrpLks):
                                            if Cand1 in Cands[r3][c3]:  Elims.append((r3, c3, Cand1))
                                if Ch[-1].Lk & 0x0f == LK_WEAK:
                                    for r3, c3 in cells_that_see_all_of([(Ch[-1].r, Ch[-1].c), (Ch[0].r, Ch[0].c)], GrpLks):
                                        if Cand1 in Cands[r3][c3]:  Elims.append((r3, c3, Cand1))
                                if Elims:
                                    Status.Tech = T_GL_EVEN_X_LOOP if GrpLks else T_EVEN_X_LOOP
                                    Status.Pattern = Ch
                                    Status.Outcome = Elims
                                    return
                        for r3, c3 in cells_that_see_all_of([(r2, c2), (Tree.r, Tree.c)], GrpLks):
                            if Cand1 in Cands[r3][c3]: Elims.append((r3, c3, Cand1))
                        if Elims:
                            Tech = T_UNDEF
                            if Lvl == 1:
                                Lk0 = Child.Chain[1].Lk
                                if Lk0 & Lk1 & Lk2 & LK_LINE: Tech = T_SKYSCRAPER
                                elif Lk0 & Lk2 & LK_LINE and Lk1 & LK_BOX: Tech = T_TWO_STRING_KITE
                                else: Tech = T_TURBOT_FISH
                            else: Tech = T_X_CHAIN
                            if GrpLks: Tech |= T_GRPLK
                            if Tech in Methods:
                                Status.Tech = Tech
                                Status.Pattern = [*Node1.Chain, NL(r2, c2, Cand2, Lk2)]
                                Status.Pattern.reverse()
                                Status.Outcome = Elims
                                return
                        Node1.Children.append(TNODE(r2, c2, Cand2, Lk2, [*Node1.Chain, NL(r2, c2, Cand2, Lk2)], Node1))
                if Node1.Children: Child.Children.append(Node1)
        # Soln not found yet, has recursion bottomed out.
        if Lvl > RECURSE_LIM:
            Child.Chldren = []
            return
