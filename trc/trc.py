from sys import stderr, path
from time import perf_counter
from inspect import getframeinfo, stack
from os.path import basename

# Hack using the end of sys.path to carry truly global vars across modules.
TRC = True if path[-1] == ".trc_true" else False

def TRCX(*args, **kwargs):
    global TRC
    if TRC:
        Fi = getframeinfo(stack()[1][0])
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}:", *args, file = stderr, flush = True, **kwargs)
    else:
        pass

