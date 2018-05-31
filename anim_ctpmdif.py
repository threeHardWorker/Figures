import math
from libnrlib import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt

import artist_ctpmdif
import par


class SubplotAnimation(animation.TimedAnimation):
    def __init__(self, m12, params, index, dcplp, stop_pos):
        self.index = index
        self.fig = plt.figure(index, figsize=(16, 9))
        self.ax = [self.fig.add_subplot(3, 4, 1),
                   self.fig.add_subplot(3, 4, 2),
                   self.fig.add_subplot(3, 4, 3),
                   self.fig.add_subplot(3, 4, 4),
                   self.fig.add_subplot(3, 4, 5),
                   self.fig.add_subplot(3, 4, 6),
                   self.fig.add_subplot(3, 4, 7),
                   self.fig.add_subplot(3, 4, 8),
                   self.fig.add_subplot(3, 4, 9),
                   self.fig.add_subplot(3, 4, 10),
                   self.fig.add_subplot(3, 4, 11),
                   self.fig.add_subplot(3, 4, 12)]

        self.region = [par.Rect() for _ in range(12)]
        self.fig.tight_layout()
        self.params = params
        self.fig.canvas.set_window_title(params.inst)

        self.m12 = m12
        self.dcplp = dcplp
        self.stop_pos = stop_pos

        self.art = []
        for i in range(12):
            self.art.append(
                artist_ctpmdif.Artist(m12, self.dcplp,
                                      self.ax[i], "art" + str(i), i))

        self.anim_interval = 10

        self.cur_pos = self.params.data_len
        self.show_future = False  # True

        if self.index == 0:
            self.fig.canvas.mpl_connect('key_press_event', self.press)
            self.fig.canvas.mpl_connect('close_event', self.handle_close)
            self.fig.canvas.mpl_connect('resize_event', self.on_resize)
            self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
                                          event_source=self.event_source, blit=True)

    def onclick(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        for i in range(12):
            if self.region[i].in_rect(event.x, event.y):
                di = int(math.pow(2, i))
                pos = int(event.xdata * di)
                minutes = int((pos - self.cur_pos) * 5 / 60)
                print '%d:( %d - %d) %d, %.02f -> %.02f'\
                      % (i, pos, pos + di, minutes,
                         event.ydata, self.m12.hop_to_price(event.ydata))

    def on_resize(self, event):
        # print 'on_resize'
        for i in range(12):
            bbox = self.ax[i].get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
            d = self.fig.dpi
            self.region[i].set_rect(bbox.x0 * d, bbox.y0 * d, bbox.x1 * d, bbox.y1 * d)
            # print i, ':', bbox.x0 * d, bbox.y0 * d, bbox.x1 * d, bbox.y1 * d
        if self.event_source is not None:
            self.event_source.stop()

    def handle_close(self, event):
        if self.event_source is not None:
            self.event_source.stop()

    def press(self, event):
        # print event.key
        if event.key == 'x':
            self.event_source.stop()
            self.params.run_status = -100
        elif event.key == 'd':
            print self.dcplp.skewer_to_string()
            self.m12.print_channel_line_attr()
        elif event.key == 'a':
            imgpath = '/home/sean/tmp/trade/' + self.params.inst + '-' \
                      + self.params.date + '-' + str(self.params.curpos) + '.png'
            plt.savefig(imgpath)
            print 'save to', imgpath
        elif event.key == 'w':
            tp = TrendPercent()
            self.m12.get_trend_percent(tp)
            print tp.up, tp.down, tp.chaos, tp.up_ch, tp.down_ch, tp.ch

    def _draw_frame(self, framedata):
        self.cur_pos = self.params.curpos

        self._drawn_artists = ()
        for i in range(0, 12):
            self._drawn_artists += self.art[i].animate(self.cur_pos, self.show_future)

    def new_frame_seq(self):
        return iter(range(self.params.all_len))

    def _init_draw(self):
        for i in range(0, 12):
            self.art[i].init_animation()
