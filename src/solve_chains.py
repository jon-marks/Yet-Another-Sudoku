from copy import deepcopy

from globals import *
from solve_utils import *


def tech_three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and not (Method == T_SKYSCRAPER or Method == T_TWO_STRING_KITE or Method == T_TURBOT_FISH): return -2
    return _three_link_x_chains(Grid, Step, Cands, Method)

def tech_gl_three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and not (Method == T_GL_SKYSCRAPER or Method == T_GL_TWO_STRING_KITE or Method == T_GL_TURBOT_FISH): return -2
    return _three_link_x_chains(Grid, Step, Cands, Method, GrpLks = True)


def tech_other_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_X_CHAIN: return -2
    return _x_chains(Grid, Step, Cands)

def tech_gl_other_x_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_X_CHAIN: return -2
    return _x_chains(Grid, Step, Cands, GrpLks = True)

def tech_even_x_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_EVEN_X_LOOP: return -2
    return _even_x_loops(Grid, Step, Cands)

def tech_gl_even_x_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_EVEN_X_LOOP: return -2
    return _even_x_loops(Grid, Step, Cands, GrpLks = True)

def tech_strong_x_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_STRONG_X_LOOP: return -2
    return _strong_x_loops(Grid, Step, Cands)

def tech_gl_strong_x_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_STRONG_X_LOOP: return -2
    return _strong_x_loops(Grid, Step, Cands, GrpLks = True)

class XCUC:  # X-Chain under construction
    def __init__(self):
        self.XC = []  # X-chain or X-loop being built
        self.OE = []  # Other end of the X-Chain/loop
        self.UN = []  # list of used nodes in the X-Chain/loop

def _three_link_x_chains(Grid, Step, Cands, Method = T_UNDEF, GrpLks = False):
    # A three link X-Chain is found by trying to join the ends of the chain starts in XCuc.

    Lks, XCuc = find_x_chain_starts(Cands, GrpLks)

    # XCuc1 = []  # Each iteration build a new structure from the old.
    CandsXC = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    for Cand in sorted(CandsXC):
        i = Cand-1
        # for z, X in enumerate(XCuc[i]):
        for X in (XCuc[i]):
            N0, Lk0 = X.XC[-1]; Noe, Lkoe = X.OE[0]
            Lk = ccells_are_linked(N0, Cand, Noe, Cand, Cands)
            if Lk == LK_NONE: continue
            # the links see each other we have an x-chain
            X.XC[-1] = (N0, LK_WEAK if Lk == LK_WEAK else LK_WKST)
            X.XC.extend(X.OE)
            H0 = link_house(X.XC[0][0], X.XC[1][0]); H1 = link_house(X.XC[2][0], X.XC[3][0])
            if H0 == H1:  Pattern = T_SKYSCRAPER
            elif (H0 == LK_ROW and H1 == LK_COL) or (H0 == LK_COL and H1 == LK_ROW):  Pattern = T_TWO_STRING_KITE
            else: Pattern = T_TURBOT_FISH
            if GrpLks: Pattern += T_GRPLK
            if Method == T_UNDEF or Method == Pattern:
                return _x_chain_elims(X.XC, Cand, Cands, Step, Pattern)
    return -1

