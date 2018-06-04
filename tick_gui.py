import ctpif
import gc
import random
import sys
import threading
import time
from ctypes import *
from datetime import datetime
from libnrlib import *
import matplotlib.pyplot as plt
from matplotlib import rcParams

import numpy as np

import anim_bigpic_ctpmdif
import tmath
import trade

# load dll
ctpif_cdll = cdll.LoadLibrary("libctpif.so")

global watch_inst, params, g_array, my_animation


class FigureThread(threading.Thread):
    def __init__(self, m12, params, dcplp):
        super(FigureThread, self).__init__()
        self.m12 = m12
        self.params = params
        self.dcplp = dcplp

    def run(self):
        global my_animation
        my_animation = anim_bigpic_ctpmdif.SubplotAnimation9(
            self.m12, self.params, self.dcplp, None)

        plt.show()


if __name__ == "__main__":
    global watch_inst, params, g_array, my_animation

    gc.disable()
    gc.enable()

    if len(sys.argv) < 5 or len(sys.argv) > 7:
        print '''
              Usage: python tick_gui.py <instrument> <end the trade day>
                                           <data file path> <config path>
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
    dcplp = Dcplp()
    nr_params.min_data_size = int(1024 * 2048 * 1.002)

    m12.set_param(nr_params)
    all_len = m12.get_tick_to_last(data_path, the_date, trade.get_hop(instrument))

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

    #
    # init params of plot
    #
    rc_params = {'legend.fontsize': 'small',
                 'axes.labelsize': 'small',
                 'axes.titlesize': 'small',
                 'xtick.labelsize': 'small',
                 'ytick.labelsize': 'small'}

    for key, value in sorted(rc_params.iteritems()):
        rcParams[key] = value

    params.curpos = start_pos
    while params.curpos <= end_pos:
        m12.do_math(params.curpos)
        dcplp.set_register(params.curpos, m12)
        params.curpos += 1
    params.curpos -= 1

    #
    # start figure gui
    #
    t_figure = FigureThread(m12, params, dcplp)
    t_figure.start()
    time.sleep(15)

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

    print 'Press X and Close figure to quit'

    while params.run_status != -100 and reader_good:
        ret = ctpif.cc_new_data(long(reader), watch_inst, da)
        if ret < 0:
            reader_good = False
            params.run_status = 0
            break

        if da.has_new == 1:
            bar = g_array[da.curpos]
            # print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
            #     da.curpos, da.count, da.isnew, bar[0], bar[1], bar[2], bar[3],
            #     bar[4], bar[5], bar[6])
            candle = CandleBar(bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6])
            m12.append(candle)

            m12.do_math(params.curpos + 1)
            dcplp.set_register(params.curpos + 1, m12)
            m12.do_math(params.curpos + 2)
            dcplp.set_register(params.curpos + 1, m12)

            params.curpos += 2

        time.sleep(0.01)

    #
    # destroy reader
    #
    ctpif_cdll.cc_destroy_reader(reader)

    #
    # close figure
    #
    t_figure.join()
