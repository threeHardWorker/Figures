import tmath, trade, animation9
from libnrlib import *
from ctypes import *
import ctpmdif
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import sys, gc, threading, time, random, datetime
from datetime import datetime

# load dll
ctpif_cdll = cdll.LoadLibrary("libctpif.so")

global watch_inst, gdm, params, gca, g_array, ani_lines


# the Candle Bar
class CandleBar(Structure):
    _fields_ = [("key", c_double),
                ("open", c_double),
                ("high", c_double),
                ("low", c_double),
                ("close", c_double),
                ("vol", c_double),
                ("interest", c_double)]

    def to_string(self, its_new):
        print its_new, self.key, self.open, self.high, self.low, self.close, self.vol, self.interest


def got_new_data_fun(inst, curpos, count, last_pos, last_total, its_new):
    global watch_inst, gdm, params, gca, g_array
    if inst != watch_inst:
        return
    # print inst, curpos, count, last_pos, last_total, its_new
    bar = garray[curpos]

    for i in range(0, len(gdm)):
        gdm[i].add_new_data(bar[2], bar[3], its_new)
        gdm[i].do_math(params.curpos + 1)

    if its_new == 1:
        params.curpos += 1
        print 'got new data fun', params.curpos

    time.sleep(params.interval)

    # print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
    #    curpos, count, its_new, bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6])


class FigureThread(threading.Thread):
    def __init__(self, dm, params, save_pos, trade=None):
        super(FigureThread, self).__init__()
        self.dm = dm
        self.trade = trade
        self.params = params
        self.save_pos = save_pos

    def run(self):
        global ani_lines
        ani_lines = animation9.SubplotAnimation9(self.dm, self.params, 0, self.save_pos)

        # self.ani_dash = Dashboard(self.dm)
        plt.show()


if __name__ == "__main__":
    global watch_inst, gdm, params, ani_lines

    gc.disable()
    gc.enable()

    if (len(sys.argv) != 4 and len(sys.argv) != 5):
        print 'Usage: python rtgame.py <instrument> <end the trade day> <data file path> [r | start datetime]'
        exit(0)

    params = tmath.Params()

    watch_inst = sys.argv[1].encode('ascii')
    instrument = trade.get_instrument_cc(watch_inst)

    thedate = sys.argv[2].encode('ascii')
    datapath = sys.argv[3].encode('ascii') + '/' + instrument

    params.run_status = 0
    params.delta = 1
    params.inst = watch_inst
    params.date = thedate
    params.data_len = 1024

    pointer, price, all_len, allx, the_date = \
        tmath.get_data_from_file(instrument, datapath, thedate, \
                                 params.min_data_size, params.predict_len)
    if (pointer == 0) or (all_len < params.min_data_size):
        exit(-100)

    params.all_len = all_len

    if len(sys.argv) != 5:
        spos = params.minlen
    elif sys.argv[4] == 'r':
        random.seed(datetime.now())
        spos = int(random.random() * (all_len - params.minlen) + params.minlen)
    else:
        dt = sys.argv[4].encode('ascii')
        spos = get_time_pos(pointer, dt)
        if spos < 0:
            print 'error when get time pos'
            exit(-101)
        elif spos < params.minlen:
            print 'less than minlen'
            exit(-102)

    print 'all data', all_len, 'start from ', spos

    params.curpos = spos

    # g_trader = trade.get_trader(trade_name)
    # g_trader.set_dm(dm)
    g_trader = None

    gdm = []
    power = 1
    lendm = 12
    hop = trade.get_hop(instrument)
    for i in range(0, lendm):
        gdm.append(tmath.DataMath(price, all_len, allx, the_date, hop, params))
        gdm[i].down_sample(2 * power)
        power *= 2

    # opq = str(raw_input("enter something to draw: (q = quit)"))
    # if (opq == 'q'):
    #    exit(0)

    rc_params = {'legend.fontsize': 'small',
                 'axes.labelsize': 'small',
                 'axes.titlesize': 'small',
                 'xtick.labelsize': 'small',
                 'ytick.labelsize': 'small'}

    for key, value in sorted(rc_params.iteritems()):
        rcParams[key] = value

    for i in range(0, len(gdm)):
        gdm[i].do_math(params.curpos)

    save_pos = [all_len - 1]
    t_figure = FigureThread(gdm, params, save_pos, g_trader)
    t_figure.start()


    if len(save_pos) > 0:
        last_pos = save_pos[-1] + 1
    else:
        last_pos = all_len

    # params.run_status = 1
    while params.run_status >= 0 and params.curpos < last_pos:
        if params.run_status == 1:
            for i in range(0, len(gdm)):
                gdm[i].do_math(params.curpos)

            if params.curpos in save_pos:
                time.sleep(3)

            # g_trader.do_trade(instrument, g_curpos)
            params.curpos += params.delta

        time.sleep(params.interval)

    # if g_trader is not None:
    #    g_trader.closePosition(instrument, params.curpos - 1)
    #    g_trader.print_trade()


    # pos = 1024 * 10 * 10
    # for i in range(0, 10):
    #  ani.draw_frame(pos + i)

    # initialize a reader with a json configure file
    # reader = ctpif_cdll.cc_init_reader('/app/sean/bin/gom/conf/gmd-datasim.json')
    reader = ctpif_cdll.cc_init_reader('/app/sean/bin/gom/conf/gmd-9-lyj.json')

    # get max data length
    datalen = ctpif_cdll.cc_get_maxlen(reader)

    # get interface of buffer-pointer
    cc_get_bufptr = ctpif_cdll.cc_get_bufptr
    cc_get_bufptr.restype = POINTER(c_double)

    # get buffer pointer to rb1801
    bufptr = cc_get_bufptr(reader, watch_inst)

    # convert to numpy matrix
    # naptr = cast(bufptr, )
    g_array = np.ctypeslib.as_array(bufptr, shape=(datalen, 7))

    # convert to dataframe
    # df = pd.DataFrame(na)

    # converto to array of CandleBar
    # CandleArray = CandleBar * datalen;
    # cc_get_bufptr.restype = POINTER(CandleArray)
    # candle_ptr = cc_get_bufptr(reader, watch_inst)
    # gca = candle_ptr.contents

    # ctpif.cc_got_new_data(long(reader), got_new_data_fun, '', 0L, 0L, 0L, 0L, 0)
    reader_good = True
    da = ctpmdif.DataAmount()
    while params.run_status > 0 and reader_good:
        ret = ctpmdif.cc_new_data(long(reader), watch_inst, da)
        if ret < 0:
            reader_good = False
            params.run_status = 0
            break

        if da.has_new == 1:
            bar = g_array[da.curpos]
            # print '%d, %d | %d > %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' % (
            #   da.curpos, da.count, da.isnew, bar[0], bar[1], bar[2], bar[3], bar[4], bar[5], bar[6])

            for i in range(0, len(gdm)):
                gdm[i].add_new_data(bar[2], bar[3], da.isnew)
                gdm[i].do_math(params.curpos + 1)

            if da.isnew == 1:
                params.curpos += 2

        time.sleep(0.01)

    # destroy reader
    ctpif_cdll.cc_destroy_reader(reader)

    tmath.release_time_pos_map(pointer)
    print 'Close figure to quit'

    t_figure.join()