def _x_chains(Grid, Step, Cands, GrpLks = False):
    # Because complexity is related to chain length and the algorithm seeks to find patterns from
    # simplest to complex, all candidates at a certain chain length are explored before advancing
    # to a longer chain length  XCuc ==> X-Chain under construction structure.

    Lks, XCuc = find_x_chain_starts(Cands, GrpLks)

    CandsXC = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    while CandsXC:
        # Each iteration attempts to add another strong link to the remaining chains.  If the link
        # cannot be added to the chain, then the chain cannot be completed and that chain is removed
        # from the XCuc[][] list.  If all the chains have been removed for a particular candidate,
        # then the candidate value is removed from CandsXC
        for Cand in sorted(CandsXC):
            XCuc1 = []  # Each iteration build a new structure from the old.
            i = Cand-1
            for X in XCuc[i]:
                N0, Lk0 = X.XC[-1]; Noe, Lkoe = X.OE[0]
                for (N2, N3) in Lks[i]:
                    Lx = []
                    if GrpLks:
                        for r, c in [N2, N3]:
                            if isinstance(r, int) and isinstance(c, int): Lx.append((r, c))
                            elif isinstance(c, int):
                                for r0 in r: Lx.append((r0, c))
                            elif isinstance(r, int):
                                for c0 in c: Lx.append((r, c0))
                    else: Lx = [N2, N3]
                    for Nx in Lx:
                        if Nx in X.UN: break
                    else:
                        Lk = ccells_are_linked(N0, Cand, N2, Cand, Cands)
                        if Lk == LK_NONE:
                            Lk = ccells_are_linked(N0, Cand, N3, Cand, Cands)
                            if Lk == LK_NONE: continue  # this link does not fit this chain.
                            else: Na = N3; Nb = N2
                        else: Na = N2; Nb = N3
                        X1 = deepcopy(X)
                        X1.XC[-1] = (N0, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                        X1.XC.extend([(Na, LK_STRG), (Nb, -1)])
                        #  Can this newly added strong link be joined to the other end (OE)
                        Lk = ccells_are_linked(Nb, Cand, Noe, Cand, Cands)
                        if Lk != LK_NONE:
                            X1.XC[-1] = (Nb, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                            X1.XC.extend(X.OE)
                            if GrpLks:
                                if _x_chain_elims(X1.XC, Cand, Cands, Step, T_GL_X_CHAIN): return 0
                            else:
                                if _x_chain_elims(X1.XC, Cand, Cands, Step, T_X_CHAIN): return 0
                            # forget about this chain as it does not produce eliminations
                        else:
                            X1.UN.extend(Lx)
                            XCuc1.append(X1)
            if len(XCuc1): XCuc[i] = XCuc1
            else:
                CandsXC.discard(Cand)
                XCuc[i] = []
    return -1

def _even_x_loops(Grid, Step, Cands, GrpLks = False):
    # Because complexity is related to chain length and the algorithm seeks to find patterns from
    # simplest to complex, all candidates at a certain chain length are explored before advancing
    # to a longer chain length  XCuc ==> X-Chain under construction structure.

    # This algorithm starts with 6 link X-Loops.  A four link X-loop is a X-Wing, and
    # this will have been picked up by the X-Wing alg which is simpler than X-loops and
    # is always ordered to execute ahead of X-loops.

    Lks, XLuc = find_even_x_loop_starts(Cands, GrpLks)

    CandsXC = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    while CandsXC:
        # Each iteration attempts to add another strong link to the remaining chains.  If the link
        # cannot be added to the chain, then the chain cannot be completed and that chain is removed
        # from the XCuc[][] list.  If all the chains have been removed for a particular candidate,
        # then the candidate value is removed from CandsXC
        for Cand in sorted(CandsXC):
            XLuc1 = []  # Each iteration build a new structure from the old.
            i = Cand-1
            for X in XLuc[i]:
                N0, Lk0 = X.XC[-1]; Noe, Lkoe = X.OE[0]
                for (N2, N3) in Lks[i]:
                    Lx = []
                    if GrpLks:
                        for r, c in [N2, N3]:
                            if isinstance(r, int) and isinstance(c, int): Lx.append((r, c))
                            elif isinstance(c, int):
                                for r0 in r: Lx.append((r0, c))
                            elif isinstance(r, int):
                                for c0 in c: Lx.append((r, c0))
                    else: Lx = [N2, N3]
                    for Nx in Lx:
                        if Nx in X.UN: break
                    else:
                        Lk = ccells_are_linked(N0, Cand, N2, Cand, Cands)
                        if Lk == LK_NONE:
                            Lk = ccells_are_linked(N0, Cand, N3, Cand, Cands)
                            if Lk == LK_NONE: continue  # this link does not fit this chain.
                            else: Na = N3; Nb = N2
                        else: Na = N2; Nb = N3
                        X1 = deepcopy(X)
                        X1.XC[-1] = (N0, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                        X1.XC.extend([(Na, LK_STRG), (Nb, -1)])
                        #  Can this newly added strong link be joined to the other end (OE)
                        Lk = ccells_are_linked(Nb, Cand, Noe, Cand, Cands)
                        if Lk != LK_NONE:
                            X1.XC[-1] = (Nb, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                            X1.XC.extend(X.OE)
                            if GrpLks:
                                if _x_loop_elims(X1.XC, Cand, Cands, Step, T_GL_EVEN_X_LOOP): return 0
                            else:
                                if _x_loop_elims(X1.XC, Cand, Cands, Step, T_EVEN_X_LOOP): return 0
                            # forget about this chain as it does not produce eliminations
                        else:
                            X1.UN.extend(Lx)
                            XLuc1.append(X1)
            if len(XLuc1): XLuc[i] = XLuc1
            else:
                CandsXC.discard(Cand)
                XLuc[i] = []
    return -1

def _strong_x_loops(Grid, Step, Cands, GrpLks = False):

    Lks, XLuc = find_strong_x_loop_starts(Cands, GrpLks)

    CandsXC = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    while CandsXC:
        for Cand in sorted(CandsXC):
            XLuc1 = []  # Each iteration build a new structure from the old.
            i = Cand-1
            for X in XLuc[i]:
                N0, Lk0 = X.XC[-1]; Noe, Lkoe = X.OE[0]
                for (N2, N3) in Lks[i]:
                    Lx = []
                    if GrpLks:
                        for r, c in [N2, N3]:
                            if isinstance(r, int) and isinstance(c, int): Lx.append((r, c))
                            elif isinstance(c, int):
                                for r0 in r: Lx.append((r0, c))
                            elif isinstance(r, int):
                                for c0 in c: Lx.append((r, c0))
                    else: Lx = [N2, N3]
                    for Nx in Lx:
                        if Nx in X.UN: break
                    else:
                        Lk = ccells_are_linked(N0, Cand, N2, Cand, Cands)
                        if Lk == LK_NONE:
                            Lk = ccells_are_linked(N0, Cand, N3, Cand, Cands)
                            if Lk == LK_NONE: continue  # this link does not fit this chain.
                            else: Na = N3; Nb = N2
                        else: Na = N2; Nb = N3
                        X1 = deepcopy(X)
                        X1.XC[-1] = (N0, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                        X1.XC.extend([(Na, LK_STRG), (Nb, -1)])
                        #  Can this newly added strong link be joined to the other end (OE)
                        Lk = ccells_are_linked(Nb, Cand, Noe, Cand, Cands)
                        if Lk != LK_NONE:
                            X1.XC[-1] = (Nb, LK_WEAK if Lk == LK_WEAK else LK_WKST)
                            X1.XC.extend(X.OE)
                            if GrpLks: return _x_loop_asnmt(X1.XC, Grid, Cand, Cands, Step, T_GL_STRONG_X_LOOP)
                            else: return _x_loop_asnmt(X1.XC, Grid, Cand, Cands, Step, T_STRONG_X_LOOP)
                        else:
                            X1.UN.extend(Lx)
                            XLuc1.append(X1)
            if len(XLuc1): XLuc[i] = XLuc1
            else:
                CandsXC.discard(Cand)
                XLuc[i] = XLuc1
    return -1

# Supporting functions follow.

def find_x_chain_starts(Cands, GrpLks = False):
    # Scans the puzzle for strong links, and find pairs of strong links, that if they were ends of
    # an x-chain would produce eliminations.  It is only worthwhile attempting to build x-chains from
    # these productive strong link ends.
    #
    # A list of strong links:
    #   Lks[Cand][...]  = SL  # a strong link
    #                   = (N0, N1)  # the Node (cell) ends of the strong link (Capital C)
    #                   = ((r0, c0), (r1, c1)) # the r/c coords of the Nodes forming the links.
    # A list of X-Chains under Construction
    #   XCuc[Cand][...].XC = [(No0, LK_STRG), (Nl0, Lk), (Na0, LK_STRG), (Na1, Lk), (Nb0, LK_STRG), (Nb1, Lk), ... ]
    #                  .OE = [(Nl1, LK_STRG), (No1, -1)]
    #                  .UN = [No0, Nl0, No1, Nl1, Na0, Na1, Nb0, Nb1, ...]

    # First build the list of strong links.
    Lks  = [[], [], [], [], [], [], [], [], []]
    XCuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand in enumerate(range(1, 10)):
        Lks[i] = find_single_cand_strong_links(Cand, Cands, GrpLks)

        lenLks = len(Lks[i])
        for l0 in range(lenLks-1):
            N0a, N0b = Lks[i][l0]
            for l1 in range(l0+1, lenLks):
                N1a, N1b = Lks[i][l1]
                for No0, Nl0, No1, Nl1 in [(N0a, N0b, N1a, N1b),
                                           (N0a, N0b, N1b, N1a),
                                           (N0b, N0a, N1a, N1b),
                                           (N0b, N0a, N1b, N1a)]:
                    for r0, c0 in cells_that_see_all_of([No0, No1]):
                        if Cand in Cands[r0][c0]:  # Eliminations are possible
                            X = XCUC()
                            # XCuc[i].append(XCUC())
                            # X = XCuc[i][-1]
                            X.XC.extend([(No0, LK_STRG), (Nl0, -1)])
                            X.OE.extend([(Nl1, LK_STRG), (No1, -1)])
                            if GrpLks:
                                for r, c in [No0, Nl0, No1, Nl1]:
                                    if isinstance(r, int) and isinstance(c, int): X.UN.append((r, c))
                                    elif isinstance(c, int):
                                        for r0 in r: X.UN.append((r0, c))
                                    elif isinstance(r, int):
                                        for c0 in c: X.UN.append((r, c0))
                            else: X.UN.extend([No0, Nl0, No1, Nl1])
                            XCuc[i].append(X)
                            break
    return Lks, XCuc


def find_even_x_loop_starts(Cands, GrpLks = False):
    # Scans the puzzle for strong links, and find pairs of strong links, that if they were ends of
    # an x-chain would produce eliminations.  It is only worthwhile attempting to build x-chains from
    # these productive strong link ends.
    #
    # A list of strong links:
    #   Lks[Cand][...]  = SL  # a strong link
    #                   = (N0, N1)  # the Node (cell) ends of the strong link (Capital C)
    #                   = ((r0, c0), (r1, c1)) # the r/c coords of the Nodes forming the links.
    # A list of X-Chains under Construction
    #   XLuc[Cand][...].XC = [(No0, LK_STRG), (Nl0, Lk), (Na0, LK_STRG), (Na1, Lk), (Nb0, LK_STRG), (Nb1, Lk), ... ]
    #                  .OE = [(Nl1, LK_STRG), (No1, Lkx)]  # lkx is the link back to No0
    #                  .UN = [No0, Nl0, No1, Nl1, Na0, Na1, Nb0, Nb1, ...]

    Lks  = [[], [], [], [], [], [], [], [], []]
    XLuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand in enumerate(range(1, 10)):
        Lks[i] = find_single_cand_strong_links(Cand, Cands, GrpLks)

        lenLks = len(Lks[i])
        for l0 in range(lenLks-1):
            N0a, N0b = Lks[i][l0]
            for l1 in range(l0+1, lenLks):
                N1a, N1b = Lks[i][l1]
                for No0, Nl0, No1, Nl1 in [(N0a, N0b, N1a, N1b),
                                           (N0a, N0b, N1b, N1a),
                                           (N0b, N0a, N1a, N1b),
                                           (N0b, N0a, N1b, N1a)]:
                    Lk = ccells_are_linked(No0, Cand, No1, Cand, Cands)
                    if Lk == LK_NONE: continue
                    #  The open ends of the potential chain are linked so a potential loop exists if
                    #  a chain can be formed from the link ends of the nodes.
                    X = XCUC()
                    # XLuc[i].append(XCUC())
                    # X = XLuc[i][-1]
                    X.XC.extend([(No0, LK_STRG), (Nl0, -1)])
                    if GrpLks:
                        for r, c in [No0, Nl0, No1]:
                            if isinstance(r, int) and isinstance(c, int): X.UN.append((r, c))
                            elif isinstance(c, int):
                                for r0 in r: X.UN.append((r0, c))
                            elif isinstance(r, int):
                                for c0 in c: X.UN.append((r, c0))
                        r, c = Nl1
                        if isinstance(r, int) and isinstance(c, int):
                            if Nl1 in X.UN: continue
                            else: X.UN.append(Nl1)
                        elif isinstance(c, int):
                            for r0 in r:
                                if (r0, c) not in X.UN: X.UN.append((r0,c))
                                else: X = None; break
                            # else: continue
                        elif isinstance(r, int):
                            for c0 in c:
                                if (r, c0) not in X.UN: X.UN.append((r, c0))
                                else: X = None; break
                    else:
                        X.UN.extend([No0, Nl0, No1])
                        if Nl1 not in X.UN: X.UN.append(Nl1)
                        else: X = None; break
                    if X:
                        X.OE.extend([(Nl1, LK_STRG), (No1, LK_WEAK if Lk == LK_WEAK else LK_WKST), (No0, -1)])
                        XLuc[i].append(X)
    return Lks, XLuc

def find_strong_x_loop_starts(Cands, GrpLks = False):
    # Scans the puzzle for strong links, and find pairs of strong links, that if they were ends of
    # an x-chain would produce eliminations.  It is only worthwhile attempting to build x-chains from
    # these productive strong link ends.
    #
    # A list of strong links:
    #   Lks[Cand][...]  = SL  # a strong link
    #                   = (N0, N1)  # the Node (cell) ends of the strong link (Capital C)
    #                   = ((r0, c0), (r1, c1)) # the r/c coords of the Nodes forming the links.
    # A list of X-Chains under Construction
    #   XLuc[Cand][...].XC = [(No0, LK_STRG), (Nl0, Lk), (Na0, LK_STRG), (Na1, Lk), (Nb0, LK_STRG), (Nb1, Lk), ... ]
    #                  .OE = [(Nl1, LK_STRG), (No1, Lkx)]  # lkx is the link back to No0
    #                  .UN = [No0, Nl0, No1, Nl1, Na0, Na1, Nb0, Nb1, ...]

    Lks  = [[], [], [], [], [], [], [], [], []]
    XLuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand in enumerate(range(1, 10)):
        Lks[i] = find_single_cand_strong_links(Cand, Cands, GrpLks)

        lenLks = len(Lks[i])
        for l0 in range(lenLks-1):
            N0a, N0b = Lks[i][l0]
            for l1 in range(l0+1, lenLks):
                N1a, N1b = Lks[i][l1]
                for No0, Nl0, No1, Nl1 in [(N0a, N0b, N1a, N1b),
                                           (N0a, N0b, N1b, N1a),
                                           (N0b, N0a, N1a, N1b),
                                           (N0b, N0a, N1b, N1a)]:
                    if No0 == No1:
                        X = XCUC()
                        # XLuc[i].append(XCUC())
                        # X = XLuc[i][-1]
                        X.XC.extend([(No0, LK_STRG), (Nl0, -1)])
                        X.OE.extend([(Nl1, LK_STRG), (No1, -1)])
                        if GrpLks:
                            for r, c in [No0, Nl0, Nl1]:
                                if isinstance(r, int) and isinstance(c, int): X.UN.append((r, c))
                                elif isinstance(c, int):
                                    for r0 in r: X.UN.append((r0, c))
                                elif isinstance(r, int):
                                    for c0 in c: X.UN.append((r, c0))
                        else: X.UN.extend([No0, Nl0, Nl1])
                        XLuc[i].append(X)
    return Lks, XLuc

def find_single_cand_strong_links(Cand, Cands, GrpLks = False):

    Lks = []
    if GrpLks:
        # look in rows
        for r in range(9):
            C = []; Twr = [set(), set(), set()]
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c); Twr[c//3].add(c)
            if len(C) == 2: Lks.append(((r, C[0]), (r, C[1])))
            else:
                if Twr[0] and Twr[1] and Twr[2]: continue
                if Twr[0] and Twr[1]: Lks.append(((r, Twr[0]), (r, Twr[1])))
                elif Twr[0] and Twr[2]: Lks.append(((r, Twr[0]), (r, Twr[2])))
                elif Twr[1] and Twr[2]: Lks.append(((r, Twr[1]), (r, Twr[2])))
        # look in cols
        for c in range(9):
            R = []; Flr = [set(), set(), set()]
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r); Flr[r//3].add(r)
            if len(R) == 2: Lks.append(((R[0], c), (R[1], c)))
            else:
                if Flr[0] and Flr[1] and Flr[2]: continue
                if Flr[0] and Flr[1]: Lks.append(((Flr[0], c), (Flr[1], c)))
                elif Flr[0] and Flr[2]: Lks.append(((Flr[0], c), (Flr[2], c)))
                elif Flr[1] and Flr[2]: Lks.append(((Flr[1], c), (Flr[2], c)))
    else:  # No group links
        # look in rows
        for r in range(9):
            C = []
            for c in range(9):
                if Cand in Cands[r][c]: C.append(c)
            if len(C) == 2: Lks.append(((r, C[0]), (r, C[1])))
        # look in cols
        for c in range(9):
            R = []
            for r in range(9):
                if Cand in Cands[r][c]: R.append(r)
            if len(R) == 2: Lks.append(((R[0], c), (R[1], c)))
    # look in boxes
    for b in range(9):
        rb = (b//3)*3; cb = (b%3)*3
        B = []
        for r in [rb, rb+1, rb+2]:
            for c in [cb, cb+1, cb+2]:
                if Cand in Cands[r][c]: B.append((r, c))
        if len(B) == 2:
            B = tuple(B)
            if B not in Lks: Lks.append(B)
    return Lks

def _x_chain_elims(XChain, Cand, Cands, Step, Method):
    # returns:  True if eliminations
    #           False if no eliminations

    LenC = len(XChain)
    (re0, ce0), le0 = XChain[0]; (re1, ce1), le1 = XChain[LenC-1]
    # print(f"Cand:{Cand}, Xchain: {XChain}")
    # if ce0 == {3, 4}:
    #     print ("Help!")
    for r0, c0 in cells_that_see_all_of([(re0, ce0), (re1, ce1)]):
        if Cand in Cands[r0][c0]:
            Cands[r0][c0].discard(Cand)
            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand]])
    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Step[P_TECH] = Method
        Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_PARO]])
        NrLks = NrGrpLks = 0
        for (r0, c0), lk0 in XChain:
            if not isinstance(r0, int) and len(r0) > 1: NrGrpLks += 1
            if not isinstance(c0, int) and len(c0) > 1: NrGrpLks += 1
            NrLks += 1
            if lk0 == -1:
                Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0]])
            else:
                Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0], [P_OP, token_link(lk0)]])
        Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NrLks - NrGrpLks) * KRAKEN_LK_DIFF + NrGrpLks * GRP_LK_DIFF
        Step[P_PTRN].extend([[P_OP, OP_PARC], [P_END, ]])
        return True
    return False

