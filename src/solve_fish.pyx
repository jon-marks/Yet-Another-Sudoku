#from copy import copy

from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "string.h" nogil:
    void * memcpy(void *, void *, size_t)
    void * memset(void *, int, size_t)

include "globals.pxi"
from globals import *
from trc cimport *
from trc import *

from misc import tkns_to_str  # TRCX
from solve_utils cimport *
from solve_fish cimport *

from solve_utils import STATUS

ctypedef struct RESULT:
    CHAIN   *Chain
    OUTCOME *Outcome

cdef int tech_x_wings_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    # A X-Wing occurs when the same candidate occurs twice each in two separate
    # rows (base sets), and these candidates lie in the same two columns (cover
    # sets).  All occurrences of the candidates in the same 2 columns (cover
    # sets) that are not part of the X-Wing can be eliminated.

    # The same holds true for columns instead of rows. That is the base sets are
    # in the columns and the cover sets in the rows.
    cdef int r0, c0, r1, c1, Cvr, lenCU, lenCS, Cand
    cdef int BaseCvrs[2][9]
    cdef int CS[2]

    for Cand in range(9):
        # look in rows
        for r0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 2: break
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        if Cvr >= 2: break
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = lenCS = 0
                        for c0 in range(9):
                            if BaseCvrs[0][c0] or BaseCvrs[1][c0]:
                                if lenCU >= 2: break
                                lenCU += 1
                            if BaseCvrs[0][c0] + BaseCvrs[1][c0] == 2:
                                if lenCS >= 2: break
                                CS[lenCS] = c0; lenCS += 1
                        else:
                            if lenCU == lenCS == 2:
                                TRCX("X-Wing found")
                                if elim_cands_in_fish(Cand, [r0, r1], 2, CS, ROW, Cands, Step): return 0
        # look in cols
        for c0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 2: break
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        if Cvr >= 2: break
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = lenCS = 0
                        for r0 in range(9):
                            if BaseCvrs[0][r0] or BaseCvrs[1][r0]:
                                if lenCU >= 2: break
                                lenCU += 1
                            if BaseCvrs[0][r0] + BaseCvrs[1][r0] == 2:
                                if lenCS >= 2: break
                                CS[lenCS] = r0; lenCS += 1
                        else:
                            if lenCU == lenCS == 2:
                                TRCX("X-Wing found")
                                if elim_cands_in_fish(Cand, [c0, c1], 2, CS, COL, Cands, Step): return 0
    return -1

cdef int tech_finned_x_wings_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, fb0, fb1, Cvr, Cand, lenCU, lenCS, lenCF, lenFB
    # cdef int Method
    cdef int BaseCvrs[2][9]
    # cdef int CU[9]
    # cdef int Bases[2]
    cdef int CS[2]
    cdef int CF[8]
    cdef int FB[8]
    cdef COORD Fins[8]

    for Cand in range(9):
        # look in rows
        for r0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = lenCS = lenCF = lenFB = 0
                        for c0 in range(9):
                            if BaseCvrs[0][c0] + BaseCvrs[1][c0] == 2:
                                if lenCS == 2: break
                                CS[lenCS] = c0; lenCS += 1
                            # if BaseCvrs[0][c0] or BaseCvrs[1][c0]: CU[lenCU] = c0; lenCU += 1
                            if BaseCvrs[0][c0] or BaseCvrs[1][c0]: lenCU += 1
                            if BaseCvrs[0][c0] and not BaseCvrs[1][c0]:
                                Fins[lenCF].r = r0; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                if not is_in_int_array(r0, FB, lenFB): FB[lenFB] = r0; lenFB += 1
                            if BaseCvrs[1][c0] and not BaseCvrs[0][c0]:
                                Fins[lenCF].r = r1; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                if not is_in_int_array(r1, FB, lenFB): FB[lenFB] = r1; lenFB += 1
                        else:
                            for Method in Methods:
                                TRCX_int_array("Bases:       ", [r0, r1], 2)
                                TRCX_int_array("Cover Set:   ", CS, lenCS)
                                TRCX_int_array("Cover Fins:  ", CF, lenCF)
                                TRCX_int_array("Fin Bases:   ", FB, lenFB)
                                TRCX_coord_array("Fins:        ", Fins, lenCF)
                                if Method == T_FINNED_X_WING and 3 <= lenCU <= 4 and lenFB == 1 and lenCS == 2 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                    if elim_cands_in_finned_fish(Cand, [r0, r1], 2, CS, lenCS, CF, lenCF, FB[0], Fins, ROW, Cands, Step): return 0
                                elif Method == T_SASHIMI_X_WING and 3 <= lenCU <= 4 and lenFB > 1 and lenCS == 1 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                    if elim_cands_in_sashimi_fish(Cand, [r0, r1], 2, CS, lenCS, CF, lenCF, FB, lenFB, Fins, ROW, Cands, Step): return 0
                                elif Method == T_KRAKEN_FINNED_X_WING and lenCS == 2 and 1 <= lenCF <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1], 2, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_FINNED_X_WING, Step): return 0
                                elif Method == T_KRAKEN_SASHIMI_X_WING and lenCS == 1 and 2 <= lenCF <= 8:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1], 2, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_SASHIMI_X_WING, Step): return 0
                                elif Method == T_GL_KRAKEN_FINNED_X_WING and lenCS == 2 and 1 <= lenCF <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1], 2, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_FINNED_X_WING, Step): return 0
                                elif Method == T_GL_KRAKEN_SASHIMI_X_WING and lenCS == 1 and 2 <= lenCF <= 8:
                                    if elim_cands_in_kraken_fish(Cand, [r0, r1], 2, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_SASHIMI_X_WING, Step): return 0
        # look in cols
        for c0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = lenCS = lenCF = lenFB = 0
                        for r0 in range(9):
                            if BaseCvrs[0][r0] + BaseCvrs[1][r0] == 2:
                                if lenCS == 2: break
                                CS[lenCS] = r0; lenCS += 1
                            # if BaseCvrs[0][r0] or BaseCvrs[1][r0]: CU[lenCU] = r0; lenCU += 1
                            if BaseCvrs[0][r0] or BaseCvrs[1][r0]:lenCU += 1
                            if BaseCvrs[0][r0] and not BaseCvrs[1][r0]:
                                Fins[lenCF].c = c0; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                if not is_in_int_array(c0, FB, lenFB): FB[lenFB] = c0; lenFB += 1
                            if BaseCvrs[1][r0] and not BaseCvrs[0][r0]:
                                Fins[lenCF].c = c1; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                if not is_in_int_array(c1, FB, lenFB): FB[lenFB] = c1; lenFB += 1
                        else:
                            for Method in Methods:
                                # TRCX_int_array("Bases:       ", [c0, c1], 2)
                                # TRCX_int_array("Cover Set:   ", CS, lenCS)
                                # TRCX_int_array("Cover Fins:  ", CF, lenCF)
                                # TRCX_int_array("Fin Bases:   ", FB, lenFB)
                                # TRCX_coord_array("Fins:        ", Fins, lenCF)
                                if Method == T_FINNED_X_WING and 3 <= lenCU <= 4 and lenFB == 1 and lenCS == 2 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                    if elim_cands_in_finned_fish(Cand, [c0, c1], 2, CS, lenCS, CF, lenCF, FB[0], Fins, COL, Cands, Step): return 0
                                elif Method == T_SASHIMI_X_WING and 3 <= lenCU <= 4 and lenFB > 1 and lenCS == 1 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                    if elim_cands_in_sashimi_fish(Cand, [c0, c1], 2, CS, lenCS, CF, lenCF, FB, lenFB, Fins, COL, Cands, Step): return 0
                                elif Method == T_KRAKEN_FINNED_X_WING and lenCS == 2 and 1 <= lenCF <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1], 2, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_FINNED_X_WING, Step): return 0
                                elif Method == T_KRAKEN_SASHIMI_X_WING and lenCS == 1 and 2 <= lenCF <= 8:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1], 2, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_SASHIMI_X_WING, Step): return 0
                                elif Method == T_GL_KRAKEN_FINNED_X_WING and lenCS == 2 and 1 <= lenCF <= 7:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1], 2, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_FINNED_X_WING, Step): return 0
                                elif Method == T_GL_KRAKEN_SASHIMI_X_WING and lenCS == 1 and 2 <= lenCF <= 8:
                                    if elim_cands_in_kraken_fish(Cand, [c0, c1], 2, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_SASHIMI_X_WING, Step): return 0
    return -1

cdef int tech_swordfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
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
    cdef int r0, c0, r1, c1, r2, c2, Cvr, lenCU, lenCS, Cand
    cdef int BaseCvrs[3][9]
    cdef int CS[3]

    for Cand in range(9):
        # Look in rows
        for r0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 3: break
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        if Cvr >= 3: break
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for c0 in range(9):
                                if Grid[r2][c0] == Cand+1: break
                                if Grid[r2][c0] or not Cands[r2][c0][Cand]: continue
                                if Cvr >= 3: break
                                BaseCvrs[2][c0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                lenCU = lenCS = 0
                                for c0 in range(9):
                                    if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]:
                                        if lenCU >= 3: break
                                        lenCU += 1
                                    if BaseCvrs[0][c0] + BaseCvrs[1][c0] + BaseCvrs[2][c0] >=2:
                                        if lenCS >= 3: break
                                        CS[lenCS] = c0; lenCS += 1
                                else:
                                    if lenCU == lenCS == 3:
                                        # TRCX(f"Swordfish found: {Cand+1}r{r0+1}{r1+1}{r2+1}c{CS[0]+1}{CS[1]+1}{CS[2]+1}")
                                        if elim_cands_in_fish(Cand, [r0, r1, r2], 3, CS, ROW, Cands, Step): return 0
        # Look in cols
        for c0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 3: break
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        if Cvr >= 3: break
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for r0 in range(9):
                                if Grid[r0][c2] == Cand+1: break
                                if Grid[r0][c2] or not Cands[r0][c2][Cand]: continue
                                if Cvr >= 3: break
                                BaseCvrs[2][r0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                lenCU = lenCS = 0
                                for r0 in range(9):
                                    if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]:
                                        if lenCU >= 3: break
                                        lenCU += 1
                                    if BaseCvrs[0][r0] + BaseCvrs[1][r0] + BaseCvrs[2][r0] >= 2:
                                        if lenCS >= 3: break
                                        CS[lenCS] = r0; lenCS += 1
                                else:
                                    if lenCU == lenCS == 3:
                                        # TRCX(f"Swordfish found: {Cand+1}c{c0+1}{c1+1}{c2+2}r{CS[0]+1}{CS[1]+1}{CS[2]+1}")
                                        if elim_cands_in_fish(Cand, [c0, c1, c2], 3, CS, COL, Cands, Step): return 0
    return -1

