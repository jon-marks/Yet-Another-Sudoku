from copy import copy
from collections import namedtuple

from globals import *
from trc import TRCX

# from solve_utils import *  # remove dependency on this file, it should only be imported
                             # by the tech modules below.
from solve_singles import *
from solve_subsets import *
from solve_fish import *
from solve_wings import *
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

LK_DIFF     = 20  # per link difficulty premium
GRP_LK_DIFF = 50  # per group link difficulty premium.

SLVR = namedtuple('SLVR', ['pFn', 'Mthds'])

class TECH_T:
    def __init__(self, Enabled=False, Text=None, Expertise=UNDEF, Difficulty=UNDEF):
        self.Enabled    = Enabled  # if true will be used to find a logic solution for the puzzle
        self.Text       = Text if Text else ""
        self.Expertise  = Expertise
        self.Difficulty = Difficulty

Tech = {T_UNDEF:                    TECH_T(True, "Undefined",                 UNDEF                   -1),
        T_EXPOSED_SINGLE:           TECH_T(True, "Exposed Single",            EXP_BEGINNER,            5),
        T_HIDDEN_SINGLE:            TECH_T(True, "Hidden Single",             EXP_BEGINNER,           10),
        T_CLAIMING_LOCKED_SINGLE:   TECH_T(True, "Claiming Locked Single",    EXP_NOVICE,             15),
        T_POINTING_LOCKED_SINGLE:   TECH_T(True, "Pointing Locked Single",    EXP_NOVICE,             15),
        T_EXPOSED_PAIR:             TECH_T(True, "Exposed Pair",              EXP_INTERMEDIATE,       15),
        T_LOCKED_EXPOSED_PAIR:      TECH_T(True, "Locked Exposed Pair",       EXP_INTERMEDIATE,       20),
        T_HIDDEN_PAIR:              TECH_T(True, "Hidden Pair",               EXP_INTERMEDIATE,       20),
        T_EXPOSED_TRIPLE:           TECH_T(False, "Exposed Triple",            EXP_INTERMEDIATE,       20),
        T_LOCKED_EXPOSED_TRIPLE:    TECH_T(False, "Locked Exposed Triple",     EXP_INTERMEDIATE,       25),
        T_HIDDEN_TRIPLE:            TECH_T(False, "Hidden Triple",             EXP_INTERMEDIATE,       30),
        T_EXPOSED_QUAD:             TECH_T(False, "Exposed Quad",              EXP_INTERMEDIATE,       35),
        T_HIDDEN_QUAD:              TECH_T(False, "Hidden Quad",               EXP_INTERMEDIATE,       40),
        T_X_WING:                   TECH_T(False, "X-Wing",                    EXP_PROFICIENT,         45),
        T_SWORDFISH:                TECH_T(False, "Swordfish",                 EXP_PROFICIENT,         50),
        T_JELLYFISH:                TECH_T(False, "Jellyfish",                 EXP_PROFICIENT,         55),
        T_FINNED_X_WING:            TECH_T(False, "Finned X-Wing",             EXP_PROFICIENT,         60),
        T_FINNED_SWORDFISH:         TECH_T(False, "Finned Swordfish",          EXP_PROFICIENT,         65),
        T_FINNED_JELLYFISH:         TECH_T(False, "Finned Jellyfish",          EXP_PROFICIENT,         70),
        T_SKYSCRAPER:               TECH_T(False, "Skyscraper",                EXP_PROFICIENT,         45),
        T_TWO_STRING_KITE:          TECH_T(False, "Two String Kite",           EXP_PROFICIENT,         45),
        T_TURBOT_FISH:              TECH_T(False, "Turbot Fish",               EXP_PROFICIENT,         50),
        T_EMPTY_RECT:               TECH_T(True, "Empty Rectangle",           EXP_PROFICIENT,         45),
        T_Y_WING:                   TECH_T(False, "Y-Wing",                    EXP_INTERMEDIATE,       50),
        T_XYZ_WING:                 TECH_T(False, "XYZ-Wing",                  EXP_PROFICIENT,         60),
        T_WXYZ_WING:                TECH_T(False, "WXYZ-Wing",                 EXP_ACCOMPLISHED,      100),
        T_BENT_EXPOSED_QUAD:        TECH_T(False, "Bent Exposed Quad",         EXP_ACCOMPLISHED,      110),
        T_X_CHAIN:                  TECH_T(False, "X-Chain",                   EXP_PROFICIENT,         70),
        T_EVEN_X_LOOP:              TECH_T(False, "Even X-Loop",               EXP_PROFICIENT,         70),
        T_STRONG_X_LOOP:            TECH_T(False, "Strong X-Loop",             EXP_PROFICIENT,         70),
        T_REMOTE_PAIR:              TECH_T(False, "Remote Pair",               EXP_ACCOMPLISHED,       80),
        T_XY_CHAIN:                 TECH_T(False, "XY-Chain",                  EXP_ACCOMPLISHED,       80),
        T_XY_LOOP:                  TECH_T(False, "XY-Loop",                   EXP_ACCOMPLISHED,       80),
        T_W_WING:                   TECH_T(False, "W-Wing",                    EXP_PROFICIENT,         55),
        T_SC_AI_CHAIN:              TECH_T(False, "Same End Candidate AI-Chain", EXP_PROFICIENT,       70),
        T_DC_AI_CHAIN:              TECH_T(False, "Different End Candidate AI-Chain", EXP_ACCOMPLISHED,80),
        T_EVEN_AI_LOOP:             TECH_T(False, "Even AI-Loop",              EXP_ACCOMPLISHED,       80),
        T_STRONG_AI_LOOP:           TECH_T(False, "Strong AI-Loop",            EXP_ACCOMPLISHED,       80),
        T_KRAKEN_X_WING:            TECH_T(False, "Kraken Finned X-Wing",      EXP_ACCOMPLISHED,      100),
        T_KRAKEN_SWORDFISH:         TECH_T(False, "Kraken Finned Swordfish",   EXP_ACCOMPLISHED,      100),
        T_KRAKEN_JELLYFISH:         TECH_T(False, "Kraken Finned Jellyfish",   EXP_ACCOMPLISHED,      100),
        T_GL_TWO_STRING_KITE:       TECH_T(False, "Group Linked Two String Kite", EXP_PROFICIENT,      45),
        T_GL_TURBOT_FISH:           TECH_T(False, "Group Linked Turbot Fish",  EXP_PROFICIENT,         50),
        T_GL_X_CHAIN:               TECH_T(False, "Group Linked X-Chain",      EXP_PROFICIENT,         70),
        T_GL_EVEN_X_LOOP:           TECH_T(False, "Group Linked Even X-Loop",  EXP_PROFICIENT,         70),
        T_GL_STRONG_X_LOOP:         TECH_T(False, "Group Linked Strong X-Loop", EXP_PROFICIENT,        70),
        T_GL_W_WING:                TECH_T(False, "Group Linked W-Wing",       EXP_PROFICIENT,         80),
        T_GL_SC_AI_CHAIN:           TECH_T(False, "Group Linked Same End Candidates AI-Chain", EXP_PROFICIENT, 80),
        T_GL_DC_AI_CHAIN:           TECH_T(False, "Group Linked Different End Candidates AI-Chain", EXP_ACCOMPLISHED, 80),
        T_GL_EVEN_AI_LOOP:          TECH_T(False, "Group Linked Even AI-Loop", EXP_ACCOMPLISHED,       80),
        T_GL_STRONG_AI_LOOP:        TECH_T(False, "Group Linked Strong AI-Loop", EXP_ACCOMPLISHED,     80),
        T_GL_KRAKEN_X_WING:         TECH_T(False, "Group Linked Kraken Finned X-Wing", EXP_ACCOMPLISHED, 100),
        T_GL_KRAKEN_SWORDFISH:      TECH_T(False, "Group Linked Kraken Finned Swordfish", EXP_ACCOMPLISHED, 100),
        T_GL_KRAKEN_JELLYFISH:      TECH_T(False, "Group Linked Kraken Finned Jellyfish", EXP_ACCOMPLISHED, 100),
        T_BRUTE_FORCE:              TECH_T(True, "Brute Force",               EXP_EXPERT,           1000),
        }

