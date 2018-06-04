import tmath
import re

g_margin = dict(
    {'CF': 0.07, 'FG': 0.06, 'MA': 0.05, 'OI': 0.05, 'RM': 0.05, 'SR': 0.06, 'TA': 0.06, 'ZC': 0.05, 'a': 0.05,
     'ag': 0.07, 'al': 0.05, 'au': 0.07, 'bu': 0.04, 'c': 0.05, 'cu': 0.05, 'i': 0.05, 'j': 0.05, 'jd': 0.05,
     'jm': 0.05, 'l': 0.05, 'm': 0.05, 'ni': 0.05, 'p': 0.05, 'pb': 0.07, 'pp': 0.05, 'rb': 0.07, 'ru': 0.05, 'v': 0.05,
     'y': 0.05, 'zn': 0.05, 'b': 0.05})
g_unit = dict({'CF': 5, 'FG': 20, 'MA': 10, 'OI': 10, 'RM': 10, 'SR': 10, 'TA': 5, 'ZC': 100, 'a': 10, 'ag': 15, 'al': 5,
             'au': 1000, 'bu': 10, 'c': 10, 'cu': 5, 'i': 100, 'j': 100, 'jd': 10, 'jm': 60, 'l': 10, 'm': 10, 'ni': 1,
             'p': 10, 'pb': 5, 'pp': 5, 'rb': 10, 'ru': 10, 'v': 5, 'y': 10, 'zn': 5, 'b': 10})
g_hop = dict(
    { 'CF' : 5,'FG' : 1, 'MA' : 1, 'OI' : 2, 'RM' : 1, 'SR' : 1, 'TA' : 2, 'ZC' : 0.2, 'a' : 1, 'b' : 1, 'c' : 1,
     'j' : 0.5, 'jm' : 0.5, 'l' : 5, 'm' : 1, 'p' : 2, 'pp' : 1, 'v' : 5, 'y' : 2, 'i' : 0.5, 'jd' : 1, 'fb' : 0.05,
     'bb' : 0.05, 'cs' : 1, 'al' : 5, 'au' : 0.05, 'ag' : 1, 'cu' : 10, 'fu' : 5, 'pb' : 5, 'rb' : 1, 'ru' : 5,
     'wr' : 1, 'zn' : 5, 'bu' : 2, 'hc' : 1, 'sn' : 10, 'ni' : 10 })

g_commision = 0.00005

my_unit = 10
my_margin = 0.05
my_hop = 1

sign = lambda x: x and (1, -1)[x < 0]


def get_instrument_code(inst):
    global my_unit, my_margin, my_hop
    match = re.match(r"([a-z]+)([0-9]+)", inst, re.I)
    code = ''
    if match:
        items = match.groups()
        code = items[0]
        my_unit = g_unit[code]
        my_margin = g_margin[code]
        my_hop = g_hop[code]

    if len(code) == 1:
        code += '9'
    return code


def get_instrument_cc(inst):
    global my_unit, my_margin, my_hop
    match = re.match(r"([a-z]+)([0-9]+)", inst, re.I)
    cc = ''
    if match:
        items = match.groups()
        code = items[0]
        my_unit = g_unit[code]
        my_margin = g_margin[code]
        my_hop = g_hop[code]
        if len(code) == 1:
            cc = code + '9888'
        elif len(code) == 2:
            cc = code + '888'
    return cc

def get_hop(inst):
    global my_hop
    match = re.match(r"([a-z]+)([0-9]+)", inst, re.I)
    if match:
        items = match.groups()
        code = items[0]
        return g_hop[code]
    return 0

class Order:
    def __init__(self, action = 0, direct = 0, pos = 0, price = 0, inst = ''):
        self.action = action
        self.direct = direct
        self.pos_ = pos
        self.price = price
        self.posrev = 0  # current revenue
        self.rev = 0  # revenue
        self.inst = inst
        self.margin = 0.0
        self.unit = 0.0

    def print_order(self):
        stro = self.inst + ', '
        if self.action == 1:
            stro += 'Open, '
        else:
            stro += 'Close, '

        if self.direct == 1:
            stro += 'Long, '
        else:
            stro += 'Short, '

        stro += str(self.pos_) + ', ' + str(self.price) + ', ' + str(self.rev)
        print stro