cdef int tech_finned_swordfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, r2, c2, Cvr, Cand, lenCU, lenCS, lenCF, lenFB
    cdef bint BaseCvrs[3][9]
    # cdef int CU[9]
    cdef int CS[3]  # needs to be large enough to collect all possibilities.
    cdef int CF[7]
    cdef int FB[7]
    cdef COORD Fins[7]

    for Cand in range(9):
        # look in rows
        for r0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for c0 in range(9):
                                if Grid[r2][c0] == Cand+1: break
                                if Grid[r2][c0] or not Cands[r2][c0][Cand]: continue
                                BaseCvrs[2][c0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                lenCU = lenCS = lenCF = lenFB = 0
                                for c0 in range(9):
                                    if BaseCvrs[0][c0] + BaseCvrs[1][c0] + BaseCvrs[2][c0] >= 2:
                                        if lenCS == 3: break
                                        CS[lenCS] = c0; lenCS += 1
                                    # if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]: CU[lenCU] = c0; lenCU += 1
                                    if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]: lenCU += 1
                                    if BaseCvrs[0][c0] and not (BaseCvrs[1][c0] or BaseCvrs[2][c0]):
                                        Fins[lenCF].r = r0; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                        if not is_in_int_array(r0, FB, lenFB): FB[lenFB] = r0; lenFB += 1
                                    if BaseCvrs[1][c0] and not (BaseCvrs[0][c0] or BaseCvrs[2][c0]):
                                        Fins[lenCF].r = r1; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                        if not is_in_int_array(r1, FB, lenFB): FB[lenFB] = r1; lenFB += 1
                                    if BaseCvrs[2][c0] and not (BaseCvrs[0][c0] or BaseCvrs[1][c0]):
                                        Fins[lenCF].r = r2; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                        if not is_in_int_array(r2, FB, lenFB): FB[lenFB] = r2; lenFB += 1
                                else:
                                    for Method in Methods:
                                        if Method == T_FINNED_SWORDFISH and 4 <= lenCU <= 5 and lenFB == 1 and lenCS == 3 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                            if elim_cands_in_finned_fish(Cand, [r0, r1, r2], 3, CS, lenCS, CF, lenCF, FB[0], Fins, ROW, Cands, Step): return 0
                                        elif Method == T_SASHIMI_SWORDFISH and 4 <= lenCU <= 5 and lenFB > 1 and lenCS == 2 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                            if elim_cands_in_sashimi_fish(Cand, [r0, r1, r2], 3, CS, lenCS, CF, lenCF, FB, lenFB, Fins, ROW, Cands, Step): return 0
                                        elif Method == T_KRAKEN_FINNED_SWORDFISH and lenCS == 3 and 1 <= lenCF <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], 3, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                        elif Method == T_KRAKEN_SASHIMI_SWORDFISH and lenCS == 2 and 2 <= lenCF <= 7:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], 3, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
                                        elif Method == T_GL_KRAKEN_FINNED_SWORDFISH and lenCS == 3 and 1 <= lenCF <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], 3, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                        elif Method == T_GL_KRAKEN_SASHIMI_SWORDFISH and lenCS == 2 and 2 <= lenCF <= 7:
                                            if elim_cands_in_kraken_fish(Cand, [r0, r1, r2], 3, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
        # look in cols
        for c0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for r0 in range(9):
                                if Grid[r0][c2] == Cand+1: break
                                if Grid[r0][c2] or not Cands[r0][c2][Cand]: continue
                                BaseCvrs[2][r0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                lenCU = lenCS = lenCF = lenFB = 0
                                for r0 in range(9):
                                    if BaseCvrs[0][r0] + BaseCvrs[1][r0] + BaseCvrs[2][r0] >= 2:
                                        if lenCS == 3: break
                                        CS[lenCS] = r0; lenCS += 1
                                    # if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]: CU[lenCU] = r0; lenCU += 1
                                    if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]: lenCU += 1
                                    if BaseCvrs[0][r0] and not (BaseCvrs[1][r0] or BaseCvrs[2][r0]):
                                        Fins[lenCF].c = c0; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                        if not is_in_int_array(c0, FB, lenFB): FB[lenFB] = c0; lenFB += 1
                                    if BaseCvrs[1][r0] and not (BaseCvrs[0][r0] or BaseCvrs[2][r0]):
                                        Fins[lenCF].c = c1; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                        if not is_in_int_array(c1, FB, lenFB): FB[lenFB] = c1; lenFB += 1
                                    if BaseCvrs[2][r0] and not (BaseCvrs[0][r0] or BaseCvrs[1][r0]):
                                        Fins[lenCF].c = c2; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                        if not is_in_int_array(c2, FB, lenFB): FB[lenFB] = c2; lenFB += 1
                                else:
                                    for Method in Methods:
                                        if Method == T_FINNED_SWORDFISH and 4 <= lenCU <= 5 and lenFB == 1 and lenCS == 3 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                            if elim_cands_in_finned_fish(Cand, [c0, c1, c2], 3, CS, lenCS, CF, lenCF, FB[0], Fins, COL, Cands, Step): return 0
                                        elif Method == T_SASHIMI_SWORDFISH and 4 <= lenCU <= 5 and lenFB > 1 and lenCS == 2 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                            if elim_cands_in_sashimi_fish(Cand, [c0, c1, c2], 3, CS, lenCS, CF, lenCF, FB, lenFB, Fins, COL, Cands, Step): return 0
                                        elif Method == T_KRAKEN_FINNED_SWORDFISH and lenCS == 3 and 1 <= lenCF <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], 3, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                        elif Method == T_KRAKEN_SASHIMI_SWORDFISH and lenCS == 2 and 2 <= lenCF <= 7:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], 3, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
                                        elif Method == T_GL_KRAKEN_FINNED_SWORDFISH and lenCS == 3 and 1 <= lenCF <= 6:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], 3, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_FINNED_SWORDFISH, Step): return 0
                                        elif Method == T_GL_KRAKEN_SASHIMI_SWORDFISH and lenCS == 2 and 2 <= lenCF <= 7:
                                            if elim_cands_in_kraken_fish(Cand, [c0, c1, c2], 3, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_SASHIMI_SWORDFISH, Step): return 0
    return -1

cdef int tech_jellyfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
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
    cdef int r0, c0, r1, c1, r2, c2, r3, c3, Cvr, lenCU, lenCS, Cand
    cdef int BaseCvrs[4][9]
    cdef int CS[4]

    for Cand in range(9):
        # Look in rows
        for r0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 4: break
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                #TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        if Cvr >= 4: break
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for c0 in range(9):
                                if Grid[r2][c0] == Cand+1: break
                                if Grid[r2][c0] or not Cands[r2][c0][Cand]: continue
                                if Cvr >= 4: break
                                BaseCvrs[2][c0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for r3 in range(r2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], 0, sizeof(int[9]))
                                    for c0 in range(9):
                                        if Grid[r3][c0] == Cand+1: break
                                        if Grid[r3][c0] or not Cands[r3][c0][Cand]: continue
                                        if Cvr >= 4: break
                                        BaseCvrs[3][c0] = 1; Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        Cvr = 0
                                        # TRCX(f"Fourth Base: {Cand+1}r{r3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        lenCU = lenCS = 0
                                        for c0 in range(9):
                                            if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]:
                                                if lenCU >= 4: break
                                                lenCU += 1
                                            if BaseCvrs[0][c0] + BaseCvrs[1][c0] + BaseCvrs[2][c0] + BaseCvrs[3][c0] >=2:
                                                if lenCS >= 4: break
                                                CS[lenCS] = c0; lenCS += 1
                                        else:
                                            if lenCU == lenCS == 4:
                                                # TRCX(f"Jellyfish found: {Cand+1}r{r0+1}{r1+1}{r2+2}{r3+1}c{CS[0]+1}{CS[1]+1}{CS[2]+1}{CS[3]+1}")
                                                if elim_cands_in_fish(Cand, [r0, r1, r2, r3], 4, CS, ROW, Cands, Step): return 0
        # TRCX("Col-wise bases")
        for c0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                if Cvr >= 4: break
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        if Cvr >= 4: break
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for r0 in range(9):
                                if Grid[r0][c2] == Cand+1: break
                                if Grid[r0][c2] or not Cands[r0][c2][Cand]: continue
                                if Cvr >= 4: break
                                BaseCvrs[2][r0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for c3 in range(c2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], 0, sizeof(int[9]))
                                    for r0 in range(9):
                                        if Grid[r0][c3] == Cand+1: break
                                        if Grid[r0][c3] or not Cands[r0][c3][Cand]: continue
                                        if Cvr >= 4: break
                                        BaseCvrs[3][r0] = 1; Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        # TRCX(f"Fourth Base: {Cand+1}c{c3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        lenCU = lenCS = 0
                                        for r0 in range(9):
                                            if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0] or BaseCvrs[3][r0]:
                                                if lenCU >= 4: break
                                                lenCU += 1
                                            if BaseCvrs[0][r0] + BaseCvrs[1][r0] + BaseCvrs[2][r0] + BaseCvrs[3][r0] >= 2:
                                                if lenCS >= 4: break
                                                CS[lenCS] = r0; lenCS += 1
                                        else:
                                            if lenCU == lenCS == 4:
                                                # TRCX(f"Jellyfish found: {Cand+1}c{c0+1}{c1+1}{c2+1}{c3+1}r{CS[0]+1}{CS[1]+1}{CS[2]+1}{CS[3]+1}")
                                                if elim_cands_in_fish(Cand, [c0, c1, c2, c3], 4, CS, COL, Cands, Step): return 0
    return -1


