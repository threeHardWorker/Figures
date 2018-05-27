import matplotlib.pyplot as plt
import tmath
from libnrlib import *

m_data_len = 1024
m_predict_len = 128


class Artist:
    def __init__(self, m12, dcplp, ax, name):
        self.m12 = m12
        self.dcplp = dcplp
        self.name = name
        self.ax = ax
        
        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([0, 100])

        colors = [(13.0 / 255.0, 57.0 / 255.0, 0.0 / 255.0),
                  (21.0 / 255.0, 96.0 / 255.0, 0.0 / 255.0),
                  (29.0 / 255.0, 125.0 / 255.0, 0.0 / 255.0),
                  (35.0 / 255.0, 155.0 / 255.0, 0.0 / 255.0),
                  (44.0 / 255.0, 196.0 / 255.0, 0.0 / 255.0),
                  (51.0 / 255.0, 227.0 / 255.0, 0.0 / 255.0),
                  (63.0 / 255.0, 255.0 / 255.0, 0.0 / 255.0),
                  (97.0 / 255.0, 255.0 / 255.0, 51.0 / 255.0),
                  (156.0 / 255.0, 255.0 / 255.0, 128.0 / 255.0),
                  (194.0 / 255.0, 255.0 / 255.0, 176.0 / 255.0)
                  ]

        self.lCurrent, = self.ax.plot([], [], lw=1, color='blue')
        self.lFuture, = self.ax.plot([], [], lw=1, color='yellow')
        self.lAnalysis, = self.ax.plot([], [], lw=1, color='red')

        self.lines = [self.lCurrent, self.lFuture, self.lAnalysis]
        self.x1 = []
        self.x2 = []
        self.x3 = []
        self.y1 = []
        self.y2 = []
        self.y3 = []

 
    def init_animation(self):
        for line in self.lines:
            line.set_data([], [])
        return self.lines


    def update_limite(self, xlim, ylim, cp, show_future):
        self.ax.set_xlim([self.x1[0], self.x2[-1]])
        self.ax.set_ylim([min(ylim[0], min(min(self.y1), min(self.y2)) - 10),
                          max(ylim[1], max(max(self.y1), max(self.y2)) + 10)])


    def update_lines(self, cp, show_future):
        self.lCurrent.set_data(self.x1, self.y1)
        if (show_future):
            self.lFuture.set_data(self.x2, self.y2)
        self.lAnalysis.set_data(self.x3, self.y3)


    def animate(self, cur_pos, epos, show_future):
        self.x1 = []
        self.y1 = []
        self.x2 = []
        self.y2 = []
        get_analysis_price(self.m12, cur_pos, epos, self.y1, self.y2,
                          self.x1, self.x2)
        self.x3 = []
        self.y3 = []
        get_analysis_data(self.dcplp, self.x3, self.y3)

        cp = cur_pos
        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        self.update_limite(xlim, ylim, cp, show_future)
        self.update_lines(cp, show_future)
        return tuple(self.lines)


    '''
    def update(self, cur_pos, show_future=True):
        cp = 1
        if cp >= len(self.price):
            return

        xlim = list(self.ax.get_xlim())
        ylim = list(self.ax.get_ylim())
        self.update_limite(xlim, ylim, cp, show_future)
        self.update_lines(cp, show_future)
    '''
