from libnrlib import *
import tmath, trade, animation9
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys, gc, threading, time, random, datetime


def read_pos_from_file(inst):
    s = False
    str_pos = []
    # filepath = './logs/' + inst + '.log'
    filepath = '/app/sean/bin/gom/bin/v6-logs/v6-4-6-logs/' + inst + '.log'
    # filepath = '/app/sean/bin/gom/bin/v3-3-logs/' + inst + '.log'

    with open(filepath) as f:
        for line in f:
            if s:
                str_pos = line.split(',')
                del str_pos[-1]
                s = False
            if line.startswith('['):
                s = True
            if line.startswith(']'):
                break

    pos = []
    for sp in str_pos:
        pos.append(int(sp))

    print 'got', len(pos), 'points'
    return pos


class FigureThread(threading.Thread):
    def __init__(self, m12, params, dcplp, stop_pos):
        super(FigureThread, self).__init__()
        self.m12 = m12
        self.params = params
        self.dcplp = dcplp
        self.stop_pos = stop_pos

    def run(self):
        ani_lines1 = animation9.SubplotAnimation9(self.m12, self.params, 0, self.dcplp, self.stop_pos)

        # self.ani_dash = Dashboard(self.dm)
        plt.show()


if __name__ == "__main__":
    gc.disable()
    gc.enable()

    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print 'Usage: python cppmath.py <instrument> <r|the end day> <data file path> [start pos] [end pos]\n'
        exit(0)

    instrument = sys.argv[1].encode('ascii')
    thedate = sys.argv[2].encode('ascii')
    datapath = sys.argv[3].encode('ascii') + '/' + instrument

    params = tmath.Params()
    ppps = NRParams()

    params.run_status = 0
    params.delta = 1
    params.inst = instrument
    params.date = thedate
    params.data_len = 1024

    m12 = Math12()
    if instrument == 'rb888':
        #     # ppps.min_data_size = int(1024 * 2048 * 1.0000005)
        ppps.min_data_size = int(1024 * 2048 * 3)
    else:
        ppps.min_data_size = int(1024 * 2048 * 1.5)
    # ppps.min_data_size = int(1024 * 2048 *1.005)

    m12.set_param(ppps)
    all_len = m12.get_data_from_file(instrument, datapath, thedate, trade.get_hop(instrument))

    trade.get_instrument_code(instrument)

    epos = 0
    spos = 0

    if len(sys.argv) == 4:
        epos = all_len - 1
        spos = params.minlen + 2048
    elif len(sys.argv) > 4:
        if sys.argv[4] == 'r':
            random.seed(datetime.datetime.now())
            spos = int(random.random() * (all_len - params.minlen) + params.minlen)
        else:
            spos = int(sys.argv[4])
            if spos < params.minlen + 2048:
                spos = params.minlen + 2048

        if len(sys.argv) == 6:
            epos = int(sys.argv[5])
        else:
            epos = all_len - 1

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

    inst_code = trade.get_instrument_code(instrument)
    # stop_pos = read_pos_from_file(inst_code)
    stop_pos = []

    # spos = stop_pos[random.randint(0, len(stop_pos)- 10) + 5 - 1] - 1
    print 'all data', all_len, 'start from', spos, 'to ', epos
    params.curpos = spos

    m12.do_math(params.curpos)

    dcplp = Dcplp()
    dcplp.set_register(params.curpos, m12)

    t_figure = FigureThread(m12, params, dcplp, stop_pos)
    t_figure.start()

    # params.curpos += 1
    params.run_status = 0

    while params.run_status >= 0 and params.curpos <= epos:
        if params.run_status == 1:
            m12.do_math(params.curpos)
            dcplp.set_register(params.curpos, m12)

            if params.curpos in stop_pos:
                print params.curpos,
                s = str(raw_input("Enter to continue:"))

            params.curpos += params.delta

        time.sleep(params.interval)

    print 'Press X and Close figure to quit'
    t_figure.join()
