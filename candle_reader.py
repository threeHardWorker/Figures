import ctpif
import gc
import random
import sys
import threading
import time
from ctypes import *
from datetime import datetime
from libnrlib import *

import numpy as np

# load dll
ctpif_cdll = cdll.LoadLibrary("libctpif.so")

global watch_inst, g_array


if __name__ == "__main__":
    global watch_inst, g_array
    gc.disable()
    gc.enable()

    watch_inst = 'rb1810'
    conf_path = '/app/sean/bin/gom/conf/gmd-9-lyj.json'

    print 'get reader'
    reader = ctpif_cdll.cc_init_reader(conf_path)
    # get max data length
    data_length = ctpif_cdll.cc_get_maxlen(reader)
    print 'max data length ', data_length

    # get interface of buffer-pointer
    cc_get_bufptr = ctpif_cdll.cc_get_bufptr
    cc_get_bufptr.restype = POINTER(c_double)

    # get buffer pointer to rb1801
    buf_ptr = cc_get_bufptr(reader, watch_inst)

    # convert to numpy matrix
    # naptr = cast(bufptr, )
    g_array = np.ctypeslib.as_array(buf_ptr, shape=(data_length, 7))

    reader_good = True
    da = ctpif.DataAmount()

    count = 0
    ftime = 0
    while count < 10:
        ret = ctpif.cc_new_data(long(reader), watch_inst, da)
        if ret < 0:
            reader_good = False
            break

        if da.has_new == 1:
            bar = g_array[da.curpos]
            if bar[0] > ftime:
                print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
                      da.curpos, da.count, da.isnew, bar[0], bar[1], bar[2], bar[3],
                      bar[4], bar[5], bar[6])
                candle = CandleBar(bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6])

                count += 1

                ftime = bar[0]

        time.sleep(0.01)

    #
    # destroy reader
    #
    ctpif_cdll.cc_destroy_reader(reader)
