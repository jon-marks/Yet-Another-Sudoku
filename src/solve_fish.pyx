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

# from solve_utils import *

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
    cdef int r0, c0, r1, c1, Base, Cvr, Cand
    cdef bint BaseCvrs[2][9]
    cdef int Bases[2]
    cdef int Cvrs[2]

    for Cand in range(9):
        # look in rows
        for r0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr >= 2: break
                    BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 instances of Cand, look for another bases
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr >= 2: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # found a second base with two instance of cand.
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        Cvr = 0
                        for c0 in range(9):
                            if BaseCvrs[0][c0] or BaseCvrs[1][c0]:
                                if Cvr >= 2: break
                                # TRCX(f"Cover {Cvr} found: Col {c0+1}")
                                Cvrs[Cvr] = c0; Cvr += 1
                        else:
                            if Cvr != 2: continue
                            # X-wing pattern found 2 bases with only two cands in the same cols.
                            # TRCX("X-Wing found")
                            Bases[0] = r0; Bases[1] = r1
                            if elim_cands_in_fish(Cand, <int*>Bases, <int*>Cvrs, ROW, <int>T_X_WING, Cands, Step): return 0
        # look in cols
        for c0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr >= 2: break
                    BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 instances of Cand, look for another bases
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr >= 2: break
                            # TRCX(f"Cands[{r0+1}][{c1+1}][{Cand+1}] = {Cands[r0][c0][Cand]}")
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # found a second base with two instance of cand.
                        # TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        Cvr = 0
                        for r0 in range(9):
                            if BaseCvrs[0][r0] or BaseCvrs[1][r0]:
                                if Cvr >= 2: break
                                # TRCX(f"Cover {Cvr} found: Row {r0+1}")
                                Cvrs[Cvr] = r0; Cvr += 1
                        else:
                            if Cvr != 2: continue
                            # X-wing pattern found 2 bases with only two cands in the same cols.
                            Bases[0] = c0; Bases[1] = c1
                            if elim_cands_in_fish(Cand, <int*>Bases, <int*>Cvrs, COL, <int>T_X_WING, Cands, Step): return 0
    return -1

