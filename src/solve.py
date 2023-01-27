from copy import copy
from collections import namedtuple

from globals import *
from misc import pgm_msg
# from trc import TRCX

# from solve_utils import *  # remove dependency on this file, it should only be imported
#                              by the tech modules below.
from solve_singles import *
from solve_subsets import *
from solve_fish import *
from solve_bent_subsets import *
from solve_sl_nets import *
from solve_x_chains import *
from solve_xy_chains import *
from solve_ai_chains import *

# Note that the order in which techniques are attempted influences the outcomes:
# * the holy grail is to solve the puzzle with the simplest techniques possible.
#     Often not achieved because a more complex technique could
#     eliminate a candidate that makes the balance of the puzzle easier to solve
#     than a candidate to eliminate found by the possible complex technique
# * from (perceived) simpler to more complex
# * order / size of condition ascends
# * some, but not all techniques depend on a prior logic condition not being
#   satisfied.
# * exposed subsets of a particular order before the hidden subset of same order
# * With fish, order (2, 3, 4) before finned (2, 3, 4) before Kraken (2, 3, 4).
# * _kraken_ refers to the technique using an AIC chain as a strong or weak link.
# * ..._gl refers to the technique using group links in its chains.

LK_DIFF     = 15  # per link difficulty premium
GRP_LK_DIFF = 20  # per group link difficulty premium.

SLVR = namedtuple('SLVR', ['pFn', 'Mthds'])

# The order of the methods in the Solver structures is significant to the underlying code, change with caution.
# The order of the Slvr items can be changed with varying result in solution path and difficulty rating.
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
           SLVR(tech_grouped_bent_pair,   [T_GROUPED_BENT_PAIR_ER_HB, T_GROUPED_BENT_PAIR_EC_HB, T_GROUPED_BENT_PAIR_HR_EB, T_GROUPED_BENT_PAIR_HC_EB]),
           SLVR(tech_bent_exposed_triples, [T_Y_WING, T_XYZ_WING]),
           SLVR(tech_x_wings,             [T_X_WING]),
           SLVR(tech_bent_hidden_triple,  [T_BENT_HIDDEN_TRIPLE]),
           SLVR(tech_x_chains,            [T_SKYSCRAPER, T_TWO_STRING_KITE, T_TURBOT_FISH]),
           SLVR(tech_exposed_quads,       [T_EXPOSED_QUAD]),
           SLVR(tech_hidden_quads,        [T_HIDDEN_QUAD]),
           SLVR(tech_swordfish,           [T_SWORDFISH]),
           SLVR(tech_jellyfish,           [T_JELLYFISH]),
           SLVR(tech_empty_rects,         [T_EMPTY_RECT]),
           SLVR(tech_bent_exposed_quads,  [T_BENT_EXPOSED_QUAD]),
           SLVR(tech_finned_x_wings,      [T_FINNED_X_WING, T_SASHIMI_X_WING]),  # finned fish never before ordinary fish
           SLVR(tech_finned_swordfish,    [T_FINNED_SWORDFISH, T_SASHIMI_SWORDFISH]),
           SLVR(tech_bent_exposed_quints, [T_BENT_EXPOSED_QUINT]),
           SLVR(tech_bent_exposed_sexts,  [T_BENT_EXPOSED_SEXT]),
           SLVR(tech_finned_jellyfish,    [T_FINNED_JELLYFISH, T_SASHIMI_JELLYFISH]),
           SLVR(tech_grouped_bent_triple, [T_GROUPED_BENT_TRIPLE_ER_HB, T_GROUPED_BENT_TRIPLE_EC_HB, T_GROUPED_BENT_TRIPLE_HR_EB, T_GROUPED_BENT_TRIPLE_HC_EB]),
           SLVR(tech_grouped_bent_quad,   [T_GROUPED_BENT_QUAD_ER_HB, T_GROUPED_BENT_QUAD_EC_HB, T_GROUPED_BENT_QUAD_HR_EB, T_GROUPED_BENT_QUAD_HC_EB]),
           SLVR(tech_remote_pairs,        [T_REMOTE_PAIR_T3]),
           SLVR(tech_strong_linked_nets,  [T_STRONG_LINKED_NET_T1, T_STRONG_LINKED_NET_T2, T_STRONG_LINKED_NET_T3]),
           SLVR(tech_x_chains,            [T_X_CHAIN_T1, T_EVEN_X_LOOP_T3, T_STRONG_X_LOOP]),  # and loops, never before three link X-Chains
           SLVR(tech_xy_chains,           [T_XY_CHAIN_T1, T_XY_CHAIN_T2, T_XY_CHAIN_T3, T_EVEN_XY_LOOP_T2, T_EVEN_XY_LOOP_T3]),
           SLVR(tech_ai_chains,           [T_W_WING, T_AI_CHAIN_T1, T_AI_CHAIN_T2, T_AI_CHAIN_T3, T_EVEN_AI_LOOP_T1, T_EVEN_AI_LOOP_T2, T_EVEN_AI_LOOP_T3, T_STRONG_AI_LOOP]),
           SLVR(tech_chained_strong_linked_nets, [T_CHAINED_STRONG_LINKED_NET_T1, T_CHAINED_STRONG_LINKED_NET_T2, T_CHAINED_STRONG_LINKED_NET_T3]),
           SLVR(tech_gl_x_chains,         [T_GL_TWO_STRING_KITE, T_GL_TURBOT_FISH, T_GL_X_CHAIN_T1, T_GL_EVEN_X_LOOP_T3, T_GL_STRONG_X_LOOP]),
           SLVR(tech_gl_ai_chains,        [T_GL_AI_CHAIN_T1, T_GL_AI_CHAIN_T2, T_GL_AI_CHAIN_T3, T_GL_EVEN_AI_LOOP_T1, T_GL_EVEN_AI_LOOP_T2, T_GL_EVEN_AI_LOOP_T3 , T_GL_STRONG_AI_LOOP]),
           SLVR(tech_finned_x_wings,      [T_KRAKEN_FINNED_X_WING, T_KRAKEN_SASHIMI_X_WING]),  # kraken fish never before finned fish
           SLVR(tech_finned_swordfish,    [T_KRAKEN_FINNED_SWORDFISH, T_KRAKEN_SASHIMI_SWORDFISH]),
           SLVR(tech_finned_jellyfish,    [T_KRAKEN_FINNED_JELLYFISH, T_KRAKEN_SASHIMI_JELLYFISH]),
           SLVR(tech_finned_x_wings,      [T_GL_KRAKEN_FINNED_X_WING, T_GL_KRAKEN_SASHIMI_X_WING]),
           SLVR(tech_finned_swordfish,    [T_GL_KRAKEN_FINNED_SWORDFISH, T_GL_KRAKEN_SASHIMI_SWORDFISH]),
           SLVR(tech_finned_jellyfish,    [T_GL_KRAKEN_FINNED_JELLYFISH, T_GL_KRAKEN_SASHIMI_JELLYFISH]),
           SLVR(tech_brute_force,         [T_BRUTE_FORCE])
           ]