def _x_loop_elims(XLoop, Cand, Cands, Step, Method):
    # In any AIC loop (X-Loop is a type of AIC loop), all Candidates in the houses of the weak
    # links that are not part of the link can be eliminated.  Also note that a strong link
    # masquerading as a weak link does not have any candidates that can be eliminated in its
    # house.

    # returns:  True  if eliminations
    #           False if no eliminations


    lenC = len(XLoop)
    for i in range(lenC - 1):
        (rx, cx), Lkx = XLoop[i]
        if Lkx != LK_WEAK: continue
        (ry, cy), Lky = XLoop[i+1]
        for r0, c0 in cells_that_see_all_of([(rx, cx), (ry, cy)]):
            if Cand in Cands[r0][c0]:
                Cands[r0][c0].discard(Cand)
                if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
                Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand]])
    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Step[P_TECH] = Method
        Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_PARO]])
        NrLks = NrGrpLks = 0
        for (r0, c0), lk0 in XLoop:
            if not isinstance(r0, int) and len(r0) > 1: NrGrpLks += 1
            if not isinstance(c0, int) and len(c0) > 1: NrGrpLks += 1
            NrLks += 1
            if lk0 == -1:
                Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0]])
            else:
                Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0], [P_OP, token_link(lk0)]])
        Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NrLks - NrGrpLks) * KRAKEN_LK_DIFF + NrGrpLks * GRP_LK_DIFF
        Step[P_PTRN].extend([[P_OP, OP_PARC], [P_END, ]])
        return True
    return False

