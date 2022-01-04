# trc.pyx - TRCX functionality.
# This module is functional for both python interpreted code and Cython code that has been
# compiled with:
#   #   "cython: linetrace=True" and
#   #   "cython: distutils: define_macros=CYTHON_TRACE_NOGIL=1"
# and when imported with "from trc import TRCX" in the compiled module needing to be traced.
#
# The back-end simply utilises Python's Py_tracefunc callback to write the captured frame into the
# globally defined pointer pPFO.  This callback occurs for every line of interpreted or Cython
# source code, so overhead needs to be minimal.
#
# The second part of this module is the TRCX function which pulls the file, line, and
# function name from *pPFO.
#
# TRCX is switched on/off under control of boolean TRC switch defined in globals.py.
# Switching TRCX off stubs out the TRCX function and does not install the callback on startup.
#
# Note:
#   1.  PyCharm incorrectly errors the syntax of the print statement in its Cython support.
#   2.  The gcc warns because of the incorrect Cython generated C code from Cython which had no
#       consequence here and can be ignored.

from sys import stderr, path
from time import perf_counter
from inspect import getframeinfo
from os.path import basename

from cpython.pystate cimport PyFrameObject, Py_tracefunc
from cpython cimport PyObject

from trc cimport *

# Hack using the end of sys.path to carry truly global vars across modules.
TRC = True if path[len(path)-1] == ".trc_true" else False

cdef extern from "frameobject.h":
    pass
cdef extern from *:
    void PyEval_SetTrace(Py_tracefunc, o)

cdef PyFrameObject *pPFO

cdef int linetrace_cb(PyObject* o, PyFrameObject* frame, int what, PyObject* arg) nogil:
    global pPFO
    pPFO = frame

if TRC: PyEval_SetTrace(linetrace_cb, None)

def TRCX(*args, **kwargs):
    global TRC
    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}:", *args, file = stderr, flush = True, **kwargs)
    else:
        pass

cdef str trc_grid(int G[9][9]):
    cdef int r

    St = ""
    for r in range(9):
        St +=f"\n{G[r][0]},{G[r][1]},{G[r][2]},{G[r][3]},{G[r][4]},{G[r][5]},{G[r][6]},{G[r][7]},{G[r][8]}"
    return St

cdef str trc_cands(bint C[9][9][9]):
    cdef int r, c, d

    St = ""
    for r in range(9):
        St1 = ""
        for c in range(9):
            St2 = ""
            for d in range(9):
                if C[r][c][d]: St2 += f"{d+1}"
                else: St2 += "."
            if St1: St1 += ","
            St1 += f"[{St2}]"
        St += f"\n{St1}"
    return St