Solvers = [SLVR(tech_exposed_singles,     [T_EXPOSED_SINGLE]),
           SLVR(tech_hidden_singles,      [T_HIDDEN_SINGLE]),
           SLVR(tech_locked_singles,      [T_CLAIMING_LOCKED_SINGLE, T_POINTING_LOCKED_SINGLE]),
           SLVR(tech_exposed_pairs,       [T_EXPOSED_PAIR, T_LOCKED_EXPOSED_PAIR]),
           SLVR(tech_hidden_pairs,        [T_HIDDEN_PAIR]),
           # SLVR(tech_exposed_triples,     [T_EXPOSED_TRIPLE, T_LOCKED_EXPOSED_TRIPLE]),
           # SLVR(tech_hidden_triples,      [T_HIDDEN_TRIPLE]),
           # SLVR(tech_exposed_quads,       [T_EXPOSED_QUAD]),
           # SLVR(tech_hidden_quads,        [T_HIDDEN_QUAD]),
           # SLVR(tech_x_wings,             [T_X_WING]),
           # SLVR(tech_swordfish,           [T_SWORDFISH]),
           # SLVR(tech_jellyfish,           [T_JELLYFISH]),
           # SLVR(tech_bent_exposed_triples, [T_Y_WING, T_XYZ_WING]),
           # SLVR(tech_three_link_x_chains, [T_SKYSCRAPER, T_TWO_STRING_KITE, T_TURBOT_FISH]),
           SLVR(tech_empty_rects,         [T_EMPTY_RECT]),
           # SLVR(tech_finned_x_wings,      [T_FINNED_X_WING]),  # finned fish never before ordinary fish
           # SLVR(tech_finned_swordfish,    [T_FINNED_SWORDFISH]),
           # SLVR(tech_finned_jellyfish,    [T_FINNED_JELLYFISH]),
           # SLVR(tech_bent_exposed_quads,  [T_WXYZ_WING, T_BENT_EXPOSED_QUAD]),
           # SLVR(tech_other_x_chains,      [T_X_CHAIN, T_EVEN_X_LOOP, T_STRONG_X_LOOP]),# and loops, never before three link X-Chains
           # SLVR(tech_remote_pairs,        [T_REMOTE_PAIR]),
           # SLVR(tech_xy_chains,           [T_XY_CHAIN]),
           # SLVR(tech_xy_loops,            [T_XY_LOOP]),
           # SLVR(tech_ai_chains,           [T_W_WING, T_SC_AI_CHAIN, T_DC_AI_CHAIN, T_EVEN_AI_LOOP, T_STRONG_AI_LOOP]),
           # SLVR(tech_gl_three_link_x_chains, [T_GL_TWO_STRING_KITE, T_GL_TURBOT_FISH]),
           # SLVR(tech_gl_other_x_chains,   [T_GL_X_CHAIN, T_GL_EVEN_X_LOOP, T_GL_STRONG_X_LOOP]), # and loops, never before three link xchains
           # SLVR(tech_gl_ai_chains,        [T_GL_W_WING, T_GL_SC_AI_CHAIN, T_GL_DC_AI_CHAIN, T_GL_EVEN_AI_LOOP, T_GL_STRONG_AI_LOOP]),
           # SLVR(tech_kraken_x_wings,      [T_KRAKEN_X_WING]),  # kraken fish never before finned fish
           # SLVR(tech_kraken_swordfish,    [T_KRAKEN_SWORDFISH]),
           # SLVR(tech_kraken_jellyfish,    [T_KRAKEN_JELLYFISH]),
           # SLVR(tech_gl_kraken_x_wings,   [T_GL_KRAKEN_X_WING]),
           # SLVR(tech_gl_kraken_swordfish, [T_GL_KRAKEN_SWORDFISH]),
           # SLVR(tech_gl_kraken_jellyfish, [T_GL_KRAKEN_JELLYFISH]),
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
    MaxLvl = 0
    if Meth != T_UNDEF and NrEmpties > 0:
        Step = STEP(Grid = [[Grid1[r][c] for c in range(9)] for r in range(9)],
                    Cands = [[copy(Cands[r][c]) for c in range(9)] for r in range(9)])
        pFn = method_solver(Meth)
        if pFn:
            NrSlvd = pFn(Grid1, Step, Cands, [Meth])
            if NrSlvd >= 0:
                Steps.append(Step)
                if Tech[Meth].Expertise > MaxLvl: MaxLvl = Tech[Meth].Expertise
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
                    if Tech[Step.Method].Expertise > MaxLvl: MaxLvl = Tech[Step.Method].Expertise
                    NrEmpties -= NrSlvd
                    if Soln:
                        Err = check_puzzle_step(Grid1, Cands, Soln)
                        if Err: return UNDEF, Steps, Err
                    break
        else:
            return UNDEF, Steps, "Can't solve step"
    return MaxLvl, Steps, ""

def solve_next_step(Grid, Elims = None, Meth = T_UNDEF, Soln = None):
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
        else: return Step, f"Unknown Method: 0x{Meth:16x}"
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(Grid1, Cands, Soln)
                if Err: return Step, Err,
            return Step, ""
    for Slvr in Solvers:
        EnMthds = []; NrSlvd = -1
        for Mthd in Slvr.Mthds:
            if Tech[Mthd].Enabled: EnMthds.append(Mthd)
        if EnMthds: NrSlvd = Slvr.pFn(Grid1, Step, Cands, EnMthds)
        if NrSlvd >= 0:
            if Soln:
                Err = check_puzzle_step(Grid1, Cands, Soln)
                if Err: return Step, Err
            return Step, ""
    else: return Step, "Can't solve step"

