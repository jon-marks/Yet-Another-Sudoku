from globals import *
from misc import tkns_to_str
from solve_utils import *

class CVR_TREE:
    def __init__(self, r = -1, c = -1, Cand = -1, FinList = None):
        self.r = r
        self.c = c
        self.Cand = Cand
        self.FinList = FinList if FinList else []

class FIN_TRUNK:
    def __init__(self, r = -1, c = -1, Cand = -1, Trunk = None, Chain = None):
        self.r = r
        self.c = c
        self.Cand = Cand
        self.Trunk = Trunk if Trunk else []
        self.Chain = Chain if Chain else []

def tech_x_wings(Grid, Step, Cands, Methods):
    # A X-Wing occurs when the same candidate occurs twice each in two separate
    # rows (base sets), and these candidates lie in the same two columns (cover
    # sets).  All occurrences of the candidates in the same 2 columns (cover
    # sets) that are not part of the X-Wing can be eliminated.

    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    for Cand in range(1, 10):
        # look at row base-sets
        for r0 in range(8):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                if len(BC0) >= 2: break
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 9):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        if len(BC1) >= 2: break
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        CU = []; CS = []
                        for c in range(9):
                            bc0 = int(c in BC0); bc1 = int(c in BC1)
                            if bc0 or bc1: CU.append(c)
                            if bc0 + bc1 == 2: CS.append(c)
                        if len(CU) == len(CS) == 2:
                            if elim_cands_in_fish(Cand, [r0, r1], CS, P_ROW, Cands, Step): return 0
        # look at col base-sets
        for c0 in range(8):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                if len(BC0) >= 2: break
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 9):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        if len(BC1) >= 2: break
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        CU = []; CS = []
                        for r in range(9):
                            bc0 = int(r in BC0); bc1 = int(r in BC1)
                            if bc0 or bc1: CU.append(r)
                            if bc0 + bc1 == 2: CS.append(r)
                        if len(CU) == len(CS) == 2:
                            if elim_cands_in_fish(Cand, [c0, c1], CS, P_COL, Cands, Step): return 0
    return -1

