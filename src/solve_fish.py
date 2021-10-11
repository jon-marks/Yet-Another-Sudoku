from copy import copy

from globals import *
from solve_utils import *

def tech_finned_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_FINNED_X_WING, AIC = 0, GrpLks = False)

def tech_kraken_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_KRAKEN_X_WING, AIC = 2, GrpLks = False)

def tech_gl_kraken_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_GL_KRAKEN_X_WING, AIC = 2, GrpLks = True)

def tech_finned_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_FINNED_SWORDFISH, AIC = 0)

def tech_kraken_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_KRAKEN_SWORDFISH, AIC = 2, GrpLks = False)

def tech_gl_kraken_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_GL_KRAKEN_SWORDFISH, AIC = 2, GrpLks = True)

def tech_finned_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_FINNED_JELLYFISH, AIC = 0)

def tech_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_KRAKEN_JELLYFISH, AIC = 2, GrpLks = False)

def tech_gl_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_GL_KRAKEN_JELLYFISH, AIC = 2, GrpLks = True)

def tech_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    # A X-Wing occurs when the same candidate occurs twice each in two separate
    # rows (base sets), and these candidates lie in the same two columns (cover
    # sets).  All occurrences of the candidates in the same 2 columns (cover
    # sets) that are not part of the X-Wing can be eliminated.

    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    if Method != T_UNDEF and Method != T_X_WING: return -2

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(8):
            if len(BC[r0]) != 2: continue
            for r1 in range(r0+1, 9):
                if len(BC[r1]) != 2: continue
                BS = [r0, r1]
                CU = sorted(BC[r0] | BC[r1])
                if len(CU) != 2:
                    continue
                for cs in CU:
                    ci = 0
                    for bs in BS:
                        if Cand in Cands[bs][cs]:
                            ci += 1
                            if ci >= 2:
                                break
                    else:
                        break
                else:
                    if _elim_cands_in_fish(Cand, BS, CU, P_ROW, Cands, Step): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(8):
            if len(BC[c0]) != 2: continue
            for c1 in range(c0+1, 9):
                if len(BC[c1]) != 2: continue
                BS = [c0, c1]
                CU = sorted(BC[c0] | BC[c1])
                if len(CU) != 2: continue
                for cs in CU:
                    ci = 0
                    for bs in BS:
                        if Cand in Cands[cs][bs]:
                            ci += 1
                            if ci >= 2: break
                    else: break
                else:
                    if _elim_cands_in_fish(Cand, BS, CU, P_COL, Cands, Step): return 0
    return -1

