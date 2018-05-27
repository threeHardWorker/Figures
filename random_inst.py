from libnrlib import *
import tmath, trade, animation8
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys, gc, threading, time, random, datetime


def get_random_instrument():
    ic = ['a9888',
      'ag888',
      'al888',
      'au888',
      'bu888',
      'c9888',
      'CF888',
      'cu888',
      'FG888',
      'i9888',
      'j9888',
      'jm888',
      'l9888',
      'm9888',
      'MA888',
      'ni888',
      'OI888',
      'p9888',
      'rb888',
      'RM888',
      'SR888',
      'TA888',
      'v9888',
      'y9888',
      'zn888']
    return ic[random.randint(0, len(ic) - 1)]


def read_pos_from_file(inst):
    s = False
    str_pos = []
    # filepath = './logs/' + inst + '.log'
    filepath = '/app/sean/bin/gom/bin/v5-1-3-logs/' + inst + '.log'
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
    def __init__(self, m12, shot, params, dcplp, stop_pos, trade = None):
        super(FigureThread, self).__init__()
        self.m12 = m12
        self.shot = shot
        self.trade = trade
        self.params = params
        self.dcplp = dcplp
        self.stop_pos = stop_pos

    def run(self):
        ani_lines1 = animation8.SubplotAnimation8(self.m12, self.shot, self.trade, self.params, 0, self.dcplp, self.stop_pos)

        # self.ani_dash = Dashboard(self.dm)
        plt.show()



if __name__ == "__main__":
    gc.disable()
    gc.enable()

    instrument = get_random_instrument()
    thedate = '20171108'
    datapath = '/app/sean/data/10s_candle_bindata'
    trade_name = ''

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
    datapath += '/' + instrument
    all_len = m12.get_data_from_file(instrument, datapath, thedate, trade.get_hop(instrument))
    shot = None

    trade.get_instrument_code(instrument)

    epos = all_len - 1
    g_trader = None


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
    stop_pos = read_pos_from_file(inst_code)
    # stop_pos = [
    # ]

    spos = stop_pos[random.randint(0, len(stop_pos)- 10) + 5 - 1] - 1
    print 'all data', all_len, 'start from', spos, 'to ', epos
    params.curpos = spos

    m12.do_math(params.curpos)

    dcplp = Dcplp()
    dcplp.set_register(params.curpos, m12)

    t_figure = FigureThread(m12, shot, params, dcplp, stop_pos, g_trader)
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