def tech_finned_x_wings(Grid, Step, Cands, Methods):
    # Handles every type of fins and patterns
    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.

    # A Finned X-Wing occurs when only one of the base sets has more (than two)
    # occurrences of the candidate outside of the cover set.  A finned
    # fish has an extra appendage or two of the same candidate called fins.
    # Only those candidates in the cover sets that are not part of the
    # X-Wing that "see" (are peers of the) fin candidates can be eliminated.

    for Cand in range(1, 10):
        # look at base-set rows
        for r0 in range(8):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 9):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                        for c in range(9):
                            bc0 = int(c in BC0); bc1 = int(c in BC1)
                            if bc0 or bc1: CU.append(c)
                            if bc0 + bc1 == 2: CS.append(c)
                            if bc0 and not bc1: Fins.append((r0, c)); FB.add(r0); CF.append(c); FinBaseChute.add(r0//3); FinCvrChute.add(c//3)
                            if bc1 and not bc0: Fins.append((r1, c)); FB.add(r1); CF.append(c); FinBaseChute.add(r1//3); FinCvrChute.add(c//3)
                        if T_FINNED_X_WING in Methods and 3 <= len(CU) <= 4 and len(CS) == 2 and len(FinBaseChute) == len(FinCvrChute) == 1:
                            if elim_cands_in_finned_fish(Cand, [r0, r1], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                        if T_SASHIMI_X_WING in Methods and 3 <= len(CU) <= 4 and len(CS) == 1 and len(FinCvrChute) == 1:
                            if elim_cands_in_sashimi_fish(Cand, [r0, r1], CS, CF, FB, Fins, P_ROW, Cands, Step): return 0
                        if T_KRAKEN_FINNED_X_WING in Methods and len(CS) == 2 and 1 <= len(CF) <= 7:
                            if elim_cands_in_kraken_fish(Cand, [r0, r1], CS, Fins, P_ROW, Cands, T_KRAKEN_FINNED_X_WING, Step): return 0
                        if T_KRAKEN_SASHIMI_X_WING in Methods and len(CS) == 1 and 2 <= len(CF) <= 8:
                            if elim_cands_in_kraken_fish(Cand, [r0, r1], CS, Fins, P_ROW, Cands, T_KRAKEN_SASHIMI_X_WING, Step): return 0
                        if T_GL_KRAKEN_FINNED_X_WING in Methods and len(CS) == 2 and 1 <= len(CF) <= 7:
                            if elim_cands_in_kraken_fish(Cand, [r0, r1], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_FINNED_X_WING, Step): return 0
                        if T_GL_KRAKEN_SASHIMI_X_WING in Methods and len(CS) == 1 and 2 <= len(CF) <= 8:
                            if elim_cands_in_kraken_fish(Cand, [r0, r1], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_SASHIMI_X_WING, Step): return 0
        # look in base-set cols
        for c0 in range(8):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 9):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                        for r in range(9):
                            bc0 = int(r in BC0); bc1 = int(r in BC1)
                            if bc0 or bc1: CU.append(r)
                            if bc0+bc1 == 2: CS.append(r)
                            if bc0 and not bc1: Fins.append((r, c0)); FB.add(c0); CF.append(r); FinBaseChute.add(c0//3); FinCvrChute.add(r//3)
                            if bc1 and not bc0: Fins.append((r, c1)); FB.add(c1); CF.append(r); FinBaseChute.add(c1//3); FinCvrChute.add(r//3)
                        if T_FINNED_X_WING in Methods and 3 <= len(CU) <= 4 and len(CS) == 2 and len(FinBaseChute) == len(FinCvrChute) == 1:
                            if elim_cands_in_finned_fish(Cand, [c0, c1], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                        if T_SASHIMI_X_WING in Methods and 3 <= len(CU) <= 4 and len(CS) == 1 and len(FinCvrChute) == 1:
                            if elim_cands_in_sashimi_fish(Cand, [c0, c1], CS, CF, FB, Fins, P_COL, Cands, Step): return 0
                        if T_KRAKEN_FINNED_X_WING in Methods and len(CS) == 2 and 1 <= len(CF) <= 7:
                            if elim_cands_in_kraken_fish(Cand, [c0, c1], CS, Fins, P_COL, Cands, T_KRAKEN_FINNED_X_WING, Step): return 0
                        if T_KRAKEN_SASHIMI_X_WING in Methods and len(CS) == 1 and 2 <= len(CF) <= 8:
                            if elim_cands_in_kraken_fish(Cand, [c0, c1], CS, Fins, P_COL, Cands, T_KRAKEN_SASHIMI_X_WING, Step): return 0
                        if T_GL_KRAKEN_FINNED_X_WING in Methods and len(CS) == 2 and 1 <= len(CF) <= 7:
                            if elim_cands_in_kraken_fish(Cand, [c0, c1], CS, Fins, P_COL, Cands, T_GL_KRAKEN_FINNED_X_WING, Step): return 0
                        if T_GL_KRAKEN_SASHIMI_X_WING in Methods and len(CS) == 1 and 2 <= len(CF) <= 8:
                            if elim_cands_in_kraken_fish(Cand, [c0, c1], CS, Fins, P_COL, Cands, T_GL_KRAKEN_SASHIMI_X_WING, Step): return 0
    return -1

def tech_swordfish(Grid, Step, Cands, Methods):
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

    for Cand in range(1, 10):
        # look at row base-sets
        for r0 in range(7):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                if len(BC0) >= 3: break
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 8):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        if len(BC1) >= 3: break
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        for r2 in range(r1+1, 9):
                            BC2 = []
                            for c in range(9):
                                if Cand == Grid[r2][c]: break
                                if Grid[r2][c] or Cand not in Cands[r2][c]: continue
                                if len(BC2) >= 3: break
                                BC2.append(c)
                            else:
                                if len(BC2) < 2: continue
                                CU = []; CS = []
                                for c in range(9):
                                    bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2)
                                    if bc0 or bc1 or bc2: CU.append(c)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(c)
                                if len(CU) == len(CS) == 3:
                                    if elim_cands_in_fish(Cand, [r0, r1, r2], CS, P_ROW, Cands, Step): return 0
        # look at col base-sets
        for c0 in range(7):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                if len(BC0) >= 3: break
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 8):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        if len(BC1) >= 3: break
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        for c2 in range(c1+1, 9):
                            BC2 = []
                            for r in range(9):
                                if Cand == Grid[r][c2]: break
                                if Grid[r][c2] or Cand not in Cands[r][c2]: continue
                                if len(BC2) >= 3: break
                                BC2.append(r)
                            else:
                                if len(BC2) < 2: continue
                                CU = []; CS = []
                                for r in range(9):
                                    bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2)
                                    if bc0 or bc1 or bc2: CU.append(r)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(r)
                                if len(CU) == len(CS) == len(CS) == 3:
                                    if elim_cands_in_fish(Cand, [c0, c1, c2], CS, P_COL, Cands, Step): return 0
    return -1

def tech_finned_swordfish(Grid, Step, Cands, Methods):
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
        # look at base-set rows
        for r0 in range(7):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 8):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        for r2 in range(r1+1, 9):
                            BC2 = []
                            for c in range(9):
                                if Cand == Grid[r2][c]: break
                                if Grid[r2][c] or Cand not in Cands[r2][c]: continue
                                BC2.append(c)
                            else:
                                if len(BC2) < 2: continue
                                CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                                for c in range(9):
                                    bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2)
                                    if bc0 or bc1 or bc2: CU.append(c)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(c)
                                    if bc0 and not (bc1 or bc2): Fins.append((r0, c)); FB.add(r0); CF.append(c); FinBaseChute.add(r0//3); FinCvrChute.add(c//3)
                                    if bc1 and not (bc0 or bc2): Fins.append((r1, c)); FB.add(r1); CF.append(c); FinBaseChute.add(r1//3); FinCvrChute.add(c//3)
                                    if bc2 and not (bc0 or bc1): Fins.append((r2, c)); FB.add(r2); CF.append(c); FinBaseChute.add(r2//3); FinCvrChute.add(c//3)
                                if T_FINNED_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(CS) == 3 and len(FinBaseChute) == len(FinCvrChute) == 1:
                                    if elim_cands_in_finned_fish(Cand, [r0, r1, r2], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                                if T_SASHIMI_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(CS) == 2 and len(FinCvrChute) == 1:
                                    if elim_cands_in_sashimi_fish(Cand, [r0, r1, r2], CS, CF, FB, Fins, P_ROW, Cands, Step): return 0
                                if T_KRAKEN_FINNED_SWORDFISH in Methods and len(CS) == 3 and 1 <= len(CF) <= 6:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], CS, Fins, P_ROW, Cands, T_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                if T_KRAKEN_SASHIMI_SWORDFISH in Methods and len(CS) == 2 and 2 <= len(CF) <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], CS, Fins, P_ROW, Cands, T_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
                                if T_GL_KRAKEN_FINNED_SWORDFISH in Methods and len(CS) == 3 and 1 <= len(CF) <= 6:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                if T_GL_KRAKEN_SASHIMI_SWORDFISH in Methods and len(CS) == 2 and 2 <= len(CF) <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
        # look at base-set cols
        for c0 in range(7):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 8):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        for c2 in range(c1+1, 9):
                            BC2 = []
                            for r in range(9):
                                if Cand == Grid[r][c2]: break
                                if Grid[r][c2] or Cand not in Cands[r][c2]: continue
                                BC2.append(r)
                            else:
                                if len(BC2) < 2: continue
                                CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                                for r in range(9):
                                    bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2)
                                    if bc0 or bc1 or bc2: CU.append(r)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(r)
                                    if bc0 and not (bc1 or bc2): Fins.append((r, c0)); FB.add(c0); CF.append(r); FinBaseChute.add(c0//3); FinCvrChute.add(r//3)
                                    if bc1 and not (bc0 or bc2): Fins.append((r, c1)); FB.add(c1); CF.append(r); FinBaseChute.add(c1//3); FinCvrChute.add(r//3)
                                    if bc2 and not (bc0 or bc1): Fins.append((r, c2)); FB.add(c2); CF.append(r); FinBaseChute.add(c2//3); FinCvrChute.add(r//3)
                                if T_FINNED_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(CS) == 3 and len(FinBaseChute) == len(FinCvrChute) == 1:
                                    if elim_cands_in_finned_fish(Cand, [c0, c1, c2], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                                if T_SASHIMI_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(CS) == 2 and len(FinCvrChute) == 1:
                                    if elim_cands_in_sashimi_fish(Cand, [c0, c1, c2], CS, CF, FB, Fins, P_COL, Cands, Step): return 0
                                if T_KRAKEN_FINNED_SWORDFISH in Methods and len(CS) == 3 and 1 <= len(CF) <= 6:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], CS, Fins, P_COL, Cands, T_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                if T_KRAKEN_SASHIMI_SWORDFISH in Methods and len(CS) == 2 and 2 <= len(CF) <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], CS, Fins, P_COL, Cands, T_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
                                if T_GL_KRAKEN_FINNED_SWORDFISH in Methods and len(CS) == 3 and 1 <= len(CF) <= 6:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], CS, Fins, P_COL, Cands, T_GL_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                if T_GL_KRAKEN_SASHIMI_SWORDFISH in Methods and len(CS) == 2 and 2 <= len(CF) <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], CS, Fins, P_COL, Cands, T_GL_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
    return -1

