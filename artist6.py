import matplotlib.pyplot as plt
import tmath
from libnrlib import *

m_data_len = 1024
m_predict_len = 128


class Artist6:
    def __init__(self, m12, shot, ax, name, level):
        self.m12 = m12
        self.shot = shot
        self.name = name
        self.ax = ax
        self.level = level
        self.down_int = m12.get_down_int(level)
        self.top_pos = 0

        self.price = []
        m12.get_hop_price(self.price, level)
        self.allx = list(range(0, len(self.price) + m_predict_len))

        self.ax.set_xlim([0, m_data_len + m_predict_len])
        self.ax.set_ylim([min(self.price[0: m_data_len]),
                          max(self.price[0: m_data_len])])

        self.pls = []
        colors = [(13.0 / 255.0, 57.0 / 255.0, 0.0 / 255.0),
                  (21.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0),
                  (29.0 / 255.0, 125.0 / 255.0, 0.0 / 255.0),
                  (35.0 / 255.0, 155.0 / 255.0, 0.0 / 255.0),
                  (44.0 / 255.0, 196.0 / 255.0, 0.0 / 255.0),
                  (51.0 / 255.0, 227.0 / 255.0, 0.0 / 255.0),
                  (63.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0),
                  (97.0 / 255.0, 255.0 / 255.0, 51.0 / 255.0),
                  (156.0 / 255.0, 255.0 / 255.0, 128.0 / 255.0),
                  (194.0 / 255.0, 255.0 / 255.0, 176.0 / 255.0)
                  ]
        change_pnt_color = (128.0 / 255.0, 28.0 / 255.0, 188.0 / 255.0)
        # self.params.queue_pl_size
        for i in range(10):
            l, = self.ax.plot([], [], lw=1, color=colors[i])
            self.pls.append(l)

        self.lmax, = self.ax.plot([], [], lw=1, color='green')
        self.lmin, = self.ax.plot([], [], lw=1, color='pink')
        # self.lPassed, = self.ax.plot([], [], lw=1, color='black')
        self.lCurrent, = self.ax.plot([], [], lw=1, color='blue')
        self.lFuture, = self.ax.plot([], [], lw=1, color='yellow')
        # self.lma_lo, = self.ax.plot([], [], lw=1, color='pink')
        # self.lma_mid, = self.ax.plot([], [], lw=1, color='black')
        self.lp_hi, = self.ax.plot([], [], lw=1, color='red')
        # self.lExtrem, = self.ax.plot([], [], 'rx', lw=1)  # lw=2, color='black', marker='o', markeredgecolor='b')
        # self.lExtremAppx, = self.ax.plot([], [], 'yo', lw=1)  # lw=2, color='black', marker='o', markeredgecolor='b')
        self.lNow, = self.ax.plot([], [], lw=1, color='green')
        self.lBest_pl, = self.ax.plot([], [], lw=1, color=change_pnt_color)
        self.lShot_pl, = self.ax.plot([], [], lw=1, color='black')
        self.lTop, = self.ax.plot([], [], lw=1, color='black')
        # self.lAppxLow, = self.ax.plot([], [], lw=1, color='red')

        self.lines = [self.lmax, self.lmin, self.lCurrent, self.lFuture, self.lNow]\
                     + self.pls\
                     + [self.lp_hi, self.lBest_pl, self.lShot_pl, self.lTop] #, self.lAppxLow]

    def init_animation(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines

    '''
        def set_dm_int(self, down_int):
            self.down_int = down_int
            self.ax.set_xlim([0, m_data_len + m_predict_len])
            # self.ax.set_ylim([min(self.dm.hp[0: self.dm.data_len]),
            #                  max(self.dm.hp[0: self.dm.data_len])])
            self.ax.set_ylim([min(self.price[0: m_data_len]),
                              max(self.price[0: m_data_len])])
    '''

    def update_limite(self, xlim, ylim, cp, show_future):
        # delta = cp + self.dm.predict_len - xlim[1]
        # if delta > 0:
        xlim[0] = cp - m_data_len
        xlim[1] = cp + m_predict_len
        self.ax.set_xlim(xlim)

        if show_future:
            # self.ax.set_ylim([min(self.dm.hp[int(xlim[0]): int(xlim[1])]),
            #                  max(self.dm.hp[int(xlim[0]): int(xlim[1])])])
            self.ax.set_ylim([min(self.price[int(xlim[0]): int(xlim[1])]),
                              max(self.price[int(xlim[0]): int(xlim[1])])])
        else:
            # self.ax.set_ylim([min(self.dm.hp[int(xlim[0]): cp]),
            #                  max(self.dm.hp[int(xlim[0]): cp])])
            self.ax.set_ylim([min(self.price[int(xlim[0]): cp]),
                              max(self.price[int(xlim[0]): cp])])

    def update_lines(self, cp, show_future):
        self.max_x = []
        self.max_y = []
        self.min_x = []
        self.min_y = []

        self.m12.get_max_min_line(self.max_x, self.max_y, self.min_x, self.min_y, self.level)
        # print cp, len(self.max_x), len(self.max_y), len(self.min_x), len(self.min_y), self.level
        self.lmax.set_data(self.max_x, self.max_y)
        self.lmin.set_data(self.min_x, self.min_y)

        # self.lCurrent.set_data(self.dm.allx[cp - self.dm.data_len: cp],
        #                        self.dm.hp[cp - self.dm.data_len: cp])
        self.lCurrent.set_data(self.allx[cp - m_data_len: cp],
                               self.price[cp - m_data_len: cp])
        # self.update_extreme_appx(cp)
        # self.update_extreme_lo(cp)

        # self.lma_lo.set_data(self.dm.allx[cp - self.dm.data_len: cp], self.dm.ma_lo)
        # self.lma_mid.set_data(self.dm.allx[self.dm.first_ext_pos - len(self.dm.appx_hi): \
        #                       self.dm.first_ext_pos], \
        #                       self.dm.appx_hi)
        # self.lma_hi.set_data(self.dm.allx[cp - self.dm.data_len: cp], self.dm.ma_hi)

        if show_future:
            # dlen = len(self.dm.hp[cp: cp + self.dm.predict_len])
            dlen = len(self.price[cp: cp + m_predict_len])
            # self.lFuture.set_data(self.dm.allx[cp: cp + dlen], \
            #                      self.dm.hp[cp: cp + self.dm.predict_len])
            self.lFuture.set_data(self.allx[cp: cp + dlen], \
                                  self.price[cp: cp + m_predict_len])
        else:
            self.lFuture.set_data([], [])

        # print self.down_int, self.dm.first_ext_pos, self.dm.cp, cp, len(self.dm.hp), len(self.dm.price)
        # self.lNow.set_data([self.dm.first_ext_pos, cp - 1], \
        #                   [self.dm.hp[self.dm.first_ext_pos], self.dm.hp[cp - 1]])
        first_ext_pos = self.m12.get_first_ext_pos(self.level)
        self.lNow.set_data([first_ext_pos, cp - 1], \
                           [self.price[first_ext_pos], self.price[cp - 1]])

        ap_hi_pos = self.m12.get_ap_hi_pos(self.level)
        # print 4, len(self.dm.allx[self.dm.ap_hi_pos: self.dm.ap_hi_pos + self.dm.predict_len]), len(self.dm.ap_hi)

        amount = self.m12.get_ph_amount_results(self.level)
        for i in range(min(amount, len(self.pls))):
            bpl = []
            pl = PredictLine()
            self.m12.get_ph_best_predict(bpl, pl, self.level, cp, i)
            if (len(bpl) > 0) and (pl.spos + pl.plen > cp):
                x = list(range(pl.spos, pl.spos + pl.plen))
                self.pls[i].set_data(x, bpl)
            else:
                self.pls[i].set_data([], [])
                # self.ph.show_size()

        for i in range(min(amount, len(self.pls)), len(self.pls)):
            self.pls[i].set_data([], [])

        # l = len(self.allx[ap_hi_pos: ap_hi_pos + m_predict_len])
        self.predict = []
        self.m12.get_predict_line(self.predict, self.level)
        self.lp_hi.set_data(self.allx[ap_hi_pos: ap_hi_pos + m_predict_len], \
                            self.predict)

        bpl = []
        pl = PredictLine()
        self.m12.get_best_predict(bpl, pl, self.level)
        if (len(bpl) > 0) and (pl.spos + pl.plen > cp):
            x = list(range(pl.spos, pl.spos + pl.plen))
            self.lBest_pl.set_data(x, bpl)
        else:
            self.lBest_pl.set_data([], [])

        bpl = []
        pl = PredictLine()
        pa = PredictAttr()
        # self.shot.get_predict_line(self.level, bpl, pl, pa)
        self.shot.get_best_predict(self.level, bpl, pl, pa)
        # print "shot.get_predict_line", len(bpl), pa.epos - pa.spos + 1
        if (len(bpl) > 0):
            x = list(range(pl.spos, pl.spos + pl.plen))
            self.lShot_pl.set_data(x, bpl)
        else:
            self.lShot_pl.set_data([], [])

        if pa.type >=4 and pa.type <= 7: #4, 5, 6, 7
            if pa.type == 6 or pa.type == 4:
                pos = pa.maxp
            else:
                pos = pa.minp
            if self.top_pos < pl.spos + pos:
                self.top_pos = pl.spos + pos
                # print self.level, '>', self.top_pos, '|',
            # ylim = list(self.ax.get_ylim())
        self.lTop.set_data([self.top_pos, self.top_pos],\
                           list(self.ax.get_ylim()))

        # appx_low = []
        # self.m12.get_approx_low_line(appx_low, self.level)
        # self.lAppxLow.set_data(self.allx[cp - m_data_len: cp], appx_low)


    def update_extreme_lo(self, cp):
        # print self.name, cp, len(self.dm.ext_pos)
        # self.lExtrem.set_data(self.dm.ext_pos, self.dm.ext_val)
        pass

    def update_extreme_appx(self, cp):
        # self.lExtremAppx.set_data(self.dm.ext_appx_pos, self.dm.ext_appx_val)
        pass

    def animate(self, cur_pos, show_future):
        cp = cur_pos / self.down_int - 1
        #
        # if (cp + self.dm.predict_len > self.dm.all_len):
        #     return
        #
        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        #
        self.update_limite(xlim, ylim, cp, show_future)
        #
        # self.dm.do_math(cp)

        self.update_lines(cp, show_future)

        return tuple(self.lines)

    def update(self, cur_pos, show_future=True):
        cp = cur_pos / self.down_int - 1
        # if cp >= len(self.dm.hp):
        if cp >= len(self.price):
            return

        #
        # if (cp + self.dm.predict_len > self.dm.all_len):
        #     return
        #
        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        #
        self.update_limite(xlim, ylim, cp, show_future)
        #
        # self.dm.do_math(cp)

        self.update_lines(cp, show_future)

    def clean_predict_lines(self):
        for ppll in self.pls:
            ppll.set_data([], [])

