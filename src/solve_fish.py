from copy import copy

from globals import *
from trc import *
from misc import tkns_to_str
from solve_utils import *

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
                        CU = []; CS = []; CF = []; Fins = []; FB = set()
                        for c in range(9):
                            bc0 = int(c in BC0); bc1 = int(c in BC1)
                            if bc0 or bc1: CU.append(c)
                            if bc0 + bc1 == 2: CS.append(c)
                            if bc0 and not bc1: Fins.append((r0, c)); FB.add(r0); CF.append(c)
                            if bc1 and not bc0: Fins.append((r1, c)); FB.add(r1); CF.append(c)
                        if T_FINNED_X_WING in Methods and 3 <= len(CU) <= 4 and len(FB) == 1 and len(CS) == 2 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                            if elim_cands_in_finned_fish(Cand, [r0, r1], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                        if T_SASHIMI_X_WING in Methods and 3 <= len(CU) <= 4 and len(FB) > 1 and len(CS) == 1 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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
                        CU = []; CS = []; CF = []; Fins = []; FB = set()
                        for r in range(9):
                            bc0 = int(r in BC0); bc1 = int(r in BC1)
                            if bc0 or bc1: CU.append(r)
                            if bc0+bc1 == 2: CS.append(r)
                            if bc0 and not bc1: Fins.append((r, c0)); FB.add(c0); CF.append(r)
                            if bc1 and not bc0: Fins.append((r, c1)); FB.add(c1); CF.append(r)
                        if T_FINNED_X_WING in Methods and 3 <= len(CU) <= 4 and len(FB) == 1 and len(CS) == 2 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                            if elim_cands_in_finned_fish(Cand, [c0, c1], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                        if T_SASHIMI_X_WING in Methods and 3 <= len(CU) <= 4 and len(FB) > 1 and len(CS) == 1 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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
                                CU = []; CS = []; CF = []; Fins = []; FB = set()
                                for c in range(9):
                                    bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2)
                                    if bc0 or bc1 or bc2: CU.append(c)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(c)
                                    if bc0 and not (bc1 or bc2): Fins.append((r0, c)); FB.add(r0); CF.append(c)
                                    if bc1 and not (bc0 or bc2): Fins.append((r1, c)); FB.add(r1); CF.append(c)
                                    if bc2 and not (bc0 or bc1): Fins.append((r2, c)); FB.add(r2); CF.append(c)
                                if T_FINNED_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(FB) == 1 and len(CS) == 3 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                                    if elim_cands_in_finned_fish(Cand, [r0, r1, r2], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                                if T_SASHIMI_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(FB) > 1 and len(CS) == 2 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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
                                CU = []; CS = []; CF = []; Fins = []; FB = set()
                                for r in range(9):
                                    bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2)
                                    if bc0 or bc1 or bc2: CU.append(r)
                                    if bc0 + bc1 + bc2 >= 2: CS.append(r)
                                    if bc0 and not (bc1 or bc2): Fins.append((r, c0)); FB.add(c0); CF.append(r)
                                    if bc1 and not (bc0 or bc2): Fins.append((r, c1)); FB.add(c1); CF.append(r)
                                    if bc2 and not (bc0 or bc1): Fins.append((r, c2)); FB.add(c2); CF.append(r)
                                if T_FINNED_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(FB) == 1 and len(CS) == 3 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                                    if elim_cands_in_finned_fish(Cand, [c0, c1, c2], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                                if T_SASHIMI_SWORDFISH in Methods and 4 <= len(CU) <= 5 and len(FB) > 1 and len(CS) == 2 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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
                                        CU = []; CS = []; CF = []; Fins = []; FB = set()
                                        for c in range(9):
                                            bc0 = int(c in BC0); bc1 = int(c in BC1); bc2 = int(c in BC2); bc3 = int(c in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(c)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(c)
                                            if bc0 and not (bc1 or bc2 or bc3): Fins.append((r0, c)); FB.add(r0); CF.append(c)
                                            if bc1 and not (bc0 or bc2 or bc3): Fins.append((r1, c)); FB.add(r1); CF.append(c)
                                            if bc2 and not (bc0 or bc1 or bc3): Fins.append((r2, c)); FB.add(r2); CF.append(c)
                                            if bc3 and not (bc0 or bc1 or bc2): Fins.append((r3, c)); FB.add(r3); CF.append(c)
                                        if T_FINNED_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(FB) == 1 and len(CS) == 4 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                                           if  elim_cands_in_finned_fish(Cand, [r0, r1, r2, r3], CS, CF, list(FB)[0], Fins, P_ROW, Cands, Step): return 0
                                        if T_SASHIMI_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(FB) > 1 and len(CS) == 3 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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
                                        CU = []; CS = []; CF = []; Fins = []; FB = set()
                                        for r in range(9):
                                            bc0 = int(r in BC0); bc1 = int(r in BC1); bc2 = int(r in BC2); bc3 = int(r in BC3)
                                            if bc0 or bc1 or bc2 or bc3: CU.append(r)
                                            if bc0 + bc1 + bc2 + bc3 >= 2: CS.append(r)
                                            if bc0 and not (bc1 or bc2 or bc3): Fins.append((r, c0)); FB.add(c0); CF.append(r)
                                            if bc1 and not (bc0 or bc2 or bc3): Fins.append((r, c1)); FB.add(c1); CF.append(r)
                                            if bc2 and not (bc0 or bc1 or bc3): Fins.append((r, c2)); FB.add(c2); CF.append(r)
                                            if bc3 and not (bc0 or bc1 or bc2): Fins.append((r, c3)); FB.add(c3); CF.append(r)
                                        if T_FINNED_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(FB) == 1 and len(CS) == 4 and (len(CF) == 1 or (len(CF) == 2 and CF[0]//3 == CF[1]//3)):
                                            if elim_cands_in_finned_fish(Cand, [c0, c1, c2, c3], CS, CF, list(FB)[0], Fins, P_COL, Cands, Step): return 0
                                        if T_SASHIMI_JELLYFISH in Methods and 5 <= len(CU) <= 6 and len(FB) > 1 and len(CS) == 3 and ((len(CF) == 2 and CF[0]//3 == CF[1]//3) or (len(CF) == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
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

    CS1 = []; FinChute = CF[0]//3 # ensure Fin(s) in the same cover chute as one of the cover-sets.
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
    S = STATUS()
    if Cvrs and find_cover_seeing_all_fins(Fins, Cvrs, Cand, Cands, Method, S):
        Step.Method = Method
        if Orient == P_ROW: Step.Pattern = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
        else: Step.Pattern = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]  # Orient == P_COL
        for r, c in sorted(Fins): Step.Pattern.extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
        Step.Pattern.append([P_SEP, ])
        NLks = NGrpLks = 0
        Chains = []
        for Ch in S.Pattern:  # one chain for each fin in S.Pattern
            if Chains: Chains.append([P_SEP, ])
            for r, c, Cand, Lk, in Ch:
                NLks += 1
                if Method & T_GRPLK:
                    if len(r) > 1: NGrpLks += 1
                    if len(c) > 1: NGrpLks += 1
                if Lk == LK_NONE: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c]])
                else: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
        Step.Pattern.extend(Chains); Step.Pattern.append([P_END, ])
        Step.NrLks = NLks; Step.NrGrpLks = NGrpLks
        for r, c, Cand in S.Outcome:
            if Method & T_GRPLK: Cands[list(r)[0]][list(c)[0]].discard(Cand)
            else: Cands[r][c].discard(Cand)
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
        Step.Outcome.append([P_END, ])
        return True
    return False


def find_cover_seeing_all_fins(Fins, Covers, Cand, Cands, Method, Status):

    Forest = []
    Tree = None
    GrpLks = Method & T_GRPLK
    if GrpLks:  # Kraken group links.
        for rc, cc in Covers:
            Forest.append(TREE({rc}, {cc}, Cand, None, None))
            for rf, cf in Fins:
                Lk = how_ccells_linked({rc}, {cc}, Cand, {rf}, {cf}, Cand, Cands, GrpLks)
                if Lk:
                    Forest[-1].FinChain.append([({rc}, {cc}, Cand, LK_WKST if Lk & LK_STRG else LK_WEAK), ({rf}, {cf}, Cand, LK_NONE)])
                    Forest[-1].FinBranch.append([])
                else:
                    Forest[-1].FinChain.append([])
                    Forest[-1].FinBranch.append(TNODE({rf}, {cf}, Cand, LK_NONE, None, None))
                    for r0, c0, Cand0, Lk0 in list_ccells_linked_to({rf}, {cf}, Cand, Cands, LK_STWK, GrpLks):  # Solving for singles prior to this method ensures LCL cannot be empty.
                        Forest[-1].FinBranch[-1].Children.append(TNODE(r0, c0, Cand0, LK_WKST if Lk0 == LK_STRG else LK_WEAK, None, Forest[-1].FinBranch[-1], None))
    else:  # kraken, non group links.
        # Plant a forest of trees, one for each cover.  Each tree has a main TNode branch and a Chain for each fin.
        # The Chain is empty until a one is found for that fin.  The MainBranch of TNodes, is used to build a tree
        # to find a chain.  Once a chain is found the branch is culled.  Tree's are grown two levels at time (LK_STRG
        # and LK_WEAK/WKST) at a time across all branches.
        for rc, cc in Covers:
        # for i, (rc, cc) in enumerate(Covers):
            Forest.append(TREE(rc, cc, Cand, None, None))
            for rf, cf in Fins:
            # for j, (rf, cf) in enumerate(Fins):
                Lk = how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands)
                if Lk:
                    Forest[-1].FinChain.append([(rc, cc, Cand, LK_WKST if Lk & LK_STRG else LK_WEAK), (rf, cf, Cand, LK_NONE)])
                    Forest[-1].FinBranch.append([])
                else:
                    Forest[-1].FinChain.append([])
                    Forest[-1].FinBranch.append(TNODE(rf, cf, Cand, LK_NONE, None, None))
                    for r0, c0, Cand0, Lk0 in list_ccells_linked_to(rf, cf, Cand, Cands, LK_STWK, GrpLks):  # Solving for singles prior to this method ensures LCL cannot be empty.
                        Forest[-1].FinBranch[-1].Children.append(TNODE(r0, c0, Cand0, LK_WKST if Lk0 == LK_STRG else LK_WEAK, None, Forest[-1].FinBranch[-1], None))
    # walk_the_forest(Forest)

    # Forest is planted with trees - one for each cover.  Each tree has a main branch for each fin.
    # Each main branch has EITHER A) grown a first level of branching, one for each weak (or strong masquerading
    # as weak) link it sees OR B) found a fin/cover link.

    while Forest:  # while there are still trees in the forest
        Culls = set()  # index of trees to cull  use set to avoid possibility of dups.
        for Tidx, Tree in enumerate(Forest):
            for Fin in range(len(Fins)):
                if Tree.FinChain[Fin]: continue
                Prunes = set()
                for Cidx, Child in enumerate(Tree.FinBranch[Fin].Children):
                    Child.Chain = [(Child.r, Child.c, Child.Cand, Child.Lk), (Tree.FinBranch[Fin].r, Tree.FinBranch[Fin].c, Tree.FinBranch[Fin].Cand, LK_NONE)]
                    find_next_child_nodes(Child, Cands, 1, Tree, Fin, GrpLks)
                    # Return conditions, each of FN's chlildren:
                    #  * Searching
                    #     - Child's children is a non empty list
                    #     - Tree.FinChain[Fin] is empty
                    #     - CvrTree.FinBranch[Fin] contains the starting TNode for this branch.
                    #  * Chain has been found:
                    #     - Child's children may or may not be an empty list
                    #     - Tree.FinChain[Fin] contains the chain.
                    #     - CvrTree.FinBranch[Fin] points to the starting TNode for this branch
                    #  * Search has BOTTOMED_OUT (recursion limit) / NOT_FOUND (could not find node to form a link in the chain)
                    #     - Child's Children is an empty list
                    #     - CvrTree.FinChain[Fin] == NULL
                    #     - CvrTree.FinBranch[Fin] points to the main branch for this fin.
                    if Tree.FinChain[Fin]: break  # a chain has been found, exit the loop promptly.
                    if not Child.Children: Prunes.add(Child)  # prune unproductive Tnode (no children/branches)
                if Tree.FinChain[Fin]: Tree.FinBranch[Fin] = []; continue  # Cull the FinBranch
                for Child in Prunes:
                    Tree.FinBranch[Fin].Children.remove(Child)
                if not Tree.FinBranch[Fin].Children:
                    Tree.FinBranch[Fin] = []  # unproductive Fin and hence cover tree. Prune Fin branch
            Found = True
            for Fin in range(len(Fins)):
                if not Tree.FinBranch[Fin] and not Tree.FinChain[Fin]: Culls.add(Tree)
                if not Tree.FinChain[Fin]: Found = False
            if Found:
                # Status.Tech = Method
                for Chain in Tree.FinChain: Status.Pattern.append(Chain)
                Status.Outcome = [(Tree.r, Tree.c, Tree.Cand)]
                return True
        for Tree in Culls:  Forest.remove(Tree)
        # walk_the_forest(Forest)
    return False

def find_next_child_nodes(Child, Cands, Lvl, Tree, Fin, GrpLks):
    # each recursive iteration grows/steps two levels of branches/children at a time. As an even number of nodes
    # are required with a strong link followed by a weak link.  1st step is odd, second step is even.
    if Child.Children:
        OddPrunes = set()
        for GrandChild in Child.Children:
            EvenPrunes = set()
            for GGrandChild in GrandChild.Children:
                find_next_child_nodes(GGrandChild, Cands, Lvl+1, Tree, Fin, GrpLks)
                # Return conditions, each of GGrandChild's chlildren:
                #  * Searching
                #     - GGrandChild's children is a non empty list
                #     - Tree.FinChain[Fin] is empty
                #     - CvrTree.FinBranch[Fin] contains the starting TNode for this branch.
                #  * Chain has been found:
                #     - GGrandChild's children may or may not be an empty list
                #     - Tree.FinChain[Fin] contains the chain.
                #     - Tree.FinBranch[Fin] points to the starting TNode for this branch
                #  * Search has BOTTOMED_OUT (recursion limit) / NOT_FOUND (could not find node to form a link in the chain)
                #     - GGrandChild's Children is an empty list
                #     - Tree.FinChain[Fin] == NULL
                #     - Tree.FinBranch[Fin] points to the main branch for this fin.
                if Tree.FinChain[Fin]: return  # A chain has been found, return promptly
                if not GGrandChild.Children: EvenPrunes.add(GGrandChild)
            for GGrandChild in EvenPrunes: GrandChild.Children.remove(GGrandChild)
            if not GrandChild.Children: OddPrunes.add(GrandChild)
        for GrandChild in OddPrunes: Child.Children.remove(GrandChild)
    else:  # at the leaves, attempt to add the next odd and even levels
        for r1, c1, Cand1, Lk1 in list_ccells_linked_to(Child.r, Child.c, Child.Cand, Cands, LK_STRG, GrpLks):
            for rx, cx, Candx, Lkx in Child.Chain:
                if r1 == rx and c1 == cx and Cand1 == Candx: break
                # if ccells_match(r1, c1, Cand1, rx, cx, Candx, GrpLks): break
            else:
                # does the r1, c1, Cand1 ccell see the cover.  if so, a chain is formed.
                Lk = how_ccells_linked(r1, c1, Cand1, Tree.r, Tree.c, Tree.Cand, Cands, GrpLks)
                if Lk:  # a chain is found; construct the chain and return promptly
                    Tree.FinChain[Fin] = [(Tree.r, Tree.c, Tree.Cand, LK_WKST if Lk & LK_STRG else LK_WEAK), (r1, c1, Cand1, LK_STRG), *Child.Chain]
                    return
                if Lvl > RECURSE_LIM: return  # Bottomed out
                # else find even child links
                for r2, c2, Cand2, Lk2 in list_ccells_linked_to(r1, c1, Cand1, Cands, LK_STWK, GrpLks):
                    for rx, cx, Candx, Lkx in Child.Chain:
                        if r2 == rx and c2 == cx and Cand2 == Candx: break
                        # if ccells_match(r2, c2, Cand2, rx, cx, Candx, GrpLks): break
                    else:  # odd and even links can be added to the chain
                        if not Child.Children or not (Child.Children[-1].r == r1 and Child.Children[-1].c == c1 and Child.Children[-1].Cand == Cand1):
                            Child.Children.append(TNODE(r1, c1, Cand1, LK_STRG, None, Child, None))
                        Lk2 = LK_WKST if Lk2 & LK_STRG else LK_WEAK
                        Child.Children[-1].Children.append(TNODE(r2, c2, Cand2, Lk2, [(r2, c2, Cand2, Lk2), (r1, c1, Cand1, LK_STRG), *Child.Chain], Child.Children[-1], None))

def walk_the_forest(Forest):
    print("Walking the forest")
    for Tree in Forest:
        for Fin in range(len(Tree.FinChain)):  # FinChain and FinBranch lists are the same length:
            if not bool(Tree.FinChain[Fin]) ^ bool(Tree.FinBranch[Fin]): print(f"ERROR: CoverTree :{Tree.Cand}r{Tree.r+1}c{Tree.c+1}: Only one of .FinChain[{Fin}] and .FinBranch[{Fin}] can exist: {Tree.FinChain[Fin]}, {Tree.FinBranch[Fin]}.")
            if Tree.FinChain[Fin]:
                St = ""
                for (r, c, Cand, Lk) in Tree.FinChain[Fin]:
                    St += f"{Cand}r{r+1}c{c+1}{OP[TKN_LK[Lk]]}"
                (r, c, Cand, Lk) = Tree.FinChain[Fin][-1]
                print(f"Cover Tree: {Tree.Cand}r{Tree.r+1}c{Tree.c+1}, Fin: {Fin}: {Cand}r{r+1}c{c+1}, Chain: {St}")
            if Tree.FinBranch[Fin]:
                print(f"Cover Tree: {Tree.Cand}r{Tree.r+1}c{Tree.c+1}, FinBranch[{Fin}]:")
                print(f"{Tree.FinBranch[Fin].Cand}r{Tree.FinBranch[Fin].r+1}c{Tree.FinBranch[Fin].c+1}")
                climb_branch(Tree.FinBranch[Fin], 1)

def climb_branch(TN, Lvl):

    if TN.Children:
        for Child in TN.Children:
            print(f"{' |'*Lvl}{OP[TKN_LK[Child.Lk]]}{Child.Cand}r{Child.r+1}c{Child.c+1}")
            climb_branch(Child, Lvl+1)
