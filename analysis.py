from libnrlib import *
import tmath, trade, animation_analysis
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys, gc, threading, time, random, datetime



class FigureThread(threading.Thread):
    def __init__(self, m12, params, dcplp, epos, stop_pos, trade = None):
        super(FigureThread, self).__init__()
        self.m12 = m12
        self.trade = trade
        self.params = params
        self.dcplp = dcplp
        self.stop_pos = stop_pos
        self.epos = epos

    def run(self):
        ani_lines1 = animation_analysis.SubplotAnimation(self.m12, self.trade,
                      self.params, 0, self.dcplp, self.epos, self.stop_pos)

        # self.ani_dash = Dashboard(self.dm)
        plt.show()



if __name__ == "__main__":
    gc.disable()
    gc.enable()

    if (len(sys.argv) < 4 or len(sys.argv) > 6):
        print 'Usage: python cppmath.py <instrument> <r|the end day> <data file path> [start pos] [end pos]\n'
        exit(0)

    instrument = sys.argv[1].encode('ascii')
    thedate = sys.argv[2].encode('ascii')
    datapath = sys.argv[3].encode('ascii') + '/' + instrument
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
    all_len = m12.get_data_from_file(instrument, datapath, thedate, trade.get_hop(instrument))

    trade.get_instrument_code(instrument)

    epos = 0
    spos = 0

    if (len(sys.argv) == 4):
        epos = all_len - 1
        spos = params.minlen + 2048
    elif (len(sys.argv) > 4):
        if sys.argv[4] == 'r':
            random.seed(datetime.datetime.now())
            spos = int(random.random() * (all_len - params.minlen) + params.minlen)
        else:
            spos = int(sys.argv[4])
            if spos < params.minlen + 2048:
                spos = params.minlen + 2048

        if (len(sys.argv) == 6):
            epos = int(sys.argv[5])
        else:
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
    stop_pos = []

    print 'all data', all_len, 'start from', spos, 'to ', epos
    params.curpos = spos

    m12.do_math(params.curpos)

    dcplp = Dcplp()
    dcplp.set_register(params.curpos, m12)

    t_figure = FigureThread(m12, params, dcplp, epos, stop_pos, g_trader)
    t_figure.start()

    # params.curpos += 1
    params.run_status = 1

    while params.run_status >= 0 and params.curpos <= epos:
        if params.run_status == 1:
            # print params.curpos
            m12.do_math(params.curpos)
            dcplp.set_register(params.curpos, m12)

            params.curpos += params.delta

        time.sleep(params.interval)

    print 'Press X and Close figure to quit'
    t_figure.join()