class Trade:
    order = []
    allrev = 0
    opened = False

    def __init__(self):
        pass

    def set_dm(self, dm, params):
        self.dm = dm
        self.pa = []
        self.dl = []
        self.la = []
        for i in range(0, len(dm)):
            self.pa.append(self.dm[i].pa)
            self.dl.append(self.dm[i].dl)
            self.la.append(self.dl[i].la)
        self.params = params

    def openLong(self, inst, cur_pos):
        if (0 == len(self.order) % 2):
            print inst, 'Open Long ', cur_pos, self.dm[0].price[cur_pos]
            self.order.append(Order(1, 1, cur_pos, self.dm[0].price[cur_pos], inst))
            self.opened = True
            return True
        else:
            return False

    def openShort(self, inst, cur_pos):
        if (0 == len(self.order) % 2):
            print inst, 'Short ', cur_pos, self.dm[0].price[cur_pos]
            self.order.append(Order(1, -1, cur_pos, self.dm[0].price[cur_pos], inst))
            self.opened = True
            return True
        else:
            return False

    def closePosition(self, inst, cur_pos):
        if (1 == len(self.order) % 2):
            c = Order(-1, self.order[-1].direct, cur_pos, self.dm[0].price[cur_pos], inst)
            if self.order[-1].direct == 1:
                c.posrev = (c.price - self.order[-1].price) * my_unit
                c.rev = (c.price - self.order[-1].price) * my_unit \
                        - (c.price + self.order[-1].price) * my_unit * g_commision
            else: # direct == -1
                c.posrev = (self.order[-1].price - c.price) * my_unit
                c.rev = (self.order[-1].price - c.price) * my_unit \
                        - (c.price + self.order[-1].price) * my_unit * g_commision
            self.order.append(c)
            self.allrev += c.rev
            print inst, 'Close', cur_pos, self.dm[0].price[cur_pos], c.posrev, c.rev, self.allrev
            self.opened = False
            return True
        else:
            return False


    def should_close_(self, inst, cur_pos):
        pass


    def should_open_(self, inst, cur_pos):
        pass


    def do_trade(self, inst, cur_pos):
        '''
        print 'PA2', self.pa[1].type, self.pa[1].minv, self.pa[1].maxv, self.pa[1].minp, self.pa[1].maxp, self.pa[1].slope_1, self.pa[1].slope_2
        print 'PA3', self.pa[2].type, self.pa[2].minv, self.pa[2].maxv, self.pa[2].minp, self.pa[2].maxp, self.pa[2].slope_1, self.pa[2].slope_2
        print 'DL2', self.la[1].i_type, self.la[1].k_max, self.la[1].y0_max, self.la[1].s_max, self.la[1].k_min, self.la[1].y0_min, self.la[1].s_min, self.la[1].i_x, self.la[1].i_y
        print 'DL3', self.la[2].i_type, self.la[2].k_max, self.la[2].y0_max, self.la[2].s_max, self.la[2].k_min, self.la[2].y0_min, self.la[2].s_min, self.la[2].i_x, self.la[2].i_y
        '''
        # if self.la[1].i_type == 0 or self.la[2].i_type == 0 or self.la[3].i_type == 0:
        #    print cur_pos, self.la[1].i_type, self.la[2].i_type, self.la[3].i_type
        if self.opened:
            self.should_close_(inst, cur_pos)
        else:
            self.should_open_(inst, cur_pos)

    def print_trade(self):
        print 'All Trade: '
        for o in self.order:
            o.print_order()
        print 'Done.'

    def update_revenue(self, cur_pos):
        o = self.order[-1]
        o.posrev = (self.dm[0].price[cur_pos] - o.price) * my_unit
        if o.direct < 0:
            o.posrev = - o.posrev
        o.posrev -= (self.dm[0].price[cur_pos] + o.price) * my_unit * g_commision