cdef int tech_finned_jellyfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, r2, c2, r3, c3, Cvr, Cand, lenCU, lenCS, lenCF, lenFB
    cdef int Method
    cdef int BaseCvrs[4][9]
    # cdef int CU[6]
    cdef int CS[4]  # needs to be large enough to collect all possibilities.
    cdef int CF[6]
    cdef int FB[6]
    cdef COORD Fins[6]

    for Cand in range(9):
        # look in rows
        for r0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for c0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][c0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for c0 in range(9):
                        if Grid[r1][c0] == Cand+1: break
                        if Grid[r1][c0] or not Cands[r1][c0][Cand]: continue
                        BaseCvrs[1][c0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for c0 in range(9):
                                if Grid[r2][c0] == Cand+1: break
                                if Grid[r2][c0] or not Cands[r2][c0][Cand]: continue
                                BaseCvrs[2][c0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for r3 in range(r2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], 0, sizeof(int[9]))
                                    for c0 in range(9):
                                        if Grid[r3][c0] == Cand+1: break
                                        if Grid[r3][c0] or not Cands[r3][c0][Cand]: continue
                                        BaseCvrs[3][c0] = 1; Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        # TRCX(f"Fourth Base: {Cand+1}r{r3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        lenCU = lenCS = lenCF = lenFB = 0
                                        for c0 in range(9):
                                            if BaseCvrs[0][c0] + BaseCvrs[1][c0] + BaseCvrs[2][c0] + BaseCvrs[3][c0] >= 2:
                                                if lenCS == 4: break
                                                CS[lenCS] = c0; lenCS += 1
                                            # if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]: CU[lenCU] = c0; lenCU += 1
                                            if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]: lenCU += 1
                                            if BaseCvrs[0][c0] and not (BaseCvrs[1][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]):
                                                Fins[lenCF].r = r0; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                                if not is_in_int_array(r0, FB, lenFB): FB[lenFB] = r0; lenFB += 1
                                            if BaseCvrs[1][c0] and not (BaseCvrs[0][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]):
                                                Fins[lenCF].r = r1; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                                if not is_in_int_array(r1, FB, lenFB): FB[lenFB] = r1; lenFB += 1
                                            if BaseCvrs[2][c0] and not (BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[3][c0]):
                                                Fins[lenCF].r = r2; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                                if not is_in_int_array(r2, FB, lenFB): FB[lenFB] = r2; lenFB += 1
                                            if BaseCvrs[3][c0] and not (BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]):
                                                Fins[lenCF].r = r3; Fins[lenCF].c = CF[lenCF] = c0; lenCF += 1
                                                if not is_in_int_array(r3, FB, lenFB): FB[lenFB] = r3; lenFB += 1
                                        else:
                                            for Method in Methods:
                                                if Method == T_FINNED_JELLYFISH and 5 <= lenCU <= 6 and lenFB == 1 and lenCS == 4 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                                    if elim_cands_in_finned_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, CF, lenCF, FB[0], Fins, ROW, Cands, Step): return 0
                                                elif Method == T_SASHIMI_JELLYFISH and 5 <= lenCU <= 6 and lenFB > 1 and lenCS == 3 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                                    if elim_cands_in_sashimi_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, CF, lenCF, FB, lenFB, Fins, ROW, Cands, Step): return 0
                                                elif Method == T_KRAKEN_FINNED_JELLYFISH and lenCS == 4 and 1 <= lenCF <= 5:
                                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                                elif Method == T_KRAKEN_SASHIMI_JELLYFISH and lenCS == 3 and 2 <= lenCF <= 6:
                                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, Fins, lenCF, ROW, Cands, T_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
                                                elif Method == T_GL_KRAKEN_FINNED_JELLYFISH and lenCS == 4 and 1 <= lenCF <= 5:
                                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                                elif Method == T_GL_KRAKEN_SASHIMI_JELLYFISH and lenCS == 3 and 2 <= lenCF <= 6:
                                                    if elim_cands_in_kraken_fish(Cand, [r0, r1, r2, r3], 4, CS, lenCS, Fins, lenCF, ROW, Cands, T_GL_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
         # look in cols
        for c0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], 0, sizeof(int[9]))
            for r0 in range(9):
                if Grid[r0][c0] == Cand+1: break
                if Grid[r0][c0] or not Cands[r0][c0][Cand]: continue
                BaseCvrs[0][r0] = 1; Cvr += 1
            else:
                if Cvr < 2: continue
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], 0, sizeof(int[9]))
                    for r0 in range(9):
                        if Grid[r0][c1] == Cand+1: break
                        if Grid[r0][c1] or not Cands[r0][c1][Cand]: continue
                        BaseCvrs[1][r0] = 1; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], 0, sizeof(int[9]))
                            for r0 in range(9):
                                if Grid[r0][c2] == Cand+1: break
                                if Grid[r0][c2] or not Cands[r0][c2][Cand]: continue
                                BaseCvrs[2][r0] = 1; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for c3 in range(c2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], 0, sizeof(int[9]))
                                    for r0 in range(9):
                                        if Grid[r0][c3] == Cand+1: break
                                        if Grid[r0][c3] or not Cands[r0][c3][Cand]: continue
                                        BaseCvrs[3][r0] = 1;  Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        # TRCX(f"Fourth Base: {Cand+1}c{c3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        lenCU = lenCS = lenCF = lenFB = 0
                                        for r0 in range(9):
                                            if BaseCvrs[0][r0] + BaseCvrs[1][r0] + BaseCvrs[2][r0] + BaseCvrs[3][r0] >= 2:
                                                if lenCS == 4: break
                                                CS[lenCS] = r0; lenCS += 1
                                            if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0] or BaseCvrs[3][r0]: lenCU += 1
                                            if BaseCvrs[0][r0] and not (BaseCvrs[1][r0] or BaseCvrs[2][r0] or BaseCvrs[3][r0]):
                                                Fins[lenCF].c = c0; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                                if not is_in_int_array(c0, FB, lenFB): FB[lenFB] = c0; lenFB += 1
                                            if BaseCvrs[1][r0] and not (BaseCvrs[0][r0] or BaseCvrs[2][r0] or BaseCvrs[3][r0]):
                                                Fins[lenCF].c = c1; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                                if not is_in_int_array(c1, FB, lenFB): FB[lenFB] = c1; lenFB += 1
                                            if BaseCvrs[2][r0] and not (BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[3][r0]):
                                                Fins[lenCF].c = c2; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                                if not is_in_int_array(c2, FB, lenFB): FB[lenFB] = c2; lenFB += 1
                                            if BaseCvrs[3][r0] and not (BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]):
                                                Fins[lenCF].c = c3; Fins[lenCF].r = CF[lenCF] = r0; lenCF += 1
                                                if not is_in_int_array(c3, FB, lenFB): FB[lenFB] = c3; lenFB += 1
                                        else:
                                            for Method in Methods:
                                                if Method == T_FINNED_JELLYFISH and 5 <= lenCU <= 6 and lenFB == 1 and lenCS == 4 and (lenCF == 1 or lenCF == 2 and CF[0]//3 == CF[1]//3):
                                                    if elim_cands_in_finned_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, CF, lenCF, FB[0], Fins, COL, Cands, Step): return 0
                                                elif Method == T_SASHIMI_JELLYFISH and 5 <= lenCU <= 6 and lenFB > 1 and lenCS == 3 and ((lenCF == 2 and CF[0]//3 == CF[1]//3) or (lenCF == 3 and CF[0]//3 == CF[1]//3 == CF[2]//3)):
                                                    if elim_cands_in_sashimi_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, CF, lenCF, FB, lenFB, Fins, COL, Cands, Step): return 0
                                                elif Method == T_KRAKEN_FINNED_JELLYFISH and lenCS == 4 and 1 <= lenCF <= 5:
                                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                                elif Method == T_KRAKEN_SASHIMI_JELLYFISH and lenCS == 3 and 2 <= lenCF <= 6:
                                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, Fins, lenCF, COL, Cands, T_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
                                                elif Method == T_GL_KRAKEN_FINNED_JELLYFISH and lenCS == 4 and 1 <= lenCF <= 5:
                                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_FINNED_JELLYFISH, Step): return 0
                                                elif Method == T_GL_KRAKEN_SASHIMI_JELLYFISH and lenCS == 3 and 2 <= lenCF <= 6:
                                                    if elim_cands_in_kraken_fish(Cand, [c0, c1, c2, c3], 4, CS, lenCS, Fins, lenCF, COL, Cands, T_GL_KRAKEN_SASHIMI_JELLYFISH, Step): return 0
    return -1

cdef bint elim_cands_in_fish(int Cand, int *Bases, int Ord, int *CS, int Orient, bint Cands[9][9][9], Step):
    cdef int r0, c0, Base

    # TRCX(f"Elim Cands: {Cand+1}r{Bases[0]+1}{Bases[1]+1}{Bases[2]+1}c{CS[0]+1}{CS[1]+1}{CS[2]+2}")
    Base = 0
    if Orient == ROW:
        for r0 in range(9):
            if Base < Ord and r0 == Bases[Base]: Base += 1; continue
            for c0 in range(Ord):
                if Cands[r0][CS[c0]][Cand]:
                    Cands[r0][CS[c0]][Cand] = False
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r0], [P_COL, CS[c0]], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
    else:  # Orient == COL
        for c0 in range(9):
            if Base < Ord and c0 == Bases[Base]: Base += 1; continue
            for r0 in range(Ord):
                if Cands[CS[r0]][c0][Cand]:
                    Cands[CS[r0]][c0][Cand] = False
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, CS[r0]], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
    if Step.Outcome:
        Step.Outcome.append([P_END, ])
        if Ord == 2: Step.Method = T_X_WING
        elif Ord == 3: Step.Method = T_SWORDFISH
        elif Ord == 4: Step.Method = T_JELLYFISH
        else: return False
        if Orient == ROW:
            if Ord == 2: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1]], [P_COL, CS[0], CS[1]], [P_END, ]]
            elif Ord == 3: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1], Bases[2]], [P_COL, CS[0], CS[1], CS[2]], [P_END, ]]
            else: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1], Bases[2], Bases[3]], [P_COL, CS[0], CS[1], CS[2], CS[3]], [P_END, ]]
        else:  # Orient == COL:
            if Ord == 2: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1]], [P_ROW, CS[0], CS[1]], [P_END, ]]
            elif Ord == 3: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1], Bases[2]], [P_ROW, CS[0], CS[1], CS[2]], [P_END, ]]
            else: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1], Bases[2], Bases[3]], [P_ROW, CS[0], CS[1], CS[2], CS[3]], [P_END, ]]
        return True
    return False

cdef bint elim_cands_in_finned_fish(int Cand, int *BS, int Ord, int *CS, int lenCS, int *CF, int lenCF, int fb, COORD *Fins, int Orient, bint Cands[9][9][9], Step):
    cdef int f0, cs, fbb, lenCS1, lenElims, FinChute
    cdef int CS1[3]
    cdef COORD Elims[6]

    FinChute = CF[0]//3; lenCS1 = 0
    for cs in range(lenCS):
        if CS[cs]//3 == FinChute: CS1[lenCS1] = CS[cs]; lenCS1 += 1
    if not lenCS1: return False
    lenElims =0; fbb = (fb//3)*3
    R = []; C = []
    if Orient == ROW:
        for f0 in range(fbb, fbb+3):
            if is_in_int_array(f0, BS, Ord): continue
            for cs in range(lenCS1):
                if Cands[f0][CS1[cs]][Cand]: Elims[lenElims].r = f0; Elims[lenElims].c = CS1[cs]; lenElims += 1
        if lenElims:
            for i in range(Ord): R.append(BS[i])
            for i in range(lenCS): C.append(CS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_ROW, R], [P_COL, C]]
    else:  # Orient == COL:
        for f0 in range(fbb, fbb+3):
            if is_in_int_array(f0, BS, Ord): continue
            for cs in range(lenCS1):
                if Cands[CS1[cs]][f0][Cand]: Elims[lenElims].r = CS1[cs]; Elims[lenElims].c = f0; lenElims += 1
        if lenElims:
            for i in range(lenCS): R.append(CS[i])
            for i in range(Ord): C.append(BS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_COL, C], [P_ROW, R]]

    if not lenElims: return False
    for i in range(lenCF):
        Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[i].r], [P_COL, Fins[i].c]])
    for e in range(lenElims):
        for f in range(lenCF):
            Step.Pattern.extend([[P_SEP, ], [P_VAL, Cand+1], [P_ROW, Elims[e].r], [P_COL, Elims[e].c], [P_OP, OP_WSLK if how_ccells_linked_c(Elims[e].r, Elims[e].c, Cand, Fins[f].r, Fins[f].c, Cand, Cands) & LK_STRG_C else OP_WLK], [P_VAL, Cand+1], [P_ROW, Fins[f].r], [P_COL, Fins[f].c]])
        if Step.Outcome: Step.Outcome.append([P_SEP, ])
        Step.Outcome.extend([[P_ROW, Elims[e].r], [P_COL, Elims[e].c], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
    for e in range(lenElims): Cands[Elims[e].r][Elims[e].c][Cand] = False
    if Ord == 2: Step.Method = T_FINNED_X_WING
    elif Ord == 3: Step.Method = T_FINNED_SWORDFISH
    else:  Step.Method = T_FINNED_JELLYFISH
    Step.Pattern.append([P_END, ])
    Step.Outcome.append([P_END, ])
    return True

cdef bint elim_cands_in_sashimi_fish(int Cand, int *BS, int Ord, int *CS, int lenCS, int *CF, int lenCF, int *FB, int lenFB, COORD *Fins, int Orient, bint Cands[9][9][9], Step):
    cdef int r, c, rc, cc, fb, bc, cf, cvr, fin, elim, Lk, lenBC, lenCvr, lenElim
    cdef int BaseChutes[3]
    cdef COORD Cvrs[12]
    cdef COORD Elims[4]

    lenBC = 0
    for fb in range(lenFB):
        if is_in_int_array((FB[fb]//3)*3, BaseChutes, lenBC): continue
        BaseChutes[lenBC] = (FB[fb]//3)*3; lenBC += 1
    if lenBC > 2: return False
    lenCvr = 0
    if Orient == ROW:
        for bc in range(lenBC):
            for r in range(BaseChutes[bc], BaseChutes[bc]+3):
                if is_in_int_array(r, BS, Ord): continue
                for cf in range(lenCF):
                    if Cands[r][CF[cf]][Cand]: Cvrs[lenCvr].r = r; Cvrs[lenCvr].c = CF[cf]; lenCvr += 1
    else:  # Orient == COL:
        for bc in range(lenBC):
            for c in range(BaseChutes[bc], BaseChutes[bc]+3):
                if is_in_int_array(c, BS, Ord): continue
                for cf in range(lenCF):
                    if Cands[CF[cf]][c][Cand]: Cvrs[lenCvr].r = CF[cf]; Cvrs[lenCvr].c = c; lenCvr += 1
    if lenCvr > 12:  TRCX_PANIC("Increase size of Cvrs array")  #########
    lenElim = 0; Links = []
    for cvr in range(lenCvr):
        rc = Cvrs[cvr].r; cc = Cvrs[cvr].c
        CFLinks = []
        for fin in range(lenCF):
            Lk = how_ccells_linked_c(rc, cc, Cand, Fins[fin].r, Fins[fin].c, Cand, Cands)
            if not Lk: break
            CFLinks.extend([[P_SEP, ], [P_VAL, Cand+1], [P_ROW, rc], [P_COL, cc], [P_OP, OP_WSLK if Lk & LK_STRG_C else OP_WLK], [P_VAL, Cand+1], [P_ROW, Fins[fin].r], [P_COL, Fins[fin].c]])
        else:
            Elims[lenElim].r = rc; Elims[lenElim].c = cc; lenElim += 1
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, rc], [P_COL, cc], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
            Links.extend(CFLinks)
    if Step.Outcome:
        for elim in range(lenElim):
            Cands[Elims[elim].r][Elims[elim].c][Cand] = False
        if Ord == 2:  Step.Method = T_SASHIMI_X_WING
        elif Ord == 3:  Step.Method = T_SASHIMI_SWORDFISH
        else: Step.Method = T_SASHIMI_JELLYFISH
        R = []; C = []
        if Orient == ROW:
            for i in range(Ord): R.append(BS[i])
            for i in range(lenCS): C.append(CS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_ROW, R], [P_COL, C]]
        else:  # Orient == COL:
            for i in range(lenCS): R.append(CS[i])
            for i in range(Ord): C.append(BS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_COL, C], [P_ROW, R]]
        for fin in range(lenCF):
            Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[fin].r], [P_COL, Fins[fin].c]])
        Step.Pattern.extend(Links)
        Step.Pattern.append([P_END, ])
        Step.Outcome.append([P_END, ])
        return True
    return False

