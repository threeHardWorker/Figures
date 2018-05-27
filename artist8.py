import matplotlib.pyplot as plt
import tmath
from libnrlib import *

m_data_len = 1024
m_predict_len = 128


class Artist8:
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

        self.lmax, = self.ax.plot([], [], lw=1, color='green')
        self.lmin, = self.ax.plot([], [], lw=1, color='green')
        self.lCurrent, = self.ax.plot([], [], lw=1, color='blue')
        self.lFuture, = self.ax.plot([], [], lw=1, color='yellow')
        self.lp_hi, = self.ax.plot([], [], lw=1, color='red')
        self.appx, = self.ax.plot([], [], lw=1, color='black')
        self.lNow, = self.ax.plot([], [], lw=1, color='green')
        self.lBest_pl, = self.ax.plot([], [], lw=1, color=change_pnt_color)

        self.lines = [self.lmax, self.lmin, self.lCurrent, self.lFuture, self.lNow, self.lp_hi, self.appx, self.lBest_pl]


    def init_animation(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines


    def update_limite(self, xlim, ylim, cp, show_future):
        xlim[0] = cp - m_data_len
        xlim[1] = cp + m_predict_len
        self.ax.set_xlim(xlim)

        if show_future:
            self.ax.set_ylim([min(self.price[int(xlim[0]): int(xlim[1])]),
                              max(self.price[int(xlim[0]): int(xlim[1])])])
        else:
            self.ax.set_ylim([min(self.price[int(xlim[0]): cp]),
                              max(self.price[int(xlim[0]): cp])])


    def update_lines(self, cp, show_future):
        self.max_x = []
        self.max_y = []
        self.min_x = []
        self.min_y = []

        self.m12.get_max_min_line(self.max_x, self.max_y, self.min_x, self.min_y, self.level)
        self.lmax.set_data(self.max_x, self.max_y)
        self.lmin.set_data(self.min_x, self.min_y)

        self.lCurrent.set_data(self.allx[cp - m_data_len: cp],
                               self.price[cp - m_data_len: cp])

        if show_future:
            dlen = len(self.price[cp: cp + m_predict_len])
            self.lFuture.set_data(self.allx[cp: cp + dlen], \
                                  self.price[cp: cp + m_predict_len])
        else:
            self.lFuture.set_data([], [])

        first_ext_pos = self.m12.get_first_ext_pos(self.level)
        self.lNow.set_data([first_ext_pos, cp - 1], \
                           [self.price[first_ext_pos], self.price[cp - 1]])

        ap_hi_pos = self.m12.get_ap_hi_pos(self.level)

        self.predict = []
        self.m12.get_predict_line(self.predict, self.level)
        self.lp_hi.set_data(self.allx[ap_hi_pos: ap_hi_pos + m_predict_len], \
                            self.predict)

        x = []
        self.m12.get_approximate(x, cp, self.level)
        self.appx.set_data(self.allx[cp - len(x) : cp], x);

        bpl = []
        pl = PredictLine()
        self.m12.get_best_predict(bpl, pl, self.level)
        if (len(bpl) > 0) and (pl.spos + pl.plen > cp):
            x = list(range(pl.spos, pl.spos + pl.plen))
            self.lBest_pl.set_data(x, bpl)
        else:
            self.lBest_pl.set_data([], [])


    def update_extreme_lo(self, cp):
        pass


    def update_extreme_appx(self, cp):
        pass


    def animate(self, cur_pos, show_future):
        cp = cur_pos / self.down_int - 1
        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        self.update_limite(xlim, ylim, cp, show_future)
        self.update_lines(cp, show_future)
        return tuple(self.lines)


    def update(self, cur_pos, show_future=True):
        cp = cur_pos / self.down_int - 1
        if cp >= len(self.price):
            return

        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        self.update_limite(xlim, ylim, cp, show_future)

        self.update_lines(cp, show_future)


    def clean_predict_lines(self):
        for ppll in self.pls:
            ppll.set_data([], [])