def tech_jellyfish(Grid, Step, Cands, Methods):
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

    for Cand in range(1, 10):
        # look at row base-sets
        for r0 in range(6):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                if len(BC0) >= 4: break
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 7):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        if len(BC1) >= 4: break
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        for r2 in range(r1+1, 8):
                            BC2 = []
                            for c in range(9):
                                if Cand == Grid[r2][c]: break
                                if Grid[r2][c] or Cand not in Cands[r2][c]: continue
                                if len(BC2) >= 4: break
                                BC2.append(c)
                            else:
                                if len(BC2) < 2: continue
                                for r3 in range(r2+1, 9):
                                    BC3 = []
                                    for c in range(9):
                                        if Cand == Grid[r3][c]: break
                                        if Grid[r3][c] or Cand not in Cands[r3][c]: continue
                                        if len(BC3) >= 4: break
                                        BC3.append(c)
                                    else:
                                        if len(BC3) < 2: continue
                                        CU = []; CS = []
                                        for c in range(9):
                                            bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2); bc3 = int(c in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(c)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(c)
                                        if len(CU) == len(CS) == 4:
                                            if elim_cands_in_fish(Cand, [r0, r1, r2, r3], CS, P_ROW, Cands, Step): return 0
        # look at col base-sets
        for c0 in range(6):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                if len(BC0) >= 4: break
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 7):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        if len(BC1) >= 4: break
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        for c2 in range(c1+1, 8):
                            BC2 = []
                            for r in range(9):
                                if Cand == Grid[r][c2]: break
                                if Grid[r][c2] or Cand not in Cands[r][c2]: continue
                                if len(BC2) >= 4: break
                                BC2.append(r)
                            else:
                                if len(BC2) < 2: continue
                                for c3 in range(c2+1, 9):
                                    BC3 = []
                                    for r in range(9):
                                        if Cand == Grid[r][c3]: break
                                        if Grid[r][c3] or Cand not in Cands[r][c3]: continue
                                        if len(BC3) >= 4: break
                                        BC3.append(r)
                                    else:
                                        if len(BC3) < 2: continue
                                        CU = []; CS = []
                                        for r in range(9):
                                            bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2); bc3 = int(r in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(r)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(r)
                                        if len(CU) == len(CS) == 4:
                                            if elim_cands_in_fish(Cand, [c0, c1, c2, c3], CS, P_COL, Cands, Step): return 0
    return -1

def tech_finned_jellyfish(Grid, Step, Cands, Methods):

    for Cand in range(1, 10):
        # look at base-set rows
        for r0 in range(6):
            BC0 = []
            for c in range(9):
                if Cand == Grid[r0][c]: break
                if Grid[r0][c] or Cand not in Cands[r0][c]: continue
                BC0.append(c)
            else:
                if len(BC0) < 2: continue
                for r1 in range(r0+1, 7):
                    BC1 = []
                    for c in range(9):
                        if Cand == Grid[r1][c]: break
                        if Grid[r1][c] or Cand not in Cands[r1][c]: continue
                        BC1.append(c)
                    else:
                        if len(BC1) < 2: continue
                        for r2 in range(r1+1, 8):
                            BC2 = []
                            for c in range(9):
                                if Cand == Grid[r2][c]: break
                                if Grid[r2][c] or Cand not in Cands[r2][c]: continue
                                BC2.append(c)
                            else:
                                if len(BC2) < 2: continue
                                for r3 in range(r2+1, 9):
                                    BC3 = []
                                    for c in range(9):
                                        if Cand == Grid[r3][c]: break
                                        if Grid[r3][c] or Cand not in Cands[r3][c]: continue
                                        BC3.append(c)
                                    else:
                                        if len(BC3) < 2: continue
                                        CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                                        for c in range(9):
                                            bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2); bc3 = int(c in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(c)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(c)
                                            if bc0 and not (bc1 or bc2 or bc3): Fins.append((r0, c)); FB.add(r0); CF.append(c); FinBaseChute.add(r0//3); FinCvrChute.add(c//3)
                                            if bc1 and not (bc0 or bc2 or bc3): Fins.append((r1, c)); FB.add(r1); CF.append(c); FinBaseChute.add(r1//3); FinCvrChute.add(c//3)
                                            if bc2 and not (bc0 or bc1 or bc3): Fins.append((r2, c)); FB.add(r2); CF.append(c); FinBaseChute.add(r2//3); FinCvrChute.add(c//3)
                                            if bc3 and not (bc0 or bc1 or bc2): Fins.append((r3, c)); FB.add(r3); CF.append(c); FinBaseChute.add(r3//3); FinCvrChute.add(c//3)
                                        if T_FINNED_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(CS) == 4 and len(FinBaseChute) == len(FinCvrChute) == 1:
                                            if elim_cands_in_finned_fish(Cand, [r0, r1, r2, r3], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                                        if T_SASHIMI_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(CS) == 3 and len(FinCvrChute) == 1:
                                            if elim_cands_in_sashimi_fish(Cand, [r0, r1, r2, r3], CS, CF, FB, Fins, P_ROW, Cands, Step): return 0
                                        if T_KRAKEN_FINNED_JELLYFISH in Methods and len(CS) == 4 and 1 <= len(CF) <= 5:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], CS, Fins, P_ROW, Cands, T_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                        if T_KRAKEN_SASHIMI_JELLYFISH in Methods and len(CS) == 3 and 2 <= len(CF) <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], CS, Fins, P_ROW, Cands, T_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
                                        if T_GL_KRAKEN_FINNED_JELLYFISH in Methods and len(CS) == 4 and 1 <= len(CF) <= 5:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                        if T_GL_KRAKEN_SASHIMI_JELLYFISH in Methods and len(CS) == 2 and 2 <= len(CF) <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], CS, Fins, P_ROW, Cands, T_GL_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
        # look at base-set Cols
        for c0 in range(6):
            BC0 = []
            for r in range(9):
                if Cand == Grid[r][c0]: break
                if Grid[r][c0] or Cand not in Cands[r][c0]: continue
                BC0.append(r)
            else:
                if len(BC0) < 2: continue
                for c1 in range(c0+1, 7):
                    BC1 = []
                    for r in range(9):
                        if Cand == Grid[r][c1]: break
                        if Grid[r][c1] or Cand not in Cands[r][c1]: continue
                        BC1.append(r)
                    else:
                        if len(BC1) < 2: continue
                        for c2 in range(c1+1, 8):
                            BC2 = []
                            for r in range(9):
                                if Cand == Grid[r][c2]: break
                                if Grid[r][c2] or Cand not in Cands[r][c2]: continue
                                BC2.append(r)
                            else:
                                if len(BC2) < 2: continue
                                for c3 in range(c2+1, 9):
                                    BC3 = []
                                    for r in range(9):
                                        if Cand == Grid[r][c3]: break
                                        if Grid[r][c3] or Cand not in Cands[r][c3]: continue
                                        BC3.append(r)
                                    else:
                                        if len(BC3) < 2: continue
                                        CU = []; CS = []; CF = []; Fins = []; FB = set(); FinBaseChute = set(); FinCvrChute = set()
                                        for r in range(9):
                                            bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2); bc3 = int(r in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(r)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(r)
                                            if bc0 and not (bc1 or bc2 or bc3): Fins.append((r, c0)); FB.add(c0); CF.append(r); FinBaseChute.add(c0//3); FinCvrChute.add(r//3)
                                            if bc1 and not (bc0 or bc2 or bc3): Fins.append((r, c1)); FB.add(c1); CF.append(r); FinBaseChute.add(c1//3); FinCvrChute.add(r//3)
                                            if bc2 and not (bc0 or bc1 or bc3): Fins.append((r, c2)); FB.add(c2); CF.append(r); FinBaseChute.add(c2//3); FinCvrChute.add(r//3)
                                            if bc3 and not (bc0 or bc1 or bc2): Fins.append((r, c3)); FB.add(c3); CF.append(r); FinBaseChute.add(c3//3); FinCvrChute.add(r//3)
                                        if T_FINNED_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(CS) == 4 and len(FinBaseChute) == len(FinCvrChute) == 1:
                                            if elim_cands_in_finned_fish(Cand, [c0, c1, c2, c3], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                                        if T_SASHIMI_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(CS) == 3 and len(FinCvrChute) == 1:
                                            if elim_cands_in_sashimi_fish(Cand, [c0, c1, c2, c3], CS, CF, FB, Fins, P_COL, Cands, Step): return 0
                                        if T_KRAKEN_FINNED_JELLYFISH in Methods and len(CS) == 4 and 1 <= len(CF) <= 5:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], CS, Fins, P_COL, Cands, T_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                        if T_KRAKEN_SASHIMI_JELLYFISH in Methods and len(CS) == 3 and 2 <= len(CF) <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], CS, Fins, P_COL, Cands, T_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
                                        if T_GL_KRAKEN_FINNED_JELLYFISH in Methods and len(CS) == 4 and 1 <= len(CF) <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], CS, Fins, P_COL, Cands, T_GL_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                        if T_GL_KRAKEN_SASHIMI_JELLYFISH in Methods and len(CS) == 3 and 2 <= len(CF) <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], CS, Fins, P_COL, Cands, T_GL_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
    return -1

# todo: tech_franken_swordfish
# todo: tech_franken_jellyfish

def elim_cands_in_fish(Cand, BS, CS, Orient, Cands, Step):

    if Orient == P_ROW:
        for r in set(range(9)) - set(BS):
            for c in CS:
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
    else:  # if Orient == P_COL:
        for c in sorted(set(range(9)) - set(BS)):
            for r in CS:
                if Cand in Cands[r][c]:
                    Cands[r][c].discard(Cand)
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
    if Step.Outcome:
        Step.Outcome.append([P_END, ])
        Ord = len(BS)
        if Ord == 2: Step.Method = T_X_WING
        elif Ord == 3: Step.Method = T_SWORDFISH
        elif Ord == 4: Step.Method = T_JELLYFISH
        else: return False
        if Orient == P_ROW:
            Step.Pattern = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS], [P_END, ]]
            return True
        else:  # if Orient == P_COL:
            Step.Pattern = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS], [P_END, ]]
            return True
    return False