'''
#define  PREDICT_LINE_TYPE_UNKNOW 0
#define  PREDICT_LINE_TYPE_DOWN   1
#define  PREDICT_LINE_TYPE_UP     2
#define  PREDICT_LINE_TYPE_TU     3
#define  PREDICT_LINE_TYPE_AO     4


class PredictAttr {
public:
  int type = 0; //PREDICT_LINE_TYPE
  int spos = 0;
  int minp = 0;
  int maxp = 0;
  int epos = 0;
  double sval = 0;
  double minv = 0;
  double maxv = 0;
  double eval = 0;
  double slope_1 = 0;
  double slope_2 = 0;
};

enum intersection_type {
    intersection_parallel = 0,
    intersection_chaos_near = 1,
    intersection_chaos_back = 2,
    intersection_farway = 3,
    intersection_backway = 4,
} intersection_type;

class LinesAttr {
public:
  int i_type; //intersection type
  double k_max;
  double y0_max;
  double s_max;
  double k_min;
  double y0_min;
  double s_min;
  double i_x;
  double i_y;
};
'''


#
# open and close at paraller two lines
#
class SimpleTrade(Trade):
    def should_close_(self, inst, cur_pos):
        if (self.opened and 0 == self.la[2].i_type)\
            and ((self.order[-1].direct == 1 and self.la[2].s_max < 0)\
                or (self.order[-1].direct == -1 and self.la[2].s_max > 0)):
            self.closePosition(inst, cur_pos)


    def should_open_(self, inst, cur_pos):
        if not self.opened and 0 == self.la[2].i_type:
            if self.la[2].s_max > 0:
                self.openLong(inst, cur_pos)
            else:
                self.openShort(inst, cur_pos)




#
# prepare to open or close at paraller two lines
# but find a good enter point
#
class PrepareParalle_v1(Trade):
    enum_action_status = dict({0: 'unkonw', 1: 'pre-open long', 2: 'pre-open short',
                               -1: 'pre-close long', -2: 'pre-close short'})
    def __init__(self):
        self.po = Order()
        self.status = 0

    def should_close_(self, inst, cur_pos):
        if self.opened:
            if self.status == 0:
                # good lines
                if 0 == self.la[2].i_type or self.la[2].i_type > 2:
                    # going up?
                    if self.la[2].s_max > 0 and self.la[2].s_min > 0:
                        # prepare open long
                        self.status = -2  # pre-open long
                        print cur_pos, 'prepare close short', self.status
                    # going down?
                    elif self.la[2].s_max < 0 and self.la[2].s_min < 0:
                        # prepare open short
                        self.status = -1  # pre-open short
                        print cur_pos, 'prepare close long', self.status
            # Now, prepare open
            elif self.status == -2:
                # keep the two lines direction
                if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                    and self.la[2].s_max > 0 \
                    and self.la[2].s_min > 0:
                    # good extreme
                    if len(self.dl[2].min_x) == len(self.dl[2].min_y) \
                        and len(self.dm[2].ve) > 0:
                        e = self.dm[2].ve[-1]
                        if e.dir == -1:
                            cp = int(cur_pos / self.dm[2].down_int)
                            hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            if hop < -1:
                                self.closePosition(inst, cur_pos)
                            # print cp, (cp - e.pos,  e.dir, e.val), (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            # print cur_pos, cp, cp + self.dm[2].predict_len, self.dm[2].price[cp - 1], '(', self.dl[2].min_x[0], ',', self.dl[2].min_y[0], ')', '(', self.dl[2].min_x[-1], ',', self.dl[2].min_y[-1], ')'
                else:
                    self.status = 0
                    print cur_pos, 'Cancel prepare close short'
            elif self.status == -1:
                # keep the two lines direction
                if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                    and self.la[2].s_max < 0 \
                    and self.la[2].s_min < 0:
                    # good extreme
                    if len(self.dl[2].max_x) == len(self.dl[2].max_y) \
                        and len(self.dm[2].ve) > 0:
                        e = self.dm[2].ve[-1]
                        if e.dir == 1:
                            cp = int(cur_pos / self.dm[2].down_int)
                            hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            if hop > 1:
                                self.closePosition(inst, cur_pos)
                else:
                    self.status = 0
                    print cur_pos, 'Cancel prepare close long'



    def should_open_(self, inst, cur_pos):
        # not open
        if not self.opened:
            # Now, don't know what to do
            if self.status == 0:
                # good lines
                if 0 == self.la[2].i_type or self.la[2].i_type > 2:
                    # going up?
                    if self.la[2].s_max > 0 and self.la[2].s_min > 0:
                        # prepare open long
                        self.status = 1 # pre-open long
                        print cur_pos, 'prepare open long', self.status
                    # going down?
                    elif self.la[2].s_max < 0 and self.la[2].s_min < 0:
                        # prepare open short
                        self.status = 2 # pre-open short
                        print cur_pos, 'prepare open short', self.status
            # Now, prepare open
            elif self.status == 1:
                # keep the two lines direction
                if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                    and self.la[2].s_max > 0 \
                    and self.la[2].s_min > 0:
                    # good extreme
                    if len(self.dl[2].min_x) == len(self.dl[2].min_y) \
                        and len(self.dm[2].ve) > 0:
                        e = self.dm[2].ve[-1]
                        if e.dir == -1:
                            cp = int(cur_pos / self.dm[2].down_int)
                            hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            if hop < -1:
                                self.openLong(inst, cur_pos)
                            # print cp, (cp - e.pos,  e.dir, e.val), (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            # print cur_pos, cp, cp + self.dm[2].predict_len, self.dm[2].price[cp - 1], '(', self.dl[2].min_x[0], ',', self.dl[2].min_y[0], ')', '(', self.dl[2].min_x[-1], ',', self.dl[2].min_y[-1], ')'
                else:
                    self.status = 0
                    print cur_pos, 'Cancel prepare open long'
            elif self.status == 2:
                # keep the two lines direction
                if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                    and self.la[2].s_max < 0 \
                    and self.la[2].s_min < 0:
                    # good extreme
                    if len(self.dl[2].max_x) == len(self.dl[2].max_y) \
                        and len(self.dm[2].ve) > 0:
                        e = self.dm[2].ve[-1]
                        if e.dir == 1:
                            cp = int(cur_pos / self.dm[2].down_int)
                            hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                            if hop > 1:
                                self.openShort(inst, cur_pos)
                else:
                    self.status = 0
                    print cur_pos, 'Cancel prepare open short'



