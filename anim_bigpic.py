import ctypes
import math
import time
from libnrlib import *

import matplotlib.animation as animation
import matplotlib.pyplot as plt

import artist9
import artist_bigpic
import par

libc = ctypes.CDLL(ctypes.util.find_library('c'))
libc.free.argtypes = (ctypes.c_void_p,)


class SubplotAnimation9:
    def __init__(self, m12, params, dcplp, stop_pos):
        self.fig = plt.figure(0, figsize=(16, 9))
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
        self.fig.canvas.set_window_title(params.inst + ' m12')

        self.m12 = m12
        self.dcplp = dcplp
        self.stop_pos = stop_pos

        self.art = []
        for i in range(12):
            self.art.append(artist9.Artist9(m12, self.dcplp, self.ax[i], "art" + str(i), i))

        self.anim_interval = 10

        self.cur_pos = self.params.data_len
        self.show_future = False  # True

        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        self.fig2 = plt.figure(1, figsize=(16, 9))
        self.ax2 = self.fig2.add_subplot(1, 1, 1)
        self.fig2.tight_layout()
        self.fig2.canvas.set_window_title(params.inst + ' bigpic')
        self.region2 = par.Rect()

        self.art2 = artist_bigpic.ArtistBigPicture(m12, dcplp, self.ax2, "bigpic", 7)
        self.fig2.canvas.mpl_connect('key_press_event', self.press)
        self.fig2.canvas.mpl_connect('close_event', self.handle_close)
        self.fig2.canvas.mpl_connect('resize_event', self.on_resize2)
        self.fig2.canvas.mpl_connect('button_press_event', self.onclick2)
        # animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
        #                                   event_source=self.event_source, blit=True)
        # animation.TimedAnimation.__init__(self, self.fig2, interval=self.anim_interval,
        #                                  event_source=self.event_source, blit=True)
        self.ani1 = animation.FuncAnimation(self.fig, self.draw_frame_1, self.params.all_len,
                                            init_func=self.init_draw_1,
                                            interval=self.anim_interval,
                                            blit=True)
        self.ani2 = animation.FuncAnimation(self.fig2, self.draw_frame_2, self.params.all_len,
                                            init_func=self.init_draw_2,
                                            interval=self.anim_interval,
                                            blit=True)

    def onclick(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        for i in range(12):
            if self.region[i].in_rect(event.x, event.y):
                di = int(math.pow(2, i))
                pos = int(event.xdata * di)
                minutes = int((pos - self.cur_pos) * 5 / 60)
                print '%d:( %d - %d) time: %d, (%.02f -> %.02f)'\
                      % (i, pos, pos + di, minutes,
                         event.ydata, self.m12.hop_to_price(event.ydata))

    def onclick2(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
        if self.region2.in_rect(event.x, event.y):
            di = int(math.pow(2, 7))
            pos = int(event.xdata * di)
            minutes = int((pos - self.cur_pos) * 5 / 60)
            print '( %d - %d) %d, %.02f -> %.02f'\
                  % (pos, pos + di, minutes,
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

    def on_resize2(self, event):
        # print 'on_resize'
        bbox = self.ax2.get_window_extent().\
            transformed(self.fig2.dpi_scale_trans.inverted())
        d = self.fig2.dpi
        self.region2.set_rect(bbox.x0 * d, bbox.y0 * d, bbox.x1 * d, bbox.y1 * d)

        if self.event_source is not None:
            self.event_source.stop()

    def handle_close(self, event):
        if self.event_source is not None:
            self.event_source.stop()

    def press(self, event):
        # print event.key
        if event.key == 't':
            self.show_future = not self.show_future
        elif event.key == 'x':
            self.event_source.stop()
            self.params.run_status = -1
            plt.close(self.fig)
            plt.close(self.fig2)
        elif event.key == 'r':
            if self.params.run_status == 1:
                self.params.run_status = 0
                self.event_source.stop()
            elif self.params.run_status == 0:
                self.params.run_status = 1
                self.event_source.start()
        elif event.key == '=':
            if self.params.interval > 0.0001:
                self.params.interval /= 2
        elif event.key == '-':
            self.params.interval *= 2
        elif event.key == 'o':
            print 'curpos', self.params.curpos
        elif event.key == 'd':
            if self.params.run_status == 1:
                self.params.run_status = 0
                time.sleep(0.5)
            print self.dcplp.skewer_to_string()
            self.m12.print_channel_line_attr()
        elif event.key == 'z':
            if self.params.run_status == 1:
                self.params.run_status = 0
                time.sleep(0.5)
            print self.dcplp.sequence_to_string()
        elif event.key == 'a':
            self.params.run_status = 0
            time.sleep(0.5)
            self.event_source.stop()
            imgpath = '/home/sean/tmp/trade/' + self.params.inst + '-' \
                      + self.params.date + '-' + str(self.params.curpos) + '.png'
            plt.savefig(imgpath)
            print 'save to', imgpath
        elif event.key == 'p':
            self.params.run_status = 0
            self.event_source.stop()
        elif event.key == 'w':
            tp = TrendPercent()
            self.m12.get_trend_percent(tp)
            print tp.up, tp.down, tp.chaos, tp.up_ch, tp.down_ch, tp.ch
        elif event.key == 'e':
            self.m12.show_predict_detail(-1)

    def draw_frame_1(self, framedata):
        self.cur_pos = self.params.curpos
        drawn_artists = ()
        for artist in self.art:
            drawn_artists += artist.animate(self.cur_pos, self.show_future)
        return drawn_artists

    def init_draw_1(self):
        lines = []
        for artist in self.art:
            lines += artist.init_animation()
        return tuple(lines)

    def draw_frame_2(self, framedata):
        self.cur_pos = self.params.curpos
        return self.art2.animate(self.cur_pos, self.show_future)

    def init_draw_2(self):
        return tuple(self.art2.init_animation())
