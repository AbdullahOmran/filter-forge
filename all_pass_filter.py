import random

import numpy as np
import pyqtgraph as pg
from scipy.signal import freqz, tf2zpk
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class AllPassFilterFeature(object):
    def __init__(self, filters = None, phase_w = None, poles_zeros_w = None):
        self.phase_scene = phase_w if phase_w is not None else pg.PlotWidget()
        self.mag_scene = pg.PlotWidget()
        self.zeros_poles_scene = poles_zeros_w if poles_zeros_w is not None else pg.PlotWidget()
        self.all_pass_filters = filters if filters is not None else []

    def get_scene(self):
        self.phase_scene.clear()
        self.mag_scene.clear()
        self.zeros_poles_scene.clear()
        for filter in self.all_pass_filters:
            mag,phase = filter.get_frequency_response_plots()
            poles,zeros,circle = filter.get_zeros_poles_plot()
            # c = (random.uniform(0,255),random.uniform(0,255),random.uniform(0,255))
            # pen = pg.mkPen(color = c)
            # self.mag_scene.setPen(pen)
            # self.phase_scene.setPen(pen)
            # self.zeros_poles_scene.setPen(pen)
            self.phase_scene.addItem(phase)
            self.mag_scene.addItem(mag)
            self.zeros_poles_scene.addItem(poles)
            self.zeros_poles_scene.addItem(zeros)
            self.zeros_poles_scene.addItem(circle)
            self.zeros_poles_scene.setBackground((25, 35, 45))
            self.x_axis = pg.InfiniteLine(pos=0, angle=0, pen=(255, 0, 0), movable=False)
            self.y_axis = pg.InfiniteLine(pos=0, angle=90, pen=(0, 255, 0), movable=False)
            self.zeros_poles_scene.addItem(self.x_axis)
            self.zeros_poles_scene.addItem(self.y_axis)

        return  self.phase_scene,self.mag_scene,self.zeros_poles_scene

    def apply_filters(self, filter):
        responses  = []
        for f in self.all_pass_filters:
            _,all_pass_res = f.get_freq_response()
            responses.append(all_pass_res)
        responses = np.array(responses)
        # apply element wise product
        all_pass_filters_res = np.prod(responses,axis=0)
        result = all_pass_filters_res * filter
        return result

class AllPassFilter:
    def __init__(self, a):
        self.a = a
        self.zeros, self.poles, self.gain = tf2zpk([-np.conjugate(a), 1], [1, -a])
        self.freq_response_plot = self.get_frequency_response_plots()
        self.zeros_poles_plot = self.get_zeros_poles_plot()
        self.frequencies, self.phase_values = self.calculate_phase_response()
        

    def transfer_function(self, z):
        return (z**-1 - self.a) / (1 - self.a * z**-1)
    def get_freq_response(self):
                # Frequency response
        frequencies, response = freqz([-np.conjugate(self.a), 1], [1, -self.a], worN=8000)
        return frequencies, response

    def get_frequency_response_plots(self):
        # Frequency response
        frequencies, response = freqz([-np.conjugate(self.a), 1], [1, -self.a], worN=8000)
        
        # Plot magnitude response

        mag_plot = pg.PlotDataItem(0.5 * frequencies / np.pi, np.abs(response))
        # Plot phase response
        phase_plot = pg.PlotDataItem(0.5 * frequencies / np.pi, np.angle(response))

        return mag_plot, phase_plot

    def get_zeros(self):
        return self.zeros

    def get_poles(self):
        return self.poles

    def get_zeros_poles_plot(self):
        # Plot zeros and poles
        # win = pg.plot(title='Zeros, Poles, and Unit Circle in Z-Plane', labels={'left': 'Imaginary', 'bottom': 'Real'}, clear=True)
        # win.plot(self.zeros.real, self.zeros.imag, symbol='o', pen=None, name='Zeros')
        # win.plot(self.poles.real, self.poles.imag, symbol='x', pen=None, name='Poles')
        # win.addLine(x=0, pen=pg.mkPen('k', width=0.8, style=pg.QtCore.Qt.DashLine))
        # win.addLine(y=0, pen=pg.mkPen('k', width=0.8, style=pg.QtCore.Qt.DashLine))
        zeros_plot = pg.PlotDataItem(self.zeros.real, self.zeros.imag,size=15, symbol='o', pen='g', brush='g')
        poles_plot = pg.PlotDataItem(self.poles.real, self.poles.imag,size=15, symbol='x', pen='w', brush='w')
        # Plot unit circle
        theta = np.linspace(0, 2 * np.pi, 100)
        x_circle = np.cos(theta)
        y_circle = np.sin(theta)
        # win.plot(x_circle, y_circle, pen=pg.mkPen('g', width=1.5), name='Unit Circle')
        circle = pg.PlotDataItem(x_circle, y_circle, pen=pg.mkPen((0, 0, 255), width=1.5))

        return poles_plot,zeros_plot,circle

    def calculate_phase_response(self):
        # Calculate phase response at different frequencies
        frequencies, response = freqz([-np.conjugate(self.a), 1], [1, -self.a], worN=8000)
        phase_values = np.angle(response)
        return 0.5 * frequencies / np.pi, phase_values

# App = QApplication([])
# win = QMainWindow()
#
#
# f1 = AllPassFilter(a = 0.7)
# f2 = AllPassFilter(a = 0.2)
# f3 = AllPassFilter(a = 0.1)
# f = AllPassFilterFeature(filters=[f1,f2,f3])
# i1,i2,i3 = f.get_scene()
# f.apply_filters(22)
#
#
# win.setCentralWidget(i3)
# win.setGeometry(100,100,600,400)
#
# win.show()
# App.exec_()