#
# prepare to open or close at paraller two lines
# but find a good enter point
#
class PrepareParalle_v2(Trade):
    enum_action_status = dict({0: 'unkonw', 1: 'pre-open long', 2: 'pre-open short',
                               -1: 'pre-close long', -2: 'pre-close short'})
    def __init__(self):
        self.status = 0

    def should_close_(self, inst, cur_pos):
        self.update_revenue(cur_pos)
        if self.status == 0:
            # bad lines
            if (1 == self.la[2].i_type or self.la[2].i_type == 2) \
                and (1 == self.la[1].i_type or self.la[1].i_type == 2):
                    # prepare open long
                    if self.order[-1].direct > 0 and self.la[2].s_max < 0:
                        self.status = -1  # pre-close long
                        print cur_pos, 'prepare close long', self.order[-1].posrev, self.la[2].s_max, self.la[2].s_min, self.la[1].s_max, self.la[1].s_min
                    elif self.order[-1].direct < 0 and self.la[2].s_min > 0:
                        self.status = -2  # pre-close short
                        print cur_pos, 'prepare close short', self.order[-1].posrev, self.la[2].s_max, self.la[2].s_min, self.la[1].s_max, self.la[1].s_min

        if self.status == -2 or self.status == -1:
            if self.order[-1].posrev > 0:
                self.closePosition(inst, cur_pos)

        self.status = 0


    def should_open_(self, inst, cur_pos):
        # Now, don't know what to do
        if self.status == 0:
            # good lines
            if 0 == self.la[2].i_type or self.la[2].i_type > 2:
                # going up?
                if self.la[2].s_max > 0 and self.la[2].s_min > 0:
                    # prepare open long
                    self.status = 1 # pre-open long
                    print cur_pos, 'prepare open long', self.status
                # going down?
                elif self.la[2].s_max < 0 and self.la[2].s_min < 0:
                    # prepare open short
                    self.status = 2 # pre-open short
                    print cur_pos, 'prepare open short', self.status
        # Now, prepare open
        elif self.status == 1:
            # keep the two lines direction
            if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                and self.la[2].s_max > 0 \
                and self.la[2].s_min > 0:
                # good extreme
                if len(self.dl[2].min_x) == len(self.dl[2].min_y) \
                    and len(self.dm[2].ve) > 0:
                    e = self.dm[2].ve[-1]
                    if e.dir == -1:
                        cp = int(cur_pos / self.dm[2].down_int)
                        hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                        if hop < -1:
                            self.openLong(inst, cur_pos)
                            self.status = 0
                        # print cp, (cp - e.pos,  e.dir, e.val), (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                        # print cur_pos, cp, cp + self.dm[2].predict_len, self.dm[2].price[cp - 1], '(', self.dl[2].min_x[0], ',', self.dl[2].min_y[0], ')', '(', self.dl[2].min_x[-1], ',', self.dl[2].min_y[-1], ')'
            else:
                self.status = 0
                print cur_pos, 'Cancel prepare open long'
        elif self.status == 2:
            # keep the two lines direction
            if (0 == self.la[2].i_type or self.la[2].i_type > 2)\
                and self.la[2].s_max < 0 \
                and self.la[2].s_min < 0:
                # good extreme
                if len(self.dl[2].max_x) == len(self.dl[2].max_y) \
                    and len(self.dm[2].ve) > 0:
                    e = self.dm[2].ve[-1]
                    if e.dir == 1:
                        cp = int(cur_pos / self.dm[2].down_int)
                        hop = (self.dm[2].price[cp] - self.dl[2].min_y[-self.dm[2].predict_len]) / my_hop
                        if hop > 1:
                            self.openShort(inst, cur_pos)
                            self.status = 0
            else:
                self.status = 0
                print cur_pos, 'Cancel prepare open short'