cdef int tech_finned_x_wings_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, Base, Cvr, Cand, lenCU, lenCS, lenCF, i, j, cu
    cdef int Method
    cdef bint BaseCvrs[2][9]
    cdef int CU[4]
    cdef int Bases[2]
    cdef int CS[4]
    cdef int CF[4]

    for Cand in range(9):
        # look in rows
        for r0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr >= 4: break   # 2 bases and up to 2 fins
                    BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 4 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr >= 4: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # found a second base with 2 to 4 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = 0
                        for c0 in range(9):
                            if lenCU > 4: break
                            if BaseCvrs[0][c0] | BaseCvrs[1][c0]: CU[lenCU] = c0; lenCU += 1
                        else:
                            if not 3 <= lenCU <= 4: continue  # 2 bases and 1 to 2 fins.
                            Bases[0] = r0; Bases[1] = r1; lenCS = lenCF = 0
                            for cu in range(lenCU):
                                i = 0
                                if Cands[r0][CU[cu]][Cand]: i += 1
                                if Cands[r1][CU[cu]][Cand]: i += 1
                                if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                            sCU = ""  ### TRCX
                            for i in range(lenCU):  ### TRCX
                                if sCU: sCU += ", "  ### TRCX
                                sCU += f"{CU[i]+1}"  ### TRCX
                            sCS = ""; sCF = ""  ### TRCX
                            for i in range(lenCS):  ### TRCX
                                if sCS: sCS += ", "  ### TRCX
                                sCS += f"{CS[i]+1}"  ### TRCX
                            for i in range(lenCF):  ### TRCX
                                if sCF: sCF += ", "  ### TRCX
                                sCF += f"{CF[i]+1}"  ### TRCX
                            TRCX(f"Row: Bases: ({r0+1}, {r1+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                            for Method in Methods:
                                if ((Method & T_SASHIMI_C) and (lenCS == 1 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 2 and 1 <= lenCF <= 2)):
                                    if elim_cands_in_finned_fish(Cand, <int *>Bases, 2, <int *>CS, lenCS, <int *>CF, lenCF, ROW, <int>Method, Cands, Step): return 0
        # look in cols
        for c0 in range(8):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr >= 4: break  # 2 bases and up to 2 fins
                    BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 4 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 9):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr >= 4: break
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # found a second base with 2 to 4 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = 0
                        for r0 in range(9):
                            if lenCU > 4: break
                            if BaseCvrs[0][r0] | BaseCvrs[1][r0]: CU[lenCU] = r0; lenCU += 1
                        else:
                            if not 3 <= lenCU <= 4: continue  # 2 bases and 1 to 2 fins.
                            Bases[0] = c0; Bases[1] = c1; lenCS = lenCF = 0
                            for cu in range(lenCU):
                                i = 0
                                if Cands[CU[cu]][c0][Cand]: i += 1
                                if Cands[CU[cu]][c1][Cand]: i += 1
                                if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                            sCU = ""  ### TRCX
                            for i in range(lenCU):  ### TRCX
                                if sCU: sCU += ", "  ### TRCX
                                sCU += f"{CU[i]+1}"  ### TRCX
                            sCS = ""; sCF = ""  ### TRCX
                            for i in range(lenCS):  ### TRCX
                                if sCS: sCS += ", "  ### TRCX
                                sCS += f"{CS[i]+1}"  ### TRCX
                            for i in range(lenCF):  ### TRCX
                                if sCF: sCF += ", "  ### TRCX
                                sCF += f"{CF[i]+1}"  ### TRCX
                            TRCX(f"Col Bases: ({c0+1}, {c1+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                            for Method in Methods:
                                if ((Method & T_SASHIMI_C) and (lenCS == 1 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 2 and 1 <= lenCF <= 2)):
                                    if elim_cands_in_finned_fish(Cand, <int*> Bases, 2, <int*> CS, lenCS, <int*> CF, lenCF, COL, <int>Method, Cands, Step): return 0
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
    cdef int r0, c0, r1, c1, r2, c2, Base, Cvr, Cand
    cdef bint BaseCvrs[3][9]
    cdef int Bases[3]
    cdef int Cvrs[3]

    for Cand in range(9):
        # Look in rows
        for r0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                  if Cvr >= 3: break
                  BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 or 3 instances of Cand, look for next two bases
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr >= 3: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        Cvr = 0
                        for c0 in range(9):
                            if BaseCvrs[0][c0] or BaseCvrs[1][c0]:
                                if Cvr >= 3: break
                                Cvr += 1
                        else:
                            if Cvr != 3: continue
                            # 2 of 3 bases found with 2 or 3 instances of cand, look for third base
                            # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                            for r2 in range(r1+1, 9):
                                Cvr = 0
                                memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                                for c0 in range(9):
                                    # TRCX(f"Seeking third base: Cands[{r2+1}][{c0+1}][{Cand+1}]: {Cands[r2][c0][Cand]}")
                                    if Cands[r2][c0][Cand]:
                                        if Cvr >= 3: break
                                        BaseCvrs[2][c0] = True; Cvr += 1
                                        # TRCX(f"Base 3 Covers {Cvr} found: r{r2+1}c{c0+1}")
                                else:
                                    if Cvr < 2: continue
                                    Cvr = 0
                                    for c0 in range(9):
                                        if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]:
                                            if Cvr >= 3: break
                                            Cvrs[Cvr] = c0; Cvr += 1
                                    else:
                                        if Cvr != 3: continue
                                        # Swordfish pattern found, 3 bases with 2 or 3 instances of cand
                                        # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        Bases[0] = r0; Bases[1] = r1; Bases[2] = r2
                                        # TRCX(f"Swordfish Pattern: {Cand+1}r{Bases[0]+1}{Bases[1]+1}{Bases[2]+2}c{Cvrs[0]+1}{Cvrs[1]+1}{Cvrs[2]+1}")
                                        if elim_cands_in_fish(Cand, <int *>Bases, <int *>Cvrs, ROW, <int>T_SWORDFISH, Cands, Step): return 0
        # Look in cols
        for c0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr >= 3: break
                    BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 or 3 instances of Cand, look for next two bases
                for c1 in range(c0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr >= 3: break
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        Cvr = 0
                        for r0 in range(9):
                            if BaseCvrs[0][r0] or BaseCvrs[1][r0]:
                                if Cvr >= 3: break
                                Cvr += 1
                        else:
                            if Cvr != 3: continue
                            # 2 of 3 bases found with 2 or 3 instances of cand, look for third base
                            for c2 in range(c1+1, 9):
                                Cvr = 0
                                memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                                for r0 in range(9):
                                    if Cands[r0][c2][Cand]:
                                        if Cvr >= 3: break
                                        BaseCvrs[2][r0] = True; Cvr += 1
                                else:
                                    if Cvr < 2: continue
                                    Cvr = 0
                                    for r0 in range(9):
                                        if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]:
                                            if Cvr >= 3: break
                                            Cvrs[Cvr] = r0; Cvr += 1
                                    else:
                                        if Cvr != 3: continue
                                        # Swordfish pattern found, 3 bases with 2 or 3 instances of cand
                                        Bases[0] = c0; Bases[1] = c1; Bases[2] = c2
                                        # TRCX(f"Swordfish Pattern: {Cand+1}c{Bases[0]+1}{Bases[1]+1}{Bases[2]+2}r{Cvrs[0]+1}{Cvrs[1]+1}{Cvrs[2]+1}")
                                        if elim_cands_in_fish(Cand, <int *>Bases, <int *>Cvrs, COL, <int>T_SWORDFISH, Cands, Step): return 0
    return -1