def elim_cands_in_finned_fish(Cand, BS, CS, CF, fb, Fins, Orient, Cands, Step):

    CS1 = []; FinChute = CF[0]//3  # ensure Fin(s) in the same cover chute as one of the cover-sets.
    for cs in CS:
        if cs//3 == FinChute: CS1.append(cs)
    if not CS1: return False
    Elims = []; fbb = (fb//3)*3
    if Orient == P_ROW:
        for r in range(fbb, fbb+3):
            if r in BS: continue
            for c in CS1:
                if Cand in Cands[r][c]: Elims.append((r, c))
        Step.Pattern = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
    else:  # Orient == P_COL
        for c in range(fbb, fbb+3):
            if c in BS: continue
            for r in CS1:
                if Cand in Cands[r][c]:  Elims.append((r, c))
        Step.Pattern = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]
    if not Elims: return False
    for rf, cf in Fins:
        Step.Pattern.extend([[P_CON, ], [P_ROW, rf], [P_COL, cf]])
    for rc, cc in Elims:
        for rf, cf in Fins:
            Step.Pattern.extend([[P_SEP, ], [P_VAL, Cand], [P_ROW, rc], [P_COL, cc], [P_OP, OP_WSLK if how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands, False) & LK_STRG else OP_WLK], [P_VAL, Cand], [P_ROW, rf], [P_COL, cf]])
        if Step.Outcome: Step.Outcome.append([P_SEP, ])
        Step.Outcome.extend([[P_ROW, rc], [P_COL, cc], [P_OP, OP_ELIM], [P_VAL, Cand]])
    for rc, cc in Elims: Cands[rc][cc].discard(Cand)
    Ord = len(BS)
    if Ord == 2:  Step.Method = T_FINNED_X_WING
    elif Ord == 3:  Step.Method = T_FINNED_SWORDFISH
    else: Step.Method = T_FINNED_JELLYFISH
    Step.Pattern.append([P_END, ])
    Step.Outcome.append([P_END, ])
    return True

