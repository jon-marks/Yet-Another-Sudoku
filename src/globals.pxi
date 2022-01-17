# Used for Cython defines and other compile time specifications

DEF SIZEOF_GRID = 324  # bytes 9 x 9 x 4
DEF SIZEOF_CANDS = 2916 # bytes 9 x 9 x 9 x 4

DEF SLVR_TECHS = 8

# Misc readability defines
DEF ROW = 0
DEF COL = 1
DEF POINTING = 0
DEF CLAIMING = 1

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