def _finned_x_wings(Grid, Step, Cands, Method, AIC = 0, GrpLks = False):
    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    # A Finned X-Wing occurs when only one of the base sets has more (than two)
    # occurrences of the candidate outside of the cover set.  A finned
    # fish has an extra appendage or two of the same candidate called fins.
    # Only those candidates in the cover sets that are not part of the
    # X-Wing that "see" (are peers of the) fin candidates can be eliminated.

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(8):
            if len(BC[r0]) < 2: continue
            for r1 in range(r0+1, 9):
                if len(BC[r1]) < 2: continue
                CU = sorted(BC[r0] | BC[r1])
                # A valid union CU is 2 cover sets and 1 or 2 fins.
                # Multiple fins must be in the same block for non-Kraken finned fish
                lenCU = len(CU)
                BS = [r0, r1]
                if lenCU == 3:  # 2 cover sets and 1 fin.
                    CI = [0, 0, 0]  # cover intersections
                    for ci, cu in enumerate(CU):
                        for bs in BS:
                            if Cand in Cands[bs][cu]:  CI[ci] += 1
                    for cx in range(2, -1, -1):
                        CS = CU.copy(); del CS[cx]
                        CF = [CU[cx]]
                        for cs in CS:
                            if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                break
                        else:  # a valid finned fish pattern, what can be eliminated?
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
                elif lenCU == 4:  # 2 cover sets and 2 fins.
                    CI = [0, 0, 0, 0]  # cover intersections
                    for ci, cu in enumerate(CU):
                        for bs in BS:
                            if Cand in Cands[bs][cu]: CI[ci] += 1
                    for cx0 in range(3, 0, -1):
                        cb0 = cx0//3
                        for cx1 in range(cx0-1, -1, -1):
                            cb1 = cx1//3
                            if cb0 != cb1: continue  # Fins must be in same cover chute
                            CS = CU.copy(); del CS[cx0]; del CS[cx1]
                            CF = [CU[cx0], CU[cx1]]
                            for cs in CS:
                                if CI[CU.index(cs)] < 2 and not (cs//3 == cb0 == cb1):  # only one cover set intersection and not in same cover chute as fin
                                    break
                            else:  # a valid finned fish pattern, what can be eliminated
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(8):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 9):
                if len(BC[c1]) < 2: continue
                CU = sorted(BC[c0] | BC[c1])
                lenCU = len(CU)
                BS = [c0, c1]
                if lenCU == 3:
                    CI = [0, 0, 0]
                    for ci, cu in enumerate(CU):
                        for bs in BS:
                            if Cand in Cands[cu][bs]: CI[ci] += 1
                    for cx in range(2, -1, -1):
                        CS = CU.copy(); del CS[cx]
                        CF = [CU[cx]]
                        for cs in CS:
                            if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                break
                        else:  # a valid finned fish pattern, what can be eliminated?
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
                elif lenCU == 4:
                    CI = [0, 0, 0, 0]
                    for ci, cu in enumerate(CU):
                        for bs in BS:
                            if Cand in Cands[cu][bs]: CI[ci] += 1
                        for cx0 in range(3, 0, -1):
                            cb0 = cx0//3
                            for cx1 in range(cx0-1, -1, -1):
                                cb1 = CU[cx1]//3
                                if cb0 != cb1: continue  # Fins must be in same cover chute.
                                CS = CU.copy(); del CS[cx0]; del CS[cx1]
                                CF = [CU[cx0], CU[cx1]]
                                for cs in CS:
                                    if CI[CU.index(cs)] < 2 and not (cs//3 == cx0//3 == cx1//3):  # only one cover set intersection and not in same cover chute as fin
                                        break
                                else:  # a valid finned fish pattern, what can be eliminated
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
    return -1


def tech_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    # A Swordfish occurs when the same candidate occurs only 2 or 3 times
    # in three separate rows (base sets)and at least two of the candidates are
    # aligned in the associated columns (cover sets).  Here the candidate can be
    # eliminated from other rows along the associated columns.  This algorithm
    # relies on the union of the cover set being exactly three columns which
    # defines the Swordfish pattern. In each of the three columns, where the
    # candidate is present in at least one of the base set rows, the candidate,
    # if present in the remaining non base set rows can be eliminated.
    #
    # Base sets can also be columns and cover sets, rows - to find column wise
    # Swordfish

    if Method != T_UNDEF and Method != T_SWORDFISH: return -2

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(7):
            if len(BC[r0]) < 2: continue
            for r1 in range(r0+1, 8):
                if len(BC[r1]) < 2: continue
                for r2 in range(r1+1, 9):
                    if len(BC[r2]) < 2: continue
                    BS = [r0, r1, r2]
                    CU = sorted(BC[r0] | BC[r1] | BC[r2])
                    if len(CU) != 3: continue
                    for cs in CU:
                        ci = 0
                        for bs in BS:
                            if Cand in Cands[bs][cs]:
                                ci += 1
                                if ci >= 2: break
                        else: break
                    else:
                        if _elim_cands_in_fish(Cand, BS, CU, P_ROW, Cands, Step): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(7):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 8):
                if len(BC[c1]) < 2: continue
                for c2 in range(c1+1, 9):
                    if len(BC[c2]) < 2: continue
                    BS = [c0, c1, c2]
                    CU = sorted(BC[c0] | BC[c1] | BC[c2])
                    if len(CU) != 3: continue
                    for cs in CU:
                        ci = 0
                        for bs in BS:
                            if Cand in Cands[cs][bs]:
                                ci += 1
                                if ci >= 2: break
                        else: break
                    else:
                        if _elim_cands_in_fish(Cand, BS, CU, P_COL, Cands, Step): return 0
    return -1

