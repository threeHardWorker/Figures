import matplotlib.pyplot as plt
import gc, sys


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

    instrument = sys.argv[1].encode('ascii')
    version = sys.argv[3].encode('ascii')
    if sys.argv[2] == 'test':
        log_path = '/app/sean/kp/q7-' + version + '-t/tick/' + instrument + '-gom.log'
    else:
        log_path = '/app/sean/kp/q7-' + version + '/tick/' + instrument + '-gom.log'

    with open(log_path) as fp:
        for line in fp:
            s = line.split(',')
            if len(s) == 11:
                x.append(float(s[3]))
                r += float(s[7])
                cls_rev.append(float(s[7]))
                rev.append(r)

    plt.plot(x, rev)
    plt.show()

    plt.plot(x, cls_rev)
    plt.show()