def elim_cands_in_sashimi_fish(Cand, BS, CS, CF, FB, Fins, Orient, Cands, Step):

    BaseChutes = set()
    for fb in FB:
        BaseChutes.add((fb//3)*3)
    if len(BaseChutes) > 2: return False
    Cvrs = []
    if Orient == P_ROW:
        for b in BaseChutes:
            for r in range(b, b+3):
                if r in BS: continue
                for c in CF:
                    if Cand in Cands[r][c]: Cvrs.append((r, c))
    else:  # Orient == P_COL:
        for b in BaseChutes:
            for c in range(b, b+3):
                if c in BS: continue
                for r in CF:
                    if Cand in Cands[r][c]: Cvrs.append((r, c))
    Links = []; Elims = []
    for rc, cc in Cvrs:
        CFLinks = []
        for rf, cf in Fins:
            Lk = how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands, False)
            if not Lk: break
            CFLinks.extend([[P_SEP, ], [P_VAL, Cand], [P_ROW, rc], [P_COL, cc], [P_OP, OP_WSLK if Lk & LK_STRG else OP_WLK], [P_VAL, Cand], [P_ROW, rf], [P_COL, cf]])
        else:
            Elims.append((rc, cc))
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, rc], [P_COL, cc], [P_OP, OP_ELIM], [P_VAL, Cand]])
            Links.extend(CFLinks)
    if Step.Outcome:
        for rc, cc in Elims: Cands[rc][cc].discard(Cand)
        Ord = len(BS)
        if Ord == 2:  Step.Method = T_SASHIMI_X_WING
        elif Ord == 3:  Step.Method = T_SASHIMI_SWORDFISH
        else: Step.Method = T_SASHIMI_JELLYFISH
        if Orient == P_ROW: Step.Pattern = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        else: Step.Pattern = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]
        for rf, cf in Fins:
            Step.Pattern.extend([[P_CON, ], [P_ROW, rf], [P_COL, cf]])
        Step.Pattern.extend(Links)
        Step.Pattern.append([P_END, ])
        Step.Outcome.append([P_END, ])
        return True
    return False

