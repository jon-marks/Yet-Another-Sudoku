"""
globals.py:  Common constants across the project

Description:
    Tuneable parameters which may find themselves in a config file sometime
    in the future and common constants shared across multiple modules.  No
    variables or flags to break the cohesiveness of the modules permitted.

Audit:
    2021-04-xx  jm  Initial Entry

"""

import wx

#DEBUG   = True
DEBUG   = False

TITLE   = 'Yet Another Sudoku App'
BLURB   = '*  Feature rich\n' \
          '*  Simple and minimal user interface'

VERSION = 'Version 0.01 - 2021-xx-xx, (c) Jonathan Marks'


FILE_WILDCARDS    = "All files (*.*)|*.*|" \
                    "Sudoku value files (*.svl)|*.svl"
MAX_SVL_FILE_SIZE = 4096  # even this value is generous

#  subdir's relative to cwd.
PUZZLES_DIR = "puzzles"
IMG_DIR     = "img"
DOC_DIR     = "doc"

#  Board and cell size and various border widths in pixels
#  Ensure cell sizes are integer multiples of 3.
TNY_CELL_SZ = 24
SML_CELL_SZ = 33
NRM_CELL_SZ = 48
LRG_CELL_SZ = 63
XLG_CELL_SZ = 93  # 96

DEFAULT_CELL_SZ      = NRM_CELL_SZ

USER_GUIDE_DLG_SZ    = wx.Size(500, 500)
LIST_SOLN_DLG_SZ     = wx.Size(580, 550)
LIST_SOLN_DLG_MIN_SZ = wx.Size(580, 450)

BOARD_BDR    = 4     # Thickness of the outer board border
BLOCK_BDR    = 4     # Thickness of block borders in the grid
CELL_BDR     = 2     # Thickness of cell borders in the grid
CELL_FRM_BDR = 5     # Thickness of the cell frame

PT2PXR       = 0.75  # Point to Pixel ratio
V_FT_SCL     = 0.87  # Value Font scale so it fits aesthetically in the cell
C_FT_SCL     = 0.85  # Cand Font scale . . .

# Font parameters for grid digits
FONT_FAM     = wx.FONTFAMILY_SWISS
FONT         = "Arial"
CELL_FONT_ST = wx.FONTSTYLE_NORMAL  # or _ITALIC
CELL_FONT_WT = wx.FONTWEIGHT_BOLD   # or _NORMAL or _LIGHT
CELL_FONT_UL = False                # True to underline

CAND_FONT_ST = wx.FONTSTYLE_NORMAL
CAND_FONT_WT = wx.FONTWEIGHT_NORMAL
CAND_FONT_UL = False

# Background picker pop up params
BG_CLR_PKR_WIDTH  = 45  # pixels
BG_CLR_PKR_BTN_HT = 15  # pixels

#  Colours
BLACK       = wx.Colour(0,     0,   0)
BLUE        = wx.Colour(0,     0, 255)
DK_BLUE     = wx.Colour(0,     0, 192)
DK_GREEN    = wx.Colour(0,    96,   0)
DK_GREY     = wx.Colour(32,   32,  32)
DK_ORANGE   = wx.Colour(208,  64,   0)
DK_RED      = wx.Colour(176,   0,   0)
GREEN       = wx.Colour(0,   255,   0)
GREY        = wx.Colour(128, 128, 128)
LT_BLUE     = wx.Colour(208, 216, 255)
LT_CYAN     = wx.Colour(208, 255, 255)
LT_GREEN    = wx.Colour(176, 255, 176)
LT_GREY     = wx.Colour(176, 176, 176)
LT_MAGENTA  = wx.Colour(255, 208, 255)
LT_ORANGE   = wx.Colour(255, 232, 200)
LT_PINK     = wx.Colour(255, 200, 200)
LT_PURPLE   = wx.Colour(240, 218, 255)
LT_YELLOW   = wx.Colour(255, 255, 168)
ORANGE      = wx.Colour(255, 128,   0)
RED         = wx.Colour(255,   0,   0)
VLT_BLUE    = wx.Colour(240, 250, 255)
VLT_GREY    = wx.Colour(200, 200, 200)
WHITE       = wx.Colour(255, 255, 255)
YELLOW      = wx.Colour(255, 255,   0)

