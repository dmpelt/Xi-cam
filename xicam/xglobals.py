import multiprocessing
from collections import OrderedDict

LUT = None
LUTlevels = None
LUTstate = None
plugins = OrderedDict()
pool = None
window = None
lastroi = None
statusbar = None

def load():
    global pool
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()


def hardresetpool():
    global pool
    pool.terminate()
    pool.join()
    pool = multiprocessing.Pool()