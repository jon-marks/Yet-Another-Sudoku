
from globals import *
from solve_utils import *

L_ROW = 0
L_COL = 1
L_BOX = 2

def tech_three_link_x_chains(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):

    if Method != T_UNDEF and not (Method == T_SKYSCRAPER or Method == T_TWO_STRING_KITE or Method == T_TURBOT_FISH): return -1

    res = _tech_three_link_x_chains(Grid, Step, Cands, ElimCands, Method)
    if res == -1:
        return _tech_three_link_x_chains(Grid, Step, Cands, ElimCands, Method, GrpLks = True)
    return res

def tech_longer_x_chains(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):

    if method != T_UNDEF and not (Method == T_X_CHAIN or Method == T_X_LOOP): return -1

    res = _tech_longer_x_chains(Grid, Step, Cands, ElimCands, Method)
    if res == -1:
        return _tech_longer_x_chains(Grid, Step, Cands, ElimCands, Method, GrpLks = True)
    return res


def _tech_three_link_x_chains(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF, GrpLks = False):

    for Cand in range(1, 10):
        Lks = find_strong_single_cand_links(Cand, Cands, GrpLks)

        # look for horizontal skyscraper, two horizontal parallel strong links that are weakly connected.
        for r0 in range(8):
            if Lks[L_ROW][r0] == (): continue
            (c0a, c0b) = Lks[L_ROW][r0]
            for r1 in range(r0+1, 9):
                if Lks[L_ROW][r1] == (): continue
                (c1a, c1b) = Lks[L_ROW][r1]
                for c0l, c1l, c0o, c1o in [(c0a, c1a, c0b, c1b), (c0b, c1b, c0a, c1a), (c0a, c1b, c0b, c1a), (c0b, c1a, c0a, c1b)]:
                    Lk = ccells_are_linked(r0, c0l, Cand, r1, c1l, Cand, Cands, LK_COL)
                    if Lk == LK_NONE: continue
                    # Horizontal Skyscraper found, what can be eliminated?
                    if Lk != LK_WEAK: Lk = LK_WKST
                    XChain = [(r0, c0o, LK_STRG), (r0, c0l, Lk), (r1, c1l, LK_STRG), (r1, c1o, -1)]
                    if _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, T_SKYSCRAPER): return 0
        # look for vertical skyscraper, two vertical parallel strong links that are weakly connected.
        for c0 in range(8):
            if Lks[L_COL][c0] == (): continue
            (r0a, r0b) = Lks[L_COL][c0]
            for c1 in range(c0+1, 9):
                if Lks[L_COL][c0] == (): continue
                (r1a, r1b) = Lks[L_COL][c1]
                for r0l, r1l, r0o, r1o in [(r0a, r1a, r0b, r1b), (r0b, r1b, r0a, r1a), (r0a, r1b, r0b, r1a), (r0b, r1a, r0a, r1b)]:
                    Lk = ccells_are_linked(r0l, c0, Cand, r1l, c1, Cand, Cands, LK_ROW)
                    if Lk == LK_NONE: continue
                    # Vertical Skyscraper found, what can be eliminated?
                    if Lk != LK_WEAK: Lk = LK_WKST
                    XChain = [(r0o, c0, LK_STRG), (r0l, c0, Lk), (r1l, c1, LK_STRG), (r1o, c1, -1)]
                    if _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, T_SKYSCRAPER): return 0
        # look for 2 string kite, a horizontal and a vertical strong link that are weakly connected (can only be through a box).
        for r0 in range(9):
            if Lks[L_ROW][r0] == (): continue
            (c0a, c0b) = Lks[L_ROW][r0]
            for c0 in range(9):
                if Lks[L_COL][c0] == (): continue
                (r0a, r0b) = Lks[L_COL][c0]
                for ((r0l, c0l), (r1l, c1l), (r0o, c0o), (r1o, c1o)) in [((r0, c0a), (r0a, c0), (r0, c0b), (r0b, c0)),
                                                                         ((r0, c0b), (r0b, c0), (r0, c0a), (r0a, c0)),
                                                                         ((r0, c0a), (r0b, c0), (r0, c0b), (r0a, c0)),
                                                                         ((r0, c0b), (r0a, c0), (r0, c0a), (r0b, c0))]:
                    Lk = ccells_are_linked(r0l, c0l, Cand, r1l, c1l, Cand, Cands, LK_BOX)
                    # Two String Kite found, what can be eliminated
                    if Lk != LK_WEAK: Lk = LK_WKST
                    XChain = [(r0o, c0o, LK_STRG), (r0l, c0l, Lk), (r1l, c1l, LK_STRG), (r1o, c1o, -1)]
                    if _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, T_TWO_STRING_KITE): return 0
        # look for turbot fish, a strongly linked row/col and box, weakly connected through a col/row.
        for b0 in range(9):
            if Lks[L_BOX][b0] == (): continue
            ((r0a, c0a), (r0b, c0b)) = Lks[L_BOX][b0]
            for r0 in range(9):
                if Lks[L_ROW][r0]: continue
                (c0c, c0d) = Lks[L_ROW][r0]
                for ((r0l, c0l), (r1l, c1l), (r0o, c0o), (r1o, c1o)) in [((r0a, c0a), (r0, c0c), (r0b, c0b), (r0, c0d)),
                                                                         ((r0b, c0b), (r0, c0d), (r0a, c0a), (r0, c0c)),
                                                                         ((r0a, c0a), (r0, c0d), (r0b, c0b), (r0, c0c)),
                                                                         ((r0b, c0b), (r0, c0c), (r0a, c0a), (r0, c0d))]:
                    Lk = ccells_are_linked(r0l, c0l, Cand, r1l, c1l, Cand, Cands, LK_COL)
                    # Turbot fish found, what can be eliminated
                    if Lk != LK_WEAK: Lk = LK_WKST
                    XChain = [(r0o, c0o, LK_STRG), (r0l, c0l, Lk), (r1l, c1l, LK_STRG), (r1o, c1o, -1)]
                    if _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, T_TURBOT_FISH): return 0
            for c0 in range(9):
                if Lks[L_COL][c] == (): continue
                (r0c, r0d) = Lks[L_COL][c0]
                for ((r0l, c0l), (r1l, c1l), (r0o, c0o), (r1o, c1o)) in [((r0a, c0a), (r0c, c0), (r0b, c0b), (r0d, c0)),
                                                                         ((r0b, c0b), (r0d, c0), (r0a, c0a), (r0c, c0)),
                                                                         ((r0a, c0a), (r0d, c0), (r0b, c0b), (r0c, c0)),
                                                                         ((r0b, c0b), (r0c, c0), (r0a, c0a), (r0c, c0))]:
                    Lk = ccells_are_linked(r0l, c0l, Cand, r1l, c1l, Cand, Cands, LK_COL)
                    # Turbot fish found, what can be eliminated
                    if Lk != LK_WEAK: Lk = LK_WKST
                    XChain = [(r0o, c0o, LK_STRG), (r0l, c0l, Lk), (r1l, c1l, LK_STRG), (r1o, c1o, -1)]
                    if _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, T_TURBOT_FISH): return 0
    return -1