def _finned_swordfish(Grid, Step, Cands, Method, AIC = 0, GrpLks = False):
    # TODO Need to update this description.  A Swordfish occurs when the same candidate occurs only 2 or 3 times
    # in three separate rows (base sets)and at least two of the candidates are
    # aligned in the associated columns (cover sets).  Here the candidate can be
    # eliminated from other rows along the associated columns.  This algorithm
    # relies on the union of the cover set being exactly three columns which
    # defines the Swordfish pattern. In each of the three columns, where the
    # candidate is present in at least one of the base set rows, the candidate,
    # if present in the remaining non base set rows can be eliminated.
    #
    # Base sets can also be columns and cover sets, rows - to find column wise
    # Swordfish

    # AIC == 0:  only look for a weak link between the ccells.
    # AIC == 1:  only look for a weak link and between the ccells or the
    #            ccells "see" a strong link
    # AIC == 2:  weak link, "see" a strong link or weak-ended-AIC.


    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(7):
            if len(BC[r0]) < 2: continue
            for r1 in range(r0+1, 8):
                if len(BC[r1]) < 2: continue
                for r2 in range(r1+1, 9):
                    if len(BC[r2]) < 2: continue
                    CU = sorted(BC[r0] | BC[r1] | BC[r2])
                    # A valid union CU is 3 cover sets and 1 or 2 fins.
                    # Multiple fins must be in the same block for non-Kraken finned fish
                    lenCU = len(CU)
                    BS = [r0, r1, r2]
                    if lenCU == 4:  # 3 cover sets and 1 fin.
                        CI = [0, 0, 0, 0]  # cover intersections
                        for ci, cu in enumerate(CU):
                            for bs in BS:
                                if Cand in Cands[bs][cu]:  CI[ci] += 1
                        for cx in range(3, -1, -1):
                            CS = CU.copy(); del CS[cx]
                            CF = [CU[cx]]
                            for cs in CS:
                                if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                    break
                            else:  # a valid finned fish pattern, what can be eliminated?
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
                    elif lenCU == 5:  # 3 cover sets and 2 fins.
                        CI = [0, 0, 0, 0, 0]  # cover intersections
                        for ci, cu in enumerate(CU):
                            for bs in BS:
                                if Cand in Cands[bs][cu]: CI[ci] += 1
                        for cx0 in range(4, 0, -1):
                            cb0 = cx0//3
                            for cx1 in range(cx0-1, -1, -1):
                                cb1 = cx1//3
                                if cb0 != cb1: continue  # Fins must be in same cover chute
                                CS = CU.copy(); del CS[cx0]; del CS[cx1]
                                CF = [CU[cx0], CU[cx1]]
                                for cs in CS:
                                    if CI[CU.index(cs)] < 2 and not (cs//3 == cb0 == cb1):  # only one cover set intersection and not in same cover chute as fin
                                        break
                                else:  # a valid finned fish pattern, what can be eliminated
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(7):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 8):
                if len(BC[c1]) < 2: continue
                for c2 in range(c1+1, 9):
                    if len(BC[c2]) < 2: continue
                    CU = sorted(BC[c0] | BC[c1] | BC[c2])
                    lenCU = len(CU)
                    BS = [c0, c1, c2]
                    if lenCU == 4:
                        CI = [0, 0, 0, 0]
                        for ci, cu in enumerate(CU):
                            for bs in BS:
                                if Cand in Cands[cu][bs]: CI[ci] += 1
                        for cx in range(3, -1, -1):
                            CS = CU.copy(); del CS[cx]
                            CF = [CU[cx]]
                            for cs in CS:
                                if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                    break
                            else:  # a valid finned fish pattern, what can be eliminated?
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
                    elif lenCU == 5:
                        CI = [0, 0, 0, 0, 0]
                        for ci, cu in enumerate(CU):
                            for bs in BS:
                                if Cand in Cands[cu][bs]: CI[ci] += 1
                            for cx0 in range(4, 0, -1):
                                cb0 = cx0//3
                                for cx1 in range(cx0-1, -1, -1):
                                    cb1 = CU[cx1]//3
                                    if cb0 != cb1: continue  # Fins must be in same cover chute.
                                    CS = CU.copy(); del CS[cx0]; del CS[cx1]
                                    CF = [CU[cx0], CU[cx1]]
                                    for cs in CS:
                                        if CI[CU.index(cs)] < 2 and not (cs//3 == cx0//3 == cx1//3):  # only one cover set intersection and not in same cover chute as fin
                                            break
                                    else:  # a valid finned fish pattern, what can be eliminated
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
    return -1


def tech_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    # A Jellyfish occurs when the same candidate occurs only 2 to 4 times in
    # in four separate rows (base sets)and at least two of the candidates are
    # aligned in the associated columns (cover sets).  Here the candidate can be
    # eliminated from other rows along the associated columns.  This algorithm
    # relies on the union of the cover set being exactly four columns which
    # defines the Jellyfish pattern. In each of the four columns, where the
    # candidate is present in at least one of the base set rows, the candidate,
    # if present in the remaining non base set rows can be eliminated.
    #
    # Base sets can also be columns and cover sets, rows - to find column wise
    # Jellyfish

    if Method != T_UNDEF and Method != T_JELLYFISH: return -2

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(6):
            if len(BC[r0]) < 2: continue
            for r1 in range(r0+1, 7):
                if len(BC[r1]) < 2: continue
                for r2 in range(r1+1, 8):
                    if len(BC[r2]) < 2: continue
                    for r3 in range(r2+1, 9):
                        if len(BC[r3]) < 2: continue
                        BS = [r0, r1, r2, r3]
                        CU = sorted(BC[r0] | BC[r1] | BC[r2] | BC[r3])
                        if len(CU) != 4: continue
                        for cs in CU:
                            ci = 0  # cover intersection
                            for bs in BS:
                                if Cand in Cands[bs][cs]:
                                    ci += 1
                                    if ci >= 2: break
                            else: break
                        else:
                            if _elim_cands_in_fish(Cand, BS, CU, P_ROW, Cands, Step): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(6):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 7):
                if len(BC[c1]) < 2: continue
                for c2 in range(c1+1, 8):
                    if len(BC[c2]) < 2: continue
                    for c3 in range(c2+1, 9):
                        if len(BC[c3]) < 2: continue
                        BS = [c0, c1, c2, c3]
                        CU = sorted(BC[c0] | BC[c1] | BC[c2] | BC[c3])
                        if len(CU) != 4: continue
                        for cs in CU:
                            ci = 0  # cover intersection
                            for bs in BS:
                                if Cand in Cands[cs][bs]:
                                    ci += 1
                                    if ci >= 2: break
                            else: break
                        else:
                            if _elim_cands_in_fish(Cand, BS, CU, P_COL, Cands, Step): return 0
    return -1