BOARD_BDR_CLR    = BLACK
BLK_BDR_CLR      = BLACK
CELL_BDR_CLR     = GREY
CELL_SEL_CLR     = YELLOW
CAND_UNSEL_CLR   = VLT_GREY
CAND_PNCL_CLR    = BLACK
BG_CLRS          = [WHITE, LT_ORANGE, LT_YELLOW, LT_GREEN, LT_CYAN, LT_BLUE,
                    LT_PURPLE, LT_MAGENTA, LT_PINK]
BG_CLR_DEFAULT   = 0
GRP_HL_TINT      = 8   # Tint RGB by this value for group highlighting

# Constants below this line influence code operation, change with caution.

# Cell value states
CVS_EMPTY = 0x0000  # Cell value is empty (value = 0)
CVS_ENTER = 0x0001  # Cell has an un-conflicted value in Entry state
CVS_GIVEN = 0x0002  # Cell contains a given value.
CVS_PLACE = 0x0003  # Cell contains a placed value (may or may not be correct)
CVS_CNFLT = 0x0010  # Cell value is conflicted with another in Entry/Solve
CVS_ERROR = 0x0005  # Cell contains an incorrectly solved value
CVS_CANDS = 0x0006  # Candidate values are being displayed in the cell.
CVS_SVGHL = 0x0007  # Same value given highlight (note val cor to CVS_GIVEN)
CVS_SVSHL = 0x0008  # Same value solve highlight (note val cor to CVS_SOLVE)

# Cell state to pen colour relationship.
CVS_CLRS = {CVS_EMPTY: BLACK,
            CVS_ENTER: DK_GREEN,
            CVS_GIVEN: BLACK,
            CVS_PLACE: DK_BLUE,
            CVS_CNFLT: DK_RED,
            CVS_ERROR: RED,
            CVS_CANDS: BLACK,
            CVS_SVGHL: DK_ORANGE,
            CVS_SVSHL: ORANGE}

# Puzzle difficulty levels:
LVL_BEGINNER     = LVL_0 = 0
LVL_NOVICE       = LVL_1 = 1
LVL_INTERMEDIATE = LVL_2 = 2
LVL_PROFICIENT   = LVL_3 = 3
LVL_ACCOMPLISHED = LVL_4 = 4
LVL_EXPERT       = LVL_5 = 5
LVL_GURU         = LVL_6 = 6
LVL_NONE         = LVL_7 = 7  # This level only valid during user entry of
# puzzles, before it is assessed.
LVL_DEFAULT = LVL_PROFICIENT
LVLS = ["Beginner",
        "Novice",
        "Intermediate",
        "Proficient",
        "Accomplished",
        "Expert",
        "Guru",
        " - - "]

# Enable menu list enumerations
EMI_IDLE  = 0
EMI_ENTER = 1
EMI_SOLVE = 2
EMI_PAUSE = 3

# Levels of assistance for Manual solving
AST_FIN_CHECK     = 0    # Check on completion and simply advise if incorrect # and conflicts.
AST_FIN_CNFLTS    = 1    # Only show conflicts on completion
AST_FIN_ERRORS    = 2    # Only show errors on completion
AST_CNFLTS        = 3    # Interactively show cell value conflicts
AST_ERRORS        = 4    # Interactively show cell value errors,
AST_DEFAULT       = AST_ERRORS
AST_LVLS          = ["Check on Finish", "Conflicts on Finish", "Errors on Finish", "Conflicts", "Errors"]
AST_CANDS_DEFAULT = True