def _tech_longer_x_chains(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF, GrpLks = False):


    CandXCState = [{XC_SLKS:   None,          # Structure containing all possible strong links for the cand
                    XC_STARTS: [],            # list of starting strong link pairs where eliminations can be made



                   } for C in range(9)]
    for Cand in range(1, 10):
        CandXCState[Cand-1][XC_SLKS] = Lks = find_strong_single_cand_links(Cand, Cands, GrpLks)
        for i0 in range(26):
            l0 = i0//9; g0 = i0%9
            if Lks[g0][l0] == (): continue
            (slk0a, slk0b) = _get_sl(Lks, g0, l0)
            for i1 in range(i0+1, 27):
                l1 = i1//9; g1 = i1%9
                if Lks[g1][l1] == (): continue
                (slk1a, slk1b) = _get_sl(Lks, g1, l1)

                for ((r0l, c0l), (r1l, c1l)), ((r0o, c0o), (r1o, c1o)) in [(slk0a, slk1a), (slk0b, slk1b),
                                                                           (slk0b, slk1b), (slk0a, slk1a),
                                                                           (slk0a, slk1b), (slk0b, slk1a),
                                                                           (slk0b, slk1a), (slk0a, slk1b)]:
                    # first check that there is a weak link between the ends and ccells can
                    # be eliminated before going to the effort of building the chain.
                    for r0, c0 in cells_that_see_all_of([(r0o, r0o), (r1o, c1o)]):
                        if Cand in Cands[r0][c0]:
                            break
                    else:
                        continue
                    # there will be eliminations.
                    # First search for another strong link that each 'l' ends of the existing strong links sees forming
                    # a five link chain.
                    for i2 in range(27):
                        l2 = i2//9; g2 = i2%9
                        if Lks[g2][l2] == (): continue
                        ((r2a, c2a), (r2b, c2b)) = _get_sl(Lks, g2, l2)
                        if (r2a, c2a) in UC1 or (r2b, c2b) in UC1: continue
                        lk1 = ccells_are_linked(r0l, c01, Cand, r2a, c2a, Cand, Cands)
                        lk2 = ccells_are_linked(r01, c01, Cand, r2b, c2b, Cand, Cands)
                        lk3 = ccells_are_linked(r1l, c1l, Cand, r2a, c2a, Cand, Cands)
                        lk4 = ccells_are_linked(r1l, c1l, Cand, r2b, cb2, Cand, Cands)
                        if lk1 or lk2 or lk3 or lk4: break
                    else:
                        #  linking ends of chain cannot see any of the strong links - continue searching
                        continue
                    if lk1 and lk2:
                        # found a chain 0o__0l..2a__2b..1l__1o
                        pass
                        return "blah blah"
                    # try the link the other way round
                    if lk3 and lk4:
                        # found a chain 0o__0l..2b__2a..1l__1o
                        pass
                        return "blah blah"
                    # add starting links to XC_STARTS so we do not search again when looking for longer chains.
                    CandXCState[Cand-1][XC_STARTS].append((((r0o, c0o), (r0l, c0l)), ((r1o, c1o), (r1l, c1l))))

    # exhausted the search for n links for all candidates, now try n + 2
    for cand in range(1, 10):
        Lks = CandXCState[Cand-1][XC_SLKS]
        for xcs, (((r0o, c0o,), (r0l, c0l)), ((r1o, c1o), (r1l, c1l))) in enumerate(copy(CAndXCState[Cand-1][XC_STARTS])):
            UC0 = [(r0o, c0o), (r0l, c0l), (r1o, c1o), (r1l, c1l)]
            for i2 in range(27):
                l2 = i2//9; g2 = i2%9
                if Lks[g2][l2] == (): continue
                ((r2a, c2a), (r2b, c2b)) = _get_sl(Lks, g2, l2)
                if (r2a, c2a) in UC0 or (r2b, c2b) in UC0: continue
                lk0l2a = ccells_are_linked(r0l, c01, Cand, r2a, c2a, Cand, Cands)
                if lk0l2a:
                    for i3 in range(27):
                        if i3 == i2: continue
                        l3 = i3//9; g3 = i3%9
                        if Lks[g3][l3] == (): continue
                        ((r3a, c3a), (r3b, c3b)) = _get_sl(Lks, g3, l3)
                        if (r3a, c3a) in UC0 or (r3b, c3b) in UC0: continue
                        lk1l3a = ccells_are_linked(r1l, c1l, Cand, r3a, c3a, Cand, Cands)
                        if lk1l3a:
                            lk2b3b = ccells_are_linked(r2b, c2b, Cand, r3b, c3b, Cand, Cands)
                            if lk2b3b:
                                # found a chain  0o__0l..2a__2b..3b__3a..1l__1o
                                pass
                                return "blah blah"
                        else:  # try link 3 the other way round.
                            lk1l3b = ccells_are_linked(r1l, c1l, Cand, r3b, c3b, Cand, Cands)
                            if lk1l3b:
                                lk2b3a = ccells_are_linked(r2b, c2b, Cand, r3a, c3a, Cand, Cands)
                                if lk2b3a:
                                    # found a chain 0o__0l..2a__2b..3a__3b..1l__1o
                                    pass
                                    return "blah blah"
                else:  #  not lk0l2a:  # try lk 2 the other way round.
                    lk0l2b = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
                    if lk0l2b:
                        for i3 in range(27):
                            if i3 == i2: continue
                            l3 = i3//9;
                            g3 = i3%9
                            if Lks[g3][l3] == (): continue
                            ((r3a, c3a), (r3b, c3b)) = _get_sl(Lks, g3, l3)
                            if (r3a, c3a) in UC0 or (r3b, c3b) in UC0: continue
                            lk1l3a = ccells_are_linked(r1l, c1l, Cand, r3a, c3a, Cand, Cands)
                            if lk1l3a:
                                lk2b3b = ccells_are_linked(r2a, c2a, Cand, r3b, c3b, Cand, Cands)
                                if lk2b3b:
                                    # found a chain  0o__0l..2b__2a..3b__3a..1l__1o
                                    pass
                                    return "blah blah"
                            else:  # try link 3 the other way round.
                                lk1l3b = ccells_are_linked(r1l, c1l, Cand, r3b, c3b, Cand, Cands)
                                if lk1l3b:
                                    lk2b3a = ccells_are_linked(r2b, c2b, Cand, r3a, c3a, Cand, Cands)
                                    if lk2b3a:
                                        # found a chain 0o__0l..2b__2a..3a__3b..1l__1o
                                        pass
                                        return "blah blah"
                                else:  # either end of lk 2 and 3 cannot make a link to the upstream chain segments
                                    # a chain cannot be constructed from these starts with this candidate, remove it
                                    # from XC_STARTS
                                    CandXCState[Cand-1][XC_STARTS].pop(xcs)
            if notlk2a

            lk3 = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
                        if :
                                # A 5 link chain has been been found.

                        else:  # Try the new strong link the other way round.
                            lk3 = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
                            if lk3:
                                l

