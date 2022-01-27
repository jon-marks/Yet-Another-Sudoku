#from copy import copy

from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "string.h" nogil:
    # void * memcpy(void *, void *, size_t)
    void * memset(void *, int, size_t)

include "globals.pxi"
from ctypedefs cimport *
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
    cdef bint res
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
                            if lenCU >= 4: break
                            if BaseCvrs[0][c0] | BaseCvrs[1][c0]: CU[lenCU] = c0; lenCU += 1
                        else:
                            if not 3 <= lenCU <= 4: continue  # 2 bases and 1 to 2 fins.
                            Bases[0] = r0; Bases[1] = r1; lenCS = lenCF = 0
                            for cu in range(lenCU):
                                i = 0
                                # for j in range(2):
                                #     if Cands[Bases[j]][CU[cu]][Cand]: i += 1
                                if Cands[Bases[0]][CU[cu]][Cand]: i += 1
                                if Cands[Bases[1]][CU[cu]][Cand]: i += 1
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
                            TRCX(f"CU: {sCU}; CS: {sCS}; CF: {sCF}, Methods:{Methods}")
                            for Method in Methods:
                                res = False
                                if (Method & T_SASHIMI and (lenCS == 1 and 2 <= lenCF <= 3)) or ((Method ^ T_SASHIMI) and (lenCS == 2 and 1 <= lenCF <= 2)):
                                    if elim_cands_in_finned_fish(Cand, <int *>Bases, 2, <int *>CS, lenCS, <int *>CF, lenCF, ROW, <int>Method, Cands, Step): return 0
                                    TRCX("Shouldn't get here")
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
                # TRCX(f"First Base: {Cand+1}r{r0+1}: {BaseCvrs[0][0]},{BaseCvrs[0][1]},{BaseCvrs[0][2]},{BaseCvrs[0][3]},{BaseCvrs[0][4]},{BaseCvrs[0][5]},{BaseCvrs[0][6]},{BaseCvrs[0][7]},{BaseCvrs[0][8]}")
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
                        # TRCX(f"Second Base: {Cand+1}r{r1+1}: {BaseCvrs[1][0]},{BaseCvrs[1][1]},{BaseCvrs[1][2]},{BaseCvrs[1][3]},{BaseCvrs[1][4]},{BaseCvrs[1][5]},{BaseCvrs[1][6]},{BaseCvrs[1][7]},{BaseCvrs[1][8]}")
                        lenCU = 0
                        for r0 in range(9):
                            if lenCU >= 4: break
                            if BaseCvrs[0][r0] | BaseCvrs[1][r0]: CU[lenCU] = r0; lenCU += 1
                        else:
                            if not 3 <= lenCU <= 4: continue  # 2 bases and 1 to 2 fins.
                            Bases[0] = c0; Bases[1] = c1; lenCS = lenCF = 0
                            for cu in range(lenCU):
                                i = 0
                                # for j in range(Ord):
                                #     if Cands[CU[cu]][Bases[j]][Cand]: i += 1
                                if Cands[CU[cu]][Bases[0]][Cand]: i += 1
                                if Cands[CU[cu]][Bases[1]][Cand]: i += 1
                                if i == 1: CF[lenCF] = CU[cu]; lenCF += 1
                                elif i >= 2: CS[lenCS] = CU[cu]; lenCS += 1
                            for Method in Methods:
                                res = False
                                if (Method & T_SASHIMI and (lenCS == 1 and 2 <= lenCF <= 3)) or ((Method ^ T_SASHIMI) and (lenCS == 2 and 1 <= lenCF <= 2)):
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
    cdef NODE_GL *Ngl
    cdef OUTCOME *Outcome

    if Orient == ROW:
        fb = -1; nFins = 0
        for b in range(Ord):
            for cf in range(lenCF):
                if Cands[Bases[b]][CF[cf]][Cand]:
                    if Method ^ T_SASHIMI:  # if not Sashimi
                        if fb == -1: fb = Bases[b]     # fins can only be in one base
                        elif fb != Bases[b]: return False
                    Fins[nFins].r = Bases[b]; Fins[nFins].c = CF[cf]; nFins += 1
        b = 0; nCvrs = 0
        if Method & T_SASHIMI:  # For sashimi, the covers are only found along (perpendicular to) the fins.
            for r in range(9):
                if b < Ord and r == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
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
            St += f"({Fins[i].r+1}, {Fins[i].c+1})"  ### TRCX
        St1 = ""   ### TRCX
        for i in range(nCvrs): ### TRCX
            if St1: St1 += ", "   ### TRCX
            St1 += f"({Cvrs[i].r+1}, {Cvrs[i].c+1})"  ### TRCX
        TRCX(f"Orient: Row, Fins: {St}, Cvrs: {St1}")

    else: # Orient == COL
        fb = -1; nFins = 0
        for b in range(Ord):
            for cf in range(lenCF):
                if Cands[CF[cf]][Bases[b]][Cand]:
                    if Method ^ T_SASHIMI:  # if not Sashimi
                        if fb == -1: fb = Bases[b]     # fins can only be in one base
                        elif fb != Bases[b]: return False
                    Fins[nFins].r = CF[cf]; Fins[nFins].c = Bases[b]; nFins += 1
        b = 0; nCvrs = 0
        if Method & T_SASHIMI:  # For sashimi, the covers are only found in the fins.
            for c in range(9):
                if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
                for r in range(lenCF):
                    if Cands[CF[r]][c][Cand]: Cvrs[nCvrs].r = CF[r]; Cvrs[nCvrs].c = c; nCvrs += 1
        else:  # non sashimi fins, the covers are in the coverset columns.
            for c in range(9):
                if b < Ord and c == Bases[b]: b += 1; continue  # skip over baseset rows (assumes ascending order)
                for r in range(lenCS):
                    if Cands[CS[r]][c][Cand]: Cvrs[nCvrs].r = CS[r]; Cvrs[nCvrs].c = c; nCvrs += 1
    if nCvrs:
        if Method & T_GRPLK:
            if not find_cover_links_to_all_fins_gl(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False
        else:
            if not find_cover_links_to_all_fins(<COORD *>Fins, nFins, <COORD *>Cvrs, nCvrs, Cand, Cands, Method, &Result): return False

        Step.Method = Method
        BSp = []; CSp = []
        for b in range(Ord): BSp.append(Bases[b]);
        for c in range(lenCS): CSp.append(CS[c])
        if Orient == ROW: Step.Pattern = [[P_VAL, Cand], [P_ROW, BSp], [P_COL, CSp]]
        else: Step.Pattern = [[P_VAL, Cand], [P_ROW, CSp], [P_COL, BSp]]
        for fb in range(nFins): Step.Pattern.extend([[P_CON, ], [P_ROW, Fins[fb].r], [P_COL, Fins[fb].c]])
        if Method & T_GRPLK:
            Chain = Result.Chain
            while 1:
                Step.Pattern.append([P_SEP, ])
                Ngl = Chain.StartGL
                while 1:
                    R = []; C = []
                    for i in range(Ngl.r.l): R.append(Ngl.r.v[i])
                    for i in range(Ngl.c.l): C.append(Ngl.c.v[i])
                    Step.NrLks += 1
                    if Ngl.r.l > 1 or Ngl.c.l > 1: Step.NrGrpLks += 1
                    Step.Pattern.extend([[P_VAL, Ngl.Cand+1], [P_ROW, R], [P_COL, C], [P_OP, token_link_c(Ngl.Lk)]])
                    if Ngl.Next: Ngl = Ngl.Next; PyMem_TRCX_Free(Ngl.Prev)
                    else: PyMem_TRCX_Free(Ngl); break
                if Chain.Next: Chain = Chain.Next; PyMem_TRCX_Free(Chain.Prev)
                else: PyMem_TRCX_Free(Chain); break
        else:  # normal scalar links, not group links.
            Chain = Result.Chain
            TRCX(f"&Result: 0x{<long long>&Result:016x}, Result.Chain: 0x{<long long> Result.Chain:016x}, Result.Outcome: 0x{<long long> Result.Outcome:016x}.")
            TRCX(f"&Chain: 0x{<long long> &Chain:016x},*Chain: 0x{<long long>Chain:016x}, Chain.Start: 0x{<long long>Chain.Start:016x}, Chain.End: 0x{<long long>Chain.End:016x}, Chain.Prev: 0x{<long long>Chain.Prev:016x}, Chain.Next: 0x{<long long>Chain.Next:016x}")
            while 1:
                Step.Pattern.append([P_SEP, ])
                N = Chain.Start
                while 1:
                    Step.NrLks += 1
                    St = f"&N: 0x{<long long> &N:016x}, N: 0x{<long long> N:016x}, N: {N.Cand+1}r{N.r+1}c{N.c+1}{OP[token_link_c(N.Lk)]}, N.Prev: 0x{<long long>N.Prev:016x}, N.Next: 0x{<long long>N.Next:016x}"
                    TRCX(St)
                    Step.Pattern.extend([[P_VAL, N.Cand+1], [P_ROW, N.r], [P_COL, N.c], [P_OP, token_link_c(N.Lk)]])
                    if N.Next: N = N.Next; PyMem_TRCX_Free(N.Prev)
                    else: PyMem_TRCX_Free(N); break
                if Chain.Next: Chain = Chain.Next; PyMem_TRCX_Free(Chain.Prev)
                else: PyMem_TRCX_Free(Chain); break
        Step.Pattern.append([P_END, ])
        St = tkns_to_str(Step.Pattern)  # TRCX
        TRCX(f"Pattern: {St}")
        Outcome = Result.Outcome
        while 1:
            Cands[Outcome.r][Outcome.c][Outcome.Cand] = False
            if Step.Outcome: Step.Outcome.append([P_SEP, ])
            Step.Outcome.extend([[P_ROW, Outcome.r], [P_COL, Outcome.c], [P_OP, Outcome.Op], [P_VAL, Outcome.Cand+1]])
            if Outcome.Next: Outcome = Outcome.Next; PyMem_TRCX_Free(Outcome.Prev)
            else: PyMem_TRCX_Free(Outcome); break
        Step.Outcome.append([P_END, ])
        St = tkns_to_str(Step.Outcome)  ### TRCX
        TRCX(f"Outcome: {St}")
        return True
    return False

cdef bint find_cover_links_to_all_fins(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
    # must free all allocated memory if returning false.
    cdef int f, c
    cdef int FinCvrLkT[3]  # max of 3 fins
    cdef CHAIN *Chain
    cdef OUTCOME *Outcome
    cdef NODE *N0 = NULL
    cdef NODE *N1 = NULL

    TRCX(f"&N0: 0x{<long long>&N0:016x}, &N1: 0x{<long long>&N1:016x}")
    TRCX(f"&Result: 0x{<long long>&Result:016x}, Result: 0x{<long long>Result:016x}, Chain: 0x{<long long>Result.Chain:016x}, Outcome: 0x{<long long>Result.Outcome:016x}.")
    Result.Chain = Result.Outcome = Chain = Outcome = NULL
    if Method ^ T_KRAKEN:  # look for direct links between each cover and all the fins - for each cover.
        for c in range(nCvrs):
            for f in range(nFins):
                FinCvrLkT[f] = how_ccells_linked_c(Cvrs[c].r, Cvrs[c].c, Cand, Fins[f].r, Fins[f].c, Cand, Cands)
                TRCX(f"CvrFinLk: Cvr({Cvrs[c].r+1}, {Cvrs[c].c+1}), Fin({Fins[f].r+1}, {Fins[f].c+1}), Link: 0x{FinCvrLkT[f]:04x}")
                if FinCvrLkT[f] == LK_NONE_C: break
            else:
                #  All fins see the cover, build the links(chains) between each fin and the cover.
                for f in range(nFins):
                    N0 = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE))
                    N1 = <NODE *>PyMem_TRCX_Malloc(sizeof(NODE))
                    N0.r = Fins[f].r; N0.c = Fins[f].c; N0.Cand = Cand; N0.Lk = LK_WKST_C if FinCvrLkT[f] & LK_STRG_C else LK_WEAK_C
                    N1.r = Cvrs[c].r; N1.c = Cvrs[c].c; N1.Cand = Cand; N1.Lk = LK_NONE_C
                    N0.Prev = N1.Next = NULL; N0.Next = N1; N1.Prev = N0
                    TRCX(f"&N0: 0x{<long long>&N0:016x}, N0: 0x{<long long>N0:016x}, N0:{N0.Cand+1}r{N0.r+1}c{N0.c+1}, LK: 0x{N0.Lk:04x}, Prev: 0x{<long long>N0.Prev:016x}, Next: 0x{<long long>N0.Next:016x}")
                    TRCX(f"&N1: 0x{<long long>&N1:016x}, N0: 0x{<long long>N0:016x}, N1:{N1.Cand+1}r{N1.r+1}c{N1.c+1}, LK: 0x{N1.Lk:04x}, Prev: 0x{<long long>N1.Prev:016x}, Next: 0x{<long long>N1.Next:016x}")
                    if Chain:
                        Chain.Next = <CHAIN *>PyMem_TRCX_Malloc(sizeof(CHAIN))
                        Chain.Next.Prev = Chain; Chain.Next = NULL
                    else: # first chain in the chain list off Result.Chain
                        Chain = <CHAIN *>PyMem_TRCX_Malloc(sizeof(CHAIN))
                        Chain.Prev = Chain.Next = NULL
                    Chain.Start = N0; Chain.End = N1
                TRCX(f"&Chain: 0x{<long long> &Chain:016x},*Chain: 0x{<long long> Chain:016x}, Chain.Start: 0x{<long long> Chain.Start:016x}, Chain.End: 0x{<long long> Chain.End:016x}, Chain.Prev: 0x{<long long> Chain.Prev:016x}, Chain.Next: 0x{<long long> Chain.Next:016x}")
                N0 = Chain.Start  # TRCX
                St = ""  # TRCX
                while 1:  # TRCX
                    if N0.Next: St += f"{N0.Cand+1}r{N0.r+1}c{N0.c+1}{OP[token_link_c(N0.Lk)]}"; N0 = N0.Next; continue  # TRCX
                    else: St += f"{N0.Cand+1}r{N0.r+1}c{N0.c+1}"; break  # TRCX
                TRCX(f"Chain: {St}.")
                if not Result.Chain: Result.Chain = Chain
                # And note cover to eliminate in the outcome.
                if Outcome:
                    Outcome.Next = <OUTCOME *>PyMem_TRCX_Malloc(sizeof(OUTCOME))
                    Outcome.Next.Prev = Outcome; Outcome.Next = NULL
                else:
                    Outcome = <OUTCOME *>PyMem_TRCX_Malloc(sizeof(OUTCOME))
                    Outcome.Prev = Outcome.Next = NULL
                Outcome.r = Cvrs[c].r; Outcome.c = Cvrs[c].c; Outcome.Op = OP_ELIM; Outcome.Cand = Cand
                if not Result.Outcome: Result.Outcome = Outcome
                TRCX(f"&Outcome: 0x{<long long>Outcome:016x}, r{Outcome.r+1}c{Outcome.c+1}{OP[Outcome.Op]}{Outcome.Cand+1}, Prev: 0x{<long long> Chain.Prev:016x}, Next: 0x{<long long> Chain.Next:016x}")
        TRCX(f"&Result: 0x{<long long> &Result:016x}, Result: 0x{<long long> Result:016x}, Chain: 0x{<long long> Result.Chain:016x}, Outcome: 0x{<long long> Result.Outcome:016x}.")
        if Result.Outcome: return True
    else:  # kraken - Weakly ended chain
        # stubbed out
        pass
    return False