# Board layout symmetries
SYM_RAND        = 0        # No symmetry - Random, 1 location
SYM_DIHEDRAL    = 1        # Quadrant diagonal reflected in 8 location
SYM_SQ_QUAD_ROT = 2        # Rotated square quadrants by 90degs, 4 location
SYM_SQ_QUAD_MRD = 3        # Mirrored square quadrants, 4 locations
SYM_DG_QUAD_ROT = 4        # Rotated diagonal quadrants, by 90degs, 4 locations
SYM_DG_QUAD_MRD = 5        # Mirrored diagonal quadrants, 4 locatons
SYM_VERT_ROT    = 6        # Rotated vertical halves by 180degs, 2 locations
SYM_VERT_MRD    = 7        # Mirrored vertical halves, 2 locations
SYM_HORZ_ROT    = 8        # Rotated horizontal halves by 180deg, 2 locs
SYM_HORZ_MRD    = 9        # Mirrored horizontal halves, 2 locs
SYM_DGTL_ROT    = 10       # Diagonal from top left, rotated by 180degs, 2 locs
SYM_DGTL_MRD    = 11       # Diagonal from top left, mirrored, 2 locs
SYM_DGBL_ROT    = 12       # Diagonal from bottom left rotated by 180degs, 2 locs
SYM_DGBL_MRD    = 13       # Diagonal from bottom left mirroed, 2 locs.
SYM_DEFAULT     = SYM_RAND

# State Transition constants
CH = -1  # Can't happen event - An event that is impossible to occur in the specific state.
IG = -2  # Ignore event - An event that can be ignored in a specific state

# Sudoku control state machine events.
EV_SC_GEN = 0   # Auto generate puzzle
EV_SC_ENT = 2   # Enter a puzzle by hand
EV_SC_LD  = 1   # Load puzzle from file
EV_SC_SCR = 9   # Scramble an entered puzzle after entry/loading before validation
EV_SC_MIN = 14  # Minimalise an entered puzzle
EV_SC_SV  = 3   # save event
EV_SC_MSE = 4   # Mouse event
EV_SC_KBD = 5   # Keyboard event
EV_SC_VLD = 6   # Validate givens
EV_SC_SLV = 7   # hand_solve event
EV_SC_PSE = 8   # Pause the hand solving of the current puzzle
EV_SC_ASL = 10  # Auto solve command
EV_SC_HNT = 11  # Hint request
EV_SC_LSN = 12  # List solution
EV_SC_RST = 13  # Restart game with givens
EV_SC_RSP = 15  # Restore a save point.
EV_SC_CND = 16  # Show / clear candidates request
EV_SC_FIN = 17  # Finished puzzle
EV_SC_NR  = 18

# Hint Types
H_VAGUE    = 0
H_CLEARER  = 1
H_CLEAREST = 2

# Names of patterns (conditions) in a puzzle that can be recognised by YAS.
# Note:  that a solving technique (method) may be able to recognise and solve for more than
# one of pattern.  For example the locked singles method in solve_singles can solve
# for both claiming and pointing locked singles, the exposed_pairs and exposed_triples
# also find the locked exposed subsets too, bent_triples finds both Y-Wings and
# XYZ-Wings, bent_quads finds all manner of bent quads included WXYZ-wings, and so on.
# Also Note:  sometimes it has been necessary to force a technique to solve for only
# one of the patterns it can recognise and resolve at a time.  This is necessary to be
# able to prioritise solving techniques, for example resolving Kraken fish is a
# simple AIC extension of finned fish, however in the sequence of solving techniques
# (human) simpler and easier than recognising kraken fish such as the simple AIC's
# should be attempted first.  Otherwize we end up with a solution path that uses much
# more complex techniques to solve a puzzle when simpler methods can be used.
T_UNDEF                     = -1
T_EXPOSED_SINGLE            = 0
T_HIDDEN_SINGLE             = 1
T_CLAIMING_LOCKED_SINGLE    = 2
T_POINTING_LOCKED_SINGLE    = 3
T_EXPOSED_PAIR              = 4
T_LOCKED_EXPOSED_PAIR       = 5
T_HIDDEN_PAIR               = 6
T_EXPOSED_TRIPLE            = 7
T_LOCKED_EXPOSED_TRIPLE     = 8
T_HIDDEN_TRIPLE             = 9
T_EXPOSED_QUAD              = 10
T_HIDDEN_QUAD               = 11
T_X_WING                    = 12
T_SWORDFISH                 = 13
T_JELLYFISH                 = 14
T_FINNED_X_WING             = 15
T_FINNED_SWORDFISH          = 16
T_FINNED_JELLYFISH          = 17
T_SKYSCRAPER                = 18
T_TWO_STRING_KITE           = 19
T_TURBOT_FISH               = 20
T_KRAKEN_X_WING             = 21
T_KRAKEN_SWORDFISH          = 22
T_KRAKEN_JELLYFISH          = 23
T_Y_WING                    = 24
T_W_WING                    = 25
T_KRAKEN_W_WING             = 26
T_XYZ_WING                  = 27
T_WXYZ_WING                 = 28
T_BENT_EXPOSED_QUAD         = 29
T_EMPTY_RECT                = 30
T_X_CHAIN                   = 31
T_X_LOOP                    = 32
T_XY_CHAIN                  = 33
T_CONTINOUS_LOOP            = 34
T_BRUTE_FORCE               = 35
T_NR_TECHS                  = 36

