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

from sys import stderr, path, exit
from time import perf_counter
from inspect import getframeinfo
from os.path import basename

from cpython.pystate cimport PyFrameObject, Py_tracefunc
from cpython cimport PyObject
from cpython.mem cimport PyMem_Malloc, PyMem_Calloc, PyMem_Free

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
    # else:
    #     pass

def TRCX_PANIC(*args, **kwargs):

    Fi = getframeinfo(<object> pPFO)
    print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: PANIC: ", *args, file = stderr, flush = True, **kwargs)
    exit(1)

cdef void TRCX_grid(int G[9][9]):
    cdef int r
    # global TRC
    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: TRCX_grid", file = stderr, flush = True)
        St = ""
        for r in range(9):
            St += f"\n{G[r][0]},{G[r][1]},{G[r][2]},{G[r][3]},{G[r][4]},{G[r][5]},{G[r][6]},{G[r][7]},{G[r][8]}"
        print(f"Grid: {St}", file = stderr, flush = True)

cdef void TRCX_cands(bint C[9][9][9]):
    cdef int r, c, d

    Fi = getframeinfo(<object> pPFO)
    print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: TRCX_cands", file = stderr, flush = True)
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
    print(f"Cands: {St}", file = stderr, flush = True)

cdef void TRCX_memdump(void *Addr, int lenA):
    cdef unsigned int Ofs, i
    cdef unsigned char *B

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: TRCX_Memdump", file = stderr, flush = True)
        if not lenA: lenA = 1
        for Ofs in range(0, lenA+15, 16):
            B = <unsigned char *>(Addr + Ofs)
            St = f"{<long long>B:016x}: {B[0]:02x} {B[1]:02x} {B[2]:02x} {B[3]:02x}  {B[4]:02x} {B[5]:02x} {B[6]:02x} {B[7]:02x} - {B[8]:02x} {B[9]:02x} {B[10]:02x} {B[11]:02x}  {B[12]:02x} {B[13]:02x} {B[14]:02x} {B[15]:02x}  "
            for i in range(16):
                if i == 8: St += " "
                St += f"{chr(B[i])}" if 0x20 <= B[i] <= 0x7f else "."
            print(f"{St}", file = stderr, flush = True)

cdef void TRCX_int_array(object sDesc, int *A, int lenA):
    cdef int i

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        St = ""
        for i in range(lenA):
            if St: St += ", "
            St += f"{A[i]+1}"
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: {sDesc}, [{St}]", file = stderr, flush = True)

cdef void TRCX_coord_array(object sDesc, COORD *A, int lenA):
    cdef int i

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        St = ""
        for i in range(lenA):
            if St: St += ", "
            St += f"({A[i].r+1}, {A[i].c+1})"
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: {sDesc}, [{St}]", file = stderr, flush = True)

cdef void *PyMem_TRCX_Malloc(size_t Bytes):
    cdef void *Mem = PyMem_Malloc(Bytes)

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: PyMem_TRCX_Malloc: 0x{<long long>Mem:016x}: Size: {Bytes}.", file = stderr, flush = True)
    return Mem

cdef void *PyMem_TRCX_Calloc(size_t Nr, size_t Bytes):
    cdef void *Mem = PyMem_Calloc(Nr, Bytes)

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: PyMem_TRCX_Calloc: 0x{<long long>Mem:016x}: Size: {Nr} * {Bytes}.", file = stderr, flush = True)
    return Mem

cdef void PyMem_TRCX_Free(void *Mem):

    if TRC:
        Fi = getframeinfo(<object>pPFO)
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}: PyMem_TRCX_Free: 0x{<long long>Mem:016x}", file = stderr, flush = True)
    PyMem_Free(Mem)