cdef bint elim_cands_in_kraken_fish(int Cand, int *BS, int Ord, int *CS, int lenCS, COORD *Fins, int lenCF, int Orient, bint Cands[9][9][9], int Method, Step):
    cdef int lenCvr, rc, cc, cs
    cdef COORD   Cvrs [63]  # up to 18 possible cvr ccells for finned (3x6 in swordfish, 2x7=14 in x-wing, 3x5=15 in jellyfish), 63 (81 - 18 on x-wing for sashimi)
    cdef RESULT  Result
    cdef CHAIN   *Chain
    cdef NODE    *N
    cdef OUTCOME *Outcome

    TRCX("Got here1")
    lenCvr = 0
    if Orient == ROW:
        if Method & T_SASHIMI_C:
            for rc in range(9):
                if is_in_int_array(rc, BS, Ord): continue
                for cc in range(9):  # For Sashimi, any non base-set ccell can be a cover.
                    if Cands[rc][cc][Cand]: Cvrs[lenCvr].r = rc; Cvrs[lenCvr].c = cc; lenCvr += 1
        else:  # Method & T_FINNED:
            for rc in range(9):
                if is_in_int_array(rc, BS, Ord): continue
                for cs in range(lenCS):
                    if Cands[rc][CS[cs]][Cand]: Cvrs[lenCvr].r = rc; Cvrs[lenCvr].c = CS[cs]; lenCvr += 1
    else:  # Orient == COL:
        if Method & T_SASHIMI_C:
            for cc in range(9):
                if is_in_int_array(cc, BS, Ord): continue
                for rc in range(9):
                    if Cands[rc][cc][Cand]: Cvrs[lenCvr].r = rc; Cvrs[lenCvr].c = cc; lenCvr += 1
        else:  # Method & T_FINNED:
            for cc in range(9):
                if is_in_int_array(cc, BS, Ord): continue
                for cs in range(lenCS):
                    if Cands[CS[cs]][cc][Cand]: Cvrs[lenCvr].r = CS[cs]; Cvrs[lenCvr].c = cc; lenCvr += 1
    TRCX("Got here2")
    TRCX_coord_array("Covers   :", Cvrs, lenCvr
    )
    if lenCvr and find_cover_seeing_all_fins(Fins, lenCF, Cvrs, lenCvr, Cand, Cands, Method, &Result):
        Step.Method = Method
        R = []; C = []
        if Orient == ROW:
            for i in range(Ord): R.append(BS[i])
            for i in range(lenCS): C.append(CS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_ROW, R], [P_COL, C]]
        else:  # Orient == COL:
            for i in range(lenCS): R.append(CS[i])
            for i in range(Ord): C.append(BS[i])
            Step.Pattern = [[P_VAL, Cand+1], [P_COL, C], [P_ROW, R]]
        for fin in range(lenCF):
            Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[fin].r], [P_COL, Fins[fin].c]])

        if Method & T_GRPLK_C:
            while Result.Chain:
                Chain = Result.Chain; Result.Chain = Chain.Next
                Step.Pattern.append([P_SEP, ])
                while Chain.Start:
                    N = Chain.Start; Chain.Start = N.Next
                    R = []; C = []
                    for i in range(N.rgl.l): R.append(N.rgl.v[i])
                    for i in range(N.cgl.l): C.append(N.cgl.v[i])
                    Step.NrLks += 1
                    if N.rgl.l > 1 or N.cgl.l > 1: Step.NrGrpLks += 1
                    Step.Pattern.extend([[P_VAL, N.Cand+1], [P_ROW, R], [P_COL, C], [P_OP, TKN_LK[N.Lk&7]]])
                    PyMem_TRCX_Free(N)
                PyMem_TRCX_Free(Chain)
        else:  # normal scalar links, not group links.
            TRCX(f"Result: 0x{<long long>&Result:016x}, Result.Chain: 0x{<long long> Result.Chain:016x}, Result.Outcome: 0x{<long long> Result.Outcome:016x}.")
            TRCX(f"Result.Chain: 0x{<long long>Result.Chain:016x}, Result.Chain.Start: 0x{<long long>Result.Chain.Start:016x}, Result.Chain.Next: 0x{<long long>Result.Chain.Next:016x}")
            while Result.Chain:
                Chain = Result.Chain; Result.Chain = Chain.Next
                Step.Pattern.append([P_SEP, ])
                while Chain.Start:
                    N = Chain.Start; Chain.Start = N.Next
                    Step.NrLks += 1
                    St = f"&N: 0x{<long long> &N:016x}, N: 0x{<long long> N:016x}, N: {N.Cand+1}r{N.r+1}c{N.c+1}{OP[TKN_LK[N.Lk&7]]}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}"
                    TRCX(St)
                    Step.Pattern.extend([[P_VAL, N.Cand+1], [P_ROW, N.r], [P_COL, N.c], [P_OP, TKN_LK[N.Lk&7]]])
                    PyMem_TRCX_Free(N)
                PyMem_TRCX_Free(Chain)
        Step.Pattern.append([P_END, ])
        St = tkns_to_str(Step.Pattern)  # TRCX
        TRCX(f"Pattern: {St}")
        Outcome = Result.Outcome
        while Result.Outcome:
            Outcome = Result.Outcome; Result.Outcome = Outcome.Next
            Cands[Outcome.r][Outcome.c][Outcome.Cand] = False
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, Outcome.r], [P_COL, Outcome.c], [P_OP, Outcome.Op], [P_VAL, Outcome.Cand+1]])
            PyMem_TRCX_Free(Outcome)
        Step.Outcome.append([P_END, ])
        St = tkns_to_str(Step.Outcome)  ### TRCX
        TRCX(f"Outcome: {St}")
        return True
    return False

    #
    # # cdef int     b, cf, fb, r, c
    # cdef int     b, cf, r, c
    # # cdef COORD   Fins[3]   # up to 3 fin ccells (in sashimi)
    # cdef int     nCvrs, nFins
    # cdef RESULT  Result
    # cdef CHAIN   *Chain
    # cdef NODE    *N
    # cdef OUTCOME *Outcome
    #
    # if Orient == ROW:
    #     fb = -1; nFins = 0
    #     for b in range(Ord):
    #         for cf in range(lenCF):
    #             if Cands[Bases[b]][CF[cf]][Cand]:
    #                 if not(Method & T_SASHIMI_C):  # if not Sashimi
    #                     if fb == -1: fb = Bases[b]     # fins can only be in one base
    #                     elif fb != Bases[b]: return False
    #                 Fins[nFins].r = Bases[b]; Fins[nFins].c = CF[cf]; nFins += 1
    #     b = 0; nCvrs = 0
    #     # if Method & T_SASHIMI_C:  # For sashimi, the covers are only found along (perpendicular to) the covers of both bases and fins.
    #     for r in range(9):
    #         if b < Ord and r == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
    #         for c in range(lenCS):
    #             if Cands[r][CS[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CS[c]; nCvrs += 1
    #         for c in range(lenCF):
    #             if Cands[r][CF[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CF[c]; nCvrs += 1
    #     # else:  # non sashimi fins, the covers are along (perpendicular) to the coverset values in the basesets
    #     #     for r in range(9):
    #     #         if b < Ord and r == Bases[b]: b += 1; continue  # skip over basesets (assumes ascending order)
    #     #         for c in range(lenCS):
    #     #             if Cands[r][CS[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CS[c]; nCvrs += 1
    #     St = ""   ### TRCX
    #     for i in range(nFins): ### TRCX
    #         if St: St += ", "   ### TRCX
    #         St += f"{Cand+1}r{Fins[i].r+1}c{Fins[i].c+1}"  ### TRCX
    #     St1 = ""   ### TRCX
    #     for i in range(nCvrs): ### TRCX
    #         if St1: St1 += ", "   ### TRCX
    #         St1 += f"{Cand+1}r{Cvrs[i].r+1}c{Cvrs[i].c+1}"  ### TRCX
    #     TRCX(f"Orient: Row, Fins: {St}, Cvrs: {St1}")
    #
    # else: # Orient == COL
    #     fb = -1; nFins = 0
    #     for b in range(Ord):
    #         for cf in range(lenCF):
    #             if Cands[CF[cf]][Bases[b]][Cand]:
    #                 if not(Method & T_SASHIMI_C):  # if not Sashimi
    #                     if fb == -1: fb = Bases[b]     # fins can only be in one base
    #                     elif fb != Bases[b]: return False
    #                 Fins[nFins].r = CF[cf]; Fins[nFins].c = Bases[b]; nFins += 1
    #     b = 0; nCvrs = 0
    #     if Method & T_SASHIMI_C:  # For sashimi, the covers are only found in the fins.
    #         for c in range(9):
    #             if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
    #             for r in range(lenCS):
    #                 if Cands[CS[r]][c][Cand]: Cvrs[nCvrs].r = CS[r]; Cvrs[nCvrs].c = c; nCvrs += 1
    #             for r in range(lenCF):
    #                 if Cands[CF[r]][c][Cand]: Cvrs[nCvrs].r = CF[r]; Cvrs[nCvrs].c = c; nCvrs += 1
    #     else:  # non sashimi fins, the covers are in the coverset columns.
    #         for c in range(9):
    #             if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
    #             for r in range(lenCS):
    #                 if Cands[CS[r]][c][Cand]: Cvrs[nCvrs].r = CS[r]; Cvrs[nCvrs].c = c; nCvrs += 1
    #     St = ""   ### TRCX
    #     for i in range(nFins): ### TRCX
    #         if St: St += ", "   ### TRCX
    #         St += f"{Cand+1}r{Fins[i].r+1}c{Fins[i].c+1}"  ### TRCX
    #     St1 = ""   ### TRCX
    #     for i in range(nCvrs): ### TRCX
    #         if St1: St1 += ", "   ### TRCX
    #         St1 += f"{Cand+1}r{Cvrs[i].r+1}c{Cvrs[i].c+1}"  ### TRCX
    #     TRCX(f"Orient: Col, Fins: {St}, Cvrs: {St1}")
    #
    # if nCvrs:
    #     if Method & T_GRPLK_C:
    #         if not find_cover_links_to_all_fins_gl(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False
    #     else:
    #         if not find_cover_links_to_all_fins(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False
    #     Step.Method = Method
    #     BSp = []; CSp = []
    #     for b in range(Ord): BSp.append(Bases[b]);
    #     for c in range(lenCS): CSp.append(CS[c])
    #     if Orient == ROW: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, BSp], [P_COL, CSp]]
    #     else: Step.Pattern = [[P_VAL, Cand+1], [P_COL, BSp], [P_ROW, CSp]]
    #     for fb in range(nFins): Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[fb].r], [P_COL, Fins[fb].c]])
    #     if Method & T_GRPLK_C:
    #         while Result.Chain:
    #             Chain = Result.Chain; Result.Chain = Chain.Next
    #             Step.Pattern.append([P_SEP, ])
    #             while Chain.Start:
    #                 N = Chain.Start; Chain.Start = N.Next
    #                 R = []; C = []
    #                 for i in range(N.rgl.l): R.append(N.rgl.v[i])
    #                 for i in range(N.cgl.l): C.append(N.cgl.v[i])
    #                 Step.NrLks += 1
    #                 if N.rgl.l > 1 or N.cgl.l > 1: Step.NrGrpLks += 1
    #                 Step.Pattern.extend([[P_VAL, N.Cand+1], [P_ROW, R], [P_COL, C], [P_OP, TKN_LK[N.Lk&7]]])
    #                 PyMem_TRCX_Free(N)
    #             PyMem_TRCX_Free(Chain)
    #     else:  # normal scalar links, not group links.
    #         TRCX(f"Result: 0x{<long long>&Result:016x}, Result.Chain: 0x{<long long> Result.Chain:016x}, Result.Outcome: 0x{<long long> Result.Outcome:016x}.")
    #         TRCX(f"Result.Chain: 0x{<long long>Result.Chain:016x}, Result.Chain.Start: 0x{<long long>Result.Chain.Start:016x}, Result.Chain.Next: 0x{<long long>Result.Chain.Next:016x}")
    #         while Result.Chain:
    #             Chain = Result.Chain; Result.Chain = Chain.Next
    #             Step.Pattern.append([P_SEP, ])
    #             while Chain.Start:
    #                 N = Chain.Start; Chain.Start = N.Next
    #                 Step.NrLks += 1
    #                 St = f"&N: 0x{<long long> &N:016x}, N: 0x{<long long> N:016x}, N: {N.Cand+1}r{N.r+1}c{N.c+1}{OP[TKN_LK[N.Lk&7]]}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}"
    #                 TRCX(St)
    #                 Step.Pattern.extend([[P_VAL, N.Cand+1], [P_ROW, N.r], [P_COL, N.c], [P_OP, TKN_LK[N.Lk&7]]])
    #                 PyMem_TRCX_Free(N)
    #             PyMem_TRCX_Free(Chain)
    #     Step.Pattern.append([P_END, ])
    #     St = tkns_to_str(Step.Pattern)  # TRCX
    #     TRCX(f"Pattern: {St}")
    #     Outcome = Result.Outcome
    #     while Result.Outcome:
    #         Outcome = Result.Outcome; Result.Outcome = Outcome.Next
    #         Cands[Outcome.r][Outcome.c][Outcome.Cand] = False
    #         if Step.Outcome: Step.Outcome.append([P_SEP, ])
    #         Step.Outcome.extend([[P_ROW, Outcome.r], [P_COL, Outcome.c], [P_OP, Outcome.Op], [P_VAL, Outcome.Cand+1]])
    #         PyMem_TRCX_Free(Outcome)
    #     Step.Outcome.append([P_END, ])
    #     St = tkns_to_str(Step.Outcome)  ### TRCX
    #     TRCX(f"Outcome: {St}")
    #     return True
    # return False

