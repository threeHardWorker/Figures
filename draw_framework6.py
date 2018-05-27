import matplotlib.pyplot as plt
import artist6
from libnrlib import *

class DrawFramework6():
    def __init__(self, m12, shot, trade, params, index):
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

        self.art = []
        for i in range(12):
            self.art.append(artist6.Artist6(m12, shot, self.ax[i], "art" + str(i), i))
            # self.art.append(artist4.Artist10l(m12, self.ax[i], i))

        self.anim_interval = 10

        self.cur_pos = self.params.data_len
        self.show_future = True


    def draw_frame(self, curpos):
        self.cur_pos = curpos
        # print self.cur_pos, len(self.save_pos)

        for i in range(0, 12):
            self.art[i].animate(self.cur_pos, self.show_future)
        # self.fig.canvas.draw()

    def save_frame(self):
        # print self.save_pos, self.cur_pos
        imgpath = self.params.imgpath + '/' + \
                  self.params.inst + '-' + \
                  self.params.date +  '-' + \
                  str(self.cur_pos) + '.png'
        plt.savefig(imgpath)
        print 'save to', imgpath


    def _init_draw(self):
        for i in range(0, 12):
            self.art[i].init_animation()