def tech_finned_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_FINNED_JELLYFISH, AIC = 0)

def tech_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_KRAKEN_JELLYFISH, AIC = 2, GrpLks = False)

def tech_gl_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_GL_KRAKEN_JELLYFISH, AIC = 2, GrpLks = True)

def _finned_jellyfish(Grid, Step, Cands, Method, AIC = 0, GrpLks = False):
    # AIC == 0:  only look for a weak link between the ccells.
    # AIC == 1:  only look for a weak link and between the ccells or the
    #            ccells "see" a strong link
    # AIC == 2:  weak link, "see" a strong link or weak-ended-AIC.

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(6):
            if len(BC[r0]) < 2: continue
            for r1 in range(r0+1, 7):
                if len(BC[r1]) < 2: continue
                for r2 in range(r1+1, 8):
                    if len(BC[r2]) < 2: continue
                    for r3 in range(r2+1, 9):
                        if len(BC[r3]) < 2: continue
                        CU = sorted(BC[r0] | BC[r1] | BC[r2] | BC[r3])
                        # A valid union CU is 4 cover sets and 1 or 2 fins.
                        # Multiple fins must be in the same block for non-Kraken finned fish
                        lenCU = len(CU)
                        BS = [r0, r1, r2, r3]
                        if lenCU == 5:  # 4 cover sets and 1 fin
                            CI = [0, 0, 0, 0, 0]  # Cover intersections
                            for ci, cu in enumerate(CU):
                                for bs in BS:
                                    if Cand in Cands[bs][cu]: CI[ci] += 1
                            for cx in range(4, -1, -1):
                                CS = CU.copy(); del CS[cx]
                                CF = [CU[cx]]          # cover fin
                                for cs in CS:
                                    # if the cover set is in the same chute as the fins, then it is permitted one or
                                    # more intersections with base sets, else it must have two or more intersections with
                                    # base sets.
                                    if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                        break
                                else:  # a valid finned fish pattern, what can be eliminated?
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
                        elif lenCU == 6:  # 4 cover sets and 2 fins.
                            CI = [0, 0, 0, 0, 0, 0]  # Cover intersections
                            for ci, cu in enumerate(CU):
                                for bs in BS:
                                    if Cand in Cands[bs][cu]: CI[ci] += 1
                            for cx0 in range(5, 0, -1):
                                cb0 = CU[cx0]//3
                                for cx1 in range(cx0-1, -1, -1):
                                    cb1 = CU[cx1]//3
                                    if cb0 != cb1: continue  # Fins must be in same cover chute.
                                    CS = CU.copy(); del CS[cx0]; del CS[cx1]
                                    CF = [CU[cx0], CU[cx1]]
                                    for cs in CS:
                                        # if the cover set is in the same chute as the fins, then it is permitted one or
                                        # more intersections with base sets, else it must have two or more intersections with
                                        # base sets.
                                        if CI[CU.index(cs)] < 2 and not (cs//3 == cb0 == cb1):  # only one cover set intersection and not in same cover chute as fin
                                            break
                                    else:  # a valid finned fish pattern, what can be eliminated
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, AIC, GrpLks): return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(6):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 7):
                if len(BC[c1]) < 2: continue
                for c2 in range(c1+1, 8):
                    if len(BC[c2]) < 2: continue
                    for c3 in range(c2+1, 9):
                        if len(BC[c3]) < 2: continue
                        CU = sorted(BC[c0] | BC[c1] | BC[c2] | BC[c3])
                        # A valid union CU is 4 cover sets and 1 or 2 fins.
                        # Multiple fins must be in the same block for non-Kraken finned fish
                        lenCU = len(CU)
                        BS = [c0, c1, c2, c3]
                        if lenCU == 5:
                            CI = [0, 0, 0, 0, 0]  # Cover intersections
                            for ci, cu in enumerate(CU):
                                for bs in BS:
                                    if Cand in Cands[cu][bs]: CI[ci] += 1
                            for cx in range(4, -1, -1):
                                CS = CU.copy(); del CS[cx]
                                CF = [CU[cx]]          # cover fin
                                for cs in CS:
                                    # if the cover set is in the same chute as the fins, then it is permitted one or
                                    # more intersections with base sets, else it must have two or more intersections with
                                    # base sets.
                                    if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
                                        break
                                else:  # a valid finned fish pattern, what can be eliminated?
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
                        elif lenCU == 6:
                            CI = [0, 0, 0, 0, 0, 0]  # Cover intersections
                            for ci, cu in enumerate(CU):
                                for bs in BS:
                                    if Cand in Cands[cu][bs]: CI[ci] += 1
                            for cx0 in range(5, 0, -1):
                                cb0 = cx0//3
                                for cx1 in range(cx0-1, -1, -1):
                                    cb1 = CU[cx1]//3
                                    if cb0 != cb1: continue  # Fins must be in same cover chute.
                                    CS = CU.copy(); del CS[cx0]; del CS[cx1]
                                    CF = [CU[cx0], CU[cx1]]
                                    for cs in CS:
                                        # if the cover set is in the same chute as the fins, then it is permitted one or
                                        # more intersections with base sets, else it must have two or more intersections with
                                        # base sets.
                                        if CI[CU.index(cs)] < 2 and not (cs//3 == cx0//3 == cx1//3):  # only one cover set intersection and not in same cover chute as fin
                                            break
                                    else:  # a valid finned fish pattern, what can be eliminated
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, AIC, GrpLks): return 0
    return -1

