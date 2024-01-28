
import numpy as np
import pyqtgraph as pg
from scipy.signal import freqz, tf2zpk
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class AllPassFilterFeature(object):
    def __init__(self):
        self.phase_scene = pg.GraphicsScene()
        self.mag_scene = pg.GraphicsScene()
        self.zeros_poles_scene = pg.GraphicsScene()
        self.all_pass_filters = []

    def get_scene(self):
        self.scene.removeItem()
        for filter in self.all_pass_filters:
            self.scene.addItem(filter)
    def apply_filters(self, filter):
        pass

class AllPassFilter:
    def __init__(self, a):
        self.a = a
        self.zeros, self.poles, self.gain = tf2zpk([1, -a], [1, -a])
        self.freq_response_plot = self.plot_frequency_response()
        self.zeros_poles_plot = self.plot_zeros_poles()
        self.frequencies, self.phase_values = self.calculate_phase_response()

    def transfer_function(self, z):
        return (z**-1 - self.a) / (1 - self.a * z**-1)

    def plot_frequency_response(self):
        # Frequency response
        frequencies, response = freqz([1, -self.a], [1, -self.a], worN=8000)

        # Plot magnitude response
        mag_plot = pg.plot(0.5 * frequencies / np.pi, np.abs(response), title='All-Pass Filter Frequency Response', xlabel='Frequency [Hz]', ylabel='Magnitude', pen='b', clear=True)

        # Plot phase response
        phase_plot = pg.plot(0.5 * frequencies / np.pi, np.angle(response), title='All-Pass Filter Phase Response', xlabel='Frequency [Hz]', ylabel='Phase [radians]', pen='r', clear=True)
       
        return mag_plot, phase_plot

    def get_zeros(self):
        return self.zeros

    def get_poles(self):
        return self.poles

    def plot_zeros_poles(self):
        # Plot zeros and poles
        win = pg.plot(title='Zeros, Poles, and Unit Circle in Z-Plane', labels={'left': 'Imaginary', 'bottom': 'Real'}, clear=True)
        win.plot(self.zeros.real, self.zeros.imag, symbol='o', pen=None, name='Zeros')
        win.plot(self.poles.real, self.poles.imag, symbol='x', pen=None, name='Poles')
        win.addLine(x=0, pen=pg.mkPen('k', width=0.8, style=pg.QtCore.Qt.DashLine))
        win.addLine(y=0, pen=pg.mkPen('k', width=0.8, style=pg.QtCore.Qt.DashLine))

        # Plot unit circle
        theta = np.linspace(0, 2 * np.pi, 100)
        x_circle = np.cos(theta)
        y_circle = np.sin(theta)
        win.plot(x_circle, y_circle, pen=pg.mkPen('g', width=1.5), name='Unit Circle')

        return win

    def calculate_phase_response(self):
        # Calculate phase response at different frequencies
        frequencies, response = freqz([1, -self.a], [1, -self.a], worN=8000)
        phase_values = np.angle(response)
        return 0.5 * frequencies / np.pi, phase_values

App = QApplication([])
window = QMainWindow()
AllPassFilter(a=0.5)
w  = pg.PlotWidget()
window.setCentralWidget(w)
window.show()
App.exec_()