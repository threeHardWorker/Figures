from libnrlib import *
import tmath, trade, draw_framework6
import matplotlib.pyplot as plt
from matplotlib import rcParams
import sys, gc, threading, time, random, datetime

def read_save_pos(inst):
    s = False
    str_pos = []
    filepath = '/home/zj/gom/logs/' + inst + '.log'
    with open(filepath) as f:
        for line in f:
            if s:
                str_pos = line.split(',')
                del str_pos[-1]
                s = False
            if line[0] == '[':
                s = True

    pos = []
    for sp in str_pos:
        pos.append(int(sp))

    return pos

if __name__ == "__main__":
    gc.disable()
    gc.enable()

    if (len(sys.argv) != 6):
        print 'Usage: python dl6.py <instrument> <r|the end day> <data file path> <split> <index>\n'
        exit(0)

    instrument = sys.argv[1].encode('ascii')
    thedate = sys.argv[2].encode('ascii')
    datapath = sys.argv[3].encode('ascii') + '/' + instrument
    split = int(sys.argv[4])
    tindex = int(sys.argv[5])
    level = 0

    params = tmath.Params()
    ppps = NRParams()

    params.run_status = 0
    params.delta = 1
    params.inst = instrument
    params.date = thedate
    params.data_len = 1024
    params.level = level
    params.imgpath = '/app/sean/tmp'

    m12 = Math12()
    if instrument == 'rb888':
        # ppps.min_data_size = int(1024 * 2048 * 1.0000005)
        ppps.min_data_size = int(1024 * 2048 * 3)
    else:
        ppps.min_data_size = int(1024 * 2048 * 1.5)

    m12.set_param(ppps)
    all_len = m12.get_data_from_file(instrument, datapath, thedate, trade.get_hop(instrument))
    shot = Snapshot()

    inst_code = trade.get_instrument_code(instrument)

    g_trader = None

    rc_params = {'legend.fontsize': 'small',
                 'axes.labelsize': 'small',
                 'axes.titlesize': 'small',
                 'xtick.labelsize': 'small',
                 'ytick.labelsize': 'small'}

    for key, value in sorted(rc_params.iteritems()):
        rcParams[key] = value

    draw = draw_framework6.DrawFramework6(m12, shot, g_trader, params, 0)

    amount = all_len - params.minlen - 2048
    pice = int(float(amount)/float(split))
    spos = params.minlen + 2048 + pice * tindex
    epos = spos + pice
    if spos - 1000 < params.minlen + 2048:
        spos = params.minlen + 2048
    else:
        spos = spos - 1000

    if epos >= all_len:
        epos = all_len - 1

    if tindex == split - 1:
        epos = all_len - 1


    print inst_code, 'from', spos, 'to', epos

    save_pos = read_save_pos(inst_code)
    print len(save_pos)

    for pos in range(spos, epos):
        m12.do_math(pos)
        changed = m12.inflexion_changed(level)
        if changed != 0:
           if 4 == m12.get_resonance_level(pos, level):
               shot.ClearSnapshot()
               shot.TakeSnapshot(pos, level, m12)

        if pos in save_pos:
            #shot.ClearSnapshot()
            #shot.TakeSnapshot(pos, level, m12)

            draw.draw_frame(pos)
            draw.save_frame()

            save_pos.remove(pos)

    print 'Done.'