SlvrLU = {}
for T in Tech.keys():
    for Slvr in Solvers:
        if T in Slvr.Mthds: SlvrLU[T] = Slvr.pFn; break
    else:
        if T != T_UNDEF: pgm_msg("Warning", f"Method: {Tech[T].Text} does not have a solver")

EnSlvrs = []
for pFn, Mthds in Solvers:
    EnMthds = []
    for T in Mthds:
        if T in Tech.keys():
            if Tech[T].Enabled: EnMthds.append(T)
        else: pgm_msg("Warning", f"Unknown Method Enumeration: {T}\n")
    if EnMthds: EnSlvrs.append(SLVR(pFn, EnMthds))

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

def logic_solve_puzzle(Grid, Elims = None, Meth = T_UNDEF, Soln = None, StepOverrides = None):
    # Solve the puzzle passed in grid, returning the ordered list of logic
    # solution steps.
    #
    # If the first method is not T_UNDEF and the first step cannot be solved
    # with the specified method, then try to solve without the method
    # constraint

    NrEmpties, Cands = determine_cands(Grid, Elims)
    Grid1 = [[Grid[r][c] for c in range(9)] for r in range(9)]

    Steps = []
    MaxExpertise = 0
    if Meth != T_UNDEF and NrEmpties > 0:
        Step = STEP(Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)],
                    Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)],
                    Soln = Soln,
                    Overrides = StepOverrides)
        NrSlvd = SlvrLU[Meth](Grid1, Step, Cands, [Meth])
        if NrSlvd >= 0:
            Steps.append(Step)
            if Tech[Meth].Expertise > MaxExpertise: MaxExpertise = Tech[Meth].Expertise
            NrEmpties -= NrSlvd
            # if Soln:
            Err = check_puzzle_step(Grid1, Cands, Soln)
            if Err: return UNDEF, Steps, Err
    while NrEmpties > 0:
        Step = STEP(Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)],
                    Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)],
                    Soln = Soln)
        for pFn, Meths in EnSlvrs:
            NrSlvd = pFn(Grid1, Step, Cands, Meths)
            if NrSlvd >= 0:
                Steps.append(Step)
                if Tech[Step.Method].Expertise > MaxExpertise: MaxExpertise = Tech[Step.Method].Expertise
                NrEmpties -= NrSlvd
                # if Soln:
                Err = check_puzzle_step(Grid1, Cands, Soln)
                if Err: return UNDEF, Steps, Err
                break
        else:
            return UNDEF, Steps, "Can't solve step"
    return MaxExpertise, Steps, ""

