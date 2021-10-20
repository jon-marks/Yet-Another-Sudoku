from copy import deepcopy

from globals import *
from solve_utils import *

class AICUC:   # AI-Chain under construction
    def __init__(self):
        self.ST  = []    # One end of AI-Chain/loop being built
        self.EN  = []    # Other end of the AI-Chain/loop
        self.UC  = []    # list of used ccells in the AI-Chain/loop
        self.EL  = []    # Ccells to eliminate if an AI Chain can be made.


def tech_sc_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_SC_AI_CHAIN: return -2

    return _sc_ai_chains(Grid, Step, Cands, Method)

def tech_dc_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_DC_AI_CHAIN: return -2

    return _dc_ai_chains(Grid, Step, Cands, Method)

def tech_even_ai_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_EVEN_AI_LOOP: return -2

    return _even_ai_loops(Grid, Step, Cands, Method)

def tech_strong_ai_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_STRONG_AI_LOOP: return -2

    return _strong_ai_loops(Grid, Step, Cands, Method)

def tech_gl_sc_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_SC_AI_CHAIN: return -2

    return _sc_ai_chains(Grid, Step, Cands, Method, GrpLks = True)

def tech_gl_dc_ai_chains(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_DC_AI_CHAIN: return -2

    return _dc_ai_chains(Grid, Step, Cands, Method, GrpLks = True)

def tech_gl_even_ai_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_EVEN_AI_LOOP: return -2

    return _even_ai_loops(Grid, Step, Cands, Method, GrpLks = True)

def tech_gl_strong_ai_loops(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_STRONG_AI_LOOP: return -2

    return _strong_ai_loops(Grid, Step, Cands, Method, GrpLks = True)

def _sc_ai_chains(Grid, Step, Cands, Method, GrpLks = False):

    AIC0 = _find_sc_ai_chain_starts(Cands, GrpLks)
    CandsAIC = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    while CandsAIC:
        for Cand in sorted(CandsAIC):
            AIC1 = []
            i = Cand-1
            # for dbg1, X in enumerate(AIC0[i]):
            for X in AIC0[i]:
                N0 = X.ST[-1]; Noe = X.EN[0]
                for r1, c1, Cand1, Lk1 in list_ccells_linked_to(N0.r, N0.c, N0.Cand, Cands, LK_STWK, GrpLks):
                    UC1 = []
                    if GrpLks:
                        if isinstance(r1, int) and isinstance(c1, int): UC1.append((r1, c1, Cand1))
                        elif isinstance(c1, int):
                            for rx in r1: UC1.append((rx, c1, Cand1))
                        elif isinstance(r1, int):
                            for cx in c1: UC1.append((r1, cx, Cand1))
                    else: UC1.append((r1, c1, Cand1))
                    for UCx in UC1:
                        if UCx in X.UC: break
                    else:
                        for r2, c2, Cand2, Lk2 in list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STRG, GrpLks):
                            UC2 = []
                            if GrpLks:
                                if isinstance(r2, int) and isinstance(c2, int): UC2.append((r2, c2, Cand2))
                                elif isinstance(c2, int):
                                    for rx in r2: UC2.append((rx, c2, Cand2))
                                elif isinstance(r2, int):
                                    for cx in c2: UC2.append((r2, cx, Cand2))
                            else: UC2.append((r2, c2, Cand2))
                            for UCx in UC2:
                                if UCx in X.UC: break
                            else:
                                X1 = deepcopy(X)
                                X1.ST[-1].Lk = Lk1
                                X1.ST.extend([NODE(r1, c1, Cand1, LK_STRG), NODE(r2, c2, Cand2, LK_NONE)])
                                # can this newly added strong link connect to the other ENd?
                                Lk = ccells_are_linked((r2, c2), Cand2, (Noe.r, Noe.c), Noe.Cand, Cands)
                                if Lk != LK_NONE:
                                    X1.ST[-1].Lk = LK_WEAK if Lk == LK_WEAK else LK_WKST
                                    X1.ST.extend(X1.EN)
                                    _aic_elims(X1, Cands, Step, T_GL_SC_AI_CHAIN if GrpLks else T_SC_AI_CHAIN)
                                    return 0
                                else:
                                    X1.UC.extend(UC1 + UC2)
                                    AIC1.append(X1)
            if AIC1: AIC0[i] = AIC1
            else:
                CandsAIC.discard(Cand)
                AIC0[i] = []
    return -1

def _dc_ai_chains(Grid, Step, Cands, Method, GrpLks = False):

    # AICDC0 = _find_dc_ai_chain_starts(Cands, GrpLks)

    return -1

def _even_ai_loops(Grid, Step, Cands, Method, GrpLks = False):

    return -1

def _strong_ai_loops(Grid, Step, Cands, Method, GrpLks = False):

    return -1


def _find_sc_ai_chain_starts(Cands, GrpLks = False):
    # find same candidate value
    # Note that it is much simpler to handle UC and EL lists as tuples rather than CCELL classes.

    # Lks   = [[], [], [], [], [], [], [], [], []]
    AICuc = [[], [], [], [], [], [], [], [], []]
    for i, Cand0 in enumerate(range(1, 10)):
        Lks = find_all_strong_cand_links(Cand0, Cands, GrpLks)

        lenLks = len(Lks)
        for l0 in range(lenLks-1):
            (Cc0o, Cc0l) = Lks[l0]  # Cc0o: open end of link 0, Cc0l: linked end of link 0
            for l1 in range(l0+1, lenLks):
                (Cc1o, Cc1l) = Lks[l1]
                if Cc0o == Cc1l and Cc0l == Cc1o: continue
                UC = []
                if GrpLks:
                    for (r, c, Cand) in [Cc0o, Cc0l, Cc1o, Cc1l]:
                        if isinstance(r, int) and isinstance(c, int): UC.append((r, c, Cand))
                        elif isinstance(c, int):
                            for r1 in r: UC.append((r1, c, Cand))
                        elif isinstance(r, int):
                            for c1 in c: UC.append((r, c1, Cand))
                else: UC = [Cc0o, Cc0l, Cc1o, Cc1l]
                if len(UC) != len(set(UC)): continue  # if UC contains duplicate links the chain start are touching which is not valid.
                EN = []  # end nodes
                if GrpLks:
                    for (r, c, Cand) in [Cc0o, Cc1o]:
                        if isinstance(r, int) and isinstance(c, int): EN.append((r, c, Cand))
                        elif isinstance(c, int):
                            for r1 in r: EN.append((r1, c, Cand))
                        elif isinstance(r, int):
                            for c1 in c: EN.append((r, c1, Cand))
                else: EN = [Cc0o, Cc1o]
                EL = []  # are there any eliminations?
                (r0o, c0o, Cand0o) = Cc0o; (r1o, c1o, Cand1o) = Cc1o
                for r0, c0 in cells_that_see_all_of([(r0o, c0o), (r1o, c1o)]):
                    if Cand0 in Cands[r0][c0]: EL.append((r0, c0, Cand0))
                    # if (r0, c0, Cand0) not in EN and Cand0 in Cands[r0][c0]: EL.append((r0, c0, Cand0))
                if EL:
                    (r0l, c0l, Cand0l) = Cc0l; (r1l, c1l, Cand1l) = Cc1l
                    X = AICUC()
                    X.ST.extend([NODE(r0o, c0o, Cand0o, LK_STRG), NODE(r0l, c0l, Cand0l, LK_NONE)])
                    X.EN.extend([NODE(r1l, c1l, Cand1l, LK_STRG), NODE(r1o, c1o, Cand1o, LK_NONE)])
                    X.UC = UC
                    X.EL = EL
                    AICuc[i].append(deepcopy(X))
    return AICuc

def _find_dc_ai_chain_starts(Cands, GrpLks = False):
    # seek out two same value candidates in a house first.

    AICDCStarts = []
    # look in rows first
    for r in range(9):
        for c0 in range(8):
            for c1 in range(c0+1, 9):
                C0iC1 = sorted(Cands[r][c0] & Cands[r][c1])
                if len(C0iC1) != 2: continue
                # found a potential candidate pair in a house. Do their ccells have strong links?

#  loop for both cands rather than inlining the loop.
                S0 = []; S1 = []
                for (ra, ca, Canda, Lka) in list_ccells_linked_to(r, c0, C0iC1[0], Cands, LK_STRG, GrpLks):
                    if ra == r: continue  # only interested in links in cols and boxes
                    S0.extend([[NODE(r, c0, C0iC1[0], LK_STRG), NODE(ra, ca, C0iC1[0], LK_NONE)]])
                for (ra, ca, Canda, Lka) in list_ccells_linked_to(r, c1, C0iC1[1], Cands, LK_STRG, GrpLks):
                    if ra == r: continue
                    S1.extend([[NODE(ra, ca, C0iC1[1], LK_STRG), NODE(r, c1, C0iC1[1], LK_NONE)]])
                for Sa in S0:
                    for Sb in S1:
                        X = AICUC()
                        X.ST = Sa
                        X.EN = Sb
                        if GrpLks:
                            X.UC = [CCELL(Sa[0].r, Sa[0].c, Sa[0].Cand), CCELL(Sb[1].r, Sb[1].c, Sb[1].Cand)]
                            if isinstance(Sa[1].r, int) and isinstance(Sa[1].c, int): X.UC.append(CCELL(Sa[1].r, Sa[1].c, Sa[1].Cand))
                            elif isinstance(S0[1].c, int):
                                for ra in Sa[1].r: X.UC.append(CCELL(ra, Sa[1].c, Sa[1].Cand))
                            elif isinstance(Sa[1].r, int):
                                for ca in Sa[1].c: X.UC.append(CCELL(Sa[1].r, ca, Sa[1].Cand))
                            if isinstance(S1[1].r, int) and isinstance(S1.c, int): X.UC.append(CCELL(S1[1].r, S1[1].c, S1[1].Cand))
                            elif isinstance(S1[1].c, int):
                                for ra in S1[1].r: X.UC.append(CCELL(ra, S1[1].c, S0[1].Cand))
                            elif isinstance(S1[1].r, int):
                                for ca in S1[1].c: X.UC.append(CCELL(S1[1].r, ca, S1[1].Cand))
                        else: X.UC = [CCELL(Sa[0].r, Sa[0].c, Sa[0].Cand), CCELL(Sb[1].r, Sb[1].c, Sb[1].Cand), CCELL(Sa[1].r, Sa[1].c, Sa[1].Cand), CCELL(S1[1].r, S1[1].c, S1[1].Cand)]
                        AICDCStarts.append(deepcopy(X))

                S0 = []; S1 = []
                for (ra, ca, Canda, Lka) in list_ccells_linked_to(r, c0, C0iC1[1], Cands, LK_STRG, GrpLks):
                    if ra == r: continue  # only interested in links in cols and boxes
                    S0.extend([[NODE(r, c0, C0iC1[0], LK_STRG), NODE(ra, ca, C0iC1[1], LK_NONE)]])
                for (ra, ca, Canda, Lka) in list_ccells_linked_to(r, c1, C0iC1[0], Cands, LK_STRG, GrpLks):
                    if ra == r: continue
                    S1.extend([[NODE(ra, ca, C0iC1[1], LK_STRG), NODE(r, c1, C0iC1[0], LK_NONE)]])
                for Sa in S0:
                    for Sb in S1:
                        X = AICUC()
                        X.ST = Sa
                        X.EN = Sb
                        if GrpLks:
                            X.UC = [CCELL(Sa[0].r, Sa[0].c, Sa[0].Cand), CCELL(Sb[1].r, Sb[1].c, Sb[1].Cand)]
                            if isinstance(Sa[1].r, int) and isinstance(Sa[1].c, int): X.UC.append(CCELL(Sa[1].r, Sa[1].c, Sa[1].Cand))
                            elif isinstance(S0[1].c, int):
                                for ra in Sa[1].r: X.UC.append(CCELL(ra, Sa[1].c, Sa[1].Cand))
                            elif isinstance(Sa[1].r, int):
                                for ca in Sa[1].c: X.UC.append(CCELL(Sa[1].r, ca, Sa[1].Cand))
                            if isinstance(S1[1].r, int) and isinstance(S1.c, int): X.UC.append(CCELL(S1[1].r, S1[1].c, S1[1].Cand))
                            elif isinstance(S1[1].c, int):
                                for ra in S1[1].r: X.UC.append(CCELL(ra, S1[1].c, S0[1].Cand))
                            elif isinstance(S1[1].r, int):
                                for ca in S1[1].c: X.UC.append(CCELL(S1[1].r, ca, S1[1].Cand))
                        else: X.UC = [CCELL(Sa[0].r, Sa[0].c, Sa[0].Cand), CCELL(Sb[1].r, Sb[1].c, Sb[1].Cand), CCELL(Sa[1].r, Sa[1].c, Sa[1].Cand), CCELL(S1[1].r, S1[1].c, S1[1].Cand)]
                        AICDCStarts.append(deepcopy(X))

        # still neeed to complete for cols and boxes.
    return AICDCStarts

def _aic_elims(X, Cands, Step, Method):
    # returns:  always True because it is only called when there are elims to be made.

    for r0, c0, Cand0 in X.EL:  # cells_that_see_all_of([(re0, ce0), (re1, ce1)]):
        Cands[r0][c0].discard(Cand0)
        if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
        Step[P_OUTC].extend([[P_ROW, r0], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand0]])
    Step[P_OUTC].append([P_END, ])
    Step[P_TECH] = Method
    NrLks = NrGrpLks = 0
    for N in X.ST:
        if not isinstance(N.r, int) and len(N.r) > 1: NrGrpLks += 1
        if not isinstance(N.c, int) and len(N.c) > 1: NrGrpLks += 1
        NrLks += 1
        if N.Lk == LK_NONE:
            Step[P_PTRN].extend([[P_VAL, N.Cand], [P_ROW, N.r], [P_COL, N.c], [P_END, ]])
        else:
            Step[P_PTRN].extend([[P_VAL, N.Cand], [P_ROW, N.r], [P_COL, N.c], [P_OP, token_link(N.Lk)]])
    Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NrLks - NrGrpLks) * KRAKEN_LK_DIFF + NrGrpLks * GRP_LK_DIFF
    return True