cdef bint find_cover_links_to_all_fins_gl(COORD *Fins, int nFins, COORD *Cvrs, int nCvrs, int Cand, bint Cands[9][9][9], int Method, RESULT *Result):
    # Kraken is implied in the function
    return False


# def _finned_x_wings(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
#     # The same holds true for columns instead of rows. That is the base sets are
#     # in the columns and the cover sets in the rows.
#
#     # A Finned X-Wing occurs when only one of the base sets has more (than two)
#     # occurrences of the candidate outside of the cover set.  A finned
#     # fish has an extra appendage or two of the same candidate called fins.
#     # Only those candidates in the cover sets that are not part of the
#     # X-Wing that "see" (are peers of the) fin candidates can be eliminated.
#
#     for Cand in range(1, 10):
#         # look at rows
#         BC = [set() for i in range(9)]
#         for r in range(9):
#             for c in range(9):
#                 if Cand in Cands[r][c]: BC[r].add(c)
#         for r0 in range(8):  # looking for base sets with two bases and zero, one or two fins.
#             if not 2 <= len(BC[r0]) <= 4: continue
#             for r1 in range(r0+1, 9):
#                 if not 2 <= len(BC[r1]) <= 4: continue
#                 CU = sorted(BC[r0] | BC[r1])
#                 # A valid union CU is either 2 cover sets and 1 or 2 fins, or 1 cover and 2 or 3 fins.
#                 lenCU = len(CU)
#                 if not 3 <= lenCU <= 4: continue
#                 BS = [r0, r1]; CS = []; CF = []
#                 for cu in CU:
#                     bi = 0
#                     for bs in BS:
#                         if Cand in Cands[bs][cu]: bi +=1
#                     if bi == 1: CF.append(cu)
#                     elif bi == 2: CS.append(cu)
#                 if (len(CS) == 2 and 1 <= len(CF) <= 2) or (len(CS) == 1 and 2 <= len(CF) <= 3):
#                     if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
#         # look at cols
#         BC = [set() for i in range(9)]
#         for c in range(9):
#             for r in range(9):
#                 if Cand in Cands[r][c]: BC[c].add(r)
#         for c0 in range(8):
#             if not 2 <= len(BC[c0]) <= 4: continue
#             for c1 in range(c0+1, 9):
#                 if not 2 <= len(BC[c1]) <= 4: continue
#                 CU = sorted(BC[c0] | BC[c1])
#                 # A valid union CU is either 2 cover sets and 1 or 2 fins, or 1 cover and 2 or 3 fins.
#                 lenCU = len(CU)
#                 if not 3 <= lenCU <= 4: continue
#                 BS = [c0, c1]; CS = []; CF = []
#                 for cu in CU:
#                     bi = 0
#                     for bs in BS:
#                         if Cand in Cands[cu][bs]: bi +=1
#                     if bi == 1: CF.append(cu)
#                     elif bi == 2: CS.append(cu)
#                 if (len(CS) == 2 and 1 <= len(CF) <= 2) or (len(CS) == 1 and 2 <= len(CF) <= 3):
#                     if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
#     return -1
#
# def _finned_swordfish(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
#     # TODO Need to update this description.  A Swordfish occurs when the same candidate occurs only 2 or 3 times
#     # in three separate rows (base sets)and at least two of the candidates are
#     # aligned in the associated columns (cover sets).  Here the candidate can be
#     # eliminated from other rows along the associated columns.  This algorithm
#     # relies on the union of the cover set being exactly three columns which
#     # defines the Swordfish pattern. In each of the three columns, where the
#     # candidate is present in at least one of the base set rows, the candidate,
#     # if present in the remaining non base set rows can be eliminated.
#     #
#     # Base sets can also be columns and cover sets, rows - to find column wise
#     # Swordfish
#
#     for Cand in range(1, 10):
#         # look at rows
#         BC = [set() for i in range(9)]
#         for r in range(9):
#             for c in range(9):
#                 if Cand in Cands[r][c]: BC[r].add(c)
#         for r0 in range(7):  # looking for bases with btwn two and three bases and btwn zero and two fins
#             if not 2 <= len(BC[r0]) <= 5: continue
#             for r1 in range(r0+1, 8):
#                 if not 2 <= len(BC[r1]) <= 5: continue
#                 for r2 in range(r1+1, 9):
#                     if not 2 <= len(BC[r2]) <= 5: continue
#                     CU = sorted(BC[r0] | BC[r1] | BC[r2])
#                     # A valid union CU is 3 cover sets and 1 or 2 fins.
#                     lenCU = len(CU)
#                     if not 4 <= lenCU <= 5: continue
#                     BS = [r0, r1, r2]; CS = []; CF = []
#                     for cu in CU:
#                         bi = 0
#                         for bs in BS:
#                             if Cand in Cands[bs][cu]: bi += 1
#                         if bi == 1: CF.append(cu)
#                         elif bi >= 2: CS.append(cu)
#                     if (len(CS) == 3 and 1 <= len(CF) <= 2) or (len(CS) == 2 and 2 <= len(CF) <= 3):
#                         if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
#         # look at cols
#         BC = [set() for i in range(9)]
#         for c in range(9):
#             for r in range(9):
#                 if Cand in Cands[r][c]: BC[c].add(r)
#         for c0 in range(7):
#             if not 2 <= len(BC[c0]) <= 5: continue
#             for c1 in range(c0+1, 8):
#                 if not 2 <= len(BC[c1]) <= 5: continue
#                 for c2 in range(c1+1, 9):
#                     if not 2 <= len(BC[c2]) <= 5: continue
#                     CU = sorted(BC[c0] | BC[c1] | BC[c2])
#                     # A valid union CU is either 3 cover sets and 1 or 2 fins, or 2 cover and 2 or 3 fins.
#                     lenCU = len(CU)
#                     if not 4 <= lenCU <= 5: continue
#                     BS = [c0, c1, c2]; CS = []; CF = []
#                     for cu in CU:
#                         bi = 0
#                         for bs in BS:
#                             if Cand in Cands[cu][bs]: bi += 1
#                         if bi == 1: CF.append(cu)
#                         elif bi >= 2: CS.append(cu)
#                     if (len(CS) == 3 and 1 <= len(CF) <= 2) or (len(CS) == 2 and 2 <= len(CF) <= 3):
#                         if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
#     return -1
#
# def _finned_jellyfish(Grid, Step, Cands, Method, Kraken = False, GrpLks = False):
#     # AIC == 0:  only look for a weak link between the ccells.
#     # AIC == 1:  only look for a weak link and between the ccells or the
#     #            ccells "see" a strong link
#     # AIC == 2:  weak link, "see" a strong link or weak-ended-AIC.
#
#     for Cand in range(1, 10):
#         # look at rows
#         BC = [set() for i in range(9)]
#         for r in range(9):
#             for c in range(9):
#                 if Cand in Cands[r][c]: BC[r].add(c)
#         for r0 in range(6):
#             if len(BC[r0]) < 2: continue
#             for r1 in range(r0+1, 7):
#                 if len(BC[r1]) < 2: continue
#                 for r2 in range(r1+1, 8):
#                     if len(BC[r2]) < 2: continue
#                     for r3 in range(r2+1, 9):
#                         if len(BC[r3]) < 2: continue
#                         CU = sorted(BC[r0] | BC[r1] | BC[r2] | BC[r3])
#                         # A valid union CU is 4 cover sets and 1 or 2 fins.
#                         # Multiple fins must be in the same block for non-Kraken finned fish
#                         lenCU = len(CU)
#                         BS = [r0, r1, r2, r3]
#                         if lenCU == 5:  # 4 cover sets and 1 fin
#                             CI = [0, 0, 0, 0, 0]  # Cover intersections
#                             for ci, cu in enumerate(CU):
#                                 for bs in BS:
#                                     if Cand in Cands[bs][cu]: CI[ci] += 1
#                             for cx in range(4, -1, -1):
#                                 CS = CU.copy(); del CS[cx]
#                                 CF = [CU[cx]]          # cover fin
#                                 for cs in CS:
#                                     # if the cover set is in the same chute as the fins, then it is permitted one or
#                                     # more intersections with base sets, else it must have two or more intersections with
#                                     # base sets.
#                                     if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
#                                         break
#                                 else:  # a valid finned fish pattern, what can be eliminated?
#                                     if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
#                         elif lenCU == 6:  # 4 cover sets and 2 fins.
#                             CI = [0, 0, 0, 0, 0, 0]  # Cover intersections
#                             for ci, cu in enumerate(CU):
#                                 for bs in BS:
#                                     if Cand in Cands[bs][cu]: CI[ci] += 1
#                             for cx0 in range(5, 0, -1):
#                                 cb0 = CU[cx0]//3
#                                 for cx1 in range(cx0-1, -1, -1):
#                                     cb1 = CU[cx1]//3
#                                     if cb0 != cb1: continue  # Fins must be in same cover chute.
#                                     CS = CU.copy(); del CS[cx0]; del CS[cx1]
#                                     CF = [CU[cx0], CU[cx1]]
#                                     for cs in CS:
#                                         # if the cover set is in the same chute as the fins, then it is permitted one or
#                                         # more intersections with base sets, else it must have two or more intersections with
#                                         # base sets.
#                                         if CI[CU.index(cs)] < 2 and not (cs//3 == cb0 == cb1):  # only one cover set intersection and not in same cover chute as fin
#                                             break
#                                     else:  # a valid finned fish pattern, what can be eliminated
#                                         if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_ROW, Cands, Step, Method, Kraken, GrpLks): return 0
#         # look at cols
#         BC = [set() for i in range(9)]
#         for c in range(9):
#             for r in range(9):
#                 if Cand in Cands[r][c]: BC[c].add(r)
#         for c0 in range(6):
#             if len(BC[c0]) < 2: continue
#             for c1 in range(c0+1, 7):
#                 if len(BC[c1]) < 2: continue
#                 for c2 in range(c1+1, 8):
#                     if len(BC[c2]) < 2: continue
#                     for c3 in range(c2+1, 9):
#                         if len(BC[c3]) < 2: continue
#                         CU = sorted(BC[c0] | BC[c1] | BC[c2] | BC[c3])
#                         # A valid union CU is 4 cover sets and 1 or 2 fins.
#                         # Multiple fins must be in the same block for non-Kraken finned fish
#                         lenCU = len(CU)
#                         BS = [c0, c1, c2, c3]
#                         if lenCU == 5:
#                             CI = [0, 0, 0, 0, 0]  # Cover intersections
#                             for ci, cu in enumerate(CU):
#                                 for bs in BS:
#                                     if Cand in Cands[cu][bs]: CI[ci] += 1
#                             for cx in range(4, -1, -1):
#                                 CS = CU.copy(); del CS[cx]
#                                 CF = [CU[cx]]          # cover fin
#                                 for cs in CS:
#                                     # if the cover set is in the same chute as the fins, then it is permitted one or
#                                     # more intersections with base sets, else it must have two or more intersections with
#                                     # base sets.
#                                     if CI[CU.index(cs)] < 2 and cs//3 != cx//3:  # only one cover set intersection and not in same cover chute as fin
#                                         break
#                                 else:  # a valid finned fish pattern, what can be eliminated?
#                                     if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
#                         elif lenCU == 6:
#                             CI = [0, 0, 0, 0, 0, 0]  # Cover intersections
#                             for ci, cu in enumerate(CU):
#                                 for bs in BS:
#                                     if Cand in Cands[cu][bs]: CI[ci] += 1
#                             for cx0 in range(5, 0, -1):
#                                 cb0 = cx0//3
#                                 for cx1 in range(cx0-1, -1, -1):
#                                     cb1 = CU[cx1]//3
#                                     if cb0 != cb1: continue  # Fins must be in same cover chute.
#                                     CS = CU.copy(); del CS[cx0]; del CS[cx1]
#                                     CF = [CU[cx0], CU[cx1]]
#                                     for cs in CS:
#                                         # if the cover set is in the same chute as the fins, then it is permitted one or
#                                         # more intersections with base sets, else it must have two or more intersections with
#                                         # base sets.
#                                         if CI[CU.index(cs)] < 2 and not (cs//3 == cx0//3 == cx1//3):  # only one cover set intersection and not in same cover chute as fin
#                                             break
#                                     else:  # a valid finned fish pattern, what can be eliminated
#                                         if _elim_cands_in_finned_fish(Cand, BS, CS, CF, P_COL, Cands, Step, Method, Kraken, GrpLks): return 0
#     return -1
#
# # todo: tech_franken_swordfish
# # todo: tech_franken_jellyfish
#
# def _elim_cands_in_finned_fish(Cand, BS, CS, CF, rc, Cands, Step, Method, Kraken = False, GrpLks = False):
#
#     Fins = []
#     Cvrs = []
#     S = STATUS()
#     Ord = len(BS)
#     FB = set()
#     if rc == P_ROW:
#         for r in BS:
#             for c in CF:
#                 if Cand in Cands[r][c]: Fins.append((r, c)), FB.add(r)
#         if len(FB) > 1 and len(CS) == Ord: return False  # Fins can only be in in one base unless sashimi
#         for r in sorted(set(range(9)) - set(BS)):
#             for c in CS if len(CS) == Ord else [*CS, *CF]:
#                 if Cand in Cands[r][c]: Cvrs.append((r, c))
#         if len(Cvrs): _find_cover_that_sees_all_fins(Fins, Cvrs, Cand, Cands, Kraken, GrpLks, S)
#     else:  # rc == P_COL:
#         for c in BS:
#             for r in CF:
#                 if Cand in Cands[r][c]: Fins.append((r, c)), FB.add(c)
#         if len(FB) > 1 and len(CS) == Ord: return False  # Fins can only be in in one base unless sashimi
#         for c in sorted(set(range(9))-set(BS)):
#             for r in CS if len(CS) == Ord else [*CS, *CF]:
#                 if Cand in Cands[r][c]: Cvrs.append((r, c))
#         if len(Cvrs): _find_cover_that_sees_all_fins(Fins, Cvrs, Cand, Cands, Kraken, GrpLks, S)
#     if S.Tech != T_UNDEF:
#         if Ord == 2: Step[P_TECH] = T_FINNED_X_WING
#         elif Ord == 3: Step[P_TECH] = T_FINNED_SWORDFISH
#         elif Ord == 4: Step[P_TECH] = T_FINNED_JELLYFISH
#         if Kraken:
#             for Ch in S.Pattern:
#                 if len(Ch) > 2: Step[P_TECH] |= T_KRAKEN; break
#         if GrpLks: Step[P_TECH] |= T_GRPLK
#
#         if rc == P_ROW: Step[P_PTRN] = [[P_VAL, Cand], [P_ROW, BS], [P_COL, CS]]
#         else: Step[P_PTRN] = [[P_VAL, Cand], [P_COL, BS], [P_ROW, CS]]  # rc == P_COL
#         for r, c in sorted(Fins): Step[P_PTRN].extend([[P_CON, ], [P_ROW, r], [P_COL, c]])
#         Step[P_PTRN].append([P_SEP, ])
#         NLks = NGrpLks = 0
#         Chains = []
#         for Ch in S.Pattern:  # one chain for each fin in S.Pattern
#             # for Ch in Chs:
#             if Chains: Chains.append([P_SEP, ])
#             for r, c, Cand, Lk, in Ch:
#                 NLks += 1
#                 if not isinstance(r, int) and len(r) > 1: NGrpLks += 1
#                 if not isinstance(c, int) and len(c) > 1: NGrpLks += 1
#                 if Lk == LK_NONE: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c]])
#                 else: Chains.extend([[P_VAL, Cand], [P_ROW, r], [P_COL, c], [P_OP, token_link(Lk)]])
#         Step[P_PTRN].extend(Chains); Step[P_PTRN].append([P_END, ])
#         Step[P_DIFF] = T[Step[P_TECH]][T_DIFF]+(NLks-NGrpLks)*LK_DIFF+NGrpLks*GRP_LK_DIFF
#         for r, c, Cand in S.Outcome:
#             Cands[r][c].discard(Cand)
#             if Step[P_OUTC]: Step[P_OUTC].append([P_SEP, ])
#             Step[P_OUTC].extend([[P_ROW, r], [P_COL, c], [P_OP, OP_ELIM], [P_VAL, Cand]])
#         Step[P_OUTC].append([P_END, ])
#         return True
#     return False
#
# class TREE:
#     def __init__(self, Root = None, Chains = None, Outcome = None, Found = False, BottomedOut = False):
#         self.Root = Root
#         self.Chains = Chains if Chains else []
#         self.Outcome = Outcome if Outcome else []
#         self.Found = Found
#         self.BottomedOut = BottomedOut
#
# def _find_cover_that_sees_all_fins(Fins, Covers, Cand, Cands, Kraken, GrpLks, Status):
#     # Finds covers that see fins by building trees (one for each cover) that grow branches which are
#     # the alternating links to next nodes until the tree links to both fins.  This algorithm builds
#     # all trees simultaneously growing a level of branches for all trees before attempting the next
#     # level.
#     #
#     # Fins:     A list of (r, c) cell coord tuples that contain Cand, that any cover must see all of
#     #           to be eliminated.
#     # Covers:   A list of (r, c) cell coord tuples that contain Cand, from which Cand can be
#     #           eliminated if it sees all fins.
#     # Cand:     The specific candidate value for eliminations
#     # Cands:    The Candidate grid.
#     # Kraken:   If True then looking for connecting chains, else just direct links.
#     # GrpLks:   If True looking for connecting chains with group links.  Not used if Kraken is false
#     # Status:   If eliminations are found, returns the found pattern and outcome.
#     #           Tech != T_UNDEF if pattern found - does not indicate which pattern.
#     #           Instance of STATUS() class.
#
#
#     if not Kraken:  # GrpLks always False when Kraken is False
#         # Find all covers that can be eliminated as not very expensive for non kraken to find
#         for rc, cc in Covers:
#             FP = []  # [] for i in len(Fins)]
#             for rf, cf in Fins:
#                 LkT, LkH = how_ccells_linked(rc, cc, Cand, rf, cf, Cand, Cands, False)
#                 if LkT == LK_NONE: break
#                 FP.append([(rc, cc, Cand, LK_WKST if LkT & LK_STRG else LK_WEAK), (rf, cf, Cand, LK_NONE)])
#             else:  # A cover that sees all the fins has been found.
#                 Status.Tech = 0
#                 Status.Pattern = FP
#                 Status.Outcome.append((rc, cc, Cand))
#     else:  # Kraken
#         # For Kraken, any cover that can see all fins can be eliminated.
#         # Find only first cover that can be eliminated as building chains is expensive.
#         # Builds an Orchard of trees, each tree being a cover, growing branches to build chains to
#         # fins.  The first cover to build chains to all the fins wins.  Algorithm grows the branches
#         # one level at a time for all trees before moving onto the next level.
#
#         # Algorithm only arrives here when no cover can see all fins directly.
#         Orchard = []; Idx = []
#         Tree = None
#         if GrpLks:  # Kraken group links.
#             Fins = [({r}, {c}, Cand) for r, c in Fins]
#             for i, (rc, cc) in enumerate(Covers):
#                 Tree = TREE(TNODE({rc}, {cc}, Cand, None, None, None, None), [[] for i in Fins], None, False, False)
#                 for r, c, Cand, LkT, LkH in list_ccells_linked_to({rc}, {cc}, Cand, Cands, LK_STWK, GrpLks):
#                     for j, (rf, cf, Candf) in enumerate(Fins):
#                         if ccells_match(r, c, Cand, rf, cf, Candf, GrpLks):
#                             Tree.Chains[j] = [({rc}, {cc}, Cand, LK_WKST if LkT == LK_STWK else LK_WEAK), (r, c, Cand, LK_NONE)]
#                     else:
#                         if LkT == LK_WEAK:
#                             Tree.Root.Children.append(TNODE(r, c, Cand, LK_WEAK, [(Tree.Root.r, Tree.Root.c, Tree.Root.Cand, LK_WEAK)], Tree, None))
#                         else:
#                             Tree.Root.Children.append(TNODE(r, c, Cand, LK_WKST, [(Tree.Root.r, Tree.Root.c, Tree.Root.Cand, LK_WKST)], Tree, None))
#                 Orchard.append(Tree)
#                 Idx.append(i)
#         else:  # kraken, non group links.
#             Fins = [(r, c, Cand) for r, c in Fins]
#             for i, (rc, cc) in enumerate(Covers):
#                 # Orchard.append(TREE(TNODE(rc, cc, Cand, None, None, None, None), [[] for i in Fins]))
#                 # # Orchard.append(TNODE(rc, cc, Cand, None, None, None, None))
#                 # Idx.append(i)
#                 Tree = TREE(TNODE(rc, cc, Cand, None, None, None, None), [[] for i in Fins], None, False, False)
#                 # UC = []
#                 for r0, c0, Cand0, LkT, LkH in list_ccells_linked_to(rc, cc, Cand, Cands, LK_STWK, GrpLks):
#                     # if (r0, c0, Cand0) in UC: continue
#                     if (r0, c0, Cand0) in Fins:
#                         Tree.Chains[Fins.index((r0, c0, Cand0))] = [(rc, cc, Cand, LK_WKST if LkT == LK_STWK else LK_WEAK), (r0, c0, Cand0, LK_NONE)]
#                     else:
#                         if LkT == LK_WEAK:
#                             Tree.Root.Children.append(TNODE(r0, c0, Cand0, LK_WEAK, [(rc, cc, Cand, LK_WEAK)], Tree.Root, None))
#                         else:
#                             # Tree.Root.Children.append(TNODE(r0, c0, Cand0, LK_STRG, [(rc, cc, Cand, LK_STRG)], Tree.Root, None))
#                             Tree.Root.Children.append(TNODE(r0, c0, Cand0, LK_WKST, [(rc, cc, Cand, LK_WKST)], Tree.Root, None))
#                 # add tree to orchard even if there are direct links from the cover to all the fins.  The duty of the algorithm
#                 # is to find a Kraken fish, not resort to a Finned Fish if one is found.
#                 Orchard.append(Tree)
#                 Idx.append(i)
#
#         while Idx:
#             # A Tree is removed from the orchard when none of its branches/Children are able to form chains to all fins
#             # While there are CvrTrees in the orchard, there is hope of finding a chain in remaining cover trees
#             # that can yield eliminations.
#
#             for i, Tree in enumerate(Orchard):
#                 if Tree.Root.Children:
#                     Tree.Root.Children = _find_next_branches(Tree.Root.Children, Fins, Cands, GrpLks, 1, Tree)
#                     if Tree.Found:
#                         Status.Tech = T_KRAKEN
#                         Status.Pattern = Tree.Chains
#                         Status.Outcome = Tree.Outcome
#                         return
#                 if not Tree.Root.Children and i in Idx: Idx.remove(i)
#
# def _find_next_branches(Children, Fins, Cands, GrpLks, Lvl, Tree):
#     # The recursing function which builds the next level of branch for a tree returns with Status filled
#     # if it has found a cover that sees all fins.  Pruning is acheived by not copying a child branch from
#     # the Children list into the Kids list.
#
#     if Lvl > RECURSE_LIM:
#         Tree.BottomedOut = True
#         return Children
#
#     Kids = []
#     for C in Children:
#         if C.Children:  # Recurse down the children
#             C.Children = _find_next_branches(C.Children, Fins, Cands, GrpLks, Lvl+1, Tree)
#             if Tree.Found or Tree.BottomedOut: return Children
#         else:
#             UC = []
#             for r, c, Cand, LkT, LkH in list_ccells_linked_to(C.r, C.c, C.Cand, Cands, LK_STWK if C.Lk == LK_STRG else LK_STRG, GrpLks):
#                 if (r, c, Cand) in UC: continue
#                 if C.Lk == LK_STRG:
#                     if LkT == LK_STWK: LkT = LK_WKST
#                 else: LkT  = LK_STRG
#                 Ch0 = [*C.Chain, *[(C.r, C.c, C.Cand, LkT)]]
#                 pos = is_in_chain(r, c, Cand, Ch0, GrpLks)
#                 if pos >= 0: continue
#                 for i, (rf, cf, Candf) in enumerate(Fins):
#                     if ccells_match(r, c, Cand, rf, cf, Candf, GrpLks):
#                         if LkT == LK_STRG: break  # A chain can intersect a Fin on a strong link enroute to another fin.
#                         # a cover chain connecting to a fin has been found.
#                         # if all chains from covers to fins are found (they are all direct links), at least one chain must
#                         # be a weakly ended AIC - which we have just found - for a successful cover elimination
#                         nDirLks = 0
#                         for Ch in Tree.Chains:
#                             if len(Ch) == 2: nDirLks += 1
#                         if nDirLks == len(Fins) or not Tree.Chains[i]:
#                         # for Ch in Tree.Chains:
#                         #     if not Ch: break
#                         # else:  # a full house of direct links, replace with found chain for that fin and return with successful elimination
#                             Tree.Chains[i] = [*Ch0, *[(rf, cf, Candf, LK_NONE)]]
#                             for Ch in Tree.Chains:
#                                 if not Ch: break
#                             else:  # Cover sees all fins with at least on being indirect (weakly linked AIC)ith
#                                 re, ce, Cande, Lke = Ch0[0]
#                                 if GrpLks: Tree.Outcome = [(list(re)[0], list(ce)[0], Cande)]
#                                 else: Tree.Outcome = [(re, ce, Cande)]
#                                 Tree.Found = True
#                                 return C
#                 UC.append((r, c, Cand))
#                 C.Children.append(TNODE(r, c, Cand, LkT, Ch0, C))
#         if C.Children: Kids.append(C)
#     return Kids
