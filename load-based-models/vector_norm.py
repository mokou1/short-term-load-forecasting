import pandas as pd
import numpy as np
import scipy.stats as sts
from matplotlib import pyplot as plt

class VectorNorm(object):
    def __init__(self):
        self.set_data()
        self.sunday = []
        self.monday = []
        self.tuesday = []
        self.wednesday = []
        self.thursday = []
        self.friday = []
        self.saturday = []
        self.day_diff = [self.sunday, self.monday, self.tuesday, self.wednesday, self.thursday,
                         self.friday, self.saturday]
        self.params = []
        self.anomalies = []
        self.expected = []
        self.actual = []
        self.confd_lev = 3.0
        self.form_sets()
        self.set_params()

    def set_data(self):
        self.data = pd.read_csv("LD2011_2014.csv")
        self.lower_lim = 365*96 - 1
        self.stop = self.lower_lim + 1096*96 + 1
        self.load_pointer = self.lower_lim

    def get_diff_vector(self):
        curr = np.array(self.data.Load_kW[self.load_pointer: self.load_pointer + 96].values)
        sim_curr = np.array(self.data.Load_kW[self.load_pointer - 96*7: self.load_pointer - 96*6].values)
        return curr - sim_curr

    def norm(self, vector_list):
        return np.linalg.norm(vector_list, 2)

    def form_sets(self):
        while True:
            for day in self.day_diff:
                if self.load_pointer >= self.stop:
                    return
                vector = self.get_diff_vector()
                day.append(self.norm(vector))
                self.load_pointer += 96

    def set_params(self):
        for day in self.day_diff:
            self.params.append(sts.norm.fit(day))

    def find_anomalies(self):
        self.load_pointer = self.lower_lim
        while True:
            for day in self.params:
                if self.load_pointer >= self.stop:
                    return
                lim = day[0] + self.confd_lev*day[1]
                self.expected.append(lim)
                val = self.norm(self.get_diff_vector())
                self.actual.append(val)
                if val > lim:
                    self.anomalies.append((self.data.YMDHMS[self.load_pointer][0:10], val, abs(val-lim)))
                self.load_pointer += 96

    def print_anomalies(self):
        for an in self.anomalies:
            print("Date: {0} \t Norm: {1} \t Difference: {2}".format(an[0], an[1], an[2]))
        print("{0} anomalies detected.".format(len(self.anomalies)))

    def get_anomalies(self):
        baddates = [d for d, n, diff in self.anomalies]
        return baddates

    def view_profiles(self):
        fig, ax = plt.subplots()
        l1, = ax.plot(self.expected, 'r', label='Expecteds')
        l2, = ax.plot(self.actual, 'y', label='Actuals')
        ax.set_xlabel('Day - 1/1/12 - 31/12/14')
        ax.set_ylabel('2nd Difference Norm wrt 1 week')
        ax.set_title("Vector Norm: Expected vs Actual")
        ax.legend((l1, l2), ('Expected', 'Actual'), shadow=True)
        plt.show()

if __name__ == "__main__":
    vn = VectorNorm()
    vn.find_anomalies()
    vn.print_anomalies()
    vn.view_profiles()