def _x_loop_asnmt(XLoop, Grid, Cand, Cands, Step, Method):

    (r, c), Lk = XLoop[0]
    Grid[r][c] = Cand
    Cands[r][c].clear()
    Step[P_TECH] = Method
    Step[P_OUTC] = [[P_ROW, r], [P_COL, c], [P_OP, OP_ASNV], [P_VAL, Cand], [P_END, ]]
    discard_cand_from_peers(Cand, r, c, Cands)
    Step[P_PTRN].extend([[P_VAL, Cand], [P_OP, OP_PARO]])
    NrLks = NrGrpLks = 0
    for (r0, c0), lk0 in XLoop:
        if not isinstance(r0, int) and len(r0) > 1: NrGrpLks += 1
        if not isinstance(c0, int) and len(c0) > 1: NrGrpLks += 1
        NrLks += 1
        if lk0 == -1:
            Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0]])
        else:
            Step[P_PTRN].extend([[P_ROW, r0], [P_COL, c0], [P_OP, token_link(lk0)]])
    Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NrLks - NrGrpLks) * KRAKEN_LK_DIFF + NrGrpLks * GRP_LK_DIFF
    Step[P_PTRN].extend([[P_OP, OP_PARC], [P_END, ]])
    return 1


# L_ROW = 0
# L_COL = 1
# L_BOX = 2
#
# def _tech_three_link_x_chains(Grid, Step, Cands, GrpLks = False):
#
#     for Cand in range(1, 10):
#         Lks = find_single_cand_strong_links(Cand, Cands, GrpLks)
#
#         # look for horizontal skyscraper, two horizontal parallel strong links that are weakly connected.
#         lenLksRow = len(Lks[L_ROW])
#         for r0 in range(lenLksRow-1):
#             Sl0a, Sl0b = Lks[L_ROW][r0]
#             for r1 in range(r0+1, lenLksRow):
#                 # if len(Lks[L_ROW][r1]) != 2:
#                 #     print("Help!")
#                 Sl1a, Sl1b = Lks[L_ROW][r1]
#                 for O0, L0, O1, L1 in [(Sl0a, Sl0b, Sl1a, Sl1b),
#                                        (Sl0a, Sl0b, Sl1b, Sl1a),
#                                        (Sl0b, Sl0a, Sl1a, Sl1b),
#                                        (Sl0b, Sl0a, Sl1b, Sl1a)]:
#                     Lk = ccells_are_linked(L0, Cand, L1, Cand, Cands, LK_COL)
#                     if Lk == LK_NONE: continue
#                     # Horizontal Skyscraper found, what can be eliminated?
#                     if Lk != LK_WEAK: Lk = LK_WKST
#                     XChain = [(O0, LK_STRG), (L0, Lk), (L1, LK_STRG), (O1, -1)]
#                     if _x_chain_elims(XChain, Cand, Cands, Step, T_SKYSCRAPER): return 0
#         # look for vertical skyscraper, two vertical parallel strong links that are weakly connected.
#         lenLksCol = len(Lks[L_COL])
#         for c0 in range(lenLksCol-1):
#             Sl0a, Sl0b = Lks[L_COL][c0]
#             for c1 in range(c0+1, lenLksCol):
#                 Sl1a, Sl1b = Lks[L_COL][c1]
#                 for O0, L0, O1, L1 in [(Sl0a, Sl0b, Sl1a, Sl1b),
#                                        (Sl0a, Sl0b, Sl1b, Sl1a),
#                                        (Sl0b, Sl0a, Sl1a, Sl1b),
#                                        (Sl0b, Sl0a, Sl1b, Sl1a)]:
#                     Lk = ccells_are_linked(L0, Cand, L1, Cand, Cands, LK_ROW)
#                     if Lk == LK_NONE: continue
#                     # Vertical Skyscraper found, what can be eliminated?
#                     if Lk != LK_WEAK: Lk = LK_WKST
#                     XChain = [(O0, LK_STRG), (L0, Lk), (L1, LK_STRG), (O1, -1)]
#                     if _x_chain_elims(XChain, Cand, Cands, Step, T_SKYSCRAPER) == 0: return 0
#         # look for 2 string kite, a horizontal and a vertical strong link that are weakly connected (can only be through a box).
#         for r0 in range(lenLksRow):
#             Sl0a, Sl0b = Lks[L_ROW][r0]
#             for c0 in range(lenLksCol):
#                 Sl1a, Sl1b = Lks[L_COL][c0]
#                 for O0, L0, O1, L1 in [(Sl0a, Sl0b, Sl1a, Sl1b),
#                                        (Sl0a, Sl0b, Sl1b, Sl1a),
#                                        (Sl0b, Sl0a, Sl1a, Sl1b),
#                                        (Sl0b, Sl0a, Sl1b, Sl1a)]:
#                     Lk = ccells_are_linked(L0, Cand, L1, Cand, Cands, LK_BOX)
#                     if Lk == LK_NONE: continue
#                     # 2 string kite found, what can be eliminated?
#                     if Lk != LK_WEAK: Lk = LK_WKST
#                     XChain = [(O0, LK_STRG), (L0, Lk), (L1, LK_STRG), (O1, -1)]
#                     if _x_chain_elims(XChain, Cand, Cands, Step, T_TWO_STRING_KITE) == 0: return 0
#         # look for turbot fish, a strongly linked row/col and box, weakly connected through a col/row.
#         lenLksBox = len(Lks[L_BOX])
#         for b0 in range(lenLksBox):
#             Sl0a, Sl0b = Lks[L_BOX][b0]
#             for r0 in range(lenLksRow):
#                 Sl1a, Sl1b = Lks[L_ROW][r0]
#                 for O0, L0, O1, L1 in [(Sl0a, Sl0b, Sl1a, Sl1b),
#                                        (Sl0a, Sl0b, Sl1b, Sl1a),
#                                        (Sl0b, Sl0a, Sl1a, Sl1b),
#                                        (Sl0b, Sl0a, Sl1b, Sl1a)]:
#                     Lk = ccells_are_linked(L0, Cand, L1, Cand, Cands, LK_COL)
#                     if Lk == LK_NONE: continue
#                     # box/row Turbot fish found, what can be eliminated?
#                     if Lk != LK_WEAK: Lk = LK_WKST
#                     XChain = [(O0, LK_STRG), (L0, Lk), (L1, LK_STRG), (O1, -1)]
#                     if _x_chain_elims(XChain, Cand, Cands, Step, T_TURBOT_FISH) == 0: return 0
#             for c0 in range(lenLksCol):
#                 Sl1a, Sl1b = Lks[L_COL][c0]
#                 for O0, L0, O1, L1 in [(Sl0a, Sl0b, Sl1a, Sl1b),
#                                        (Sl0a, Sl0b, Sl1b, Sl1a),
#                                        (Sl0b, Sl0a, Sl1a, Sl1b),
#                                        (Sl0b, Sl0a, Sl1b, Sl1a)]:
#                     Lk = ccells_are_linked(L0, Cand, L1, Cand, Cands, LK_ROW)
#                     if Lk == LK_NONE: continue
#                     # box/col Turbot fish found, what can be eliminated?
#                     if Lk != LK_WEAK: Lk = LK_WKST
#                     XChain = [(O0, LK_STRG), (L0, Lk), (L1, LK_STRG), (O1, -1)]
#                     if _x_chain_elims(XChain, Cand, Cands, Step, T_TURBOT_FISH): return 0
#     return -1
#
# def find_single_cand_strong_links(Cand, Cands, GrpLks = False):
#
#     Lk = {L_ROW: [], L_COL: [], L_BOX: []}
#     if GrpLks:
#         # look in rows
#         for r in range(9):
#             C = []; Twr = [set(), set(), set()]
#             for c in range(9):
#                 if Cand in Cands[r][c]: C.append(c); Twr[c//3].add(c)
#             if len(C) == 2: Lk[L_ROW].append(((r, C[0]), (r, C[1])))
#             else:
#                 if Twr[0] and Twr[1] and Twr[2]: continue
#                 if Twr[0] and Twr[1]: Lk[L_ROW].append(((r, Twr[0]), (r, Twr[1])))
#                 elif Twr[0] and Twr[2]: Lk[L_ROW].append(((r, Twr[0]), (r, Twr[2])))
#                 elif Twr[1] and Twr[2]: Lk[L_ROW].append(((r, Twr[1]), (r, Twr[2])))
#         # look in cols
#         for c in range(9):
#             R = []; Flr = [set(), set(), set()]
#             for r in range(9):
#                 if Cand in Cands[r][c]: R.append(r); Flr[r//3].add(r)
#             if len(R) == 2: Lk[L_COL].append(((R[0], c), (R[1], c)))
#             else:
#                 if Flr[0] and Flr[1] and Flr[2]: continue
#                 if Flr[0] and Flr[1]: Lk[L_COL].append(((Flr[0], c), (Flr[1], c)))
#                 elif Flr[0] and Flr[2]: Lk[L_COL].append(((Flr[0], c), (Flr[2], c)))
#                 elif Flr[1] and Flr[2]: Lk[L_COL].append(((Flr[1], c), (Flr[2], c)))
#     else:  # No group links
#         # look in rows
#         for r in range(9):
#             C = []
#             for c in range(9):
#                 if Cand in Cands[r][c]: C.append(c)
#             if len(C) == 2: Lk[L_ROW].append(((r, C[0]), (r, C[1])))
#         # look in cols
#         for c in range(9):
#             R = []
#             for r in range(9):
#                 if Cand in Cands[r][c]: R.append(r)
#             if len(R) == 2: Lk[L_COL].append(((R[0], c), (R[1], c)))
#     # look in boxes
#     for b in range(9):
#         rb = (b//3)*3; cb = (b%3)*3
#         B = []
#         for r in [rb, rb+1, rb+2]:
#             for c in [cb, cb+1, cb+2]:
#                 if Cand in Cands[r][c]: B.append((r, c))
#         if len(B) == 2: Lk[L_BOX].append((B[0], B[1]))
#     return Lk
#