def elim_cands_in_kraken_fish(Cand, BS, CS, Fins, Orient, Cands, Method, Step):

    Cvrs = []
    if Orient == P_ROW:
        if Method & T_SASHIMI:
            for rc in range(9):
                if rc in BS: continue
                for cc in range(9):
                    if Cand in Cands[rc][cc]: Cvrs.append((rc, cc))
        else:
            for rc in range(9):
                if rc in BS: continue
                for cc in CS:
                    if Cand in Cands[rc][cc]: Cvrs.append((rc, cc))
    else:  # Orient == P_COL:
        if Method & T_SASHIMI:
            for cc in range(9):
                if cc in BS: continue
                for rc in range(9):
                    if Cand in Cands[rc][cc]: Cvrs.append((rc, cc))
        else:
            for cc in range(9):
                if cc in BS: continue
                for rc in CS:
                    if Cand in Cands[rc][cc]: Cvrs.append((rc, cc))
    S = STATE()
    if Cvrs and new_find_cvr_seeing_all_fins(Fins, Cvrs, Cand, Cands, Method, S):
        Step.Method = Method
        if Orient == P_ROW: Step.Pattern = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        else: Step.Pattern = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]  # Orient == P_COL
        for r, c in Fins: Step.Pattern.extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
        Chains = []
        for Ch in S.Pattern:  # one chain for each fin in S.Pattern
            Chains.append([P_SEP, ])
            for i in range(len(Ch)-1):
                Step.NrLks += 1
                if Method & T_GRPLK:
                    if len(Ch[i].r) > 1: Step.NrGrpLks += 1
                    if len(Ch[i].c) > 1: Step.NrGrpLks += 1
                Chains.extend([[P_VAL, Ch[i].Cand], [P_ROW, Ch[i].r], [P_COL, Ch[i].c], [P_OP, token_link(Ch[i+1].Lk & 0x0f)]])
            Chains.extend([[P_VAL, Ch[-1].Cand], [P_ROW, Ch[-1].r], [P_COL, Ch[-1].c], [P_OP, OP_NONE]])
        Step.Pattern.extend(Chains); Step.Pattern.append([P_END, ])
        for r, c, Cand in S.Elims:
            if Method & T_GRPLK: Cands[list(r)[0]][list(c)[0]].discard(Cand)
            else: Cands[r][c].discard(Cand)
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
        Step.Outcome.append([P_END, ])
        return True
    return False

