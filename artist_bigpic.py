from libnrlib import *

m_data_len = 1024
m_predict_len = 128


class ArtistBigPicture:
    def __init__(self, m12, dcplp, ax, name, level):
        self.m12 = m12
        self.dcplp = dcplp
        self.name = name
        self.ax = ax
        self.level = level
        self.down_int = m12.get_down_int(level)
        self.top_pos = 0

        self.price = []
        self.max_x = []
        self.max_y = []
        self.min_x = []
        self.min_y = []
        self.predict = []

        m12.get_hop_price(self.price, level)
        self.allx = list(range(0, len(self.price) + m_predict_len))

        self.ax.set_xlim([0, m_data_len + m_predict_len])
        self.ax.set_ylim([min(self.price[0: m_data_len]),
                          max(self.price[0: m_data_len])])

        change_pnt_color = (128.0 / 255.0, 28.0 / 255.0, 188.0 / 255.0)

        self.lmax, = self.ax.plot([], [], lw=1, color='green')
        self.lmin, = self.ax.plot([], [], lw=1, color='green')
        self.lCurrent, = self.ax.plot([], [], lw=1, color='blue')
        self.lFuture, = self.ax.plot([], [], lw=1, color='yellow')
        self.lp_hi, = self.ax.plot([], [], lw=1, color='red')
        self.appx, = self.ax.plot([], [], lw=1, color='black')
        self.lNow, = self.ax.plot([], [], lw=1, color='green')
        self.lBest_pl, = self.ax.plot([], [], lw=1, color=change_pnt_color)
        self.lTop, = self.ax.plot([], [], lw=1, color='black')

        self.lHTop = []
        self.lHTail = []

        self.lines = [self.lmax, self.lmin, self.lCurrent, self.lFuture, self.lNow, self.lp_hi, self.appx,
                      self.lBest_pl, self.lTop]
        for i in range(0, 12):
            top, = self.ax.plot([], [], lw=1, color='red', linestyle=':')
            tail, = self.ax.plot([], [], lw=1, color='green', linestyle=':')
            self.lHTop.append(top)
            self.lHTail.append(tail)
            self.lines.append(self.lHTop[i])
            self.lines.append(self.lHTail[i])

        self.lPrevPredict, = self.ax.plot([], [], lw=1, color='green')
        self.lines.append(self.lPrevPredict)

    def init_animation(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines

    def update_limit(self, x_lim, cp, show_future):
        x_lim[0] = cp - m_data_len
        x_lim[1] = cp + m_predict_len
        self.ax.set_xlim(x_lim)

        if show_future:
            self.ax.set_ylim([min(self.price[int(x_lim[0]): int(x_lim[1])]),
                           max(self.price[int(x_lim[0]): int(x_lim[1])])])
        else:
            self.ax.set_ylim([min(self.price[int(x_lim[0]): cp]),
                              max(self.price[int(x_lim[0]): cp])])

    def update_lines(self, cp, show_future, toggle):
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
            data_len = len(self.price[cp: cp + m_predict_len])
            self.lFuture.set_data(self.allx[cp: cp + data_len],
                                  self.price[cp: cp + m_predict_len])
        else:
            self.lFuture.set_data([], [])

        first_ext_pos = self.m12.get_first_ext_pos(self.level)
        # print self.down_int, first_ext_pos, cp
        self.lNow.set_data([first_ext_pos, cp - 1],
                           [self.price[first_ext_pos], self.price[cp - 1]])

        ap_hi_pos = self.m12.get_ap_hi_pos(self.level)

        self.predict = []
        self.m12.get_predict_line(self.predict, self.level)
        self.lp_hi.set_data(self.allx[ap_hi_pos: ap_hi_pos + m_predict_len],
                            self.predict)

        x = []
        self.m12.get_approximate(x, cp, self.level)
        self.appx.set_data(self.allx[cp - len(x): cp], x)

        bpl = []
        pl = PredictLine()
        self.m12.get_best_predict(bpl, pl, self.level)
        if (len(bpl) > 0) and (pl.spos + pl.plen > cp):
            x = list(range(pl.spos, pl.spos + pl.plen))
            self.lBest_pl.set_data(x, bpl)
        else:
            self.lBest_pl.set_data([], [])

        if toggle:
            hv = []
            self.dcplp.get_horizon_val(hv)
            len_hv = len(hv)
            self.set_ylim(hv)
            for i in range(0, len_hv):
                self.lHTop[i].set_data(list(self.ax.get_xlim()), [hv[i], hv[i]])
                self.lHTail[i].set_data([], [])
            for i in range(len_hv, 12):
                self.lHTop[i].set_data([], [])
                self.lHTail[i].set_data([], [])
        else:
            for i in range(0, 12):
                val = []
                ret = self.dcplp.get_top_val(i, val)
                if ret == 2:
                    self.set_ylim(val)
                    self.lHTop[i].set_data(list(self.ax.get_xlim()),
                                           [val[0], val[0]])
                    self.lHTail[i].set_data(list(self.ax.get_xlim()),
                                            [val[1], val[1]])
                elif ret >= 1:
                    self.set_ylim(val)
                    self.lHTop[i].set_data([], [])
                    self.lHTail[i].set_data(list(self.ax.get_xlim()),
                                            [val[0], val[0]])
                else:
                    self.lHTop[i].set_data([], [])
                    self.lHTail[i].set_data([], [])

            self.top_pos = self.dcplp.get_top_pos(self.level)
            if self.top_pos > 0:
                self.lTop.set_data([self.top_pos, self.top_pos],
                                   list(self.ax.get_ylim()))
            else:
                self.lTop.set_data([], [])

        pa = PredictAttr()
        ret = self.dcplp.get_previous_predict_attr(pa, self.level)
        if ret == 0:
            self.lPrevPredict.set_data([], [])
        else:
            print "PREV PA: ", pa.spos, pa.sval, pa.epos, pa.eval, pa.ipos, pa.ival

    def animate(self, cur_pos, show_future, toggle):
        cp = cur_pos / self.down_int - 1
        x_lim = list(self.ax.get_xlim())
        self.update_limit(x_lim, cp, show_future)
        self.update_lines(cp, show_future, toggle)
        return tuple(self.lines)

    def update(self, cur_pos, show_future=True):
        cp = cur_pos / self.down_int - 1
        if cp >= len(self.price):
            return

        x_lim = list(self.ax.get_xlim())
        self.update_limit(x_lim, cp, show_future)
        self.update_lines(cp, show_future)

    def set_ylim(self, val):
        y_lim = list(self.ax.get_ylim())
        for v in val:
            y_lim[0] = min(y_lim[0], v)
            y_lim[1] = max(y_lim[1], v)
        self.ax.set_ylim(y_lim)
