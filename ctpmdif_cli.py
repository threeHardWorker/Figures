import ctpif
import gc
import random
import sys
import time
from ctypes import *
from datetime import datetime
from libnrlib import *

import numpy as np

import tmath
import trade

# load dll
ctpif_cdll = cdll.LoadLibrary("libctpif.so")

global watch_inst, params, g_array

'''
def got_new_data_fun(inst, curpos, count, last_pos, last_total, its_new):
    global watch_inst, params, g_array
    if inst != watch_inst:
        return
    # print inst, curpos, count, last_pos, last_total, its_new
    bar = g_array[curpos]

    if its_new == 1:
        params.curpos += 1
        print 'got new data fun', params.curpos

    time.sleep(params.interval)

    # print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
    #    curpos, count, its_new, bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6])
'''

if __name__ == "__main__":
    global watch_inst, params

    gc.disable()
    gc.enable()

    if len(sys.argv) < 5 or len(sys.argv) > 7:
        print '''
              Usage: python ctpmdif_cli.py <instrument> <end the trade day>
              <data file path> <config path> [r | start datetime]
              '''
        exit(0)

    params = tmath.Params()

    watch_inst = sys.argv[1].encode('ascii')
    instrument = trade.get_instrument_cc(watch_inst)

    the_date = sys.argv[2].encode('ascii')
    data_path = sys.argv[3].encode('ascii') + '/' + instrument
    conf_path = sys.argv[4].encode('ascii')

    params.run_status = 0
    params.delta = 1
    params.inst = watch_inst
    params.date = the_date
    params.data_len = 1024
    hop = trade.get_hop(instrument)

    nr_params = NRParams()
    m12 = Math12()
    nr_params.min_data_size = int(1024 * 2048 * 1.02)

    m12.set_param(nr_params)
    all_len = m12.get_data_from_file(instrument, data_path, the_date, trade.get_hop(instrument))

    #
    # Get Start position of index and Ending-position of index
    #
    end_pos = 0
    start_pos = 0

    if len(sys.argv) == 5:
        end_pos = all_len - 1
        start_pos = params.minlen + 2048
    elif len(sys.argv) > 5:
        if sys.argv[5] == 'r':
            random.seed(datetime.datetime.now())
            start_pos = int(random.random() * (all_len - params.minlen) + params.minlen)
        else:
            start_pos = int(sys.argv[5])
            if start_pos < params.minlen + 2048:
                start_pos = params.minlen + 2048

        if len(sys.argv) == 7:
            end_pos = int(sys.argv[6])
        else:
            end_pos = all_len - 1

    params.all_len = all_len
    print 'all data', all_len, 'start from', start_pos, 'to ', end_pos

    for i in range(start_pos, all_len):
        m12.do_math(i)

    params.curpos = end_pos

    #
    # Get Ctp Data Reader
    #
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
    params.run_status = 1

    while params.run_status > 0 and reader_good:
        ret = ctpif.cc_new_data(long(reader), watch_inst, da)
        if ret < 0:
            reader_good = False
            params.run_status = 0
            break

        if da.has_new == 1:
            bar = g_array[da.curpos]
            print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
                da.curpos, da.count, da.isnew, bar[0], bar[1], bar[2], bar[3],
                bar[4], bar[5], bar[6])

            m12.append(CandleBar(bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6]))

            m12.do_math(params.curpos + 1)
            params.curpos += 1

            m12.do_math(params.curpos + 1)
            params.curpos += 1

        time.sleep(0.01)

    #
    # destroy reader
    #
    ctpif_cdll.cc_destroy_reader(reader)
