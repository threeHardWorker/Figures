import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import artist6
from libnrlib import *

class SubplotAnimation6(animation.TimedAnimation):
    def __init__(self, m12, shot, trade, params, index, save_pos):
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

        self.fig.tight_layout()
        self.params = params
        self.fig.canvas.set_window_title(params.inst)

        self.m12 = m12
        self.shot = shot
        self.trade = trade
        self.save_pos = save_pos

        self.art = []
        for i in range(12):
            self.art.append(artist6.Artist6(m12, shot, self.ax[i], "art" + str(i), i))
            # self.art.append(artist2.Artist10l(m12, self.ax[i], i))

        self.anim_interval = 10

        self.cur_pos = self.params.data_len
        self.show_future = True

        if self.index == 0:
            self.fig.canvas.mpl_connect('key_press_event', self.press)
            self.fig.canvas.mpl_connect('close_event', self.handle_close)
            self.fig.canvas.mpl_connect('resize_event', self.on_resize)

        # self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
                                          event_source=self.event_source, blit=True)

    def on_resize(self, event):
        self.event_source.stop()

    def handle_close(self, event):
        self.event_source.stop()

    def jump(self, pos):
        self.params.run_status = 0
        time.sleep(0.25)
        if pos > 10 or pos < 0:
            for art in self.art:
                art.clean_predict_lines()

            self.m12.ph_clear()
            self.m12.do_math(self.params.curpos)

        self.params.curpos += pos


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
        elif event.key == 'h':
            self.jump(-100)
        elif event.key == 'j':
            self.jump(-10)
        elif event.key == '\'':
            self.jump(101)
        elif event.key == ';':
            self.jump(10)
        elif event.key == 'n':
            self.jump(-1000)
        elif event.key == 'm':
            self.jump(1000)
        elif event.key == ',':
            self.jump(-1)
        elif event.key == '.':
            self.jump(1)
        elif event.key == 'o':
            print 'curpos', self.params.curpos
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
        # print self.cur_pos, len(self.save_pos)

        self._drawn_artists = ()
        for i in range(0, 12):
            self._drawn_artists += self.art[i].animate(self.cur_pos, self.show_future)
        # self.fig.canvas.draw()

        if self.cur_pos in self.save_pos:
            # print self.save_pos, self.cur_pos
            imgpath = '/home/sean/tmp/trade/' + self.params.inst + '-' \
                        + self.params.date + '-' + str(self.cur_pos) + '.png'
            plt.savefig(imgpath)
            self.save_pos.remove(self.cur_pos)
            print 'save to', imgpath, len(self.save_pos)


    def new_frame_seq(self):
        return iter(range(self.params.all_len))

    def _init_draw(self):
        for i in range(0, 12):
            self.art[i].init_animation()

