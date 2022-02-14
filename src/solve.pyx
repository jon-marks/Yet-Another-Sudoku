
include "globals.pxi"
from globals import *
from trc cimport *
from trc import *

# from misc import tkns_to_str
# # for debugging.

from solve_utils cimport *
from solve_singles cimport *
from solve_subsets cimport *
from solve_fish cimport *

# from solve_singles import *
# from solve_subsets import *
# from solve_fish import *
# from solve_wings import *
# from solve_x_chains import *
# from solve_xy_chains import *
# from solve_ai_chains import *

# Note that the order in which techniques are attempted influences the outcomes:
# * the holy grail is to solve the puzzle with the simplest techniques possible.
#     which is often not achieved because a more complex technique could
#     eliminate a candidate that makes the balance of the puzzle easier to solve
#     than a candidate to eliminate found by the the possible complex technique
# * from (perceived) simpler to more complex
# * order / size of of condition ascends
# * some, but not all techniques depend on a prior logic condition not being
#   satisfied.
# * exposed subsets of a particular order before the hidden subset of same order
# * With fish, order (2, 3, 4) before finned (2, 3, 4) before Kraken (2, 3, 4).
# * The reason there are less techniques than there are patterns (T_... enums)
#   is that some techniques are able to resolve more than one pattern.
# * _kraken_ refers to the technique using an AIC chain as a strong or weak link.
# * ..._gl refers to the technique using group links in its chains.

ctypedef int (*PSLVRFN)(int[9][9], object Step, bint[9][9][9], object Methods)

ctypedef struct SLVR_C:
    PSLVRFN pFn
    int     Techs[SLVR_TECHS]

LK_DIFF     = 20  # per Kraken link
GRP_LK_DIFF = 50  # per group link

cdef SLVR_C Solvers[24]
Solvers[0].pFn = tech_exposed_singles_c;    Solvers[0].Techs  = [T_EXPOSED_SINGLE, -1, -1, -1, -1, -1, -1, -1]
Solvers[1].pFn = tech_hidden_singles_c;     Solvers[1].Techs  = [T_HIDDEN_SINGLE, -1, -1, -1, -1, -1, -1, -1]
Solvers[2].pFn = tech_locked_singles_c;     Solvers[2].Techs  = [T_CLAIMING_LOCKED_SINGLE, T_POINTING_LOCKED_SINGLE, -1, -1, -1, -1, -1, -1]
Solvers[3].pFn = tech_exposed_pairs_c;      Solvers[3].Techs  = [T_EXPOSED_PAIR, T_LOCKED_EXPOSED_PAIR, -1, -1, -1, -1, -1, -1]
Solvers[4].pFn = tech_hidden_pairs_c;       Solvers[4].Techs  = [T_HIDDEN_PAIR, -1, -1, -1, -1, -1, -1, -1]
Solvers[5].pFn = tech_exposed_triples_c;    Solvers[5].Techs  = [T_EXPOSED_TRIPLE, T_LOCKED_EXPOSED_TRIPLE, -1, -1, -1, -1, -1, -1]
Solvers[6].pFn = tech_hidden_triples_c;     Solvers[6].Techs  = [T_HIDDEN_TRIPLE, -1, -1, -1, -1, -1, -1, -1]
Solvers[7].pFn = tech_exposed_quads_c;      Solvers[7].Techs  = [T_EXPOSED_QUAD, -1, -1, -1, -1, -1, -1, -1]
Solvers[8].pFn = tech_hidden_quads_c;       Solvers[8].Techs  = [T_HIDDEN_QUAD, -1, -1, -1, -1, -1, -1, -1]
Solvers[9].pFn = tech_empty_rects_c;        Solvers[9].Techs  = [T_EMPTY_RECT, -1, -1, -1, -1, -1, -1, -1]
Solvers[10].pFn = tech_x_wings_c;           Solvers[10].Techs = [T_X_WING, -1, -1, -1, -1, -1, -1, -1]
Solvers[11].pFn = tech_swordfish_c;         Solvers[11].Techs = [T_SWORDFISH, -1, -1, -1, -1, -1, -1, -1]
Solvers[12].pFn = tech_jellyfish_c;         Solvers[12].Techs = [T_JELLYFISH, -1, -1, -1, -1, -1, -1, -1]
Solvers[13].pFn = tech_finned_x_wings_c;    Solvers[13].Techs = [T_FINNED_X_WING, T_SASHIMI_X_WING, -1, -1, -1, -1, -1, -1]
Solvers[14].pFn = tech_finned_swordfish_c;  Solvers[14].Techs = [T_FINNED_SWORDFISH, T_SASHIMI_SWORDFISH, -1, -1, -1, -1, -1, -1]
Solvers[15].pFn = tech_finned_jellyfish_c;  Solvers[15].Techs = [T_FINNED_JELLYFISH, T_SASHIMI_JELLYFISH, -1, -1, -1, -1, -1, -1]
Solvers[16].pFn = tech_finned_x_wings_c;    Solvers[16].Techs = [T_KRAKEN_X_WING, T_KRAKEN_SASHIMI_X_WING, -1, -1, -1, -1, -1, -1]
Solvers[17].pFn = tech_finned_swordfish_c;  Solvers[17].Techs = [T_KRAKEN_SWORDFISH, T_KRAKEN_SASHIMI_SWORDFISH, -1, -1, -1, -1, -1, -1]
Solvers[18].pFn = tech_finned_jellyfish_c;  Solvers[18].Techs = [T_KRAKEN_JELLYFISH, T_KRAKEN_SASHIMI_JELLYFISH, -1, -1, -1, -1, -1, -1]
Solvers[19].pFn = tech_finned_x_wings_c;    Solvers[19].Techs = [T_GL_KRAKEN_X_WING, T_GL_KRAKEN_SASHIMI_X_WING, -1, -1, -1, -1, -1, -1]
Solvers[20].pFn = tech_finned_swordfish_c;  Solvers[20].Techs = [T_GL_KRAKEN_SWORDFISH, T_GL_KRAKEN_SASHIMI_SWORDFISH, -1, -1, -1, -1, -1, -1]
Solvers[21].pFn = tech_finned_jellyfish_c;  Solvers[21].Techs = [T_GL_KRAKEN_JELLYFISH, T_GL_KRAKEN_SASHIMI_JELLYFISH, -1, -1, -1, -1, -1, -1]
Solvers[22].pFn = tech_brute_force_c;       Solvers[22].Techs = [T_BRUTE_FORCE, -1, -1, -1, -1, -1, -1, -1]
Solvers[23].pFn = NULL;                     Solvers[23].Techs = [-1, -1, -1, -1, -1, -1, -1, -1]