cdef bint find_cover_seeing_all_fins(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
    # must free all allocated memory if returning false.
    # cdef int f, c, FBcnt, FCcnt, Lk
    cdef int f = 0, c, Lk
    # cdef int FinCvrLkT[3]  # max of 3 fins, for scalar (non-kraken) links
    cdef CHAIN *Chain  # This is a list of chains, not a list of nodes in a chain
    cdef CHAIN *C0
    cdef OUTCOME *Outcome
    # cdef NODE *N0 = NULL
    # cdef NODE *N1 = NULL
    cdef TREE_FFISH *Forest
    cdef TREE_FFISH *CvrTree  # pointer to CvrTree in Forest
    cdef TREE_FFISH *CT
    cdef NODE *LCL  # linked ccell list.
    cdef NODE *LC   # pointer to ccell link.
    # cdef NODE *ChN  # Chain node ==> Node element in chain.
    cdef TNODE_FFISH *FN   # pointer to First level TNODE (one for every fin in each cover tree)
    cdef TNODE_FFISH *CN0  # pointers to Child TNODEs
    cdef TNODE_FFISH *CN1

    # # TRCX(f"&Result: 0x{<long long>&Result:016x}, Result: 0x{<long long>Result:016x}, Chain: 0x{<long long>Result.Chain:016x}, Outcome: 0x{<long long>Result.Outcome:016x}.")
    # Result.Chain = Result.Outcome = Chain = Outcome = NULL
    # if not(Method & T_KRAKEN_C):  # look for direct links between each cover and all the fins - for each cover.
    #     for c in range(nCvrs):
    #         for f in range(nFins):
    #             FinCvrLkT[f] = how_ccells_linked_c(Cvrs[c].r, Cvrs[c].c, Cand, Fins[f].r, Fins[f].c, Cand, Cands)
    #             TRCX(f"CvrFinLk: Cvr({Cvrs[c].r+1}, {Cvrs[c].c+1}), Fin({Fins[f].r+1}, {Fins[f].c+1}), Link: 0x{FinCvrLkT[f]:04x}")
    #             if FinCvrLkT[f] == LK_NONE_C: break
    #         else:
    #             #  All fins can see the cover, build the links(chains) between each fin and the cover.
    #             TRCX(f"Cvrs: ({Cvrs[c].r+1}, {Cvrs[c].c+1} sees all fins")
    #             for f in range(nFins):
    #                 if Chain: Chain.Next = <CHAIN *>PyMem_TRCX_Calloc(1, sizeof(CHAIN)); Chain = Chain.Next
    #                 else: Chain = Result.Chain = <CHAIN *>PyMem_TRCX_Calloc(1, sizeof(CHAIN))
    #                 Chain.Start = <NODE *>PyMem_TRCX_Calloc(1, sizeof(NODE))
    #                 Chain.Start.Next = <NODE *>PyMem_TRCX_Calloc(1, sizeof(NODE))
    #                 Chain.Start.r = Cvrs[f].r; Chain.Start.c = Cvrs[f].c; Chain.Start.Cand = Cand; Chain.Start.Lk = LK_WKST_C if FinCvrLkT[f] & LK_STRG_C else LK_WEAK_C
    #                 Chain.Start.Next.r = Fins[c].r; Chain.Start.Next.c = Fins[c].c; Chain.Start.Next.Cand = Cand; Chain.Start.Next.Lk = LK_NONE_C
    #             TRCX(f"*Chain: 0x{<long long> Chain:016x}, Chain.Start: 0x{<long long> Chain.Start:016x}, Chain.Next: 0x{<long long> Chain.Next:016x}")
    #             if Outcome:  Outcome.Next = <OUTCOME *>PyMem_TRCX_Calloc(1, sizeof(OUTCOME)); Outcome = Outcome.Next
    #             else: Outcome = Result.Outcome = <OUTCOME *>PyMem_TRCX_Calloc(1, sizeof(OUTCOME))
    #             Outcome.r = Cvrs[c].r; Outcome.c = Cvrs[c].c; Outcome.Op = OP_ELIM_C; Outcome.Cand = Cand
    #             N0 = Chain.Start  # TRCX
    #             C0 = Chain  # TRCX
    #             St = ""  # TRCX
    #             while C0:  # TRCX
    #                 if St: St += "; "  #### TRCX
    #                 St += f"{C0.Start.Cand+1}r{C0.Start.r+1}c{C0.Start.c+1}{OP[TKN_LK[C0.Start.Lk&7]]}{C0.Start.Next.Cand+1}r{C0.Start.Next.r+1}c{C0.Start.Next.c+1}"  ### TRCX
    #                 C0 = C0.Next  ### TRCX
    #             TRCX(f"Chain: {St}.")
    #             TRCX(f"&Outcome: 0x{<long long>Outcome:016x}, r{Outcome.r+1}c{Outcome.c+1}{OP[Outcome.Op]}{Outcome.Cand+1}, Next: 0x{<long long> Outcome.Next:016x}")
    #     TRCX(f"&Result: 0x{<long long> &Result:016x}, Result: 0x{<long long> Result:016x}, Chain: 0x{<long long> Result.Chain:016x}, Outcome: 0x{<long long> Result.Outcome:016x}.")
    #     return True if Result.Outcome else False
    # else:  # kraken - Weakly ended chain
    # Plant a forest of TREE_FFISH CvrTrees - finned fish trees to search of chains linking all fins to a cover, all one level at a time.
    # Plant a forest of trees, one for each cover.  Each tree has a main TNode Finbranch and a FinChain for each fin.
    # The Chain is empty until a one is found for that fin.  The MainBranch of TNodes, is used to build a tree
    # to find a chain.  Once a chain is found the Main (Fin) branch is culled.  Tree's are grown two levels at time (LK_STRG
    # and LK_WEAK/WKST) at a time across all branches.
    Forest = CvrTree = NULL
    if Method & T_GRPLK_C:
        return False # stubbed out
    else:  # scalar links only
        for c in range(nCvrs):
            if CvrTree:
                TRCX(f"Plant next CvrTree in forest for {Cand+1}r{Cvrs[c].r+1}c{Cvrs[c].c+1}")
                CvrTree.Next = <TREE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TREE_FFISH))
                CvrTree.Next.Prev = CvrTree; CvrTree = CvrTree.Next
            else:  # first tree in forest
                TRCX(f"Plant first CvrTree in forest for {Cand+1}r{Cvrs[c].r+1}c{Cvrs[c].c+1}")
                Forest = CvrTree = <TREE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TREE_FFISH))
                # CvrTree.Prev = CvrTree.Next = NULL
            CvrTree.r = Cvrs[c].r; CvrTree.c = Cvrs[c].c; CvrTree.Cand = Cand; CvrTree.nFins = nFins
            TRCX(f"CvrTree: 0x{<long long>CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}, nFins: {CvrTree.nFins}, Prev: 0x{<long long>CvrTree.Prev:016x}, Next: 0x{<long long>CvrTree.Next:016x}")
            for f in range(nFins):
                # First check if the fin and cvr are linked.
                TRCX(f"Seeking direct link for Cand: {Cand+1} between Fin: r{Fins[f].r+1}c{Fins[f].c+1} and Cvr: r{Cvrs[c].r+1}c{Cvrs[c].c+1}")
                Lk = how_ccells_linked_c(Cvrs[c].r, Cvrs[c].c, Cand, Fins[f].r, Fins[f].c, Cand, Cands)
                if Lk:
                    CvrTree.FinChain[f] = LC = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE))  # create a node for the cvr
                    LC.r = Cvrs[c].r; LC.c = Cvrs[c].c; LC.Cand = Cand; LC.Lk = LK_WKST_C if Lk & LK_STRG_C else LK_WEAK_C
                    LC.Next = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE)); LC = LC.Next  # create a node for the fin.
                    LC.r = Fins[f].r; LC.c = Fins[f].c; LC.Cand = Cand; LC.Lk = LK_NONE_C; LC.Next = NULL
                    TRCX(f"Direct link found: CvrTree.FinChain[{f}]: {CvrTree.FinChain[f].Cand+1}r{CvrTree.FinChain[f].r+1}c{CvrTree.FinChain[f].c+1}{OP[TKN_LK[CvrTree.FinChain[f].Lk&7]]}{CvrTree.FinChain[f].Next.Cand+1}r{CvrTree.FinChain[f].Next.r+1}c{CvrTree.FinChain[f].Next.c+1}, CvrTree.FinChain[{f}].Next.Next: {<long long>CvrTree.FinChain[f].Next.Next:016x}")
                    continue
                # No direct link was found, grow a main branch for this fin.
                TRCX("Direct link not found, grow a main branch to build chain ")
                FN = CvrTree.FinBranch[f] = <TNODE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                ChN = FN.ChainN = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE))
                ChN.r = Fins[f].r; ChN.c = Fins[f].c; ChN.Cand = Cand; ChN.Lk = LK_NONE_C; ChN.Next = ChN.Prev = NULL
                TRCX(f"Main Branch TNode for Fin: CvrTree.FinBranch[{f}] 0x{<long long> FN:016x}: .ChainN: -> {ChN.Cand+1}r{ChN.r+1}c{ChN.c+1}{OP[TKN_LK[(LK_WKST_C if Lk & LK_STRG_C else LK_WEAK_C)]]},"
                     f".Parent: 0x{<long long>FN.Parent:016x}, .SibPrev: 0x{<long long>FN.SibPrev:016x}, .SibNext: 0x{<long long>FN.SibNext:016x}, .ChildStart: 0x{<long long>FN.ChildStart:016x}, .ChildEnd: 0x{<long long>FN.ChildEnd:016x}")
                # Generate the list of nodes that can see the fin.
                LCL = list_ccells_linked_to_c(Fins[f].r, Fins[f].c, Cand, Cands, LK_STWK_C)
                St = "";  LC = LCL  #### TRCX
                while LC:  #### TRCX
                    if St: St += ", "   #### TRCX
                    St += f"{LC.Cand+1}r{LC.r+1}c{LC.c+1}{OP[TKN_LK[LC.Lk&7]]}"  #### TRCX
                    LC = LC.Next  ### TRCX
                TRCX(f"Links to Fin: {Cand+1}r{Fins[f].r+1}c{Fins[f].c+1} -> {St}")
                # Grow the children one for each node in lcl.
                LC = LCL    # linked cell = start of linked cell list.
                CN0 = NULL   # Child TNode
                TRCX(f"Child TNODE Branches off Main Branch (links to Fin)")
                while LCL:
                    LC = LCL; LCL = LCL.Next
                    if CN0:
                        CN0.SibNext = <TNODE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                        CN0.SibNext.SibPrev = CN0; CN0 = CN0.SibNext
                    else:
                        FN.ChildStart = CN0 = <TNODE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                    CN0.Parent = FN
                    CN0.ChainN = LC; LC.Next = FN.ChainN
                    LC.Lk   = LK_WKST_C if LC.Lk & LK_STRG_C else LK_WEAK_C  # Strong link becomes Strong masq as Weak link.
                FN.ChildEnd = CN0
                TRCX(f"FN.ChildStart: 0x{<long long>FN.ChildStart:016x}, FN.ChildEnd: 0x{<long long>FN.ChildEnd:016x}")
                CN0 = FN.ChildStart  ### TRCX
                while CN0:  ### TRCX
                    TRCX(f"CN0: 0x{<long long>CN0:016x}.ChainN: 0x{<long long> CN0.ChainN:016x} -> {CN0.ChainN.Cand+1}r{CN0.ChainN.r+1}c{CN0.ChainN.c+1}{OP[TKN_LK[CN0.ChainN.Lk&7]]}, "
                         f".Parent: 0x{<long long> CN0.Parent:016x}, .SibPrev: 0x{<long long> CN0.SibPrev:016x}, .SibNext: 0x{<long long> CN0.SibNext:016x}, .ChildStart: 0x{<long long> CN0.ChildStart:016x}, .ChildEnd: 0x{<long long> CN0.ChildEnd:016x}")
                    CN0 = CN0.SibNext

        # Forest is planted with trees - one for each cover.  Each tree has a main branch for each fin.
        # Each main branch has EITHER A) grown a first level of branching, one for each weak (or strong masquerading
        # as weak) link it sees OR B) found a fin/cover link.

        walk_the_forest(Forest)  # TRCX

        while Forest:  # while there are still trees in the forest
            CvrTree = Forest
            while CvrTree:    # for each tree in the forest
                CT = NULL
                TRCX(f"CvrTree: 0x{<long long> CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}, nFins: {CvrTree.nFins}, Prev: 0x{<long long> CvrTree.Prev:016x}, Next: 0x{<long long> CvrTree.Next:016x}")
                for f in range(CvrTree.nFins):  # for each fin (main branch) of each tree
                    TRCX(f"CvrTree: {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1} .FinBranch[{f}]: 0x{<long long>CvrTree.FinBranch[f]:016x}, CvrTree.FinChain[{f}]: 0x{<long long>CvrTree.FinChain[f]:016x}")
                    if (not CvrTree.FinBranch[f] and not CvrTree.FinChain[f]) or (CvrTree.FinBranch[f] and CvrTree.FinChain[f]): TRCX_PANIC("Can't both be NULL or contain structs")
                    if CvrTree.FinChain[f]: continue  # chain already found for this fin
                    FN = CvrTree.FinBranch[f]
                    TRCX(f"Entering FN Children loop: CvrTree: {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1} .FinBranch[{f}]: {FN.ChainN.Cand+1}r{FN.ChainN.r+1}c{FN.ChainN.c+1}, Parent: {<long long>FN.Parent:016x}, SibPrev: {<long long>FN.SibPrev:016x}, SibNext: {<long long>FN.SibNext:016x}, ChildStart: {<long long>FN.ChildStart:016x}, ChildEnd: {<long long>FN.ChildEnd:016x}")
                    CN0 = FN.ChildStart
                    while CN0:
                        TRCX(f"In FN Children Loop, Calling top level find_next_child_nodes() with FN child: CN0: 0x{<long long>CN0:016x}: {CN0.ChainN.Cand+1}r{CN0.ChainN.r+1}c{CN0.ChainN.c+1}{OP[TKN_LK[CN0.ChainN.Lk&7]]}, Parent: {<long long>CN0.Parent:016x}, SibPrev: {<long long>CN0.SibPrev:016x}, SibNext: {<long long>CN0.SibNext:016x}, ChildStart: {<long long>CN0.ChildStart:016x}, ChildEnd: {<long long>CN0.ChildEnd:016x}")
                        find_next_child_nodes(CN0, Cands, 1, CvrTree, f)
                        # Return conditions, each of FN's chlildren:
                        #  * Searching
                        #     - CN0.ChildStart points to list of children
                        #     - CN0.ChainN points to the Node asc with this TNODE
                        #     - CvrTree.FinChain[Fin] == NULL
                        #     - CvrTree.FinBranch[Fin] points to the main branch for this fin.
                        #  * Chain has been found:
                        #     - CN0.ChildStart points to the list of children
                        #     - CN0.ChainN == NULL (moved to correct location in chain pointed to by CvrTree.FinChain[Fin].
                        #     - CvrTree.FinChain[Fin] points to the chain.
                        #     - CvrTree.FinBranch[Fin] points to main branch for this fin with the chain Nodes missing from the respective TNodes
                        #  * Search has BOTTOMED_OUT (recursion limit) / NOT_FOUND (could not find node to form a link in the chain)
                        #     - CN0.ChildStart == NULL
                        #     - CN0.Chain points to the Node asc with this TNODE
                        #     - CvrTree.FinChain[Fin] == NULL
                        #     - CvrTree.FinBranch[Fin] points to the main branch for this fin.
                        TRCX(f"Returned to top level in FN Children Loop - find_next_child_nodes() CN0: 0x{<long long> CN0:016x}: .ChainN: 0x{<long long> CN0.ChainN:016x}, .Parent: {<long long> CN0.Parent:016x}, .SibPrev: {<long long> CN0.SibPrev:016x}, .SibNext: {<long long> CN0.SibNext:016x}, .ChildStart: {<long long> CN0.ChildStart:016x}, .ChildEnd: {<long long> CN0.ChildEnd:016x}")
                        if CvrTree.FinChain[f]:
                            TRCX(f"Chain found break out FN Children loop).")
                            break  # A chain has been found, exit loop promptly.
                        CN1 = CN0; CN0 = CN0.SibNext
                        if not CN1.ChildStart:
                            TRCX(f"No more children of this FN's child, splice out this unproductive node.")
                            splice_out_tnode(CN1)  # splice out unproductive node.
                    TRCX(f"Returned from Recursing down to find_next_child_nodes() leaves, FN: 0x{<long long> FN:016x}: .ChainN: 0x{<long long> FN.ChainN:016x}, .Parent: {<long long> FN.Parent:016x}, .SibPrev: {<long long> FN.SibPrev:016x}, .SibNext: {<long long> FN.SibNext:016x}, .ChildStart: {<long long> FN.ChildStart:016x}, .ChildEnd: {<long long>FN.ChildEnd:016x}")
                    if CvrTree.FinChain[f]:
                        TRCX(f"Chain found, Cull the main branch for this fin.")
                        cull_children_of(FN, 1)
                        PyMem_TRCX_Free(FN); CvrTree.FinBranch[f] = NULL
                    elif not FN.ChildStart:
                        TRCX(f"Chain not found for this Fin - unproductive Fin and consequently CvrTree, free FN and break out of Fin loop.")
                        if CvrTree.FinChain[f]: TRCX_PANIC(f" 0x{<long long> CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1} .FinChain[{f}] must be NULL")
                        if FN.ChainN: PyMem_TRCX_Free(FN.ChainN)
                        PyMem_TRCX_Free(FN); CvrTree.FinBranch[f] = NULL
                        CT = CvrTree; break
                if CT:  # set when CvrTree.FinChain[f] and CvrTree.FinBranch[f] are NULL - unproductive cover tree.
                    TRCX(f"Unproductive Cover Tree {CT.Cand+1}r{CT.r+1}c{CT.c+1}: Both FinBranch[{f}] and FinChain[{f}] are Null. Splice it out of forest and cull it.")
                    TRCX(f"Cover Tree: 0x{<long long>CT:016x}, .Prev: 0x{<long long>CT.Prev:016x}, .Next: 0x{<long long>CT.Next:016x}, ")
                    CvrTree = CT.Next
                    if CT.Next: CT.Next.Prev = CT.Prev
                    if CT.Prev: CT.Prev.Next = CT.Next
                    else: Forest = CT.Next
                    cull_cover_tree(CT)
                    continue
                for f in range(CvrTree.nFins):
                    # if (not CvrTree.FinChain[f]) and (not CvrTree.FinBranch[f]):  CT = CvrTree; break  #  both pointers are NULL, unproductive cover tree.
                    # if CvrTree.FinChain[f] and CvrTree.FinBranch[f]: TRCX_PANIC(f"0x{<long long> CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}: Only one of .FinChain[{F}] or .FinBranch[{f}] can point to chain/branch")
                    if CvrTree.FinBranch[f]: break
                else:
                    TRCX("**** FOUND **** All fins see cover, Build Result struct.")
                    walk_the_forest(Forest)
                    C0 = NULL
                    for f in range(nFins):
                        if C0: C0.Next = <CHAIN*> PyMem_TRCX_Calloc(1, sizeof(CHAIN)); C0 = C0.Next
                        else: C0 = Result.Chain = <CHAIN*> PyMem_TRCX_Calloc(1, sizeof(CHAIN))
                        TRCX(f"Add FinChain[{f}]: {<long long>CvrTree.FinChain[f]:016x}")
                        C0.Start = CvrTree.FinChain[f]; CvrTree.FinChain[f] = NULL
                    Result.Outcome = <OUTCOME*> PyMem_TRCX_Calloc(1, sizeof(OUTCOME))
                    Result.Outcome.r = CvrTree.r; Result.Outcome.c = CvrTree.c; Result.Outcome.Op = OP_ELIM_C; Result.Outcome.Cand = CvrTree.Cand
                    TRCX("Cull the forest")
                    while Forest:
                        CT = Forest; Forest = Forest.Next
                        TRCX(f"Culling CvrTree: 0x{<long long> CT:016x}: {CT.Cand+1}r{CT.r+1}c{CT.c+1}")
                        cull_cover_tree(CT)
                    return True
                # for f in range(CvrTree.nFins):  # for each fin (main branch) of each tree
                CvrTree = CvrTree.Next
            # while CvrTree:  # for each tree in the forest
            walk_the_forest(Forest)
        # while Forest:
    # end if kraken:
    return False