# todo: tech_franken_swordfish
# todo: tech_franken_jellyfish

def _elim_cands_in_fish(Cand, BS, CS, rc, Cands, Step):

    if rc == P_ROW:
        for r in set(range(9)) - set(BS):
            for c in CS:
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
    elif rc == P_COL:
        for c in sorted(set(range(9)) - set(BS)):
            for r in CS:
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])

    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Ord = len(BS)
        if Ord == 2: Step[P_TECH] = T_X_WING
        elif Ord == 3: Step[P_TECH] = T_SWORDFISH
        elif Ord == 4: Step[P_TECH] = T_JELLYFISH
        else: return False
        if rc == P_ROW:
            Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS], [P_END, ]]
            return True
        elif rc == P_COL:
            Step[P_PTRN] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS], [P_END, ]]
            return True
    return False

def _elim_cands_in_finned_fish(Cand, BS, CS, CF, rc, Cands, Step, Method, AIC = 0, GrpLks = False):
    # AIC == 0:  only look for a weak link between the ccells.
    # AIC == 1:  only look for a weak link and between the ccells or the
    #            ccells "see" a strong link
    # AIC == 2:  weak link, "see" a strong link or weak-ended-AIC.
#     # searck for all non group linked AIC's first before looking for group links.
#     res = _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = AIC)
#     if res == -1 and AIC:
#         return _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = AIC, GrpLks = True)
#     return res
#
# def _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = 0, GrpLks = False):
    Fins = []
    Chains = []
    AICFound = False
    NrLks = 0  # #links is one less than #Nodes
    NrGrpLks = 0
    if rc == P_ROW:
        for r in BS:
            for c in CF:
                if Cand in Cands[r][c]:
                    Fins.append((r, c))
        for r in sorted(set(range(9)) - set(BS)):
            for c in CS:
                if Cand not in Cands[r][c]: continue
                # each cover out of [r][c] must see (be weakly linked to) all the fins.
                NL = [[] for i in range(len(Fins))]
                for i, (Rf, Cf) in enumerate(Fins):
                    NL[i] = are_ccells_weakly_linked(Rf, Cf, Cand, r, c, Cand, Cands, AIC = AIC, GrpLks = GrpLks)
                    if not NL[i]: break
                else:  # the cover in rc sees all the fins.
                    if AIC:
                        for N in NL:
                            if len(N) > 2: AICFound = True
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                    for N in sorted(NL):
                        if Chains: Chains.append([P_SEP, ])
                        for r0, c0, Cand, Lk in N:
                            if isinstance(r0, set) or isinstance(c0, set):  NrGrpLks += 1
                            if Lk == -1:
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0]])
                            else:
                                NrLks += 1
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk)]])
    elif rc == P_COL:
        for c in BS:
            for r in CF:
                if Cand in Cands[r][c]:
                    Fins.append((r, c))
        for c in sorted(set(range(9)) - set(BS)):
            for r in CS:
                if Cand not in Cands[r][c]: continue
                NL = [[] for i in range(len(Fins))]
                for i, (Rf, Cf) in enumerate(Fins):
                    NL[i] = are_ccells_weakly_linked(Rf, Cf, Cand, r, c, Cand, Cands, AIC = AIC, GrpLks = GrpLks)
                    if not NL[i]: break
                else:
                    if AIC:
                        for N in NL:
                            if len(N) > 2: AICFound = True
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                    for N in sorted(NL):
                        if Chains: Chains.append([P_SEP, ])
                        for r0, c0, Cand, Lk in N:
                            if isinstance(r0, set) or isinstance(c0, set): NrGrpLks +=1
                            if Lk == -1:
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0]])
                            else:
                                NrLks += 1
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk)]])
    if Step[P_OUTC]:
        # Ord = len(BS)
        # if Ord == 2: Step[P_TECH] = T_FINNED_X_WING if not AICFound else T_KRAKEN_X_WING
        # elif Ord == 3: Step[P_TECH] = T_FINNED_SWORDFISH if not AICFound else T_KRAKEN_SWORDFISH
        # elif Ord == 4: Step[P_TECH] = T_FINNED_JELLYFISH if not AICFound else T_KRAKEN_JELLYFISH
        # else: return -1
        Step[P_TECH] = Method
        Step[P_DIFF] = T[Step[P_TECH]][T_DIFF] + (NrLks - NrGrpLks) * KRAKEN_LK_DIFF + NrGrpLks * GRP_LK_DIFF
        if rc == P_ROW:
            Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        elif rc == P_COL:
            Step[P_PTRN] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]
        else:
            return False
        Step[P_OUTC].append([P_END, ])
        for r, c in sorted(Fins):
            Step[P_PTRN].extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
        Step[P_PTRN].append([P_SEP, ])
        Step[P_PTRN].extend(Chains)
        Step[P_PTRN].append([P_END, ])
        return True
    return False