cdef PSLVRFN method_solver(int Tech):
    cdef SLVR_C Slvr
    cdef int T

    for Slvr in Solvers:
        if not Slvr.pFn: return NULL
        for T in Slvr.Techs:
            if T == Tech: return Slvr.pFn
            if T == -1: break
    return NULL

cdef check_puzzle_step(int GridC[9][9], bint CandsC[9][9][9], Soln):
    for r in range(9):
        for c in range(9):
            if GridC[r][c] > 0:
                if GridC[r][c] != Soln[r][c]:
                    return f"Invalid Assignment: r{r+1}c{c+1}:={Soln[r][c]}."
            else:
                if not CandsC[r][c][Soln[r][c]-1]:  # not in Cands[r][c]:
                    return f"Invalid Elimination: r{r+1}c{c+1}-={Soln[r][c]}."
    return None

def logic_solve_puzzle(Grid, Elims = None, Meth = T_UNDEF, Soln = None):
    # Solve the puzzle passed in grid, returning the ordered list of logic
    # solution steps.
    #
    # If the first method is not T_UNDEF and the first step cannot be solved
    # with the the specified method, then try to solve without the method
    # constraint

    # Returns Expertise Level and Steps to solve, unless an error is encountered, and in which
    # case returns UNDEF (-1) and a possible text error message in place of Steps.

    cdef int GridC[9][9]
    cdef bint ElimsC[9][9][9]
    cdef bint CandsC[9][9][9]
    cdef int NrEmpties, NrSlvd
    
    pgrid_2_cgrid(Grid, GridC)
    if Elims:
        pcands_2_ccands(Elims, ElimsC)
        NrEmpties = determine_cands_c(GridC, ElimsC, CandsC)
    else:
        NrEmpties = determine_cands_c(GridC, <pCANDSC>NULL, CandsC)

    TRCX(f"Solving puzzle: First try Method: {Tech[Meth].Text}")
    Steps = []
    MaxLvl = 0
    if Meth != T_UNDEF and NrEmpties > 0:
        Step = STEP(Grid = [[Grid[r][c] for c in range(9)] for r in range(9)],
                    Cands = ccands_2_pcands(CandsC))
        pFn = method_solver(Meth)
        if pFn:
            NrSlvd = pFn(GridC, Step, CandsC, [Meth])
            if NrSlvd >= 0:
                Steps.append(Step)
                TRCX(f"Step: {Tech[Step.Method].Text}: {Step.Outcome}")
                if Tech[Meth].Expertise > MaxLvl: MaxLvl = Tech[Meth].Expertise
                NrEmpties -= NrSlvd
                if Soln:
                    Err = check_puzzle_step(GridC, CandsC, Soln)
                    if Err: return UNDEF, Steps, Err

    while NrEmpties > 0:
        Step = STEP(Grid = [[GridC[r][c] for c in range(9)] for r in range(9)],
                    Cands = ccands_2_pcands(CandsC))
        for Slvr in Solvers:
            EnMthds = []
            St = "" ####TRCX
            for Mthd in Slvr.Techs:
                if Mthd == -1: break
                if Tech[Mthd].Enabled:
                    EnMthds.append(Mthd)
                    if St: St += ", "   ####TRCX
                    St += Tech[Mthd].Text   ####TRCX
            if EnMthds:
                TRCX(f"Solving for methods: {St}")
                NrSlvd = Slvr.pFn(GridC, Step, CandsC, EnMthds)
                if NrSlvd == -2: return UNDEF, Steps, "DEBUG STOP"
                if NrSlvd >= 0:
                    Steps.append(Step)
                    TRCX(f"Step: {Tech[Step.Method].Text}: {Step.Outcome}")
                    if Tech[Step.Method].Expertise > MaxLvl: MaxLvl = Tech[Step.Method].Expertise
                    NrEmpties -= NrSlvd
                    if Soln:
                        Err = check_puzzle_step(GridC, CandsC, Soln)
                        if Err: return UNDEF, Steps, Err
                    break
        else:
            return UNDEF, Steps, "Can't solve step"
    return MaxLvl, Steps, ""