# cdef bint find_cover_links_to_all_fins_gl(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
#      return False

cdef void find_next_child_nodes(TNODE_FFISH *ChildN, bint Cands[9][9][9], int Lvl, TREE_FFISH *CvrTree, int Fin):
    # Valid Weakly ended AIC chains require an even number of nodes.  So it makes sense to grow two levels of branches
    # for each recursive iteration.  However chain building can run out of nodes at any level.
    cdef bint           LC1used, LC2used
    cdef int            Lk
    cdef TNODE_FFISH    *CN0
    cdef TNODE_FFISH    *CN1  # odd level
    cdef TNODE_FFISH    *CN2  # even level
    cdef NODE           *LCLodd
    cdef NODE           *LCLeven
    cdef NODE           *LC0
    cdef NODE           *LC1
    cdef NODE           *LC2

    TRCX(f"ChildN: {<long long>ChildN:016x}, Lvl: {Lvl}, CvrTree: {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1} @ 0x{<long long>CvrTree:016x}, Fin: {Fin}")
    TRCX("Searching, Check for link to cover, and if none exist build next two levels of children")
    if ChildN.ChildStart:  # Not at leaves yet, recurse down the tree two node levels at a time,
        TRCX(f"Not at leaves, recurse down LvL: {Lvl}, ChildN: 0x{<long long> ChildN:016x}: {ChildN.ChainN.Cand+1}r{ChildN.ChainN.r+1}c{ChildN.ChainN.c+1}{OP[TKN_LK[ChildN.ChainN.Lk&7]]}, Parent: {<long long> ChildN.Parent:016x}, SibPrev: {<long long> ChildN.SibPrev:016x}, SibNext: {<long long> ChildN.SibNext:016x}, ChildStart: {<long long> ChildN.ChildStart:016x}, ChildEnd: {<long long> ChildN.ChildEnd:016x}")
        CN1 = ChildN.ChildStart
        while CN1:
            TRCX(f"Recursing down to find_next_child_nodes(), LVl: {Lvl}, Odd CN1: 0x{<long long> CN1:016x}: {CN1.ChainN.Cand+1}r{CN1.ChainN.r+1}c{CN1.ChainN.c+1}{OP[TKN_LK[CN1.ChainN.Lk & 0x07]]}, Parent: {<long long> CN1.Parent:016x}, SibPrev: {<long long> CN1.SibPrev:016x}, SibNext: {<long long> CN1.SibNext:016x}, ChildStart: {<long long> CN1.ChildStart:016x}, ChildEnd: {<long long> CN1.ChildEnd:016x}")
            CN2 = CN1.ChildStart
            while CN2:
                TRCX(f"Recurse down to find_next_child_nodes(), Lvl: {Lvl}, Even CN2: 0x{<long long> CN2:016x}: {CN2.ChainN.Cand+1}r{CN2.ChainN.r+1}c{CN2.ChainN.c+1}{OP[TKN_LK[CN2.ChainN.Lk&7]]}, Parent: {<long long> CN2.Parent:016x}, SibPrev: {<long long> CN2.SibPrev:016x}, SibNext: {<long long> CN2.SibNext:016x}, ChildStart: {<long long> CN2.ChildStart:016x}, ChildEnd: {<long long> CN2.ChildEnd:016x}")
                find_next_child_nodes(CN2, Cands, Lvl+1, CvrTree, Fin)
                # Return conditions:
                #  * Searching
                #     - CN2.ChainN points to the Node asc with this TNODE
                #     - CN2.ChildStart points to list of children
                #     - CvrTree.FinChain[Fin] == NULL
                #     - CvrTree.FinBranch[Fin] points to the main branch for this fin.
                #  * Chain has been found:
                #     - CN2.ChainN == NULL (moved to correct location in chain pointed to by CvrTree.FinChain[Fin].
                #     - CN2.ChildStart == NULL - no children, so this node can be spliced out it's Siblist.
                #     - CvrTree.FinChain[Fin] points to the chain.
                #     - CvrTree.FinBranch[Fin] points to main branch for this fin with the chain Nodes missing from the respective TNodes
                #  * Search has BOTTOMED_OUT (recursion limit) / NOT_FOUND (could not find node to form a link in the chain)
                #     - CN2.Chain points to the Node asc with this TNODE
                #     - CN2.ChildStart == NULL - no children so this node can be spliced out it's Siblist
                #     - CvrTree.FinChain[Fin] == NULL
                #     - CvrTree.FinBranch[Fin] points to the main branch for this fin.
                TRCX(f"Returned from find_next_child_nodes(), Lvl: {Lvl}, Even CN2: 0x{<long long> CN2:016x}: .ChainN: 0x{<long long>CN2.ChainN:016x}, .Parent: {<long long> CN2.Parent:016x}, .SibPrev: {<long long> CN2.SibPrev:016x}, .SibNext: {<long long> CN2.SibNext:016x}, .ChildStart: {<long long> CN2.ChildStart:016x}, .ChildEnd: {<long long> CN2.ChildEnd:016x}")
                if CvrTree.FinChain[Fin]: return  # A chain has been found, climb out of recursion as fast a possilbe.
                CN0 = CN2; CN2 = CN2.SibNext
                if not CN0.ChildStart: splice_out_tnode(CN0)  # splice out unproductive node.
            TRCX(f"Returning from Recursing down to find_next_child_nodes() leaves, Lvl: {Lvl}, Odd CN1: 0x{<long long> CN1:016x}: .ChainN: 0x{<long long>CN1.ChainN:016x}, .Parent: {<long long> CN1.Parent:016x}, .SibPrev: {<long long> CN1.SibPrev:016x}, .SibNext: {<long long> CN1.SibNext:016x}, .ChildStart: {<long long> CN1.ChildStart:016x}, .ChildEnd: {<long long> CN1.ChildEnd:016x}")
            CN0 = CN1; CN1 = CN1.SibNext
            if not CN0.ChildStart: splice_out_tnode(CN0)
            TRCX(f"CvrTree.FinChain[{Fin}]: 0x{<long long>CvrTree.FinChain[Fin]:016x}")
    else: # at the leaves, add the next odd and even level of branches.
        TRCX(f"At leaves look for next odd level of (strong) linked nodes to {ChildN.ChainN.Cand+1}r{ChildN.ChainN.r+1}c{ChildN.ChainN.c+1}")
        LCLodd = list_ccells_linked_to_c(ChildN.ChainN.r, ChildN.ChainN.c, ChildN.ChainN.Cand, Cands, LK_STRG_C)
        if LCLodd:  ### TRCX
            LC1 = LCLodd; St = ""  #### TRCX
            while LC1:   #### TRCX
                if St: St += ", "   #### TRCX
                St += f"{LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}{OP[TKN_LK[LC1.Lk&7]]}"  #### TRCX
                LC1 = LC1.Next  ### TRCX
            TRCX(f"Links to ChildN: {ChildN.ChainN.Cand+1}r{ChildN.ChainN.r+1}c{ChildN.ChainN.c+1} -> {St}")
        else:
            TRCX(f"No odd links found, chain can't be made")
        while LCLodd:
            LC1 = LCLodd; LCLodd = LCLodd.Next
            TRCX(f"LC1: 0x{<long long>LC1:016x}, {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}{OP[TKN_LK[LC1.Lk&7]]}, LC1.Next: 0x{<long long>LC1.Next:016x}.")
            # Find first LC1 that is not in the chain.  A node can only be used once in a chain.
            # if the node is being used, cull it and advance to next.
            CN0 = ChildN; LC1used = False
            while CN0:
                if CN0.ChainN.r == LC1.r and CN0.ChainN.c == LC1.c and CN0.ChainN.Cand == LC1.Cand: LC1used = True; break
                else: CN0 = CN0.Parent
            if LC1used:
                TRCX(f"Node: {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1} is in the chain, cull it")
                # LC1 = LCLodd; LCLodd = LCLodd.Next
                PyMem_TRCX_Free(LC1)
                continue
                # if not LCLodd: break  # no more odd nodes left, break out loop.
            # LC1 is the first unused node that can be used in the chain.
            Lk = how_ccells_linked_c(CvrTree.r, CvrTree.c, CvrTree.Cand, LC1.r, LC1.c, LC1.Cand, Cands)
            TRCX(f"LC1: {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}{OP[TKN_LK[Lk&7]]} to CvrTree: {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}")
            if Lk: # not LK_NONE_C  - **** A chain has been found  *****.
                TRCX(f"Chain is completed with Node to cover: {OP[TKN_LK[LC1.Lk&7]]}{LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}{OP[TKN_LK[Lk&7]]}{CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}")
                LC0 = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE))  # create a node for the cvr
                LC0.r = CvrTree.r; LC0.c = CvrTree.c; LC0.Cand = CvrTree.Cand; LC0.Lk = LK_WKST_C if Lk & LK_STRG_C else LK_WEAK_C
                LC0.Prev = NULL; LC0.Next = LC1; LC1.Prev = LC0
                CvrTree.FinChain[Fin] = LC0   # pin the chain being built to CvrTree.FinChain[Fin]
                # splice LC1 out of LCLodd
                # LC1 = LCLodd; LCLodd = LCLodd.Next

                # give back the rest of the LCLodd list
                while LCLodd:
                    LC0 = LCLodd; LCLodd = LCLodd.Next
                    PyMem_TRCX_Free(LC0)

                # Splice LC1 into the chain, finish constructing the chain, release it from child nodes.
                TRCX(f"ChildN.ChainN: 0x{<long long>ChildN.ChainN:016x}, {ChildN.ChainN.Cand+1}r{ChildN.ChainN.r+1}c{ChildN.ChainN.c+1}{OP[TKN_LK[ChildN.ChainN.Lk]]}, .Next: 0x{<long long>ChildN.ChainN.Next:016x}")
                # LC1.Next = ChildN.ChainN
                # ChildN.ChainN.Prev = LC1
                CN0 = ChildN
                while CN0:
                    LC1.Next = CN0.ChainN; CN0.ChainN = NULL
                    LC1 = LC1.Next; CN0 = CN0.Parent
                St = f"Returning with found Chain in CvrTree.FinChain[{Fin}]: "
                LC0 = CvrTree.FinChain[Fin]  ### TRCX
                while LC0:  #### TRCX
                    St += f"{LC0.Cand+1}r{LC0.r+1}c{LC0.c+1}{OP[TKN_LK[LC0.Lk&7]]}"  ### TRCX
                    LC0 = LC0.Next  ### TRCX
                TRCX(St)
                return
            if Lvl > RECURSE_LIM_C:
                # give back the LCLodd list
                while LCLodd:
                    LC0 = LCLodd; LCLodd = LCLodd.Next
                    PyMem_TRCX_Free(LC0)
                PyMem_TRCX_Free(LC1)
                TRCX("Bottomed Out, returning")
                return

            # LC1 did not see a cover, find the Even nodes that see LCLodd.
            TRCX(f"Node: {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}{OP[TKN_LK[LC1.Lk&7]]} cannot see cover, get list of even nodes for this odd node, and build out child nodes.")
            LCLeven = list_ccells_linked_to_c(LC1.r, LC1.c, LC1.Cand, Cands, LK_STWK_C)  #LC1.Lk)
            TRCX(f"LCLeven: {<long long>LCLeven:016x}")
            if not LCLeven:
                TRCX(f"No even links found to LC1: {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1}, chain can't be made, give back LCLodd")
                # LC1 = LCLodd; LCLodd = LCLodd.Next
                PyMem_TRCX_Free(LC1)
                continue
            # LCLeven links found
            LC2 = LCLeven; St = ""  #### TRCX
            while LC2:  #### TRCX
                if St: St += ", "  #### TRCX
                St += f"{LC2.Cand+1}r{LC2.r+1}c{LC2.c+1}{OP[TKN_LK[LC2.Lk&7]]}"  #### TRCX
                LC2 = LC2.Next  ### TRCX
            TRCX(f"LCLeven Links to LC1: {LC1.Cand+1}r{LC1.r+1}c{LC1.c+1} -> {St}")
            CN1 = NULL
            while LCLeven:
                LC2 = LCLeven; LCLeven = LCLeven.Next
                TRCX(f"LC2: 0x{<long long> LC2:016x}, {LC2.Cand+1}r{LC2.r+1}c{LC2.c+1}{OP[TKN_LK[LC2.Lk&7]]}")
                # Find first LC2 that is not in the chain.  A node can only be used once in a chain.
                # if the node is being used, cull it and advance to next.
                CN0 = ChildN; LC2used = False
                while CN0:
                    if CN0.ChainN.r == LC2.r and CN0.ChainN.c == LC2.c and CN0.ChainN.Cand == LC2.Cand: LC2used = True; break
                    else: CN0 = CN0.Parent
                if LC2used:
                    TRCX(f"LC2 Node: {<long long>LC2:016x}, {LC2.Cand+1}r{LC2.r+1}c{LC2.c+1} is in in the chain, cull it")
                    PyMem_TRCX_Free(LC2)
                    # if not LCLeven and not CN1: # no more even nodes left and child node not created for LC1.
                    #     TRCX(f"Run out of LCLeven nodes, and CN1 not created - chain cannot be created, cull LC1: {<long long>LC1:016x}")
                    #     PyMem_TRCX_Free(LC1)
                    continue
                TRCX(f"LC2 Node: {<long long>LC2:016x}, {LC2.Cand+1}r{LC2.r+1}c{LC2.c+1} not in chain. ")
                if not CN1:  # if not previously created, Create the odd Child node first and splice it in the TNODE tree.
                    TRCX(f"CN1 not previously created, creating it")
                    if ChildN.ChildStart == ChildN.ChildEnd == NULL:  # empty siblist
                        ChildN.ChildStart = ChildN.ChildEnd = CN1 = <TNODE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                    else:  # append to end of siblist
                        ChildN.ChildEnd.SibNext = CN1 = <TNODE_FFISH *>PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                        CN1.SibPrev = ChildN.ChildEnd
                        CN1.SibNext = NULL; ChildN.ChildEnd = CN1
                    CN1.Parent = ChildN
                    # Splice LC1 out of LCLodd and into CN1.ChainN
                    # LC1 = LCLodd; LCLodd = LCLodd.Next
                    CN1.ChainN = LC1
                    CN1.ChainN.Next = ChildN.ChainN
                    TRCX(f"LC1 in CN1: CN1.ChainN: 0x{<long long>CN1.ChainN:016x}: {CN1.ChainN.Cand+1}r{CN1.ChainN.r+1}c{CN1.ChainN.c+1}{OP[TKN_LK[CN1.ChainN.Lk&7]]}, .Next: {<long long>CN1.ChainN.Next:016x}.")
                    TRCX(f"Odd Child CN1: 0x{<long long>CN1:016x} Parent: {<long long> CN1.Parent:016x}, SibPrev: {<long long> CN1.SibPrev:016x}, SibNext: {<long long> CN1.SibNext:016x}, ChildStart: {<long long> CN1.ChildStart:016x}, ChildEnd: {<long long> CN1.ChildEnd:016x}")
                TRCX("Create a CN2 for LC2 and add CN2 to CN1's list of children.")
                if CN1.ChildStart == CN1.ChildEnd == NULL:  # empty siblist
                    CN1.ChildStart = CN1.ChildEnd = CN2 = <TNODE_FFISH*> PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                else:  # append to end of siblist
                    CN1.ChildEnd.SibNext = CN2 = <TNODE_FFISH*> PyMem_TRCX_Calloc(1, sizeof(TNODE_FFISH))
                    CN2.SibPrev = CN1.ChildEnd; CN2.SibNext = NULL; CN1.ChildEnd = CN2
                CN2.Parent = CN1
                # TRCX(f"got here 11, CN1: {<long long>CN1:016x}")
                # Splice LC2 out of LCLeven and into CN1.ChainN
                # LC2 = LCLeven; LCLeven = LCLeven.Next
                LC2.Lk = LK_WKST_C if LC2.Lk & LK_STRG_C else LK_WEAK_C
                CN2.ChainN = LC2
                CN2.ChainN.Next = CN1.ChainN
                # TRCX(f"got here 12, CN1: {<long long>CN1:016x}")
                # LCLeven = LCLeven.Next
                TRCX(f"LC2 in CN2: CN2.ChainN: 0x{<long long> CN2.ChainN:016x}: {CN2.ChainN.Cand+1}r{CN2.ChainN.r+1}c{CN2.ChainN.c+1}{OP[TKN_LK[CN2.ChainN.Lk&7]]}, .Next: {<long long>CN2.ChainN.Next:016x}.")
            # while LCLeven
            if not CN1:
                TRCX(f"Run out of LCLeven nodes, and CN1 not created - chain cannot be created, cull LC1: {<long long> LC1:016x}")
                PyMem_TRCX_Free(LC1)
            if CN1:    #### TRCX
                CN2 = CN1.ChildStart  #### TRCX
                while CN2:   #### TRCX
                    TRCX(f"Even Child CN2: 0x{<long long>CN2:016x}: {CN2.ChainN.Cand+1}r{CN2.ChainN.r+1}c{CN2.ChainN.c+1}{OP[TKN_LK[CN2.ChainN.Lk&7]]}, Parent: {<long long> CN2.Parent:016x}, SibPrev: {<long long> CN2.SibPrev:016x}, SibNext: {<long long> CN2.SibNext:016x}, ChildStart: {<long long> CN2.ChildStart:016x}, ChildEnd: {<long long> CN2.ChildEnd:016x}")
                    CN2 = CN2.SibNext  ### TRCX
            TRCX("Got here 1")
        TRCX("Got here 2")
    TRCX("Got here 3")

