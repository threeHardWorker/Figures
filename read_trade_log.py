import matplotlib.pyplot as plt
import gc
from libnrlib import *
import trade

class Position:
    def __init__(self, pos=0, price=0, money=0, ftime=0, hop_rev=0, rev=0):
        self.pos = int(pos)
        self.price = float(price)
        self.money = float(money)
        self.ftime = float(ftime)
        self.hop_rev = float(hop_rev)
        self.rev = float(rev)

    def show(self):
        print self.pos, self.price, self.money, self.ftime, self.hop_rev, self.rev


if __name__ == "__main__":
    gc.disable()
    gc.enable()

    ol = []
    os = []
    cl = []
    cs = []

    instrument = 'jm888'
    thedate = '20171108'
    datapath = '/app/sean/bak/tick/online'
    logpath = '/app/sean/kp/q7-1-1/tick/x-' + instrument + '.log'
    datapath += '/' + instrument

    with open(logpath) as fp:
        for line in fp:
            s = line.split(',')
            if len(s) == 8:
                if s[2] == '1':
                    ol.append(Position(s[3], s[4], s[5], s[7]))
                else:
                    os.append(Position(s[3], s[4], s[5], s[7]))
            elif len(s) == 11:
                if s[2] == '1':
                    cl.append(Position(s[3], s[5], 0, s[10], s[6], s[7]))
                else:
                    cs.append(Position(s[3], s[5], 0, s[10], s[6], s[7]))

    m12 = Math12()
    m12_params = NRParams()

    if instrument == 'rb888':
        m12_params.min_data_size = int(1024 * 2048 * 3)
    else:
        m12_params.min_data_size = int(1024 * 2048 * 1.5)

    m12.set_param(m12_params)
    all_len = m12.get_tick_from_file(datapath, thedate, trade.get_hop(instrument))
    if all_len < 0:
        exit(-1)

    s_pos = 1024 * 2048 + 2048
    e_pos = all_len - 1

    allx = list(range(s_pos, e_pos + 1))
    price = []
    m12.get_price(price, 0)

    plt.plot(allx, price[s_pos:])
    x = []
    y = []
    for p in ol:
        x.append(p.pos)
        y.append(p.price)
    plt.plot(x, y, 'rx')

    del(x[:])
    del(y[:])
    for p in os:
        x.append(p.pos)
        y.append(p.price)
    plt.plot(x, y, 'gx')

    del(x[:])
    del(y[:])
    for p in cl:
        x.append(p.pos)
        y.append(p.price)
    plt.plot(x, y, 'ro')

    del(x[:])
    del(y[:])
    for p in cs:
        x.append(p.pos)
        y.append(p.price)
    plt.plot(x, y, 'go')

    plt.show()

