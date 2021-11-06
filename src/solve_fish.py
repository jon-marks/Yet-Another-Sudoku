from copy import copy

from globals import *
from solve_utils import *

def tech_finned_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_FINNED_X_WING, Kraken = False, GrpLks = False)

def tech_kraken_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_KRAKEN_X_WING, Kraken = True, GrpLks = False)

def tech_gl_kraken_x_wings(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_X_WING: return -2
    return _finned_x_wings(Grid, Step, Cands, T_GL_KRAKEN_X_WING, Kraken = True, GrpLks = True)

def tech_finned_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_FINNED_SWORDFISH, Kraken = False, GrpLks = False)

def tech_kraken_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_KRAKEN_SWORDFISH, Kraken = True, GrpLks = False)

def tech_gl_kraken_swordfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_SWORDFISH: return -2
    return _finned_swordfish(Grid, Step, Cands, T_GL_KRAKEN_SWORDFISH, Kraken = True, GrpLks = True)

def tech_finned_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_FINNED_JELLYFISH, Kraken = False, GrpLks = False)

def tech_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_KRAKEN_JELLYFISH, Kraken = True, GrpLks = False)

def tech_gl_kraken_jellyfish(Grid, Step, Cands, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_GL_KRAKEN_JELLYFISH: return -2
    return _finned_jellyfish(Grid, Step, Cands, T_GL_KRAKEN_JELLYFISH, Kraken = True, GrpLks = True)

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

def _finned_x_wings(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
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
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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

def _finned_swordfish(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
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
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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

def _finned_jellyfish(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
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
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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
                                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
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

def _elim_cands_in_finned_fish(Cand, BS, CS, CF, rc, Cands, Step, Method, Kraken = False, GrpLks = False):
#     # searck for all non group linked AIC's first before looking for group links.
#     res = _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = AIC)
#     if res == -1 and AIC:
#         return _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = AIC, GrpLks = True)
#     return res
#
# def _elim_cands_in_finned_fish1(Cand, BS, CS, CF, rc, Cands, Step, AIC = 0, GrpLks = False):
    Fins = []
    Cvrs = []
    S = STATUS()
    if rc == P_ROW:
        for r in BS:
            for c in CF:
                if Cand in Cands[r][c]: Fins.append((r, c))
        for r in sorted(set(range(9)) - set(BS)):
            for c in CS:
                if Cand in Cands[r][c]: Cvrs.append((r, c))
        _find_cover_that_sees_all_fins(Fins, Covers, Cand, Cands, Kraken, GrpLks, S)
    else:  # rc == P_COL:
        for c in BS:
            for r in CF:
                if Cand in Cands[r][c]: Fins.append((r, c))
        for c in sorted(set(range(9))-set(BS)):
            for r in CS:
                if Cand in Cands[r][c]: Cvrs.append((r, c))
        _find_cover_that_sees_all_fins(Fins, Covers, Cand, Cands, Kraken, GrpLks, S)
    if S.Tech != T_UNDEF:
        Ord = len(BS)
        if Ord == 2: Step[P_TECH] = T_FINNED_X_WING
        elif Ord == 3: Step[P_TECH] = T_FINNED_SWORDFISH
        elif Ord == 4: Step[P_TECH] = T_FINNED_JELLYFISH
        if Kraken: Step[P_TECH] |= T_KRAKEN
        if GrpLks: Step[P_TECH] |= T_GRPLK

        if rc == P_ROW: Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        else: Step[P_PTRN] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]  # rc == P_COL
        for r, c in sorted(Fins): Step[P_PTRN].extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
        Step[P_PTRN].append([P_SEP, ])
        NLks = NGrpLks = 0
        Chains = []
        for Ch in S.Pattern:  # one chain for each fin in S.Pattern
            if Chains: Chains.append([P_SEP, ])
            for r, c, Cand, Lk, in Ch:
                NLks += 1
                if not isinstance(r, int) and len(N.r) > 1: NGrpLks += 1
                if not isinstance(c, int) and len(N.c) > 1: NGrpLks += 1
                if Lk == LK_NONE: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c]])
                else: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
        Step[P_PTRN].extend(Chains).append([P_END, ])
        Step[P_DIFF] = T[Step[P_TECH]][T_DIFF]+(NLks-NGrpLks)*KRAKEN_LK_DIFF+NGrpLks*GRP_LK_DIFF
        for r, c, Cand in S.Outcome:
            Cands[r][c].discard(Cand)
            if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
            Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
        Step[P_OUTC].append([P_END, ])
        return 0
    return -1

