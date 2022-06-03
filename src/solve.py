from copy import copy
from collections import namedtuple

from globals import *
from trc import TRCX

# from solve_utils import *  # remove dependency on this file, it should only be imported
#                              by the tech modules below.
from solve_singles import *
from solve_subsets import *
from solve_fish import *
from solve_bent_subsets import *
from solve_x_chains import *
from solve_xy_chains import *
from solve_ai_chains import *

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

LK_DIFF     = 15  # per link difficulty premium
GRP_LK_DIFF = 20  # per group link difficulty premium.

SLVR = namedtuple('SLVR', ['pFn', 'Mthds'])

# the order of the methods in the Solver structures is significant to the underlying code, change with caution.
# the order of the Slvr items can be changed with varying result in solution path and difficulty rating.
#   But do not do stupid things like:
#   *  putting the equivalent group linked pattern ahead of its scalar pattern:
#   *  changing the order of fish from X_WING before SWORDFISH before JELLYFISH
#   *  changing the fish sub order of ordinary before FINNED before SASHIMI, before KRAKEN before GL_KRAKEN
#   *  not maintaining the loose order of singles, subsets, (fish, bent subsets, empty rectangle, 3 link x chains)
#   *       (remote pairs, xy-chains, finned fish), x chains, ai chains, Kraken fish.
#   *       - order of grouped items can be changed

Solvers = [SLVR(tech_exposed_singles,     [T_EXPOSED_SINGLE]),
           SLVR(tech_hidden_singles,      [T_HIDDEN_SINGLE]),
           SLVR(tech_locked_singles,      [T_CLAIMING_LOCKED_SINGLE, T_POINTING_LOCKED_SINGLE]),
           SLVR(tech_exposed_pairs,       [T_EXPOSED_PAIR, T_LOCKED_EXPOSED_PAIR]),
           SLVR(tech_hidden_pairs,        [T_HIDDEN_PAIR]),
           SLVR(tech_exposed_triples,     [T_EXPOSED_TRIPLE, T_LOCKED_EXPOSED_TRIPLE]),
           SLVR(tech_hidden_triples,      [T_HIDDEN_TRIPLE]),
           SLVR(tech_exposed_quads,       [T_EXPOSED_QUAD]),
           SLVR(tech_hidden_quads,        [T_HIDDEN_QUAD]),
           SLVR(tech_x_wings,             [T_X_WING]),
           SLVR(tech_swordfish,           [T_SWORDFISH]),
           SLVR(tech_jellyfish,           [T_JELLYFISH]),
           SLVR(tech_empty_rects,         [T_EMPTY_RECT]),
           SLVR(tech_bent_exposed_triples, [T_Y_WING, T_XYZ_WING]),
           SLVR(tech_x_chains,            [T_SKYSCRAPER, T_TWO_STRING_KITE, T_TURBOT_FISH]),
           SLVR(tech_bent_exposed_quads,  [T_WXYZ_WING, T_BENT_EXPOSED_QUAD]),
           SLVR(tech_finned_x_wings,      [T_FINNED_X_WING, T_SASHIMI_X_WING]),  # finned fish never before ordinary fish
           SLVR(tech_finned_swordfish,    [T_FINNED_SWORDFISH, T_SASHIMI_SWORDFISH]),
           SLVR(tech_finned_jellyfish,    [T_FINNED_JELLYFISH, T_SASHIMI_JELLYFISH]),
           SLVR(tech_remote_pairs,        [T_REMOTE_PAIR]),
           SLVR(tech_x_chains,            [T_X_CHAIN, T_EVEN_X_LOOP, T_STRONG_X_LOOP]),# and loops, never before three link X-Chains
           SLVR(tech_xy_chains,           [T_SC_XY_CHAIN, T_DC_IBVC_XY_CHAIN, T_XY_LOOP]),
           SLVR(tech_ai_chains,           [T_W_WING, T_SC_AI_CHAIN, T_DC_AI_CHAIN, T_DC_IBVC_AI_CHAIN, T_EVEN_AI_LOOP, T_STRONG_AI_LOOP]),
           SLVR(tech_gl_x_chains,         [T_GL_TWO_STRING_KITE, T_GL_TURBOT_FISH, T_GL_X_CHAIN, T_GL_EVEN_X_LOOP, T_GL_STRONG_X_LOOP]),
           SLVR(tech_gl_ai_chains,        [T_GL_SC_AI_CHAIN, T_GL_DC_AI_CHAIN, T_GL_DC_IBVC_AI_CHAIN, T_GL_EVEN_AI_LOOP, T_GL_STRONG_AI_LOOP]),
           SLVR(tech_finned_x_wings,      [T_KRAKEN_FINNED_X_WING, T_KRAKEN_SASHIMI_X_WING]),  # kraken fish never before finned fish
           SLVR(tech_finned_swordfish,    [T_KRAKEN_FINNED_SWORDFISH, T_KRAKEN_SASHIMI_SWORDFISH]),
           SLVR(tech_finned_jellyfish,    [T_KRAKEN_FINNED_JELLYFISH, T_KRAKEN_SASHIMI_JELLYFISH]),
           SLVR(tech_finned_x_wings,      [T_GL_KRAKEN_FINNED_X_WING, T_GL_KRAKEN_SASHIMI_X_WING]),
           SLVR(tech_finned_swordfish,    [T_GL_KRAKEN_FINNED_SWORDFISH, T_GL_KRAKEN_SASHIMI_SWORDFISH]),
           SLVR(tech_finned_jellyfish,    [T_GL_KRAKEN_FINNED_JELLYFISH, T_GL_KRAKEN_SASHIMI_JELLYFISH]),
           SLVR(tech_brute_force,         [T_BRUTE_FORCE])
           ]

