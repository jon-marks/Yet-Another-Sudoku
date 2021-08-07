from copy import copy

from globals import *
from solve_utils import *

def tech_x_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # A X-Wing occurs when the same candidate occurs twice each in two separate
    # rows (base sets), and these candidates lie in the same two columns (cover
    # sets).  All occurrences of the candidates in the same 2 columns (cover
    # sets) that are not part of the X-Wing can be eliminated.

    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    if Method != T_UNDEF and Method != T_X_WING: return -1

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
                BS = {r0, r1}
                CU = BC[r0] | BC[r1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [r0, r1]:
                        if Cand in Cands[base][cvr]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 2 and CU == CS:
                    if _elim_cands_in_fish(Cand, BS, CS, P_ROW, Cands, ElimCands, Step) == 0:
                        return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(8):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 9):
                if len(BC[c1]) < 2: continue
                BS = {c0, c1}
                CU = BC[c0] | BC[c1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [c0, c1]:
                        if Cand in Cands[cvr][base]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 2 and CU == CS:
                    if _elim_cands_in_fish(Cand, BS, CS, P_COL, Cands, ElimCands, Step) == 0:
                        return 0
    return -1

def tech_finned_x_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_X_WING: return -1
    return _finned_x_wings(Grid, Step, Cands, ElimCands, AIC = 0)

def tech_kraken_x_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_X_WING: return -1
    return _finned_x_wings(Grid, Step, Cands, ElimCands, AIC = 2)

def _finned_x_wings(Grid, Step, Cands, ElimCands = None, AIC = 0):
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
                BS = {r0, r1}
                CU = BC[r0] | BC[r1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [r0, r1]:
                        if Cand in Cands[base][cvr]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 2 and len(CF):
                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, ElimCands, Step, AIC = AIC) == 0:
                        return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(8):
            if len(BC[c0]) < 2: continue
            for c1 in range(c0+1, 9):
                if len(BC[c1]) < 2: continue
                BS = {c0, c1}
                CU = BC[c0] | BC[c1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [c0, c1]:
                        if Cand in Cands[cvr][base]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 2 and len(CF):
                    if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, ElimCands, Step, AIC = AIC) == 0:
                        return 0
    return -1

def tech_almost_x_wings(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    # An Almost X-Wing is different variation of fish.  These are fish that are
    # missing an appendage - ie a candidate value in a cell, that if present,
    # would make the fish.  Filling that cell with a a phantom candidate creates
    # a Hidden X-Wing
    # or Hidden Finned X-Wing from which candidates can be eliminated. There may
    # be more than one possibility of placing a candidate in a cell to create a
    # hidden (finned) fish, all possibilities should be explored.

    if Method != T_UNDEF and Method != T_ALMOST_X_WING: return -1

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(8):
            if not len(BC[r0]): continue
            for r1 in range(r0+1, 9):
                if not len(BC[r1]): continue
                BS = {r0, r1}
                CU = BC[r0] | BC[r1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [r0, r1]:
                        if Cand in Cands[base][cvr]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 1 and len(CF):  # found an almost x-wing
                    for r4 in [r0, r1]:
                        for c4 in sorted(CF):
                            if Cand not in Cands[r4][c4]:
                                Cands[r4][c4].add(Cand)
                                CF1 = copy(CF)
                                CS1 = copy(CS)
                                CF1.discard(c4)
                                CS1.add(c4)
                                if len(CS1) == 2 and CU == CS1:  # found a hidden X-Wing
                                    SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                    if _elim_cands_in_fish(Cand, BS, CS1, P_ROW, Cands, ElimCands, SubStep) == 0:
                                        SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                           [P_ROW, r4], [P_COL, c4],
                                                           [P_CON, ]] + SubStep[P_COND]
                                        Step[P_SUBS].append(SubStep)
                                        Step[P_OUTC].extend(SubStep[P_OUTC])
                                elif len(CS1) == 2 and len(CF1):  # found a Hidden Finned X-Wing
                                    SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                    if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_ROW, Cands, ElimCands,
                                                                  SubStep, AIC = 2) == 0:
                                        SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                           [P_ROW, r4], [P_COL, c4],
                                                           [P_CON, ]] + SubStep[P_COND]
                                        Step[P_SUBS].append(SubStep)
                                        Step[P_OUTC].extend(SubStep[P_OUTC])
                                Cands[r4][c4].discard(Cand)
                    if len(Step[P_SUBS]):
                        Step[P_TECH] = T_ALMOST_X_WING
                        BR = sorted(BS)
                        Step[P_COND] = [[P_VAL, Cand], [P_ROW, BR], [P_COL, CS]]
                        for br in BR:
                            for fc in sorted(CF):
                                if Cand in Cands[br][fc]:
                                    Step[P_COND].extend([[P_CON, ], [P_ROW, br], [P_COL, fc]])
                        Step[P_COND].append([P_END, ])
                        return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(8):
            if not len(BC[c0]): continue
            for c1 in range(c0+1, 9):
                if not len(BC[c1]): continue
                BS = {c0, c1}
                CU = BC[c0] | BC[c1]
                CS = set()
                CF = set()
                for cvr in sorted(CU):
                    ci = 0  # cover intersection
                    for base in [c0, c1]:
                        if Cand in Cands[cvr][base]: ci += 1
                    if ci > 1: CS.add(cvr)
                    else: CF.add(cvr)
                if len(CS) == 1 and len(CF):  # found an almost x-wing
                    for c4 in sorted(BS):
                        for r4 in sorted(CF):
                            if Cand not in Cands[r4][c4]:
                                Cands[r4][c4].add(Cand)
                                CF1 = copy(CF)
                                CS1 = copy(CS)
                                CF1.discard(r4)
                                CS1.add(r4)
                                if len(CS1) == 2 and CU == CS1:  # found a hidden X-Wing
                                    SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                    if _elim_cands_in_fish(Cand, BS, CS1, P_COL, Cands, ElimCands, SubStep) == 0:
                                        SubStep[P_TECH] = T_X_WING
                                        SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                           [P_ROW, r4], [P_COL, c4],
                                                           [P_CON, ]] + SubStep[P_COND]
                                        Step[P_SUBS].append(SubStep)
                                        Step[P_OUTC].extend(SubStep[P_OUTC])
                                elif len(CS1) == 2 and len(CF1):  # found a Hidden Finned XWing
                                    SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                    if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_COL, Cands, ElimCands,
                                                                  SubStep, AIC = 2) == 0:
                                        SubStep[P_TECH] = T_FINNED_X_WING
                                        SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                           [P_ROW, r4], [P_COL, c4],
                                                           [P_CON, ]] + SubStep[P_COND]
                                        Step[P_SUBS].append(SubStep)
                                        Step[P_OUTC].extend(SubStep[P_OUTC])
                                Cands[r4][c4].discard(Cand)
                    if len(Step[P_SUBS]):
                        Step[P_TECH] = T_ALMOST_X_WING
                        BC = sorted(BS)
                        Step[P_COND] = [[P_VAL, Cand], [P_COL, BC], [P_ROW, CS]]
                        for bc in BC:
                            for fr in sorted(CF):
                                if Cand in Cands[fr][bc]:
                                    Step[P_COND].extend([[P_CON, ], [P_ROW, fr], [P_COL, bc]])
                        Step[P_COND].append([P_END, ])
                        return 0
    return -1


