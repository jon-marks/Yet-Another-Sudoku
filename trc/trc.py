from sys import stderr
from time import perf_counter
from inspect import getframeinfo, stack
from os.path import basename

from globals import TRC

if TRC:
    def TRCX(*args, **kwargs):
        Fi = getframeinfo(stack()[1][0])
        print(f"{perf_counter():0.6f}:{basename(Fi.filename)}:{Fi.lineno}:{Fi.function}:", *args, file = stderr, flush = True, **kwargs)
else:
    def TRCX(*args, **kwargs):
        pass