cdef void cull_cover_tree(TREE_FFISH *CT):
    cdef                int f
    cdef NODE           *CN

    for f in range(CT.nFins):
        while CT.FinChain[f]:
            CN = CT.FinChain[f]; CT.FinChain[f] = CN.Next
            TRCX(f"Culling link from .FinChain[{f}], 0x{<long long>CN:016x}, {CN.Cand+1}r{CN.r+1}c{CN.r+1}{OP[TKN_LK[CN.Lk]]}, .Next: 0x{<long long>CN.Next:016x}")
            PyMem_TRCX_Free(CN)
        if CT.FinBranch[f]:
            TRCX(f"Culling children_of .FinBranch[{f}]: 0x{<long long>CT.FinBranch[f]:016x} ..ChainN: 0x{<long long>CT.FinBranch[f].ChainN:016x}  Parent: {<long long>CT.FinBranch[f].Parent:016x}, SibPrev: {<long long>CT.FinBranch[f].SibPrev:016x}, SibNext: {<long long>CT.FinBranch[f].SibNext:016x}, ChildStart: {<long long>CT.FinBranch[f].ChildStart:016x}, ChildEnd: {<long long>CT.FinBranch[f].ChildEnd:016x}")
            cull_children_of(CT.FinBranch[f], 1)
            TRCX(f"Culled children_of .FinBranch[{f}]: 0x{<long long>CT.FinBranch[f]:016x} ..ChainN: 0x{<long long>CT.FinBranch[f].ChainN:016x}, culling it.")
            if CT.FinBranch[f].ChainN: PyMem_TRCX_Free(CT.FinBranch[f].ChainN)
            PyMem_TRCX_Free(CT.FinBranch[f])
    PyMem_TRCX_Free(CT)