def tech_swordfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
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

    if Method != T_UNDEF and Method != T_SWORDFISH: return -1

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
                    BS = {r0, r1, r2}
                    CU = BC[r0] | BC[r1] | BC[r2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [r0, r1, r2]:
                            if Cand in Cands[base][cvr]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 3 and CU == CS:
                        if _elim_cands_in_fish(Cand, BS, CS, P_ROW, Cands, ElimCands, Step) == 0:
                            return 0
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
                    BS = {c0, c1, c2}
                    CU = BC[c0] | BC[c1] | BC[c2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [c0, c1, c2]:
                            if Cand in Cands[cvr][base]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 3 and CU == CS:
                        if _elim_cands_in_fish(Cand, BS, CS, P_COL, Cands, ElimCands, Step) == 0:
                            return 0
    return -1

def tech_finned_swordfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_SWORDFISH: return -1
    return _finned_swordfish(Grid, Step, Cands, ElimCands, AIC = 0)

def tech_kraken_swordfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_SWORDFISH: return -1
    return _finned_swordfish(Grid, Step, Cands, ElimCands, AIC = 2)

def _finned_swordfish(Grid, Step, Cands, ElimCands = None, AIC = 0):
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
                    BS = {r0, r1, r2}
                    CU = BC[r0] | BC[r1] | BC[r2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [r0, r1, r2]:
                            if Cand in Cands[base][cvr]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 3 and len(CF):
                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, ElimCands, Step, AIC = AIC) == 0:
                            return 0
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
                    BS = {c0, c1, c2}
                    CU = BC[c0] | BC[c1] | BC[c2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [c0, c1, c2]:
                            if Cand in Cands[cvr][base]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 3 and len(CF):
                        if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, ElimCands, Step, AIC = AIC) == 0:
                            return 0
    return -1

def tech_almost_swordfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
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

    if Method != T_UNDEF and Method != T_ALMOST_SWORDFISH: return -1

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(7):
            if not len(BC[r0]): continue
            for r1 in range(r0+1, 8):
                if not len(BC[r1]): continue
                for r2 in range(r1+1, 9):
                    if not len(BC[r2]): continue
                    BS = {r0, r1, r2}
                    CU = BC[r0] | BC[r1] | BC[r2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [r0, r1, r2]:
                            if Cand in Cands[base][cvr]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 2 and len(CF):  # found an almost swordfish.
                        for r4 in [r0, r1, r2]:
                            for c4 in sorted(CF):
                                if Cand not in Cands[r4][c4]:
                                    Cands[r4][c4].add(Cand)
                                    CF1 = copy(CF)
                                    CS1 = copy(CS)
                                    CF1.discard(c4)
                                    CS1.add(c4)
                                    if len(CS1) == 3 and CU == CS1:  # found a hidden swordfish
                                        SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                        if _elim_cands_in_fish(Cand, BS, CS1, P_ROW, Cands, ElimCands, SubStep) == 0:
                                            SubStep[P_TECH] = T_SWORDFISH
                                            SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                               [P_ROW, r4], [P_COL, c4],
                                                               [P_CON, ]] + SubStep[P_COND]
                                            Step[P_SUBS].append(SubStep)
                                            Step[P_OUTC].extend(SubStep[P_OUTC])
                                    elif len(CS1) == 3 and len(CF1):  # found a Hidden finned swordfish
                                        SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                        if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_ROW, Cands, ElimCands,
                                                                      SubStep, AIC = True) == 0:
                                            SubStep[P_TECH] = T_FINNED_SWORDFISH
                                            SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                               [P_ROW, r4], [P_COL, c4],
                                                               [P_CON, ]] + SubStep[P_COND]
                                            Step[P_SUBS].append(SubStep)
                                            Step[P_OUTC].extend(SubStep[P_OUTC])
                                    Cands[r4][c4].discard(Cand)
                        if len(Step[P_SUBS]):
                            Step[P_TECH] = T_ALMOST_SWORDFISH
                            BR = sorted(BS)
                            Step[P_COND] = [[P_VAL, Cand], [P_ROW, BR], [P_COL, CS]]
                            for br in BR:
                                for fc in sorted(CF):
                                    if Cand in Cands[br][fc]:
                                        Step[P_COND].extend([[P_CON, ], [P_ROW, br], [P_COL, fc]])
                            Step[P_COND].append([P_END, ])
                            return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(7):
            if not len(BC[c0]): continue
            for c1 in range(c0+1, 8):
                if not len(BC[c1]): continue
                for c2 in range(c1+1, 9):
                    if not len(BC[c2]): continue
                    BS = {c0, c1, c2}
                    CU = BC[c0] | BC[c1] | BC[c2]
                    CS = set()
                    CF = set()
                    for cvr in sorted(CU):
                        ci = 0  # cover intersection
                        for base in [c0, c1, c2]:
                            if Cand in Cands[cvr][base]: ci += 1
                        if ci > 1: CS.add(cvr)
                        else: CF.add(cvr)
                    if len(CS) == 2 and len(CF):  # found an almost swordfish
                        for c4 in sorted(BS):
                            for r4 in sorted(CF):
                                if Cand not in Cands[r4][c4]:
                                    Cands[r4][c4].add(Cand)
                                    CF1 = copy(CF)
                                    CS1 = copy(CS)
                                    CF1.discard(r4)
                                    CS1.add(r4)
                                    if len(CS1) == 3 and CU == CS1:  # found a hidden swordfish
                                        SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                        if _elim_cands_in_fish(Cand, BS, CS1, P_COL, Cands, ElimCands, SubStep) == 0:
                                            SubStep[P_TECH] = T_SWORDFISH
                                            SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                               [P_ROW, r4], [P_COL, c4],
                                                               [P_CON, ]] + SubStep[P_COND]
                                            Step[P_SUBS].append(SubStep)
                                            Step[P_OUTC].extend(SubStep[P_OUTC])
                                    elif len(CS1) == 3 and len(CF1):  # found a Hidden Finned swordfish
                                        SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                        if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_COL, Cands, ElimCands,
                                                                      SubStep, AIC = True) == 0:
                                            SubStep[P_TECH] = T_FINNED_SWORDFISH
                                            SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                               [P_ROW, r4], [P_COL, c4],
                                                               [P_CON, ]] + SubStep[P_COND]
                                            Step[P_SUBS].append(SubStep)
                                            Step[P_OUTC].extend(SubStep[P_OUTC])
                                    Cands[r4][c4].discard(Cand)
                        if len(Step[P_SUBS]):
                            Step[P_TECH] = T_ALMOST_SWORDFISH
                            BC = sorted(BS)
                            Step[P_COND] = [[P_COL, BC], [P_ROW, CS]]
                            for bc in BC:
                                for fr in sorted(CF):
                                    if Cand in Cands[fr][bc]:
                                        Step[P_COND].extend([[P_CON, ], [P_ROW, fr], [P_COL, bc]])
                            Step[P_COND].extend([[P_OP, OP_PRES], [P_VAL, Cand], [P_END, ]])
                            return 0
    return -1