cdef int tech_finned_swordfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, r2, c2, Base, Cvr, Cand, lenCU, lenCS, lenCF, i, j, cu
    cdef int Method
    cdef bint BaseCvrs[3][9]
    cdef int CU[5]
    cdef int Bases[3]
    cdef int CS[5]  # needs to be large enough to collect all possilbilites.
    cdef int CF[5]

    for Cand in range(9):
        # look in rows
        for r0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr > 5: break   # 3 bases and up to 2 fins
                    BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 5 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr > 5: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # Second base with 2 to 5 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                            for c0 in range(9):
                                if Cands[r2][c0][Cand]:
                                    if Cvr > 5: break
                                    BaseCvrs[2][c0] = True; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # Third base with 2 to 5 instances of Cand (Base + up to 2 fins).
                                TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                # How are the bases covered?
                                lenCU = 0
                                for c0 in range(9):
                                    if lenCU > 5: break
                                    if BaseCvrs[0][c0] | BaseCvrs[1][c0] | BaseCvrs[2][c0]: CU[lenCU] = c0; lenCU += 1
                                else:
                                    if not 4 <= lenCU <= 5: continue  # 3 bases and 1 to 2 fins or for sashimi,  2 bases and 2 - 3 fins.
                                    Bases[0] = r0; Bases[1] = r1; Bases[2] = r2; lenCS = lenCF = 0
                                    for cu in range(lenCU):
                                        i = 0
                                        if Cands[r0][CU[cu]][Cand]: i += 1
                                        if Cands[r1][CU[cu]][Cand]: i += 1
                                        if Cands[r2][CU[cu]][Cand]: i += 1
                                        if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                        elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                                    sCU = ""  ### TRCX
                                    for i in range(lenCU):  ### TRCX
                                        if sCU: sCU += ", "  ### TRCX
                                        sCU += f"{CU[i]+1}"  ### TRCX
                                    sCS = ""; sCF = ""  ### TRCX
                                    for i in range(lenCS):  ### TRCX
                                        if sCS: sCS += ", "  ### TRCX
                                        sCS += f"{CS[i]+1}"  ### TRCX
                                    for i in range(lenCF):  ### TRCX
                                        if sCF: sCF += ", "  ### TRCX
                                        sCF += f"{CF[i]+1}"  ### TRCX
                                    TRCX(f"Row Bases: ({r0+1}, {r1+1}, {r2+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                                    for Method in Methods:
                                        if ((Method & T_SASHIMI_C) and (lenCS == 2 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 3 and 1 <= lenCF <= 2)):
                                            if elim_cands_in_finned_fish(Cand, <int *>Bases, 3, <int *>CS, lenCS, <int *>CF, lenCF, ROW, <int>Method, Cands, Step): return 0
        # look in cols
        for c0 in range(7):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr > 5: break  # 3 bases and up to 2 fins
                    BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 5 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 8):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr > 5: break
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # Second base found with 2 to 5 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 9):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                            for r0 in range(9):
                                if Cands[r0][c2][Cand]:
                                    if Cvr > 5: break
                                    BaseCvrs[2][r0] = True; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # Third base found  with 2 to 5 instances of Cand (Base + up to 2 fins).
                                TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                lenCU = 0
                                for r0 in range(9):
                                    if lenCU > 5: break
                                    if BaseCvrs[0][r0] | BaseCvrs[1][r0] | BaseCvrs[2][r0]: CU[lenCU] = r0; lenCU += 1
                                else:
                                    if not 4 <= lenCU <= 5: continue  # 3 bases and 1 to 2 fins.
                                    Bases[0] = c0; Bases[1] = c1; Bases[2] = c2; lenCS = lenCF = 0
                                    for cu in range(lenCU):
                                        i = 0
                                        if Cands[CU[cu]][c0][Cand]: i += 1
                                        if Cands[CU[cu]][c1][Cand]: i += 1
                                        if Cands[CU[cu]][c2][Cand]: i += 1
                                        if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                        elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                                    sCU = ""  ### TRCX
                                    for i in range(lenCU):  ### TRCX
                                        if sCU: sCU += ", "  ### TRCX
                                        sCU += f"{CU[i]+1}"  ### TRCX
                                    sCS = ""; sCF = ""  ### TRCX
                                    for i in range(lenCS):  ### TRCX
                                        if sCS: sCS += ", "  ### TRCX
                                        sCS += f"{CS[i]+1}"  ### TRCX
                                    for i in range(lenCF):  ### TRCX
                                        if sCF: sCF += ", "  ### TRCX
                                        sCF += f"{CF[i]+1}"  ### TRCX
                                    TRCX(f"Col Bases: ({c0+1}, {c1+1}, {c2+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                                    for Method in Methods:
                                        if ((Method & T_SASHIMI_C) and (lenCS == 2 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 3 and 1 <= lenCF <= 2)):
                                            if elim_cands_in_finned_fish(Cand, <int*> Bases, 3, <int*> CS, lenCS, <int*> CF, lenCF, COL, <int>Method, Cands, Step): return 0
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
    cdef int r0, c0, r1, c1, r2, c2, r3, c3, Base, Cvr, Cand
    cdef bint BaseCvrs[4][9]
    cdef int Bases[4]
    cdef int Cvrs[4]

    for Cand in range(9):
        # Look in rows
        for r0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                  if Cvr >= 4: break
                  BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 4 instances of Cand, look for next three bases
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr >= 4: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # TRCX(f"Potential Second Base: {Cand+1}r{r1+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                        Cvr = 0
                        for c0 in range(9):
                            if BaseCvrs[0][c0] or BaseCvrs[1][c0]:
                                if Cvr >= 4: break
                                Cvr += 1
                        else:
                            # TRCX(f"Got Here, Cvr = {Cvr}")
                            if not (3 <= Cvr <= 4): continue
                            # 2 of 4 bases found with 2 to 4 instances of cand, look for third base
                            # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                            for r2 in range(r1+1, 8):
                                Cvr = 0
                                memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                                for c0 in range(9):
                                     if Cands[r2][c0][Cand]:
                                        if Cvr >= 4: break
                                        BaseCvrs[2][c0] = True; Cvr += 1
                                else:
                                    if Cvr < 2: continue
                                    Cvr = 0
                                    for c0 in range(9):
                                        if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0]:
                                            if Cvr >= 4: break
                                            Cvr += 1
                                    else:
                                        if Cvr != 4: continue
                                        # 3 of 4 bases with 2 to 4 instances of cand, look for fourth base
                                        # TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        for r3 in range(r2+1, 9):
                                            Cvr = 0
                                            memset(<void*> BaseCvrs[3], False, sizeof(int[9]))
                                            for c0 in range(9):
                                                if Cands[r3][c0][Cand]:
                                                    if Cvr >= 4: break
                                                    BaseCvrs[3][c0] = True; Cvr += 1
                                            else:
                                                if Cvr < 2: continue
                                                Cvr = 0
                                                for c0 in range(9):
                                                    if BaseCvrs[0][c0] or BaseCvrs[1][c0] or BaseCvrs[2][c0] or BaseCvrs[3][c0]:
                                                        if Cvr >= 4: break
                                                        Cvrs[Cvr] = c0; Cvr += 1
                                                else:
                                                    if Cvr != 4: continue
                                                    # Jellyfish pattern found, 4 bases with 2 to 4 instances of cand
                                                    # TRCX(f"Fourth Base: {Cand+1}r{r3+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                                    Bases[0] = r0; Bases[1] = r1; Bases[2] = r2; Bases[3] = r3
                                                    if elim_cands_in_fish(Cand, <int *>Bases, <int *>Cvrs, ROW, <int>T_JELLYFISH, Cands, Step): return 0
        # Look in cols
        # TRCX("Col-wise bases")
        for c0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                  if Cvr >= 4: break
                  BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 4 instances of Cand, look for next three bases
                # TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr >= 4: break
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        Cvr = 0
                        for r0 in range(9):
                            if BaseCvrs[0][r0] or BaseCvrs[1][r0]:
                                if Cvr >= 4: break
                                Cvr += 1
                        else:
                            if not (3 <= Cvr <= 4): continue
                            # 2 of 4 bases found with 2 to 4 instances of cand, look for third base
                            # TRCX(f"Second Base: {Cand+1}r{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                            for c2 in range(c1+1, 8):
                                Cvr = 0
                                memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                                for r0 in range(9):
                                    if Cands[r0][c2][Cand]:
                                        if Cvr >= 4: break
                                        BaseCvrs[2][r0] = True; Cvr += 1
                                else:
                                    if Cvr < 2: continue
                                    Cvr = 0
                                    for r0 in range(9):
                                        if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0]:
                                            if Cvr >= 4: break
                                            Cvr += 1
                                    else:
                                        if Cvr != 4: continue
                                        # 3 of 4 bases with 2 to 4 instances of cand, look for 4th base
                                        # TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        for c3 in range(c2+1, 9):
                                            Cvr = 0
                                            memset(<void *>BaseCvrs[3], False, sizeof(int[9]))
                                            for r0 in range(9):
                                                if Cands[r0][c3][Cand]:
                                                    if Cvr >= 4: break
                                                    BaseCvrs[3][r0] = True; Cvr += 1
                                            else:
                                                if Cvr < 2: continue
                                                Cvr = 0
                                                for r0 in range(9):
                                                    if BaseCvrs[0][r0] or BaseCvrs[1][r0] or BaseCvrs[2][r0] or BaseCvrs[3][r0]:
                                                        if Cvr >= 4: break
                                                        Cvrs[Cvr] = r0; Cvr += 1
                                                else:
                                                    if Cvr != 4: continue
                                                    # Jellyfish pattern found, r bases with 2 to 3 instances of cand
                                                    # TRCX(f"Fourth Base: {Cand+1}c{c3+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                                    Bases[0] = c0; Bases[1] = c1; Bases[2] = c2; Bases[3] = c3
                                                    if elim_cands_in_fish(Cand, <int *>Bases, <int *>Cvrs, COL, <int>T_JELLYFISH, Cands, Step): return 0
    return -1