def _find_covers_that_see_all_fins(Fins, Covers, Cand, Cands, Kraken, GrpLks, Status):
    # Finds covers that see fins by building trees (one for each cover) that grow branches which are
    # the alternating links to next nodes until the tree links to both fins.  This algorithm builds
    # all trees simultaneously growing a level of branches for all trees before attempting the next
    # level.
    #
    # Fins:     A list of (r, c) cell coord tuples that contain Cand, that any cover must see all of
    #           to be eliminated.
    # Covers:   A list of (r, c) cell coord tuples that contain Cand, from which Cand can be
    #           eliminated if it sees all fins.
    # Cand:     The specific candidate value for eliminations
    # Cands:    The Candidate grid.
    # Kraken:   If True then looking for connecting chains, else just direct links.
    # GrpLks:   If True looking for connecting chains with group links.  Not used if Kraken is false
    # Status:   If eliminations are found, returns the found pattern and outcome.
    #           Tech != T_UNDEF if pattern found - does not indicate which pattern.
    #           Instance of STATUS() class.


    if not Kraken:  # GrpLks always False when Kraken is False
        # Find all covers that can be eliminated as not very expensive for non kraken to find
        for rc, cc in Covers:
            FP = [[] for i in len(Fins)]
            for i, rf, cf in enumerate(Fins):
                LkT, LkH = how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands, False)
                if LkT == LK_NONE: break
                FP[i].extend([(rc, cc, Cand, LkT), (rf, cf, Cand, LK_NONE)])
            else:  # A cover that sees all the fins has been found.
                Status.Tech = 0
                Status.Pattern.append(FP)
                Status.Outcome.append((rcvr, ccvr, Cand))
    else:  # Kraken
        # Find only first cover that can be eliminated as building chains is expensive.
        # Builds an Orchard of trees, each tree being a cover, growing branches to build chains to
        # fins.  The first cover to build chains to all the fins wins.  Algorithm grows the branches
        # one level at a time for all trees before moving onto the next level.
        Orchard = []; Idx = []

        for i, rc, cc in enumerate(Covers):
            if GrpLks:
                rc = {rc}; cc = {cc}
                Fins = [({r}, {c}, Cand) for r, c in Fins]
            else:
                Fins = [(r, c, Cand) for r, c in Fins]
            Orchard.append(TNODE({rc}, {cc}, Cand, None, None, None, None))
            Idx.append(i)
            Tree = Orchard[-1]
            for r, c, Cand, LkT, LkH in list_ccells_linked_to({rc}, {cc}, Cand, Cands, LK_STWK, GrpLks):
                if LkT == LK_WEAK:
                    Tree.Children.append(TNODE(r, c, Cand, LK_WEAK, [(Tree.r, Tree.c, Tree.Cand, LK_WEAK)], Tree, None))
                else:
                    Tree.Children.append(TNODE(r, c, Cand, LK_STRG, [(Tree.r, Tree.c, Tree.Cand, LK_STRG)], Tree, None))
                    Tree.Children.append(TNODE(r, c, Cand, LK_WKST, [(Tree.r, Tree.c, Tree.Cand, LK_WKST)], Tree, None))
        while Idx:
            # A CvrTree is removed from the orchard when none of its branches are able to form chains to all fins
            # While there are CvrTrees in the orchard, there is hope of finding a chain in remaining cover trees
            # that can yield eliminations.
            for i, Tree in enumerate(Orchard):
                if Tree:
                    Tree = find_next_branches(Tree, Fins, Cands, GrpLks, 1, Status)
                    if Status.Tech != T_UNDEF: return
                    if not CvrTree.Root.Children:
                        Idx.remove(i)
                        CvrTree.Root = None

def _find_next_branches(Branch, Fins, Cands, GrpLks, Lvl, Status):
    # The recursing function which builds the next level of branch for a tree returns with Status filled
    # if it has found a cover that sees all fins.  Pruning is acheived by not copying a child branch from
    # the Children list into the Kids list.

    Kids = []
    for C in Branch.Children:
        if C.Children:  # Recurse down the children
            C.Children = _find_next_branches(C.Children, Fins, Cands, GrpLks, Lvl+1, Status)
            if Status.Tech != T_UNDEF: return Children
        else:
            for r, c, Cand, LkT, LkH in list_cells_linked_to(C.r, C.c, C.Cand, Cands, LK_STWK if C.Lk == LK_STRG else LK_STRG, GrpLks):
                if C.Lk == LK_STRG:
                    if LkT == LK_STWK: LkT = LK_WKST
                else: LkT  = LK_STRG
                Ch0 = [*C.Chain, *[(C.r, C.c, C.Cand, LkT)]]
                pos = is_in_chain(r, c, Cand, Ch0, GrpLks)
                if pos >= 0: continue
                for rf, cf, Candf in Fins:
                    if are_same_cells(r, c, Cand, rf, cf, Candf, GrpLks): break
                else:  # node does not intersect chain or fins and can be adopted as a child.
                    if Lvl & 0x01:  # But first if the chain is odd length, see if node connects to a fin
                        for i, rf, cf, Candf in enumerate(Fins):
                            LkTf, LkHf = how_cells_linked(r, c, Cand, rf, cf, Candf, GrpLks)
                            if LkTf == LK_NONE: continue
                            if LkT == LK_STRG:
                                if LkTf == LK_STWK: LkTf = LK_WKST
                                if LkTf == LK_WEAK or LkTf == LK_WKST:  # a valid chain to a fin.
                                    Status.Pattern.append([*Ch0, *[(r, c, Cand, LkTf), (rf, cf, Candf, LK_NONE)]])
                            else:  # LkT ==  LK_WEAK or LK_WKST
                                if LkTf == LK_STWK:
                                    LkTf = LK_STRG
                                    Status.Pattern.append([*Ch0, *[(r, c, Cand, LkTf), (rf, cf, Candf, LK_NONE)]])
                            if len(Fins) == len(Status.Pattern):  # cover elimination possible
                                re, ce, Cande, Lke = Ch0[0]
                                Status.Outcome = [(re, ce, Cande)]
                                Status.Tech = T_KRAKEN
                                return
                    else:  # add the child branch
                        C.Children.append(TNODE(r, c, Cand, LkT, C, Ch0))
        if C.Children: Kids.append(C)
    return Kids
