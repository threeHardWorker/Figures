from libnrlib import *
import Queue
import numpy
from scipy.stats.stats import pearsonr


def get_data_from_file(instrument, datapath, thedate, min_data_size, predict_len):
    price = []
    ftime = []

    # ret = load_10s_ts_from_date_v1(instrument, datapath, thedate, min_data_size, price, ftime)
    # ret = load_10s_ts_from_date_v2(instrument, datapath, thedate, min_data_size, my_hop, price, ftime)

    pointer = load_10s_ts_from_date_v4(instrument, datapath, thedate, min_data_size, price, ftime)
    if (pointer == 0):
        print "error load 10s ts data v4"

    all_len = len(price)
    allx = list(range(0, all_len + predict_len))
    return pointer, price, all_len, allx, thedate, ftime


def release_time_pos_map(pointer):
    release_dict(pointer)


def cal_fast_dtw(x, y):
    c = []
    delta = y[0] - x[0]
    for yy in y:
        c.append(yy - delta)
    return fast_dtw(x, c) / 128.0



class Params:
    minlen = 1024 * 2048
    # min_data_size = int(minlen * 1.0000005)
    # min_data_size = int(minlen * 1.0005)
    min_data_size = int(minlen * 1.5)
    # min_data_size = int(minlen * 3)
    # min_data_size = int(minlen * 1.8)
    predict_len = 128
    run_status = 0
    delta = 0
    curpos = 0
    queue_pl_size = 10
    queue_cp_size = 10
    interval = 0.01
    inst = ''
    date = ''
    data_len = 1024
    all_len = min_data_size
    level = 0
    imgpath = ''

    def __init__(self):
        pass

class DataLines:
    def __init__(self):
        self.max_x = []
        self.max_y = []
        self.min_x = []
        self.min_y = []
        self.la = LinesAttr()

    def set_data(self, ve, max_x, min_x, cp, prdlen, h, w = 1024.0):
        # type: (object, object, object, object, object, object, object) -> object
        if (len(max_x) > 1 and len(min_x) > 1):
            self.max_x = []
            self.max_y = []
            self.min_x = []
            self.min_y = []
            # int fit_line(const std::vector<NR::Extreme>& ext, const bp::list& imax,
            # const bp::list& imin, const double hop,
            # const int current_pos, const int predict_len,
            # LinesAttr& la, bp::list& max_line, bp::list& min_line)
            fit_line(ve, max_x, min_x, cp, prdlen, 5.0/18.0*w/h, self.la, self.max_y, self.min_y)
            # print slope1, slope2
            # print la.k_max, la.y0_max, la.k_min, la.y0_min
            # print slope1 - la.k_max, slope2 - la.k_min, slope1 - la.k_max < 1e-12, slope2 - la.k_min < 1e-12
            # print max_x[0], cp, prdlen, cp+prdlen
            self.max_x = list(range(ve[max_x[0]].pos, cp + prdlen))
            self.min_x = list(range(ve[min_x[0]].pos, cp + prdlen))
            # print len(self.max_x), len(self.max_y)


class PredictResult:
    def __init__(self, curpos, pos, da, line):
        self.curpos = curpos
        self.pos = pos
        self.da = da
        self.pl = line

