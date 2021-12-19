# Project wide Cython structs

ctypedef enum LK_STR:
    # strength enums
    LK_NONE_C = 0x0000
    LK_WEAK_C = 0x0001
    LK_STRG_C = 0x0002
    LK_STWK_C = 0x0003
    LK_WKST_C = 0x0007

ctypedef enum LK_ORIENT:
    # orientation enums
    LK_LINE_C = 0x0100
    LK_ROW_C  = 0x0010 | LK_LINE_C
    LK_COL_C  = 0x0020 | LK_LINE_C
    LK_BOX_C  = 0x0040
    LK_CELL_C = 0x0080

ctypedef enum OPERATORS:  # Cell grammar operators  #OP Array in misc.py depends on this order change in tandem.
    OP_POS_C  = 0   # "?-" Possibility, perhaps something to try
    OP_PRES_C = 1   # "--" Presence of candidate / value in cell
    OP_ABS_C  = 2   # "!-" Absence of candidate in cell.
    OP_EQ_C   = 3   # "==" Presence of only candidates or value in cell
    OP_NEQ_C  = 4   # "!=" Cell cannot assume that value
    OP_ASNV_C = 5   # ":="  Assign value to cell.
    OP_ASNC_C = 6   # "+=" Add candidate to cell.
    OP_ELIM_C = 7   # "-=" Eliminate candidate from cell.
    OP_WLK_C  = 8   # "-"  Weak link
    OP_SLK_C  = 9   # "="  Strong link
    OP_WSLK_C = 10  # "~"  Strong link masquerading as a weak link
    OP_CNT_C  = 11  # "#"  Number of occurrences or count.
    OP_PARO_C = 12  # "("  Opening parenthesis
    OP_PARC_C = 13  # ")"  Closing parenthesis
    OP_SETO_C = 14  # "{"  Opening set
    OP_SETC_C = 15  # "}"  Closing set
    OP_NR_OPS_C = 16

ctypedef struct SET3:
    int l
    int v[3]

ctypedef struct SOLN_T:
    int Found
    int SlvdG[9][9]

# Chain nodes for linked lists.
ctypedef struct NODEC:
    int       r, c, Cand
    LK_ORIENT Lk  # Link to next node
    LK_STR    LkSt
    NODEC      *Prev
    NODEC      *Next

ctypedef struct NODE_GL:
    SET3      r, c
    int       Cand
    LK_ORIENT Lk
    LK_STR    LkSt
    NODE_GL   *Prev
    NODE_GL   *Next

ctypedef struct CHAIN:
    NODEC *Start
    NODEC *End

ctypedef struct CHAIN_GL:
    NODE_GL *Start
    NODE_GL *End

# Tree nodes for tree structures for building chains.
ctypedef struct TREE_NODE:
    int             r, c, Cand
    LK_ORIENT       Lk
    CHAIN           Chain
    TREE_NODE       *Parent
    TREE_NODE       *Children[9]
    int             NrChildren

ctypedef struct TREE_NODE_GL:
    SET3            r, c
    int             Cand
    LK_ORIENT       Lk
    CHAIN_GL        Chain
    TREE_NODE       *Parent
    TREE_NODE       *Children[9]
    int             NrChildren


# cdef extern from *:
#     """
#     #include <stdio.h>
#     #define PREFIX_LEN 100
#     #define PREFIX()        make_prefix(sPrefix, PREFIX_LEN, __FILE__, __LINE__, __FUNCTION__)
#
#     static char sPrefix[PREFIX_LEN];
#     char *make_prefix(char *sPrefix, unsigned nLen, const char *sFile, unsigned nLine, const char *sFn)
#     {
#         snprintf(sPrefix, nLen, "%s:%u:%s:", sFile, nLine, sFn);
#         return sPrefix;
#     };
#
#     """
#     char *PREFIX() nogil