def tech_jellyfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
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

    if Method != T_UNDEF and Method != T_JELLYFISH: return -1

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
                        BS = {r0, r1, r2, r3}
                        CU = BC[r0] | BC[r1] | BC[r2] | BC[r3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [r0, r1, r2, r3]:
                                if Cand in Cands[base][cvr]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 4 and CU == CS:
                            if _elim_cands_in_fish(Cand, BS, CS, P_ROW, Cands, ElimCands, Step) == 0:
                                return 0
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
                        BS = {c0, c1, c2, c3}
                        CU = BC[c0] | BC[c1] | BC[c2] | BC[c3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [c0, c1, c2, c3]:
                                if Cand in Cands[cvr][base]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 4 and CU == CS:
                            if _elim_cands_in_fish(Cand, BS, CS, P_COL, Cands, ElimCands, Step) == 0:
                                return 0
    return -1

def tech_finned_jellyfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_FINNED_JELLYFISH: return -1
    return _finned_jellyfish(Grid, Step, Cands, ElimCands, AIC = 0)

def tech_kraken_jellyfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    if Method != T_UNDEF and Method != T_KRAKEN_JELLYFISH: return -1
    return _finned_jellyfish(Grid, Step, Cands, ElimCands, AIC = 2)

def _finned_jellyfish(Grid, Step, Cands, ElimCands = None, AIC = 0):
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
                        BS = {r0, r1, r2, r3}
                        CU = BC[r0] | BC[r1] | BC[r2] | BC[r3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [r0, r1, r2, r3]:
                                if Cand in Cands[base][cvr]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 4 and len(CF):
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, ElimCands, Step, AIC) == 0:
                                return 0
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
                        BS = {c0, c1, c2, c3}
                        CU = BC[c0] | BC[c1] | BC[c2] | BC[c3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [c0, c1, c2, c3]:
                                if Cand in Cands[cvr][base]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 4 and len(CF):
                            if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, ElimCands, Step, AIC) == 0:
                                return 0
    return -1

def tech_almost_jellyfish(Grid, Step, Cands, ElimCands = None, Method = T_UNDEF):
    #  Logic techniques tech_swordfish and tech_finned_swordfish must be tried
    #  prior to trying this technique.

    if Method != T_UNDEF and Method != T_ALMOST_JELLYFISH: return -1

    for Cand in range(1, 10):
        # look at rows
        BC = [set() for i in range(9)]
        for r in range(9):
            for c in range(9):
                if Cand in Cands[r][c]: BC[r].add(c)
        for r0 in range(6):
            if not len(BC[r0]): continue
            for r1 in range(r0+1, 7):
                if not len(BC[r1]): continue
                for r2 in range(r1+1, 8):
                    if not len(BC[r2]): continue
                    for r3 in range(r2+1, 9):
                        if not len(BC[r3]): continue
                        BS = {r0, r1, r2, r3}
                        CU = BC[r0] | BC[r1] | BC[r2] | BC[r3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [r0, r1, r2, r3]:
                                if Cand in Cands[base][cvr]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 3 and len(CF):  # found an almost jellyfish
                            for r4 in [r0, r1, r2, r3]:
                                for c4 in sorted(CF):
                                    if Cand not in Cands[r4][c4]:
                                        Cands[r4][c4].add(Cand)
                                        CF1 = copy(CF)
                                        CS1 = copy(CS)
                                        CF1.discard(c4)
                                        CS1.add(c4)
                                        if len(CS1) == 4:
                                            if CU == CS1:  # found a hidden jellyfish
                                                SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                                if _elim_cands_in_fish(Cand, BS, CS1, P_ROW, Cands, ElimCands, SubStep) == 0:
                                                    SubStep[P_TECH] = T_JELLYFISH
                                                    SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                                       [P_ROW, r4], [P_COL, c4],
                                                                       [P_CON, ]] + SubStep[P_COND]
                                                    Step[P_SUBS].append(SubStep)
                                                    Step[P_OUTC].extend(SubStep[P_OUTC])
                                            else:
                                                for base in [r0, r1, r2, r3]:
                                                    if len(BC[base] - CF1) < 2:
                                                        Cands[r4][c4].discard(Cand)
                                                        break
                                                SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                                if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_ROW, Cands, ElimCands,
                                                                              SubStep, AIC = True) == 0:
                                                    SubStep[P_TECH] = T_FINNED_JELLYFISH
                                                    SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                                       [P_ROW, r4], [P_COL, c4],
                                                                       [P_CON, ]] + SubStep[P_COND]
                                                    Step[P_SUBS].append(SubStep)
                                                    Step[P_OUTC].extend(SubStep[P_OUTC])
                                        Cands[r4][c4].discard(Cand)
                            if len(Step[P_SUBS]):
                                Step[P_TECH] = T_ALMOST_JELLYFISH
                                BR = sorted(BS)
                                Step[P_COND] = [[P_VAL, Cand], [P_ROW, BR], [P_COL, CS]]
                                for br in BR:
                                    for fc in sorted(CF):
                                        if Cand in Cands[br][fc]:
                                            Step[P_COND].extend([[P_CON, ], [P_ROW, br], [P_COL, fc]])
                                Step[P_COND].append([P_END, ])
                                return 0
        # look at cols
        BC = [set() for i in range(9)]
        for c in range(9):
            for r in range(9):
                if Cand in Cands[r][c]: BC[c].add(r)
        for c0 in range(6):
            if not len(BC[c0]): continue
            for c1 in range(c0+1, 7):
                if not len(BC[c1]): continue
                for c2 in range(c1+1, 8):
                    if not len(BC[c2]): continue
                    for c3 in range(c2+1, 9):
                        if not len(BC[c3]): continue
                        BS = {c0, c1, c2, c3}
                        CU = BC[c0] | BC[c1] | BC[c2] | BC[c3]
                        CS = set()
                        CF = set()
                        for cvr in sorted(CU):
                            ci = 0  # cover intersection
                            for base in [c0, c1, c2, c3]:
                                if Cand in Cands[cvr][base]: ci += 1
                            if ci > 1: CS.add(cvr)
                            else: CF.add(cvr)
                        if len(CS) == 3 and len(CF):  # found an almost jellyfish
                            for c4 in [c0, c1, c2, c3]:
                                for r4 in sorted(CF):
                                    if Cand not in Cands[r4][c4]:
                                        Cands[r4][c4].add(Cand)
                                        CF1 = copy(CF)
                                        CS1 = copy(CS)
                                        CF1.discard(r4)
                                        CS1.add(r4)
                                        if len(CS1) == 4 and CU == CS1:  # found a hidden jellyfish
                                            SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                            if _elim_cands_in_fish(Cand, BS, CS1, P_COL, Cands, ElimCands, SubStep) == 0:
                                                SubStep[P_TECH] = T_JELLYFISH
                                                SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                                   [P_ROW, r4], [P_COL, c4],
                                                                   [P_CON, ]] + SubStep[P_COND]
                                                Step[P_SUBS].append(SubStep)
                                                Step[P_OUTC].extend(SubStep[P_OUTC])
                                        elif len(CS1) == 4 and len(CF1):  # found a Hidden finned jellyfish
                                            SubStep = {P_TECH: T_UNDEF, P_COND: [], P_OUTC: [], P_SUBS: []}
                                            if _elim_cands_in_finned_fish(Cand, BS, CS1, CF1, P_COL, Cands, ElimCands,
                                                                          SubStep, AIC = True) == 0:
                                                SubStep[P_TECH] = T_FINNED_JELLYFISH
                                                SubStep[P_COND] = [[P_VAL, Cand], [P_OP, OP_POS],
                                                                   [P_ROW, r4], [P_COL, c4],
                                                                   [P_CON, ]] + SubStep[P_COND]
                                                Step[P_SUBS].append(SubStep)
                                                Step[P_OUTC].extend(SubStep[P_OUTC])
                                        Cands[r4][c4].discard(Cand)
                            if len(Step[P_SUBS]):
                                Step[P_TECH] = T_ALMOST_JELLYFISH
                                BC = sorted(BS)
                                Step[P_COND] = [[P_VAL, Cand], [P_COL, BC], [P_ROW, CS]]
                                for bc in BC:
                                    for fr in sorted(CF):
                                        if Cand in Cands[fr][bc]:
                                            Step[P_COND].extend([[P_CON, ], [P_ROW, fr], [P_COL, bc]])
                                Step[P_COND].append([P_END, ])
                                return 0
    return -1