class DataMath:
    def __init__(self, price, all_len, allx, the_date, hop, params):
        self.price = price
        self.all_len = all_len
        self.allx = allx
        self.the_date = the_date

        self.down_int = 1
        self.data_len = 1024
        self.predict_len = 128

        self.lvl_hi = 7
        self.appx_hi_len = self.data_len
        self.appx_hi = []
        self.ap_hi = []
        self.ap_hi_pos = 0
        self.pa = PredictAttr()

        self.predict = Predict(self.data_len, self.predict_len)
        self.wt = WaveletFilter(1, self.data_len, self.lvl_hi)

        self.ext_pos = []
        self.ext_val = []
        self.first_ext_pos = -1
        self.ve = VectorExtreme()

        self.veAppx = VectorExtreme()
        self.ext_appx_pos = []
        self.ext_appx_val = []

        self.dl = DataLines()

        # self.hp = []
        # self.hop = hop
        # self.price0 = self.price[0]

        self.cp = 0

        self.lpr = LPRelation()

        self.params = params

        self.ph = PredictHouse(10, 10)

        self.new_amount = 0

    def add_new_data(self, high, low, its_new):
        if its_new:
            self.new_amount += 1
            if (0 == self.new_amount % self.down_int):
                self.new_amount = 0
                self.all_len += 2
                self.allx.append(self.allx[-1] + 1)
                self.allx.append(self.allx[-1] + 1)
                self.price.append(high)
                self.price.append(low)
                # self.hp.append((high - self.price0)/self.hop)
                # self.hp.append((low - self.price0)/self.hop)

        # print 'update ', high, low
        self.price[-2] = high
        self.price[-1] = low
        # self.hp[-2] = (high - self.price0)/self.hop
        # self.hp[-1] = (low - self.price0)/self.hop


    def set_not_chagne(self):
        self.prdct_change = False


    def add_new_pl_3(self, da, curpos):
        # print curpos, self.cp, self.ap_hi_pos
        # pr = PredictResult(curpos, self.ap_hi_pos, da, self.ap_hi)
        # if self.change_point is None:
        #     self.change_point = pr
        # else:
        #     fdtw = fast_dtw(self.change_point.pl, self.ap_hi)
        #     corr = pearsonr(numpy.array(self.change_point.pl), numpy.array(self.ap_hi))
        #     if fdtw > 10 or corr[0] < 0.95:
        #         self.change_point = pr
        #         self.prdct_change = True
        #         if self.qcp.qsize() >= self.params.queue_cp_size:
        #             self.qcp.get()
        #         self.qcp.put(pr)
        #     else:
        #         self.prdct_change = False
        # if self.qpl.qsize() >= self.params.queue_pl_size:
        #     self.qpl.get()
        # self.qpl.put(pr)
        da = DiffAttr()
        # print curpos, self.down_int, self.cp, "***", len(self.ap_hi), "***"
        self.ph.push_back(self.params.curpos, self.cp, self.ap_hi_pos, self.ap_hi, da)
            # print self.down_int, self.params.curpos, self.cp, self.ap_hi_pos, '->'
            # print curpos, self.cp, "-->"
        # self.ph.cal_match(self.hp[self.cp - self.predict_len: self.cp], self.cp + 1 - self.predict_len, self.cp)
        self.ph.cal_match(self.price[self.cp - self.predict_len: self.cp], self.cp + 1 - self.predict_len, self.cp)
        # amount = self.ph.get_amount_results()
        # for i in range(amount):
        #     bpl = []
        #     pl = PredictLine()
        #     self.ph.get_best_predict(self.cp, i, bpl, pl)
        #     print len(bpl), pl.spos
        #     # self.ph.show_size()



    def down_sample(self, down_int):
        self.down_int = down_int / 2
        if self.down_int > 1:
            # plt.plot(list(range(0, len(self.price))), self.price)
            # plt.show()
            # print self.price[182000:185201:200]
            self.price = sample_max_min(self.price, down_int)

        # self.hp = []
        # for p in self.price:
        #    self.hp.append((p - self.price0) / self.hop)

        # plt.plot(list(range(0, len(self.price))), self.price)
        # plt.show()
        self.all_len = len(self.price)
        self.allx = list(range(0, self.all_len + self.predict_len))

    def do_math(self, curpos):
        self.cp = curpos / self.down_int - 1
        # print curpos, cp, self.all_len

        self.ext_val = []
        self.ext_pos = []
        # self.ve = get_sample_extreme(self.hp[self.cp + 1 - self.data_len: self.cp],
        self.ve = get_sample_extreme(self.price[self.cp + 1 - self.data_len: self.cp],
                                     50, self.cp + 1 - self.data_len,
                                     self.ext_pos, self.ext_val)

        if len(self.ext_pos) < 1 or (self.first_ext_pos == self.ext_pos[-1]):
            return

        self.first_ext_pos = self.ext_pos[-1]

        pos = 0
        if (self.first_ext_pos - self.data_len < 0):
            self.appx_hi_len = self.first_ext_pos
        else:
            self.appx_hi_len = self.data_len
            pos = self.first_ext_pos - self.data_len

        self.wt.set(1, self.appx_hi_len, self.lvl_hi)
        # self.wt.setdata(self.hp[pos: self.first_ext_pos])
        self.wt.setdata(self.price[pos: self.first_ext_pos])
        self.appx_hi = self.wt.filter()

        self.ap_hi_pos = self.first_ext_pos
        self.predict.setdata(self.appx_hi)
        da = DiffAttr()
        self.ap_hi = self.predict.predict(da)

        # h = max(self.hp[self.cp + 1 - self.data_len: self.cp]) - min(self.hp[self.cp + 1 - self.data_len : self.cp])
        h = max(self.price[self.cp + 1 - self.data_len: self.cp]) - min(self.price[self.cp + 1 - self.data_len: self.cp])

        if abs(h) < 1e-6:
            h = 1.0
        find_predict_extreme(self.ap_hi, 5.0/18.0*1024.0/h, self.pa)
        # print cp, pa.type, pa.slope_1, pa.slope_2

        self.ext_appx_pos = []
        self.ext_appx_val = []

        self.veAppx = get_appx_org_extreme(self.appx_hi + self.ap_hi, \
                                           self.ve, \
                                           self.cp + 1 - self.data_len, \
                                           self.ext_appx_pos, \
                                           self.ext_appx_val)
        # print self.ext_appx_pos

        pricemax = []
        pricemin = []
        # print "math ", self.down_int, " ve ",
        # print_ve(self.ve)
        # print "math ", self.down_int, " veappx ",
        # print_ve(self.veAppx)
        if len(self.veAppx) > 0:
            get_last_slice(self.ve, self.veAppx, pricemax, pricemin)
            print "ve, veappx price max, min", len(self.ve), len(self.veAppx), len(pricemax), len(pricemin)

            # print pricemax, pricemin
            self.dl.set_data(self.ve, pricemax, pricemin, self.cp, self.predict_len, h)
            # if self.down_int == 100:
            # print self.cp - self.first_ext_pos, self.cp, self.first_ext_pos
            get_LP_relation(self.dl.max_y, self.dl.min_y, self.ap_hi, self.predict_len, self.cp - self.first_ext_pos, self.lpr)

        self.add_new_pl_3(da, curpos)

    def print_values(self):
        print 'PA> %d-%d %d %d|%.2f,%.2f,%.2f,%.2f|%.2f,%.2f' % ( \
                self.pa.type, \
                self.first_ext_pos, \
                self.pa.maxp, \
                self.pa.minp, \
                self.pa.sval, \
                self.pa.eval, \
                self.pa.maxv, \
                self.pa.minv, \
                self.pa.slope_1, \
                self.pa.slope_2)
        print   'LPR>', self.lpr.type, self.lpr.ni_max, \
                self.lpr.ni_min, self.lpr.i_max, self.lpr.i_min, \
                self.lpr.s_max,  self.lpr.s_min, self.lpr.part_pct
        print 'LA> %.2f,%.2f,%d' \
              % (self.dl.la.s_max, self.dl.la.s_min, self.dl.la.i_type)
        print 'PP>',
        for i in range(self.qpl.qsize()):
            corr = pearsonr(self.qpl.queue[i].pl, self.change_point.pl)
            fdtw = fast_dtw(self.qpl.queue[i].pl, self.change_point.pl)
            print '(%d#%.02f,%.02f)' %(i, corr[0], fdtw),
        print

    def find_shape(self):
        print 'find_shape'
