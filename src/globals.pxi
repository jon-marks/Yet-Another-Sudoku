# Used for Cython defines and other compile time specifications

DEF SIZEOF_GRID = 324  # bytes 9 x 9 x 4
DEF SIZEOF_CANDS = 2916 # bytes 9 x 9 x 9 x 4

DEF SLVR_TECHS = 8

DEF RECURSE_LIM_C = 10

# Misc readability defines
DEF ROW = 0
DEF COL = 1
DEF POINTING = 0
DEF CLAIMING = 1

# Technique Extensions flags:
DEF T_KRAKEN_C   = 0x00000100
DEF T_GRPLK_C    = 0x00000200
DEF T_SASHIMI_C  = 0x00000400

    # link strengths
DEF LK_NONE_C = 0x0000
DEF LK_WEAK_C = 0x0001
DEF LK_STRG_C = 0x0002
DEF LK_STWK_C = 0x0003
DEF LK_WKST_C = 0x0007

    # link types / orientations
DEF LK_LINE_C = 0x0100
DEF LK_ROW_C  = (0x0010 | LK_LINE_C)
DEF LK_COL_C  = (0x0020 | LK_LINE_C)
DEF LK_BOX_C  = 0x0040
DEF LK_CELL_C = 0x0080

DEF OP_NONE_C = 0   # ""
DEF OP_POS_C  = 1   # "?-" Possibility, perhaps something to try
DEF OP_PRES_C = 2   # "--" Presence of candidate / value in cell
DEF OP_ABS_C  = 3   # "!-" Absence of candidate in cell.
DEF OP_EQ_C   = 4   # "==" Presence of only candidates or value in cell
DEF OP_NEQ_C  = 5   # "!=" Cell cannot assume that value
DEF OP_ASNV_C = 6   # ":="  Assign value to cell.
DEF OP_ASNC_C = 7   # "+=" Add candidate to cell.
DEF OP_ELIM_C = 8   # "-=" Eliminate candidate from cell.
DEF OP_WLK_C  = 9   # "-"  Weak link
DEF OP_SLK_C  = 10  # "="  Strong link
DEF OP_WSLK_C = 11  # "~"  Strong link masquerading as a weak link
DEF OP_CNT_C  = 12  # "#"  Number of occurrences or count.
DEF OP_PARO_C = 13  # "("  Opening parenthesis
DEF OP_PARC_C = 14  # ")"  Closing parenthesis
DEF OP_SETO_C = 15  # "{"  Opening set
DEF OP_SETC_C = 16  # "}"  Closing set
DEF OP_NR_OPS_C = 17

# States when searching for chains in trees being grown.
DEF SEARCHING       = 0  # Still looking for a chain.
DEF FOUND           = 1  # Chain has been found
DEF NOT_FOUND       = 2  # No more nodes to create chain
DEF BOTTOMED_OUT    = 4  # recursion limit reached before finding chain or running out of nodes.

