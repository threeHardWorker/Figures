from libnrlib import *

m_data_len = 1024
m_predict_len = 128


class Artist:
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
        self.lHTop, = self.ax.plot([], [], lw=1, color='red', linestyle=':')
        self.lHTail, = self.ax.plot([], [], lw=1, color='green', linestyle=':')

        self.lines = [self.lmax, self.lmin, self.lCurrent, self.lFuture, self.lNow, self.lp_hi, self.appx,
                      self.lBest_pl, self.lTop, self.lHTop, self.lHTail]

        self.lPrevPredict, = self.ax.plot([], [], lw=1, color='green')
        self.lines.append(self.lPrevPredict)

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
        del self.max_x[:]
        del self.max_y[:]
        del self.min_x[:]
        del self.min_y[:]

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
        if first_ext_pos < cp:
            self.lNow.set_data([first_ext_pos, cp],
                               [self.price[first_ext_pos], self.price[cp]])

        ap_hi_pos = self.m12.get_ap_hi_pos(self.level)

        del self.predict[:]
        self.m12.get_predict_line(self.predict, self.level)
        if len(self.predict) == \
                len(self.allx[ap_hi_pos: ap_hi_pos + m_predict_len]):
                self.lp_hi.set_data(
                    self.allx[ap_hi_pos: ap_hi_pos + m_predict_len],
                    self.predict)

        x = []
        self.m12.get_approximate(x, cp, self.level)
        self.appx.set_data(self.allx[cp - len(x): cp], x);

        bpl = []
        pl = PredictLine()
        self.m12.get_best_predict(bpl, pl, self.level)
        if (len(bpl) > 0) and (pl.spos + pl.plen > cp):
            x = list(range(pl.spos, pl.spos + pl.plen))
            self.lBest_pl.set_data(x, bpl)
        else:
            self.lBest_pl.set_data([], [])

        self.top_pos = self.dcplp.get_top_pos(self.level)
        if self.top_pos > 0:
            self.lTop.set_data([self.top_pos, self.top_pos],
                               list(self.ax.get_ylim()))
        else:
            self.lTop.set_data([], [])

        val = []

        ret = self.dcplp.get_top_val(self.level, val)
        if ret == 2:
            self.lHTop.set_data(list(self.ax.get_xlim()),
                                [val[0], val[0]])
            self.lHTail.set_data(list(self.ax.get_xlim()),
                                 [val[1], val[1]])
        elif ret >= 1:
            self.lHTop.set_data([], [])
            self.lHTail.set_data(list(self.ax.get_xlim()),
                                 [val[0], val[0]])
        else:
            self.lHTop.set_data([], [])
            self.lHTail.set_data([], [])

        pa = PredictAttr()
        ret = self.dcplp.get_previous_predict_attr(pa, self.level)
        if ret == 0:
            self.lPrevPredict.set_data([], [])
        else:
            # print "PREV PA type: ", pa.type, " Level: ", self.level,\
            #    " Values: ", pa.spos, pa.sval, pa.epos, pa.eval, pa.ipos, pa.ival
            if 3 >= pa.type > 0:
                self.lPrevPredict.set_data([pa.cp, pa.cp + pa.epos], [pa.sval, pa.eval])
            elif pa.type >= 4:
                self.lPrevPredict.set_data([pa.cp, pa.cp + pa.ipos, pa.cp + pa.epos],
                                           [pa.sval, pa.ival, pa.eval])
            else:
                self.lPrevPredict.set_data([], [])
            '''
                #define  PREDICT_LINE_TYPE_UNKNOW          0
                #define  PREDICT_LINE_TYPE_FLAT            1
                #define  PREDICT_LINE_TYPE_UP              2
                #define  PREDICT_LINE_TYPE_DOWN            3
                #define  PREDICT_LINE_TYPE_CONVEX          4
                #define  PREDICT_LINE_TYPE_CONCAVE         5
                #define  PREDICT_LINE_TYPE_UP_CONVEX       6
                #define  PREDICT_LINE_TYPE_DOWN_CONCAVE    7
            '''

    def animate(self, cur_pos, show_future):
        # update the price data
        del self.price[:]
        self.m12.get_hop_price(self.price, self.level)
        cp = cur_pos / self.down_int - 1
        if cp >= len(self.price):
            print "Error!"
            return tuple()

        self.allx = list(range(0, len(self.price) + m_predict_len))

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