def new_find_cvr_seeing_all_fins(Fins, Cvrs, Cand, Cands, Method, Status):

    GrpLks = Method & T_GRPLK
    if GrpLks:
        Fins1 = []; Cvrs1 = []
        for rc, cc in Cvrs: Cvrs1.append(({rc}, {cc}))
        for rf, cf in Fins: Fins1.append(({rf}, {cf}))
        Fins = Fins1; Cvrs = Cvrs1

    SLNodes = {}
    for Cand2 in range(1, 10):
        for ((r0, c0, Cand0, Lk0), (r1, c1, Cand1, Lk1)) in list_all_cand_strong_links(Cand2, Cands, GrpLks, True):
            Hash = str(Cand0)+str(r0)+str(c0)
            if Hash not in SLNodes:
                SLNodes[Hash] = TNODE(r0, c0, Cand0, Lk0)
            SLNodes[Hash].Children.append(TNODE(r1, c1, Cand1, Lk1))

    Forest = []
    for rc, cc in Cvrs:
        FList = []
        CvrFound = True  # assumed True until proven False
        for rf, cf in Fins:
            FinHash = str(Cand) + str(rf) + str(cf)
            FinTrunk = FIN_TRUNK(rf, cf, Cand)
            Lk = how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands, GrpLks)
            if Lk:
                if Lk & LK_STRG: Lk |= LK_WKST
                FinTrunk.Chain = [NL(rf, cf, Cand, LK_NONE), NL(rc, cc, Cand, Lk)]
            else:
                for r0, c0, Cand0, Lkf in list_ccells_linked_to(rf, cf, Cand, Cands, LK_STWK, GrpLks, True):
                    Hash = str(Cand0) + str(r0) + str(c0)
                    if Hash in SLNodes:
                        SLN = SLNodes[Hash]
                        ANode = ANODE(Hash, Lkf)
                        if Lkf & LK_STRG: Lkf |= LK_WKST
                        for SLNC in SLN.Children:
                            if (rf, cf, Cand) == (SLNC.r, SLNC.c, SLNC.Cand): continue
                            Lkc = how_ccells_linked(SLNC.r, SLNC.c, SLNC.Cand, rc, cc, Cand, Cands, GrpLks)
                            if Lkc:  # Cover and fin see each other through SLN=SLNC
                                if Lkc & LK_STRG: Lkc |= LK_WKST
                                FinTrunk.Chain = [NL(rf, cf, Cand, LK_NONE), NL(SLN.r, SLN.c, SLN.Cand, Lkf), NL(SLNC.r, SLNC.c, SLNC.Cand, SLNC.Lk), NL(rc, cc, Cand, Lkc)]
                                break
                            else: ANode.Children.append(ANODE(str(SLNC.Cand) + str(SLNC.r) + str(SLNC.c), SLNC.Lk))
                        if FinTrunk.Chain: break
                        if ANode.Children: FinTrunk.Trunk.append(ANode)
            if not FinTrunk.Chain: CvrFound = False
            FList.append(FinTrunk)
        if CvrFound:  # Cover sees all fins
            for Fin in FList: Status.Pattern.append(Fin.Chain)
            Status.Elims = [(rc, cc, Cand)]
            return True
        if FList: Forest.append(CVR_TREE(rc, cc, Cand, FList))

    State = STATE(SLNodes, Method)
    while Forest:
        Culls = set()
        for CTree in Forest:
            UnproductiveCvr = False
            CvrFound = True  # assumed True until proven False
            for Fin in CTree.FinList:
                if Fin.Chain: continue
                Chain = [NL(Fin.r, Fin.c, Fin.Cand, LK_NONE)]
                Prunes = set()
                State.Pattern = []
                for FTrunk in Fin.Trunk:
                    kraken_chain_next_level(FTrunk, Chain, Cands, 1, CTree, State, GrpLks)
                    if State.Pattern:  Fin.Chain = State.Pattern; break  # if chain from fin to cvr is found, it will be placed in Fin.Chain
                    if not FTrunk.Children: Prunes.add(FTrunk)
                for FTrunk in Prunes: Fin.Trunk.remove(FTrunk)
                if not Fin.Chain: CvrFound = False
                if not Fin.Chain and not Fin.Trunk: UnproductiveCvr = True; break
            if CvrFound:
                for Fin in CTree.FinList: Status.Pattern.append(Fin.Chain)
                Status.Elims = [(CTree.r, CTree.c, CTree.Cand)]
                return True
            if UnproductiveCvr: Culls.add(CTree)
        for CTree in Culls: Forest.remove(CTree)
    return False

