import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import artist_analysis
from libnrlib import *
import par
import math
import ctypes


libc = ctypes.CDLL(ctypes.util.find_library('c'))
libc.free.argtypes = (ctypes.c_void_p,)


class SubplotAnimation(animation.TimedAnimation):
    def __init__(self, m12, trade, params, index, dcplp, epos, stop_pos):
        self.index = index
        self.fig = plt.figure(index, figsize=(8, 4.5))
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.tight_layout()
        self.params = params
        self.epos = epos
        self.fig.canvas.set_window_title(params.inst)

        self.m12 = m12
        self.trade = trade
        self.dcplp = dcplp
        self.stop_pos = stop_pos

        self.art = artist_analysis.Artist(m12, dcplp, self.ax, "art")

        self.anim_interval = 10

        self.cur_pos = self.params.data_len
        self.show_future = True

        if self.index == 0:
            self.fig.canvas.mpl_connect('key_press_event', self.press)
            self.fig.canvas.mpl_connect('close_event', self.handle_close)

        # self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
                                          event_source=self.event_source, blit=True)


    def handle_close(self, event):
        self.event_source.stop()

    def press(self, event):
        # print event.key
        if event.key == 't':
            self.show_future = not self.show_future
        elif event.key == 'x':
            self.event_source.stop()
            self.params.run_status = -1
        elif event.key == 'r':
            if (self.params.run_status == 1):
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
 

    def _draw_frame(self, framedata):
        self.cur_pos = self.params.curpos

        self._drawn_artists = ()
        for i in range(0, 12):
            self._drawn_artists += self.art.animate(self.cur_pos, self.epos, self.show_future)



    def new_frame_seq(self):
        return iter(range(self.params.all_len))

    def _init_draw(self):
        for i in range(0, 12):
            self.art.init_animation()
