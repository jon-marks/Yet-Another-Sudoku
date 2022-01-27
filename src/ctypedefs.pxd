# Project wide Cython structs

include "globals.pxi"


ctypedef struct COORD:
    int r, c

ctypedef struct SET3:
    int l
    int v[3]

ctypedef struct SOLN_T:
    int Found
    int SlvdG[9][9]

# Chain nodes for linked lists.

ctypedef struct OUTCOME:
    int     r, c, Op, Cand
    OUTCOME *Prev
    OUTCOME *Next

ctypedef struct NODE:
    int     r, c, Cand
    int     Lk
    NODE    *Prev
    NODE    *Next

ctypedef struct NODE_GL:
    SET3    r, c
    int     Cand
    int     Lk
    NODE_GL *Prev
    NODE_GL *Next

ctypedef struct CHAIN:
    NODE    *Start
    NODE    *End
    NODE_GL *StartGL
    NODE_GL *EndGL
    CHAIN   *Prev
    CHAIN   *Next
# ctypedef struct CHAIN:
#     NODE *Start
#     NODE *End
#
# ctypedef struct CHAIN_GL:
#     NODE_GL *Start
#     NODE_GL *End

# Tree nodes for tree structures for building chains.
# ctypedef struct TREE_NODE:
#     int             r, c, Cand, Lk
#     CHAIN           Chain
#     TREE_NODE       *Parent
#     TREE_NODE       *Children[9]
#     int             NrChildren
#
# ctypedef struct TREE_NODE_GL:
#     SET3            r, c
#     int             Cand, Lk
#     CHAIN_GL        Chain
#     TREE_NODE       *Parent
#     TREE_NODE       *Children[9]
#     int             NrChildren


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