def _get_sl(Lks, g, l):

    if g == L_ROW:
        (a, b) = Lks[g][l]
        return ((l, a), (l, b))
    if g == L_COL:
        (a, b) = Lks[g][l]
        return ((a, l), (b, l))
    else:  # g == L_BOX
        return Lks[g][l]

        # look for x loops.  Find two cells that see each other, and build out a strong ended AIC from
        # both ends and get them to connect.  If a connection is formed, then all same valued ccells in
        # weakly linked houses that are not part of the chain can be eliminated.


def _x_chain_elims(XChain, Cand, Cands, ElimCands, Step, Mthd):

    LenC = len(XChain)
    re0, ce0, le0 = XChain[0]; re1, ce1, le1 = XChain[LenC-1]
    for r0, c0 in cells_that_see_all_of([(re0, ce0), (re1, ce1)]):
        if Cand in Cands[r0][c0]:
            Cands[r0][c0].discard(Cand)
            if Step[L_OUTC]: Step[L_OUTC].append([L_SEP, ])
            Step[L_OUTC].extend([[L_ROW, r0], [L_COL, c0], [L_OP, OL_ELIM], [L_VAL, Cand]])
            if ElimCands is not None:
                ElimCands[r0][c0].add(Cand)
    if Step[L_OUTC]:
        Step[L_OUTC].append([L_END, ])
        Step[L_TECH] = Mthd
        Step[L_PTRN].extend([[L_VAL, Cand], [L_OP, OL_PARO]])
        for r0, c0, lk0 in XChain:
            if lk0 == -1:
                Step[L_PTRN].extend([[L_ROW, r0], [L_COL, c0]])
            else:
                Step[L_PTRN].extend([[L_ROW, r0], [L_COL, c0], [L_OP, token_link(lk0)]])
        Step[L_PTRN].extend([[L_OP, OL_PARC], [L_END, ]])
        return True
    return False