#
# prepare to open or close at paraller two lines
# but find a good enter point
#
class PrepareParalle_v3(Trade):
    enum_action_status = dict({0: 'unkonw', 1: 'pre-open long', 2: 'pre-open short',
                               -1: 'pre-close long', -2: 'pre-close short'})
    def __init__(self):
        self.status = 0

    def do_not_wait_to_close__(self, cur_pos):
        # print "--->", cur_pos
        return False

    def should_close_(self, inst, cur_pos):
        if self.order[-1].direct == 1:
            # i9888 20171013 1038510, 1045010
            if (self.la[1].s_max < 0 and self.la[1].s_min < 0) \
                  or ((self.la[1].i_type == 2 or self.la[1].i_type == 1) \
                    and (self.la[1].s_max < 0)):
                if self.la[0].s_max > 0 and (self.la[3].s_max < 0 and self.la[3].s_min < 0):
                    if self.do_not_wait_to_close__(cur_pos):
                        self.closePosition(inst, cur_pos)
        else:

            pass

    def price_near_min_line__(self, cur_pos):
        pos = - self.dm[2].predict_len
        near = abs(self.dm[2].hp[self.dm[2].cp] - self.dl[2].min_y[pos])/(self.dl[2].max_y[pos] - self.dl[2].min_y[pos])
        # print 'near --', pos, near, self.dm[2].hp[pos], self.dl[2].max_y[pos], self.dl[2].min_y[pos]
        if near > 0 and near < 0.1:
            return True
        else:
            return False

    def should_open_(self, inst, cur_pos):
        threshold_max = 30.0
        threshold_min = 25.0
        if 0 == self.la[2].i_type:
            # i9888 20171013 1034010
            # 034011 2:33.99,28.07,0 1:61.50,13.84,2 0:43.86,27.25,2
            # price_near_min_line = 0.024
            #     s_max >= 40 is strong doing up and s_max >= 60 is very strong
            # if 0,1 strong going up and the new price .lt. first extreme and near to min_line
            if self.la[2].s_max > threshold_max and self.la[2].s_min > threshold_min:
                if self.la[1].s_max > threshold_max and self.la[1].s_min > 0 \
                    and self.la[0].s_max > threshold_max and self.la[0].s_min > 0:
                    if self.price_near_min_line__(cur_pos):
                        self.openLong(inst, cur_pos)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass


class TrendsPredict_v1(Trade):
    pass

def get_trader(trade_name):
    if trade_name == 'tp1':
        return TrendsPredict_v1()
    elif trade_name == 's':
        return SimpleTrade()
    elif trade_name == 'p1':
        return PrepareParalle_v1()
    elif trade_name == 'p2':
        return PrepareParalle_v2()
    elif trade_name == 'p3':
        return PrepareParalle_v3()
    else:
        return Trade()