cdef int tech_finned_jellyfish_c(int Grid[9][9], Step, bint Cands[9][9][9], Methods):
    cdef int r0, c0, r1, c1, r2, c2, r3, c3, Base, Cvr, Cand, lenCU, lenCS, lenCF, i, j, cu
    cdef int Method
    cdef bint BaseCvrs[4][9]
    cdef int CU[6]
    cdef int Bases[4]
    cdef int CS[6]  # needs to be large enough to collect all possilbilites.
    cdef int CF[6]

    for Cand in range(9):
        # look in rows
        for r0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for c0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr > 6: break   # 4 bases and up to 2 fins
                    BaseCvrs[0][c0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 6 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for r1 in range(r0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for c0 in range(9):
                        if Cands[r1][c0][Cand]:
                            if Cvr > 6: break
                            BaseCvrs[1][c0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # Second base with 2 to 6 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for r2 in range(r1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                            for c0 in range(9):
                                if Cands[r2][c0][Cand]:
                                    if Cvr > 6: break
                                    BaseCvrs[2][c0] = True; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # Third base with 2 to 6 instances of Cand (Base + up to 2 fins).
                                TRCX(f"Third Base: {Cand+1}r{r2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for r3 in range(r2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], False, sizeof(int[9]))
                                    for c0 in range(9):
                                        if Cands[r3][c0][Cand]:
                                            if Cvr > 6: break
                                            BaseCvrs[3][c0] = True; Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        # Fourth base with 2 to 6 instances of Cand (Base + up to 2 fins).
                                        TRCX(f"Fourth Base: {Cand+1}r{r3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        # How are the bases covered?
                                        lenCU = 0
                                        for c0 in range(9):
                                            if lenCU > 6: break
                                            if BaseCvrs[0][c0] | BaseCvrs[1][c0] | BaseCvrs[2][c0] | BaseCvrs[3][c0]: CU[lenCU] = c0; lenCU += 1
                                        else:
                                            if not 5 <= lenCU <= 6: continue  # 4 bases and 1 to 2 fins or for sashimi,  2 bases and 2 - 3 fins.
                                            Bases[0] = r0; Bases[1] = r1; Bases[2] = r2; Bases[3] = r3; lenCS = lenCF = 0
                                            for cu in range(lenCU):
                                                i = 0
                                                if Cands[r0][CU[cu]][Cand]: i += 1
                                                if Cands[r1][CU[cu]][Cand]: i += 1
                                                if Cands[r2][CU[cu]][Cand]: i += 1
                                                if Cands[r3][CU[cu]][Cand]: i += 1
                                                if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                                elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                                            sCU = ""  ### TRCX
                                            for i in range(lenCU):  ### TRCX
                                                if sCU: sCU += ", "  ### TRCX
                                                sCU += f"{CU[i]+1}"  ### TRCX
                                            sCS = ""; sCF = ""  ### TRCX
                                            for i in range(lenCS):  ### TRCX
                                                if sCS: sCS += ", "  ### TRCX
                                                sCS += f"{CS[i]+1}"  ### TRCX
                                            for i in range(lenCF):  ### TRCX
                                                if sCF: sCF += ", "  ### TRCX
                                                sCF += f"{CF[i]+1}"  ### TRCX
                                            TRCX(f"Row:  Bases: ({r0+1}, {r1+1}, {r2+1}, {r3+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                                            for Method in Methods:
                                                if ((Method & T_SASHIMI_C) and (lenCS == 3 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 4 and 1 <= lenCF <= 2)):
                                                    if elim_cands_in_finned_fish(Cand, <int *>Bases, 4, <int *>CS, lenCS, <int *>CF, lenCF, ROW, <int>Method, Cands, Step): return 0
        # look in cols
        for c0 in range(6):
            Cvr = 0
            memset(<void*> BaseCvrs[0], False, sizeof(int[9]))
            for r0 in range(9):
                if Cands[r0][c0][Cand]:
                    if Cvr > 6: break  # 4 bases and up to 2 fins
                    BaseCvrs[0][r0] = True; Cvr += 1
            else:
                if Cvr < 2: continue
                # first base found with 2 to 6 instances of Cand, look for another bases
                TRCX(f"First Base: {Cand+1}c{c0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
                for c1 in range(c0+1, 7):
                    Cvr = 0
                    memset(<void*> BaseCvrs[1], False, sizeof(int[9]))
                    for r0 in range(9):
                        if Cands[r0][c1][Cand]:
                            if Cvr > 6: break
                            BaseCvrs[1][r0] = True; Cvr += 1
                    else:
                        if Cvr < 2: continue
                        # Second base found with 2 to 6 instances of Cand (Base + up to 2 fins).
                        TRCX(f"Second Base: {Cand+1}c{c1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        for c2 in range(c1+1, 8):
                            Cvr = 0
                            memset(<void*> BaseCvrs[2], False, sizeof(int[9]))
                            for r0 in range(9):
                                if Cands[r0][c2][Cand]:
                                    if Cvr > 6: break
                                    BaseCvrs[2][r0] = True; Cvr += 1
                            else:
                                if Cvr < 2: continue
                                # Third base found  with 2 to 6 instances of Cand (Base + up to 2 fins).
                                TRCX(f"Third Base: {Cand+1}c{c2+1}: {BaseCvrs[2][0]},{BaseCvrs[2][1]},{BaseCvrs[2][2]},{BaseCvrs[2][3]},{BaseCvrs[2][4]},{BaseCvrs[2][5]},{BaseCvrs[2][6]},{BaseCvrs[2][7]},{BaseCvrs[2][8]}")
                                for c3 in range(c2+1, 9):
                                    Cvr = 0
                                    memset(<void*> BaseCvrs[3], False, sizeof(int[9]))
                                    for r0 in range(9):
                                        if Cands[r0][c3][Cand]:
                                            if Cvr > 6: break
                                            BaseCvrs[3][r0] = True;  Cvr += 1
                                    else:
                                        if Cvr < 2: continue
                                        # Fourth  base found  with 2 to 6 instances of Cand (Base + up to 2 fins).
                                        TRCX(f"Fourth Base: {Cand+1}c{c3+1}: {BaseCvrs[3][0]},{BaseCvrs[3][1]},{BaseCvrs[3][2]},{BaseCvrs[3][3]},{BaseCvrs[3][4]},{BaseCvrs[3][5]},{BaseCvrs[3][6]},{BaseCvrs[3][7]},{BaseCvrs[3][8]}")
                                        lenCU = 0
                                        for r0 in range(9):
                                            if lenCU > 6: break
                                            if BaseCvrs[0][r0] | BaseCvrs[1][r0] | BaseCvrs[2][r0] | BaseCvrs[3][r0]: CU[lenCU] = r0; lenCU += 1
                                        else:
                                            if not 5 <= lenCU <= 6: continue  # 4 bases and 1 to 2 fins.
                                            Bases[0] = c0; Bases[1] = c1; Bases[2] = c2; Bases[3] = c3; lenCS = lenCF = 0
                                            for cu in range(lenCU):
                                                i = 0
                                                if Cands[CU[cu]][c0][Cand]: i += 1
                                                if Cands[CU[cu]][c1][Cand]: i += 1
                                                if Cands[CU[cu]][c2][Cand]: i += 1
                                                if Cands[CU[cu]][c3][Cand]: i += 1
                                                if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                                elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                                            sCU = ""  ### TRCX
                                            for i in range(lenCU):  ### TRCX
                                                if sCU: sCU += ", "  ### TRCX
                                                sCU += f"{CU[i]+1}"  ### TRCX
                                            sCS = ""; sCF = ""  ### TRCX
                                            for i in range(lenCS):  ### TRCX
                                                if sCS: sCS += ", "  ### TRCX
                                                sCS += f"{CS[i]+1}"  ### TRCX
                                            for i in range(lenCF):  ### TRCX
                                                if sCF: sCF += ", "  ### TRCX
                                                sCF += f"{CF[i]+1}"  ### TRCX
                                            TRCX(f"Col: Bases: ({c0+1}, {c1+1}, {c2+1}, {c3+1}), CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                                            for Method in Methods:
                                                if ((Method & T_SASHIMI_C) and (lenCS == 3 and 2 <= lenCF <= 3)) or (not(Method & T_SASHIMI_C) and (lenCS == 4 and 1 <= lenCF <= 2)):
                                                    if elim_cands_in_finned_fish(Cand, <int*> Bases, 4, <int*> CS, lenCS, <int*> CF, lenCF, COL, <int>Method, Cands, Step): return 0
    return -1

cdef bint elim_cands_in_fish(int Cand, int *Bases, int *Cvrs, int Orient, Method, bint Cands[9][9][9], Step):
    cdef int Ord, r0, c0, Base

    if Method == T_X_WING: Ord = 2
    elif Method == T_SWORDFISH: Ord = 3
    elif Method == T_JELLYFISH: Ord = 4
    else: return False

    # TRCX(f"Elim Cands: {Cand+1}r{Bases[0]+1}{Bases[1]+1}{Bases[2]+1}c{Cvrs[0]+1}{Cvrs[1]+1}{Cvrs[2]+2}")  ### Row swordfish
    Base = 0
    if Orient == ROW:
        for r0 in range(9):
            if Base < Ord and r0 == Bases[Base]: Base += 1; continue
            for c0 in range(Ord):
                if Cands[r0][Cvrs[c0]][Cand]:
                    Cands[r0][Cvrs[c0]][Cand] = False
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, r0], [P_COL, Cvrs[c0]], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
    else:  # Orient == COL
        for c0 in range(9):
            if Base < Ord and c0 == Bases[Base]: Base += 1; continue
            for r0 in range(Ord):
                if Cands[Cvrs[r0]][c0][Cand]:
                    Cands[Cvrs[r0]][c0][Cand] = False
                    if Step.Outcome: Step.Outcome.append([P_SEP, ])
                    Step.Outcome.extend([[P_ROW, Cvrs[r0]], [P_COL, c0], [P_OP, OP_ELIM], [P_VAL, Cand+1]])
    if Step.Outcome:
        Step.Outcome.append([P_END, ])
        Step.Method = Method
        if Orient == ROW:
            if Ord == 2: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1]], [P_COL, Cvrs[0], Cvrs[1]], [P_END, ]]
            elif Ord == 3: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1], Bases[2]], [P_COL, Cvrs[0], Cvrs[1], Cvrs[2]], [P_END, ]]
            else: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, Bases[0], Bases[1], Bases[2], Bases[3]], [P_COL, Cvrs[0], Cvrs[1], Cvrs[2], Cvrs[3]], [P_END, ]]
        else:  # Orient == COL:
            if Ord == 2: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1]], [P_ROW, Cvrs[0], Cvrs[1]], [P_END, ]]
            elif Ord == 3: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1], Bases[2]], [P_ROW, Cvrs[0], Cvrs[1], Cvrs[2]], [P_END, ]]
            else: Step.Pattern = [[P_VAL, Cand+1], [P_COL, Bases[0], Bases[1], Bases[2], Bases[3]], [P_ROW, Cvrs[0], Cvrs[1], Cvrs[2], Cvrs[3]], [P_END, ]]
        return True
    return False