#todo: tech_franken_swordfish
#todo: tech_franken_jellyfish

def _elim_cands_in_fish(Cand, BS, CS, rc, Cands, ElimCands, Step):

    if rc == P_ROW:
        for r in set(range(9)) - BS:
            for c in sorted(CS):
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                    if ElimCands is not None:
                        ElimCands[r][c].add(Cand)
    elif rc == P_COL:
        for c in set(range(9)) - BS:
            for r in sorted(CS):
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                    if ElimCands is not None:
                        ElimCands[r][c].add(Cand)

    if Step[P_OUTC]:
        Step[P_OUTC].append([P_END, ])
        Ord = len(BS)
        if Ord == 2:
            Step[P_TECH] = T_X_WING
        elif Ord == 3:
            Step[P_TECH] = T_SWORDFISH
        elif Ord == 4:
            Step[P_TECH] = T_JELLYFISH
        else:
            return -1
        if rc == P_ROW:
            Step[P_COND] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS], [P_END, ]]
            return 0
        elif rc == P_COL:
            Step[P_COND] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS], [P_END, ]]
            return 0
    return -1

def _elim_cands_in_finned_fish(Cand, BS, CS, CF, rc, Cands, ElimCands, Step, AIC = 0):
    # AIC == 0:  only look for a weak link between the ccells.
    # AIC == 1:  only look for a weak link and between the ccells or the
    #            ccells "see" a strong link
    # AIC == 2:  weak link, "see" a strong link or weak-ended-AIC.

    Fins = []
    Chains = []
    NrLks = 0  # #links is one less than #Nodes
    Cvrs = 0
    if rc == P_ROW:
        for r in sorted(BS):
            for c in sorted(CF):
                if Cand in Cands[r][c]:
                    Fins.append((r, c))
        for r in set(range(9)) - BS:
            for c in sorted(CS):
                if Cand not in Cands[r][c]: continue
                # each cover out of [r][c] must see (be weakly linked to) all the fins.
                NL = [[] for i in range(len(Fins))]
                for i, (Rf, Cf) in enumerate(Fins):
                    NL[i] = are_ccells_weakly_linked(Rf, Cf, Cand, r, c, Cand, Cands, AIC = AIC)
                    if not NL[i]: break
                else:  # the cover in rc sees all the fins.
                    Cvrs += 1
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
                    if ElimCands is not None:
                        ElimCands[r][c].add(Cand)
                    for N in NL:
                        if Chains: Chains.append([P_SEP, ])
                        for r0, c0, Cand, Lk in N:
                            if Lk == -1:
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0]])
                            else:
                                NrLks += 1
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk)]])
    elif rc == P_COL:
        for c in sorted(BS):
            for r in sorted(CF):
                if Cand in Cands[r][c]:
                    Fins.append((r, c))
        for c in set(range(9)) - BS:
            for r in sorted(CS):
                if Cand not in Cands[r][c]: continue
                NL = [[] for i in range(len(Fins))]
                for i, (Rf, Cf) in enumerate(Fins):
                    NL[i] = are_ccells_weakly_linked(Rf, Cf, Cand, r, c, Cand, Cands, AIC = AIC)
                    if not NL[i]: break
                else:
                    Cvrs += 1
                    Cands[r][c].discard(Cand)
                    if Step[P_OUTC]:
                        Step[P_OUTC].append([P_SEP, ])
                    Step[P_OUTC].extend([[P_ROW, r], [P_COL, c],
                                         [P_OP, OP_ELIM], [P_VAL, Cand]])
                    if ElimCands is not None:
                        ElimCands[r][c].add(Cand)
                    for N in NL:
                        if Chains: Chains.append([P_SEP, ])
                        for r0, c0, Cand, Lk in N:
                            if Lk == -1:
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0]])
                            else:
                                NrLks += 1
                                Chains.extend([[P_VAL, Cand], [P_ROW, r0], [P_COL, c0], [P_OP, token_link(Lk)]])
    if Step[P_OUTC]:
        Ord = len(BS)
        if Ord == 2:
            Step[P_TECH] = T_FINNED_X_WING if NrLks == Cvrs else T_KRAKEN_X_WING
            Step[P_DIFF] = T[T_FINNED_X_WING][T_DIFF] + NrLks * AIC_LK_DIFF
        elif Ord == 3:
            Step[P_TECH] = T_FINNED_SWORDFISH if NrLks == Cvrs else T_KRAKEN_SWORDFISH
            Step[P_DIFF] = T[T_FINNED_SWORDFISH][T_DIFF] + NrLks * AIC_LK_DIFF
        elif Ord == 4:
            Step[P_TECH] = T_FINNED_JELLYFISH if NrLks == Cvrs else T_KRAKEN_JELLYFISH
            Step[P_DIFF] = T[T_FINNED_JELLYFISH][T_DIFF] + NrLks * AIC_LK_DIFF
        else:
            return -1
        if rc == P_ROW:
            Step[P_COND] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        elif rc == P_COL:
            Step[P_COND] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]
        else:
            return -1
        Step[P_OUTC].append([P_END, ])
        for r, c in Fins:
            Step[P_COND].extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
        Step[P_COND].append([P_SEP, ])
        Step[P_COND].extend(Chains)
        Step[P_COND].append([P_END, ])
        return 0
    return -1