def find_strong_single_cand_links(Cand, Cands, GrpLks = False):

    Lk = {L_ROW: [], L_COL: [], L_BOX: []}
    # Lk = {L_ROW: [[] for i in range(9)], L_COL: [[] for i in range(9)], L_BOX: [[] for i in range(9)]}

    if GrpLks:
        for r in range(9):
        # look in rows
            C = []; Twr = [set(), set(), set()]
            for c in range(9):
                if Cand in Cands[r][c]:
                    C.append(c); Twr[c//3].add(c)
            lenC = len(C)
            if lenC < 2: Lk[L_ROW].append(())
            elif lenC == 2: Lk[L_ROW].append((C[0], C[1]))
            # if lenC < 2: continue
            # elif lenC == 2: Lk[L_ROW][r].append((C[0], C[1]))
            else:
                if Twr[0] and Twr[1] and Twr[2]: Lk[L_ROW].append(())
                if Twr[0] and Twr[1]: Lk[L_ROW].append((Twr[0], Twr[1]))
                elif Twr[0] and Twr[2]: Lk[L_ROW].append((Twr[0], Twr[2]))
                elif Twr[1] and Twr[2]: Lk[L_ROW].append((Twr[1], Twr[2]))
                else: Lk[L_ROW].append(())
                # if Twr[0] and Twr[1] and Twr[2]: continue
                # if Twr[0] and Twr[1]: Lk[L_ROW][r].append((Twr[0], Twr[1]))
                # elif Twr[0] and Twr[2]: Lk[L_ROW][r].append((Twr[0], Twr[2]))
                # elif Twr[1] and Twr[2]: Lk[L_ROW][r].append((Twr[1], Twr[2]))
        # look in cols
        for c in range(9):
            R = []; Flr = [set(), set(), set()]
            for r in range(9):
                if Cand in Cands[r][c]:
                    R.append(r); Flr[r//3].add(r)
            lenR = len(R)
            if lenR < 2: Lk[L_COL].append(())
            elif lenR == 2: Lk[L_COL].append((R[0], R[1]))
            # if lenR < 2: continue
            # elif lenR == 2: Lk[L_COL][c].append((R[0], R[1]))
            else:
                if Flr[0] and Flr[1] and Flr[2]: Lk[L_COL].append(())
                if Flr[0] and Flr[1]: Lk[L_COL].append((Flr[0], Flr[1]))
                elif Flr[0] and Flr[2]: Lk[L_COL].append((Flr[0], Flr[2]))
                elif Flr[1] and Flr[2]: Lk[L_COL].append((Flr[1], Flr[2]))
                else: Lk[L_COL].append(())
                # if Flr[0] and Flr[1] and Flr[2]: continue
                # if Flr[0] and Flr[1]: Lk[L_COL][c].append((Flr[0], Flr[1]))
                # elif Flr[0] and Flr[2]: Lk[L_COL][c].append((Flr[0], Flr[2]))
                # elif Flr[1] and Flr[2]: Lk[L_COL][c].append((Flr[1], Flr[2]))
    else:  # No group links
        for r in range(9):
            C = []
            for c in range(9):
                if Cand in Cands[r][c]:
                    C.append(c)
            lenC = len(C)
            # if lenC == 2: Lk[L_ROW][r].append((C[0], C[1]))
            if lenC == 2: Lk[L_ROW].append((C[0], C[1]))
            else: Lk[L_ROW].append(())
        # look in cols
        for c in range(9):
            R = []
            for r in range(9):
                if Cand in Cands[r][c]:
                    R.append(r)
            lenR = len(R)
            # if lenR == 2: Lk[L_COL][c].append((R[0], R[1]))
            if lenR == 2: Lk[L_COL].append((R[0], R[1]))
            else: Lk[L_COL].append(())

    # look in boxes
    for b in range(9):
        rb = (b//3)*3; cb = (b%3)*3
        B = []
        for rb0 in [rb, rb+1, rb+2]:
            for cb0 in [cb, cb+1, cb+2]:
                if Cand in Cands[rb0][cb0]: B.append((rb0, cb0))
        # if len(B) == 2: Lk[L_BOX][b].append((B[0], B[1]))
        if len(B) == 2: Lk[L_BOX].append((B[0], B[1]))
        else: Lk[L_BOX].append(())
    return Lk