def solve_next_step(Grid, Elims = None, Meth = T_UNDEF, Soln = None, MethodEnableOverride = False, StepOverrides = None, JustThisMeth = False):

    # Find the solution for the next step, used in providing hints to users.
    # Hints cannot be taken from the solution list as the user more than likely
    # solved the puzzle to this point taking a different path to that of the
    # solution list, and the current puzzle state may be different to any state
    # in the solution list.  Also note that this function does not check if the
    # puzzle is correct if interactive error checking is disabled and will still
    # attempt to find a solution.

    NrEmpties, Cands = determine_cands(Grid, Elims)
    Grid1 = [[Grid[r][c] for c in range(9)] for r in range(9)]
    Step = STEP(Soln = Soln)
    if not NrEmpties: return Step, "Puzzle already solved!"
    if Meth != T_UNDEF:
        Step.Overrides = StepOverrides
        NrSlvd = SlvrLU[Meth](Grid1, Step, Cands, [Meth])
        if NrSlvd >= 0:
            # if Soln:
            Err = check_puzzle_step(Grid1, Cands, Soln)
            if Err: return Step, Err,
            return Step, ""
        if JustThisMeth: return Step, ""  # f"Can't solve step with {Tech[Meth].Text}."
    Step.Overrides = {}
    for pFn, Meths in Solvers if MethodEnableOverride else EnSlvrs:
        NrSlvd = pFn(Grid1, Step, Cands, Meths)
        if NrSlvd >= 0:
            # if Soln:
            Err = check_puzzle_step(Grid1, Cands, Soln)
            if Err: return Step, Err
            return Step, ""
    else: return Step, "Can't solve step"

def pattern_search(oPzl, Meths, PSMeths, Overrides):

    NrEmpties = oPzl.NrEmpties
    Cands = [[copy(oPzl.Cands[r][c]) for c in range(9)] for r in range(9)]
    Grid1 = [[oPzl.Grid[r][c] for c in range(9)] for r in range(9)]
    Steps = []; Step = STEP(Soln = oPzl.Soln)
    while NrEmpties > 0:
        for m in Meths:  # pFn, Meths in EnSlvrs:
            Step.Pattern = []; Step.Outcome = []
            NrSlvd = SlvrLU[m](Grid1, Step, Cands, [m])  # Meths)
            if NrSlvd >= 0:
                NrEmpties -= NrSlvd
                Err = check_puzzle_step(Grid1, Cands, oPzl.Soln)
                if Err: return Steps, Err
                break
        else:
            if NrEmpties > 0:
                for m in PSMeths:
                    Step.Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)]
                    Step.Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)]
                    Step.Overrides = Overrides
                    Step.Pattern = []; Step.Outcome = []
                    NrSlvd = SlvrLU[m](Grid1, Step, Cands, [m])
                    if NrSlvd >= 0:
                        Steps.append(Step); Step = STEP(Soln = oPzl.Soln)
                        NrEmpties -= NrSlvd
                        Err = check_puzzle_step(Grid1, Cands, oPzl.Soln)
                        if Err: return Steps, Err
                else:
                    Step.Overrides = {}
                    for pFn, Meths1 in Solvers:
                        Meths2 =sorted({*Meths1} - {*Meths, *PSMeths})
                        if Meths2:  NrSlvd = pFn(Grid1, Step, Cands, Meths2)
                        else: continue
                        if NrSlvd >= 0:
                            NrEmpties -= NrSlvd
                            Err = check_puzzle_step(Grid1, Cands, oPzl.Soln)
                            if Err: return Steps, Err
                            break
    return Steps, ""