def solve_next_step(Grid, Elims = None, Meth = T_UNDEF, Soln = None, OverrideEnableMthds = False):
    # Find the solution for the next step, used in providing hints to users.
    # Hints cannot be taken from the solution list as the user more than likely
    # solved the puzzle to this point taking a different path to that of the
    # solution list, and the current puzzle state may be different to any state
    # in the solution list.  Also note that this function does not check if the
    # puzzle is correct if interactive error checking is disabled and will still
    # attempt to find a solution.

    cdef int GridC[9][9]
    cdef bint ElimsC[9][9][9]
    cdef bint CandsC[9][9][9]

    pgrid_2_cgrid(Grid, GridC)
    if Elims:
        pcands_2_ccands(Elims, ElimsC)
        determine_cands_c(GridC, ElimsC, CandsC)
    else:
        determine_cands_c(GridC, <pCANDSC>NULL, CandsC)

    Step = STEP()
    if Meth != T_UNDEF:
        # TRCX(f"Meth:{Meth}")
        pFn  = method_solver(Meth)
        if pFn: NrSlvd = pFn(GridC, Step, CandsC, [Meth])
        else: return Step, f"Unknown Method: 0x{Meth:04x}"
        # TRCX(f"NrSlvd:{NrSlvd}, Step.Method:{Step.Method}")
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(GridC, CandsC, Soln)
                if Err: return Step, Err
            return Step, ""
    for Slvr in Solvers:
        EnMthds = []; NrSlvd = -1
        for Mthd in Slvr.Techs:
            if Mthd == -1: break
            if Tech[Mthd].Enabled or OverrideEnableMthds: EnMthds.append(Mthd)
        if EnMthds: NrSlvd = Slvr.pFn(GridC, Step, CandsC, EnMthds)
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(GridC, CandsC, Soln)
                if Err: return Step, Err
            return Step, ""
    else: return Step, "Can't solve step"
