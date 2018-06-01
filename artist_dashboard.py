class DashboardArtist:
    def __init__(self, m12, dcplp, ax):
        self.m12 = m12
        self.dcplp = dcplp
        self.ax = ax

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
        self.pa_s1 = self.ax.text(200, 420, '', fontsize=9, color='black')
        self.pa_s2 = self.ax.text(500, 420, '', fontsize=9, color='black')

        self.artist_ = (self.la_gcp, self.la_cp, self.la_s_max, self.la_s_min, self.la_i_type,
                        self.pa_type, self.pa_spos, self.pa_sval, self.pa_epos,
                        self.pa_eval, self.pa_maxp, self.pa_maxv, self.pa_minp,
                        self.pa_minv, self.pa_s1, self.pa_s2)

    def init_animation(self):
        return []

    def update(self, cur_pos):
        pass

    def animate(self, cur_pos):
        self.update(cur_pos)
        return self.artist_