cdef void cull_children_of(TNODE_FFISH *CN, Lvl):  ### TRCX
    cdef TNODE_FFISH *CN0
    cdef TNODE_FFISH *CN1

    CN1 = CN.ChildStart
    while CN1:
        CN0 = CN1; CN1 = CN1.SibNext
        St = ""
        if CN0.ChainN: St = f"{CN0.ChainN.Cand+1}r{CN0.ChainN.r+1}c{CN0.ChainN.c+1}{OP[TKN_LK[CN0.ChainN.Lk & 7]]}"
        TRCX(f"Lvl: {Lvl}: Culling children_of: 0x{<long long> CN0:016x}, ..ChainN: 0x{<long long> CN0.ChainN:016x}, {St},  Parent: {<long long> CN0.Parent:016x}, SibPrev: {<long long> CN0.SibPrev:016x}, SibNext: {<long long> CN0.SibNext:016x}, ChildStart: {<long long> CN0.ChildStart:016x}, ChildEnd: {<long long> CN0.ChildEnd:016x}")
        cull_children_of(CN0, Lvl+1)
        TRCX(f"Lvl: {Lvl}: Culled children of 0x{<long long>CN0:016x}, .ChainN: 0x{<long long>CN0.ChainN:016x}.")
        if CN0.ChainN: PyMem_TRCX_Free(CN0.ChainN)
        PyMem_TRCX_Free(CN0)
    CN.ChildStart = NULL

cdef void splice_out_tnode(TNODE_FFISH *N):
    cdef TNODE_FFISH *P  # parent

    if N.ChainN: PyMem_TRCX_Free(N.ChainN)
    P = N.Parent
    if P.ChildStart == P.ChildEnd == N: P.ChildStart = P.ChildEnd = NULL  # only Childnode in the sibling list
    elif P.ChildStart == N: P.ChildStart = N.SibNext; N.SibNext.SibPrev = NULL  # Child node is at the start of the sibling list.
    elif P.ChildEnd == N: P.ChildEnd = N.SibPrev; N.SibPrev.SibNext = NULL  # Child node is at the end of the sibling list.
    else: N.SibNext.SibPrev = N.SibPrev; N.SibPrev.SibNext = N.SibNext # Child node is somewhere in between the start and end of the sibling list
    PyMem_TRCX_Free(N)

cdef void walk_the_forest(TREE_FFISH *Forest):
    cdef TREE_FFISH *CvrTree
    cdef NODE       *LCStart
    cdef int        f

    TRCX("Walking the trees in the forest for nodes from fins towards covers")
    TRCX("******************************************************************")
    CvrTree = Forest
    while CvrTree:
        TRCX(f"CvrTree: 0x{<long long> CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}, nFins: {CvrTree.nFins}, Prev: 0x{<long long> CvrTree.Prev:016x}, Next: 0x{<long long> CvrTree.Next:016x}")
        for f in range(CvrTree.nFins):
            if CvrTree.FinChain[f]:
                N = CvrTree.FinChain[f]; St = ""
                while N: St += f"{N.Cand+1}r{N.r+1}c{N.c+1}{OP[TKN_LK[N.Lk&7]]}"; N = N.Next
                TRCX(f"FinChain[{f}]: {St}.")  # CvrTree.FinChain[f].Cand+1}r{CvrTree.FinChain[f].r+1}c{CvrTree.FinChain[f].c+1}{OP[TKN_LK[CvrTree.FinChain[f].Lk&7]]}{CvrTree.FinChain[f].Next.Cand+1}r{CvrTree.FinChain[f].Next.r+1}c{CvrTree.FinChain[f].Next.c+1}")
            if CvrTree.FinBranch[f]:
                TRCX(f"FinBranch[{f}]: {CvrTree.FinBranch[f].ChainN.Cand+1}r{CvrTree.FinBranch[f].ChainN.r+1}c{CvrTree.FinBranch[f].ChainN.c+1}")
                climb_next_br(CvrTree.FinBranch[f], 0)
        CvrTree = CvrTree.Next

cdef void climb_next_br(TNODE_FFISH *TN, int Lvl):
    cdef TNODE_FFISH *TN0

    St = " |" * Lvl
    if TN.ChainN: St += f"{OP[TKN_LK[TN.ChainN.Lk&7]]}{TN.ChainN.Cand+1}r{TN.ChainN.r+1}c{TN.ChainN.c+1}: .Next: {<long long>TN.ChainN.Next:016x}, "
    else: St += f"Empty ChainN, "
    St += f"TN: {<long long>TN:016x}, TN.ChainN: {<long long>TN.ChainN:016x}, Parent: {<long long>TN.Parent:016x}, SibPrev: {<long long>TN.SibPrev:016x}, SibNext: {<long long>TN.SibNext:016x}, ChildStart: {<long long>TN.ChildStart:016x}, ChildEnd: {<long long>TN.ChildEnd:016x}"
    TRCX(St)
    TN0 = TN.ChildStart
    while TN0:
        climb_next_br(TN0, Lvl+1)
        TN0 = TN0.SibNext