#
#         for ((Co0, Cl0), (Co1, Cl1)) in Ends[Cand]:
#             Lk = ccells_are_linked(Cl0, Cand, Cl1, Cand)
#
#
#     CandXCState = [{XC_SLKS:   None,          # Structure containing all possible strong links for the cand
#                     XC_STARTS: [],            # list of starting strong link pairs where eliminations can be made
#
#
#
#                     } for C in range(9)]
#     for Cand in range(1, 10):
#         CandXCState[Cand-1][XC_SLKS] = Lks = find_single_cand_strong_links(Cand, Cands, GrpLks)
#         for i0 in range(26):
#             l0 = i0//9; g0 = i0%9
#             if Lks[g0][l0] == (): continue
#             (slk0a, slk0b) = _get_sl(Lks, g0, l0)
#             for i1 in range(i0+1, 27):
#                 l1 = i1//9; g1 = i1%9
#                 if Lks[g1][l1] == (): continue
#                 (slk1a, slk1b) = _get_sl(Lks, g1, l1)
#
#                 for ((r0l, c0l), (r1l, c1l)), ((r0o, c0o), (r1o, c1o)) in [(slk0a, slk1a), (slk0b, slk1b),
#                                                                            (slk0b, slk1b), (slk0a, slk1a),
#                                                                            (slk0a, slk1b), (slk0b, slk1a),
#                                                                            (slk0b, slk1a), (slk0a, slk1b)]:
#                     # first check that there is a weak link between the ends and ccells can
#                     # be eliminated before going to the effort of building the chain.
#                     for r0, c0 in cells_that_see_all_of([(r0o, r0o), (r1o, c1o)]):
#                         if Cand in Cands[r0][c0]:
#                             break
#                     else:
#                         continue
#                     # there will be eliminations.
#                     # First search for another strong link that each 'l' ends of the existing strong links sees forming
#                     # a five link chain.
#                     for i2 in range(27):
#                         l2 = i2//9; g2 = i2%9
#                         if Lks[g2][l2] == (): continue
#                         ((r2a, c2a), (r2b, c2b)) = _get_sl(Lks, g2, l2)
#                         if (r2a, c2a) in UC1 or (r2b, c2b) in UC1: continue
#                         lk1 = ccells_are_linked(r0l, c01, Cand, r2a, c2a, Cand, Cands)
#                         lk2 = ccells_are_linked(r01, c01, Cand, r2b, c2b, Cand, Cands)
#                         lk3 = ccells_are_linked(r1l, c1l, Cand, r2a, c2a, Cand, Cands)
#                         lk4 = ccells_are_linked(r1l, c1l, Cand, r2b, cb2, Cand, Cands)
#                         if lk1 or lk2 or lk3 or lk4: break
#                     else:
#                         #  linking ends of chain cannot see any of the strong links - continue searching
#                         continue
#                     if lk1 and lk2:
#                         # found a chain 0o__0l..2a__2b..1l__1o
#                         pass
#                         return "blah blah"
#                     # try the link the other way round
#                     if lk3 and lk4:
#                         # found a chain 0o__0l..2b__2a..1l__1o
#                         pass
#                         return "blah blah"
#                     # add starting links to XC_STARTS so we do not search again when looking for longer chains.
#                     CandXCState[Cand-1][XC_STARTS].append((((r0o, c0o), (r0l, c0l)), ((r1o, c1o), (r1l, c1l))))
#
#     # exhausted the search for n links for all candidates, now try n + 2
#     for Cand in range(1, 10):
#         Lks = CandXCState[Cand-1][XC_SLKS]
#         for xcs, (((r0o, c0o,), (r0l, c0l)), ((r1o, c1o), (r1l, c1l))) in enumerate(copy(CAndXCState[Cand-1][XC_STARTS])):
#             UC0 = [(r0o, c0o), (r0l, c0l), (r1o, c1o), (r1l, c1l)]
#             for i2 in range(27):
#                 l2 = i2//9; g2 = i2%9
#                 if Lks[g2][l2] == (): continue
#                 ((r2a, c2a), (r2b, c2b)) = _get_sl(Lks, g2, l2)
#                 if (r2a, c2a) in UC0 or (r2b, c2b) in UC0: continue
#                 lk0l2a = ccells_are_linked(r0l, c01, Cand, r2a, c2a, Cand, Cands)
#                 if lk0l2a:
#                     for i3 in range(27):
#                         if i3 == i2: continue
#                         l3 = i3//9; g3 = i3%9
#                         if Lks[g3][l3] == (): continue
#                         ((r3a, c3a), (r3b, c3b)) = _get_sl(Lks, g3, l3)
#                         if (r3a, c3a) in UC0 or (r3b, c3b) in UC0: continue
#                         lk1l3a = ccells_are_linked(r1l, c1l, Cand, r3a, c3a, Cand, Cands)
#                         if lk1l3a:
#                             lk2b3b = ccells_are_linked(r2b, c2b, Cand, r3b, c3b, Cand, Cands)
#                             if lk2b3b:
#                                 # found a chain  0o__0l..2a__2b..3b__3a..1l__1o
#                                 pass
#                                 return "blah blah"
#                         else:  # try link 3 the other way round.
#                             lk1l3b = ccells_are_linked(r1l, c1l, Cand, r3b, c3b, Cand, Cands)
#                             if lk1l3b:
#                                 lk2b3a = ccells_are_linked(r2b, c2b, Cand, r3a, c3a, Cand, Cands)
#                                 if lk2b3a:
#                                     # found a chain 0o__0l..2a__2b..3a__3b..1l__1o
#                                     pass
#                                     return "blah blah"
#                 else:  # not lk0l2a:  # try lk 2 the other way round.
#                     lk0l2b = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
#                     if lk0l2b:
#                         for i3 in range(27):
#                             if i3 == i2: continue
#                             l3 = i3//9; g3 = i3%9
#                             if Lks[g3][l3] == (): continue
#                             ((r3a, c3a), (r3b, c3b)) = _get_sl(Lks, g3, l3)
#                             if (r3a, c3a) in UC0 or (r3b, c3b) in UC0: continue
#                             lk1l3a = ccells_are_linked(r1l, c1l, Cand, r3a, c3a, Cand, Cands)
#                             if lk1l3a:
#                                 lk2b3b = ccells_are_linked(r2a, c2a, Cand, r3b, c3b, Cand, Cands)
#                                 if lk2b3b:
#                                     # found a chain  0o__0l..2b__2a..3b__3a..1l__1o
#                                     pass
#                                     return "blah blah"
#                             else:  # try link 3 the other way round.
#                                 lk1l3b = ccells_are_linked(r1l, c1l, Cand, r3b, c3b, Cand, Cands)
#                                 if lk1l3b:
#                                     lk2b3a = ccells_are_linked(r2b, c2b, Cand, r3a, c3a, Cand, Cands)
#                                     if lk2b3a:
#                                         # found a chain 0o__0l..2b__2a..3a__3b..1l__1o
#                                         pass
#                                         return "blah blah"
#                                 else:  # either end of lk 2 and 3 cannot make a link to the upstream chain segments
#                                     # a chain cannot be constructed from these starts with this candidate, remove it
#                                     # from XC_STARTS
#                                     CandXCState[Cand-1][XC_STARTS].pop(xcs)
#             # if notlk2a
#             #
#             # lk3 = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
#             #             if :
#             #                     # A 5 link chain has been been found.
#             #
#             #             else:  # Try the new strong link the other way round.
#             #                 lk3 = ccells_are_linked(r0l, c0l, Cand, r2b, c2b, Cand, Cands)
#             #                 if lk3:
#             #                     l
#
# def _get_sl(Lks, g, lk):
#
#     if g == L_ROW:
#         a, b = Lks[g][lk]
#         return (lk, a), (lk, b)
#     if g == L_COL:
#         a, b = Lks[g][lk]
#         return (a, ll), (b, ll)
#     else:  # g == L_BOX
#         return Lks[g][lk]
#
#         # look for x loops.  Find two cells that see each other, and build out a strong ended AIC from
#         # both ends and get them to connect.  If a connection is formed, then all same valued ccells in
#         # weakly linked houses that are not part of the chain can be eliminated.
