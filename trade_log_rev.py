import matplotlib.pyplot as plt
import gc, sys
from datetime import datetime


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'Usage: python trade_log_rev.py <instrument> <train|test> <version>\n'
        exit(0)

    gc.disable()
    gc.enable()

    x = []
    cls_rev = []
    rev = []
    r = 0.0
    str_pair = []

    instrument = sys.argv[1].encode('ascii')
    version = sys.argv[3].encode('ascii')
    if sys.argv[2] == 'test':
        log_path = '/app/sean/kp/q7-' + version + '-t/tick/' + instrument + '-gom.log'
    else:
        log_path = '/app/sean/kp/q7-' + version + '/tick/' + instrument + '-gom.log'

    with open(log_path) as fp:
        for line in fp:
            if line[0] == '[':
                continue

            s = line.split(',')
            if len(s) == 11:
                x.append(float(s[3]))
                c_rev = float(s[7])
                r += c_rev
                cls_rev.append(c_rev)
                rev.append(r)
                str_time = \
                    datetime.fromtimestamp(float(s[10])).strftime("%y-%m-%d %H:%M:%S")
                pair = '[\"%s\",%.02f]' % (str_time, r)
                str_pair.append(pair)

    plt.plot(x, rev)
    plt.show()

    plt.plot(x, cls_rev)
    plt.show()

    datapath = 'data.echats-' + instrument
    with open(datapath, 'w') as fp:
        fp.write('[')
        fp.write(str_pair[0])
        size = len(str_pair)
        i = 1
        while i < size:
            fp.write(',')
            fp.write(str_pair[i])
            i += 1
        fp.write(']')