def kraken_chain_next_level(ANode, Chain, Cands, Lvl, CTree, State, GrpLks):

    SLN = State.SLNodes[ANode.Hash]
    Chain1 = [*Chain, NL(SLN.r, SLN.c, SLN.Cand, ANode.Lk)]
    PrunesC = set()
    for ANChild in ANode.Children:
        SLNC = State.SLNodes[ANChild.Hash]
        PrunesGC = set()
        Chain2 = [*Chain1, NL(SLNC.r, SLNC.c, SLNC.Cand, ANChild.Lk)]
        if ANChild.Children:  # not at the leaves yet.
            for ANGChild in ANChild.Children:
                kraken_chain_next_level(ANGChild, Chain2, Cands, Lvl+1, CTree, State, GrpLks)
                if State.Pattern: return
                if not ANGChild.Children: PrunesGC.add(ANGChild)
            for X in PrunesGC:
                for i in range(len(ANChild.Children)):
                    if ANChild.Children[i].Hash == X.Hash: del ANChild.Children[i]; break
        else:  # at the leaves
            for r1, c1, Cand1, Lk1 in list_ccells_linked_to(SLNC.r, SLNC.c, SLNC.Cand, Cands, LK_STWK, GrpLks, True):
                Hash = str(Cand1)+str(r1)+str(c1)
                if Hash not in State.SLNodes: continue
                for rx, cx, Candx, Lkx in Chain1:
                    if ccells_intersect(r1, c1, Cand1, rx, cx, Candx, GrpLks): break
                else:
                    if Lk1 & LK_STRG: Lk1 |= LK_WKST
                    Chain3 = [*Chain2, NL(r1, c1, Cand1, Lk1)]
                    SLNGC = State.SLNodes[Hash]
                    ANGChild = ANODE(Hash, Lk1)
                    for SLNGGC in SLNGC.Children:
                        for rx, cx, Candx, Lkx in Chain3:
                            if ccells_intersect(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, rx, cx, Candx, GrpLks): break
                        else:
                            Lk2 = how_ccells_linked(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, CTree.r, CTree.c, CTree.Cand, Cands, GrpLks)
                            if Lk2:
                                if Lk2 & LK_STRG: Lk2 |= LK_WKST
                                State.Pattern = [*Chain3, NL(SLNGGC.r, SLNGGC.c, SLNGGC.Cand, SLNGGC.Lk), NL(CTree.r, CTree.c, CTree.Cand, Lk2)]
                                return
                            if Lvl <= KRAKEN_RECURSE_LIM: ANGChild.Children.append(ANODE(str(SLNGGC.Cand) + str(SLNGGC.r) + str(SLNGGC.c), SLNGGC.Lk))
                    if ANGChild.Children:  ANChild.Children.append(ANGChild)
        if not ANChild.Children or Lvl > KRAKEN_RECURSE_LIM:  PrunesC.add(ANChild)
    for X in PrunesC:
        for i in range(len(ANode.Children)):
            if ANode.Children[i].Hash == X.Hash: del ANode.Children[i]; break