cdef bint elim_cands_in_finned_fish(int Cand, int *Bases, int Ord, int *CS, int lenCS,  int *CF, int lenCF, int Orient, int Method, bint Cands[9][9][9], Step):
    cdef int     b, cf, fb, r, c
    cdef COORD   Fins[3]   # up to 3 fin ccells (in sashimi)
    cdef COORD   Cvrs [18]  # up to 18 possible cvr ccells (3x6 in swordfish, 2x7=14 in x-wing, 3x5=15 in jellyfish)
    cdef int     nCvrs, nFins
    cdef RESULT  Result
    cdef CHAIN   *Chain
    cdef NODE    *N
    cdef OUTCOME *Outcome

    if Orient == ROW:
        fb = -1; nFins = 0
        for b in range(Ord):
            for cf in range(lenCF):
                if Cands[Bases[b]][CF[cf]][Cand]:
                    if not(Method & T_SASHIMI_C):  # if not Sashimi
                        if fb == -1: fb = Bases[b]     # fins can only be in one base
                        elif fb != Bases[b]: return False
                    Fins[nFins].r = Bases[b]; Fins[nFins].c = CF[cf]; nFins += 1
        b = 0; nCvrs = 0
        if Method & T_SASHIMI_C:  # For sashimi, the covers are only found along (perpendicular to) the covers of both bases and fins.
            for r in range(9):
                if b < Ord and r == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
                for c in range(lenCS):
                    if Cands[r][CS[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CS[c]; nCvrs += 1
                for c in range(lenCF):
                    if Cands[r][CF[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CF[c]; nCvrs += 1
        else:  # non sashimi fins, the covers are along (perpendicular) to the coverset values in the basesets
            for r in range(9):
                if b < Ord and r == Bases[b]: b += 1; continue  # skip over basesets (assumes ascending order)
                for c in range(lenCS):
                    if Cands[r][CS[c]][Cand]: Cvrs[nCvrs].r = r; Cvrs[nCvrs].c = CS[c]; nCvrs += 1
        St = ""   ### TRCX
        for i in range(nFins): ### TRCX
            if St: St += ", "   ### TRCX
            St += f"{Cand+1}r{Fins[i].r+1}c{Fins[i].c+1}"  ### TRCX
        St1 = ""   ### TRCX
        for i in range(nCvrs): ### TRCX
            if St1: St1 += ", "   ### TRCX
            St1 += f"{Cand+1}r{Cvrs[i].r+1}c{Cvrs[i].c+1}"  ### TRCX
        TRCX(f"Orient: Row, Fins: {St}, Cvrs: {St1}")

    else: # Orient == COL
        fb = -1; nFins = 0
        for b in range(Ord):
            for cf in range(lenCF):
                if Cands[CF[cf]][Bases[b]][Cand]:
                    if not(Method & T_SASHIMI_C):  # if not Sashimi
                        if fb == -1: fb = Bases[b]     # fins can only be in one base
                        elif fb != Bases[b]: return False
                    Fins[nFins].r = CF[cf]; Fins[nFins].c = Bases[b]; nFins += 1
        b = 0; nCvrs = 0
        if Method & T_SASHIMI_C:  # For sashimi, the covers are only found in the fins.
            for c in range(9):
                if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
                for r in range(lenCF):
                    if Cands[CF[r]][c][Cand]: Cvrs[nCvrs].r = CF[r]; Cvrs[nCvrs].c = c; nCvrs += 1
        else:  # non sashimi fins, the covers are in the coverset columns.
            for c in range(9):
                if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
                for r in range(lenCS):
                    if Cands[CS[r]][c][Cand]: Cvrs[nCvrs].r = CS[r]; Cvrs[nCvrs].c = c; nCvrs += 1
        St = ""   ### TRCX
        for i in range(nFins): ### TRCX
            if St: St += ", "   ### TRCX
            St += f"{Cand+1}r{Fins[i].r+1}c{Fins[i].c+1}"  ### TRCX
        St1 = ""   ### TRCX
        for i in range(nCvrs): ### TRCX
            if St1: St1 += ", "   ### TRCX
            St1 += f"({Cand+1},r{Cvrs[i].r+1}c{Cvrs[i].c+1}"  ### TRCX
        TRCX(f"Orient: Col, Fins: {St}, Cvrs: {St1}")

    if nCvrs:
        if Method & T_GRPLK_C:
            if not find_cover_links_to_all_fins_gl(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False
        else:
            if not find_cover_links_to_all_fins(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False
        Step.Method = Method
        BSp = []; CSp = []
        for b in range(Ord): BSp.append(Bases[b]);
        for c in range(lenCS): CSp.append(CS[c])
        if Orient == ROW: Step.Pattern = [[P_VAL, Cand+1], [P_ROW, BSp], [P_COL, CSp]]
        else: Step.Pattern = [[P_VAL, Cand+1], [P_COL, BSp], [P_ROW, CSp]]
        for fb in range(nFins): Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[fb].r], [P_COL, Fins[fb].c]])
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

cdef bint find_cover_links_to_all_fins(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
    # must free all allocated memory if returning false.
    cdef int f, c, FBcnt, FCcnt, Lk
    cdef int FinCvrLkT[3]  # max of 3 fins, for scalar (non-kraken) links
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

    # TRCX(f"&Result: 0x{<long long>&Result:016x}, Result: 0x{<long long>Result:016x}, Chain: 0x{<long long>Result.Chain:016x}, Outcome: 0x{<long long>Result.Outcome:016x}.")
    Result.Chain = Result.Outcome = Chain = Outcome = NULL
    if not(Method & T_KRAKEN_C):  # look for direct links between each cover and all the fins - for each cover.
        for c in range(nCvrs):
            for f in range(nFins):
                FinCvrLkT[f] = how_ccells_linked_c(Cvrs[c].r, Cvrs[c].c, Cand, Fins[f].r, Fins[f].c, Cand, Cands)
                TRCX(f"CvrFinLk: Cvr({Cvrs[c].r+1}, {Cvrs[c].c+1}), Fin({Fins[f].r+1}, {Fins[f].c+1}), Link: 0x{FinCvrLkT[f]:04x}")
                if FinCvrLkT[f] == LK_NONE_C: break
            else:
                #  All fins can see the cover, build the links(chains) between each fin and the cover.
                TRCX(f"Cvrs: ({Cvrs[c].r+1}, {Cvrs[c].c+1} sees all fins")
                for f in range(nFins):
                    if Chain: Chain.Next = <CHAIN *>PyMem_TRCX_Calloc(1, sizeof(CHAIN)); Chain = Chain.Next
                    else: Chain = Result.Chain = <CHAIN *>PyMem_TRCX_Calloc(1, sizeof(CHAIN))
                    Chain.Start = <NODE *>PyMem_TRCX_Calloc(1, sizeof(NODE))
                    Chain.Start.Next = <NODE *>PyMem_TRCX_Calloc(1, sizeof(NODE))
                    Chain.Start.r = Fins[f].r; Chain.Start.c = Fins[f].c; Chain.Start.Cand = Cand; Chain.Start.Lk = LK_WKST_C if FinCvrLkT[f] & LK_STRG_C else LK_WEAK_C
                    Chain.Start.Next.r = Cvrs[c].r; Chain.Start.Next.c = Cvrs[c].c; Chain.Start.Next.Cand = Cand; Chain.Start.Next.Lk = LK_NONE_C
                TRCX(f"*Chain: 0x{<long long> Chain:016x}, Chain.Start: 0x{<long long> Chain.Start:016x}, Chain.Next: 0x{<long long> Chain.Next:016x}")
                if Outcome:  Outcome.Next = <OUTCOME *>PyMem_TRCX_Calloc(1, sizeof(OUTCOME)); Outcome = Outcome.Next
                else: Outcome = Result.Outcome = <OUTCOME *>PyMem_TRCX_Calloc(1, sizeof(OUTCOME))
                Outcome.r = Cvrs[c].r; Outcome.c = Cvrs[c].c; Outcome.Op = OP_ELIM_C; Outcome.Cand = Cand
                N0 = Chain.Start  # TRCX
                C0 = Chain  # TRCX
                St = ""  # TRCX
                while C0:  # TRCX
                    if St: St += "; "  #### TRCX
                    St += f"{C0.Start.Cand+1}r{C0.Start.r+1}c{C0.Start.c+1}{OP[TKN_LK[C0.Start.Lk&7]]}{C0.Start.Next.Cand+1}r{C0.Start.Next.r+1}c{C0.Start.Next.c+1}"  ### TRCX
                    C0 = C0.Next  ### TRCX
                TRCX(f"Chain: {St}.")
                TRCX(f"&Outcome: 0x{<long long>Outcome:016x}, r{Outcome.r+1}c{Outcome.c+1}{OP[Outcome.Op]}{Outcome.Cand+1}, Next: 0x{<long long> Outcome.Next:016x}")
        TRCX(f"&Result: 0x{<long long> &Result:016x}, Result: 0x{<long long> Result:016x}, Chain: 0x{<long long> Result.Chain:016x}, Outcome: 0x{<long long> Result.Outcome:016x}.")
        return True if Result.Outcome else False
    else:  # kraken - Weakly ended chain
        # Plant a forest of TREE_FFISH CvrTrees - finned fish trees to search of chains linking all fins to a cover, all one level at a time.
        Forest = CvrTree = NULL
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
                        #     - CN0.ChildStart points ot list of children
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
                    # TRCX(f"Walk CvrTree.FinBranch[{f}]:  CvrTree: {<long long>CvrTree:016x}")
                    # climb_next_br(CvrTree.FinBranch[f], 0)
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
                    for f in range(CvrTree.nFins):
                        # if (not CvrTree.FinChain[f]) and (not CvrTree.FinBranch[f]):  CT = CvrTree; break  #  both pointers are NULL, unproductive cover tree.
                        if CvrTree.FinChain[f] and CvrTree.FinBranch[f]: TRCX_PANIC(f"0x{<long long> CvrTree:016x}, {CvrTree.Cand+1}r{CvrTree.r+1}c{CvrTree.c+1}: Only one of .FinChain[{F}] or .FinBranch[{f}] can point to chain/branch")
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
                    if CT:  break # set when CvrTree.FinChain[f] and CvrTree.FinBranch[f] are NULL - unproductive cover tree.
                    TRCX(f"Both .FinBranch[{f}] nand FinChain[{f}] Null.  Unproductive cover tree - break out of Fins loop.")
                # for f in range(CvrTree.nFins):  # for each fin (main branch) of each tree
                CvrTree = CvrTree.Next
                if CT:  # Unproductive cover tree, splice it out the forest and cull it.
                    if CT.Next: CT.Next.Prev = CT.Prev
                    if CT.Prev: CT.Prev.Next = CT.Next
                    else: Forest = CT.Next
                    cull_cover_tree(CT)
            # while CvrTree:  # for each tree in the forest
            walk_the_forest(Forest)
        # while Forest:
    # end if kraken:
    return False

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


cdef bint find_cover_links_to_all_fins_gl(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
    # Kraken is implied in the function
    return False

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

    TRCX(f"ChildN: {<long long>ChildN:016x}, Lvl: {Lvl}, CvrTree: 0x{<long long>CvrTree:016x}, Fin: {Fin}")
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
            TRCX(f"CvrTree.FinChain[{Fin}]: 0x{<long long>CvrTree.FinChain[Fin]}")
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
        TRCX(f"Lvl: {Lvl}: Culled children of 0x{<long long>CN0:016x}, ..ChainN: 0x{<long long>CN0.ChainN:016x}, culling it.")
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