# Technique attribute field enums
TA_TXT  = 0
TA_LVL  = 1
TA_DIFF = 2

# Logic Technique Step Attributes
P_TECH = 0  # The logic technique used
P_PTRN = 1  # Ordered list of cell properties identified for the logic technique
P_OUTC = 2  # Ordered list of cell updates on applying the logic technique
P_DIFF = 3  # The total difficulty of the step
P_SUBS = 4  # Ordered list of sub-steps - a recursion of Step Attributes
P_GRID = 5  # The grid before logic steps.
P_ELIM = 6  # The grid of eliminated candidates before the logic step

# The lexical tokens of for cell description phrases
P_ROW = 10  # cell row index
P_COL = 11  # cell column index or set of cell column indices
P_BOX = 12  # box coords (down, across)
P_OP  = 13  # Operator
P_VAL = 14  # digit 0 - 9
P_SEP = 15  # Separator between cell phrases
P_CON = 16  # Concatinator for combining cell collections
P_END = 17  # End of list of phrases

# Logic technique operator enumerations
OP_POS  = 0   # "?-" Possibility, perhaps something to try
OP_PRES = 1   # "--" Presence of candidate / value in cell
OP_ABS  = 2   # "!-" Absence of candidate in cell.
OP_EQ   = 3   # "==" Presence of only candidates or value in cell
OP_NEQ  = 4   # "!=" Cell cannot assume that value
OP_ASNV = 5   # ":="  Assign value to cell.
OP_ASNC = 6   # "+=" Add candidate to cell.
OP_ELIM = 7   # "-=" Eliminate candidate from cell.
OP_WLK  = 8   # "-"  Weak link
OP_SLK  = 9   # "="  Strong link
OP_WSLK = 10  # "~"  Strong link masquerading as a weak link
OP_CNT  = 11  # "#"  Number of occurrences or count.
OP_PARO = 12  # "("  Opening parenthesis
OP_PARC = 13  # ")"  Closing parenthesis
OP_SETO = 14  # "{"  Opening set
OP_SETC = 15  # "}"  Closing set
OP_NR_OPS = 16

# Puzzle Solution attributes
S_FOUND = 0  # True if found, false otherwise
S_GRID  = 1  # The solved grid if not None.

# Puzzle properties histogram attribute enums
HT_NR    = 0  # Count of logic technique used
HT_TXT   = 1  # Textual name of logic technique
HT_LVL   = 2  # Expertise level of technique
HT_DIFF  = 3  # Difficulty score of the technique
HT_ADIFF = 4  # Accumulated difficulty score

# Puzzle properties
PR_REQ_LVL    = 0  # Requested level of expertise
PR_ACT_LVL    = 1  # Actual level of expertise
PR_NR_HOLES   = 2  # The total number of holes dug
PR_GVN_HISTO  = 3  # Value histogram of the givens
PR_STEPS      = 4  # The list of steps a solution path
PR_HISTO      = 5  # Solution steps histogram
PR_DIFF       = 6  # The difficulty of the puzzle.
PR_GIVENS     = 7  # Grid containing only givens