def method_solver(Tech):
    for Slvr in Solvers:
        if Tech in Slvr.Mthds: return Slvr.pFn
    else: return None

def check_puzzle_step(Grid, Cands, Soln):
    for r in range(9):
        for c in range(9):
            if Grid[r][c] > 0:
                if Grid[r][c] != Soln[r][c]:
                    return f"Invalid Assignment: r{r+1}c{c+1}:={Soln[r][c]}."
            else:
                if Soln[r][c] not in Cands[r][c]:
                    return f"Invalid Elimination: r{r+1}c{c+1}-={Soln[r][c]}."
    return None

def logic_solve_puzzle(Grid, Elims = None, Meth = T_UNDEF, Soln = None):
    # Solve the puzzle passed in grid, returning the ordered list of logic
    # solution steps.
    #
    # If the first method is not T_UNDEF and the first step cannot be solved
    # with the the specified method, then try to solve without the method
    # constraint

    NrEmpties, Cands = determine_cands(Grid, Elims)
    Grid1 = [[Grid[r][c] for c in range(9)] for r in range(9)]

    Steps = []
    MaxExpertise = 0
    if Meth != T_UNDEF and NrEmpties > 0:
        Step = STEP(Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)],
                    Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)])
        pFn = method_solver(Meth)
        if pFn:
            NrSlvd = pFn(Grid1, Step, Cands, [Meth])
            if NrSlvd >= 0:
                Steps.append(Step)
                if Tech[Meth].Expertise > MaxExpertise: MaxExpertise = Tech[Meth].Expertise
                NrEmpties -= NrSlvd
                if Soln:
                    Err = check_puzzle_step(Grid1, Cands, Soln)
                    if Err: return UNDEF, Steps, Err

    while NrEmpties > 0:
        Step = STEP(Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)],
                    Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)])
        for Slvr in Solvers:
            EnMthds = []; NrSlvd = -1
            for Mthd in Slvr.Mthds:
                if Tech[Mthd].Enabled: EnMthds.append(Mthd)
            if EnMthds:
                NrSlvd = Slvr.pFn(Grid1, Step, Cands, EnMthds)
                if NrSlvd >= 0:
                    Steps.append(Step)
                    if Tech[Step.Method].Expertise > MaxExpertise: MaxExpertise = Tech[Step.Method].Expertise
                    NrEmpties -= NrSlvd
                    if Soln:
                        Err = check_puzzle_step(Grid1, Cands, Soln)
                        if Err: return UNDEF, Steps, Err
                    break
        else:
            return UNDEF, Steps, "Can't solve step"
    return MaxExpertise, Steps, ""

def solve_next_step(Grid, Elims = None, Meth = T_UNDEF, Soln = None, OverrideEnableMthds = False):
    # Find the solution for the next step, used in providing hints to users.
    # Hints cannot be taken from the solution list as the user more than likely
    # solved the puzzle to this point taking a different path to that of the
    # solution list, and the current puzzle state may be different to any state
    # in the solution list.  Also note that this function does not check if the
    # puzzle is correct if interactive error checking is disabled and will still
    # attempt to find a solution.

    NrEmpties, Cands = determine_cands(Grid, Elims)
    Grid1 = [[Grid[r][c] for c in range(9)] for r in range(9)]
    Step = STEP()
    if Meth != T_UNDEF:
        pFn = method_solver(Meth)
        if pFn: NrSlvd = pFn(Grid1, Step, Cands, [Meth])
        else: return Step, f"Unknown Method: 0x{Meth:4x}"
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(Grid1, Cands, Soln)
                if Err: return Step, Err,
            return Step, ""
    for Slvr in Solvers:
        EnMthds = []; NrSlvd = -1
        for Mthd in Slvr.Mthds:
            if Tech[Mthd].Enabled or OverrideEnableMthds: EnMthds.append(Mthd)
        if EnMthds: NrSlvd = Slvr.pFn(Grid1, Step, Cands, EnMthds)
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(Grid1, Cands, Soln)
                if Err: return Step, Err
            return Step, ""
    else: return Step, "Can't solve step"