'''
class AllPredictAnimation(animation.TimedAnimation):
    def __init__(self, dm):
        self.dm = dm

        self.fig = plt.figure(0, figsize=(9, 5))
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.art = artist.Artist10l(dm, self.ax)
        self.fig.tight_layout()
        self.art.set_dm_int(dm.down_int)
        self.fig.canvas.set_window_title('Math')

        self.anim_interval = 0

        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
        self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        # self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
                                          event_source=self.event_source, blit=True)

    def _draw_frame(self, framedata):
        self.dm.do_math(self.cur_pos)
        if self.dm.qpl.qsize() >= 10:
            self._drawn_artists = self.art.animate(self.cur_pos)
        self.cur_pos += 1

    def new_frame_seq(self):
        return iter(range(1024000 + 128))

    def _init_draw(self):
        self.cur_pos = 1024000 - 1 # dm[0].all_len - 10
        self.art.init_animation()

    def on_resize(self, event):
        self.event_source.stop()

    def handle_close(self, event):
        self.event_source.stop()

    def press(self, event):
        if event.key == 'x':
            self.event_source.stop()




class DashboardArtist:
    def __init__(self, dm, ax, name):
        self.name = name
        self.ax = ax

        self.ax.set_xlim([0, 900])
        self.ax.set_ylim([0, 500])

        self.dm = dm
        self.dl = dm.dl
        self.la = dm.dl.la
        self.pa = dm.pa

        self.lines = []

        self.la_gcp = self.ax.text(1, 1, '', fontsize=9, color='black')
        self.la_cp = self.ax.text(300, 1, '', fontsize=9, color='black')
        self.la_s_max = self.ax.text(1, 70, '', fontsize=9, color='red')
        self.la_s_min = self.ax.text(200, 70, '', fontsize=9, color='green')
        self.la_i_type = self.ax.text(400, 70, '', fontsize=9, color='blue')

        self.pa_maxp = self.ax.text(1, 140, '', fontsize=9, color='red')
        self.pa_maxv = self.ax.text(450, 140, '', fontsize=9, color='red')
        self.pa_minp = self.ax.text(1, 210, '', fontsize=9, color='green')
        self.pa_minv = self.ax.text(450, 210, '', fontsize=9, color='green')


        self.pa_spos = self.ax.text(1, 280, '', fontsize=9, color='blue')
        self.pa_sval = self.ax.text(450, 280, '', fontsize=9, color='blue')
        self.pa_epos = self.ax.text(1, 350, '', fontsize=9, color='black')
        self.pa_eval = self.ax.text(450, 350, '', fontsize=9, color='black')

        self.pa_type = self.ax.text(1, 420, '', fontsize=9, color='black')
        self.pa_s1   = self.ax.text(200, 420, '', fontsize=9, color='black')
        self.pa_s2   = self.ax.text(500, 420, '', fontsize=9, color='black')

        self.artist_ = (self.la_gcp, self.la_cp, self.la_s_max, self.la_s_min, self.la_i_type,
                        self.pa_type, self.pa_spos, self.pa_sval, self.pa_epos,
                        self.pa_eval, self.pa_maxp, self.pa_maxv, self.pa_minp,
                        self.pa_minv, self.pa_s1, self.pa_s2)

    def init_animation(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines

    def set_dm_int(self, down_int):
        self.down_int = down_int

    def update(self, cp):
        global g_ani_curpos
        self.la_gcp.set_text(str(g_ani_curpos))
        self.la_cp.set_text(str(cp))
        self.la_s_max.set_text('%.02f' % (self.la.s_max))
        self.la_s_min.set_text('%.02f' % (self.la.s_min))
        self.la_i_type.set_text('%d' % (self.la.i_type))

        self.pa_type.set_text('%d'   % (self.pa.type))
        self.pa_maxp.set_text('%d'   % (self.pa.maxp)) # + cp))
        self.pa_minp.set_text('%d'   % (self.pa.minp)) # + cp))
        self.pa_spos.set_text('%d'   % (self.pa.spos)) # + cp))
        self.pa_epos.set_text('%d'   % (self.pa.epos)) # + cp))
        self.pa_maxv.set_text('%.02f' %(self.pa.maxv))
        self.pa_minv.set_text('%.02f' %(self.pa.minv))
        self.pa_sval.set_text('%.02f' %(self.pa.sval))
        self.pa_eval.set_text('%.02f' %(self.pa.eval))
        self.pa_s1  .set_text('%.02f' %(self.pa.slope_1  ))
        self.pa_s2  .set_text('%.02f' %(self.pa.slope_2  ))

    def animate(self, cur_pos):
        cp = cur_pos / self.down_int
        self.update(cp)

        return tuple(self.lines) + self.artist_


class Dashboard(animation.TimedAnimation):
    def __init__(self, dm):
        self.fig = plt.figure(0, figsize=(5,2.5))
        self.ax = []
        for i in range(0, len(dm)):
            ax = self.fig.add_subplot(2, 2, i + 1)
            cur_axes = plt.gca()
            cur_axes.axes.get_xaxis().set_ticks([])
            cur_axes.axes.get_yaxis().set_ticks([])

            self.ax.append(ax)

        self.fig.tight_layout()
        self.fig.canvas.set_window_title('Dashboard')

        self.dm = dm

        self.art = []
        for i in range(0, len(dm)):
            self.art.append(DashboardArtist(dm[i], self.ax[i], "art" + str(i)))
            self.art[i].set_dm_int(dm[i].down_int)

        self.anim_interval = 10
        self.cur_pos = dm[0].data_len

        self.event_source = self.fig.canvas.new_timer()
        self.event_source.interval = self.anim_interval

        animation.TimedAnimation.__init__(self, self.fig, interval=self.anim_interval,
                                          event_source=self.event_source, blit=True)


    def _draw_frame(self, framedata):
        global g_ani_curpos
        self.cur_pos = g_ani_curpos

        self._drawn_artists = ()
        for i in range(0, 4):
            self._drawn_artists += self.art[i].animate(self.cur_pos)

    def new_frame_seq(self):
        return iter(range(self.dm[0].all_len))

    def _init_draw(self):
        global g_ani_curpos
        self.cur_pos = g_ani_curpos # dm[0].all_len - 10
        for i in range(0, 4):
            self.art[i].init_animation()
'''
