import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QCheckBox
import numpy as np
from PyQt5.QtCore import Qt
from scipy.signal import freqz
from scipy import signal
import matplotlib.pyplot as plt

class ZPlanePlot(QWidget):
    def __init__(self):
        super().__init__()
        self.delete_flag = False  # Flag to control deletion or creation
        self.conjugate_flag = False  # Flag to determine if conjugate plotting is enabled

        self.init_ui()

    def init_ui(self):
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked()
        self.plot_widget.showGrid(x=False, y=False)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)

        # Draw the unit circle as a CircleROI
        self.unit_circle = pg.CircleROI([-1, -1], size=[2, 2], movable=False, pen=(0, 0, 255))
        self.plot_widget.addItem(self.unit_circle)

        # Draw x-axis and y-axis at the center of the circle
        self.x_axis = pg.InfiniteLine(pos=0, angle=0, pen=(255, 0, 0), movable=False)
        self.y_axis = pg.InfiniteLine(pos=0, angle=90, pen=(0, 255, 0), movable=False)
        self.plot_widget.addItem(self.x_axis)
        self.plot_widget.addItem(self.y_axis)

        self.zeros = []
        self.poles = []
        self.zero_items = []
        self.pole_items = []

        # for conjugate zerosf and polesf are for positions ------ otherwise are for items
        self.zerosf = []
        self.polesf = []
        self.zero_itemsf = []
        self.pole_itemsf = []
        self.plot_widget.scene().sigMouseClicked.connect(self.on_click)

        # Connect the double-click signal
        self.plot_widget.scene().sigMouseClicked.connect(self.on_double_click)

        # Add a QPushButton to clear all zeros and poles
        self.clear_all_button = QPushButton('Clear Zeros and Poles', self)
        self.clear_all_button.clicked.connect(self.clear_zeros_and_poles)
        layout.addWidget(self.clear_all_button)

        # Add a QPushButton to clear only the poles
        self.clear_poles_button = QPushButton('Clear Poles', self)
        self.clear_poles_button.clicked.connect(self.clear_poles)
        layout.addWidget(self.clear_poles_button)

        # Add a QPushButton to clear only the zeros
        self.clear_zeros_button = QPushButton('Clear Zeros', self)
        self.clear_zeros_button.clicked.connect(self.clear_zeros)
        layout.addWidget(self.clear_zeros_button)

        # Add a button to plot the frequency response
        self.plot_response_button = QPushButton('Plot Frequency Response', self)
        self.plot_response_button.clicked.connect(self.plot_frequency_response)
        layout.addWidget(self.plot_response_button)

        # Add a checkbox for reflection around x-axis
        self.reflect_checkbox = QCheckBox('Reflect around X-axis', self)
        # self.reflect_checkbox.stateChanged.connect(self.redraw_zeros_and_poles)

        layout.addWidget(self.reflect_checkbox)

        self.setLayout(layout)

    # def redraw_zeros_and_poles(self):
    #     # Clear existing items
    #     # self.clear_zeros_and_poles()
    #
    #     # Draw zeros
    #     for zero in self.zerosf:
    #         self.plot_zero(zero[0], zero[1])
    #
    #     # Draw poles
    #     for pole in self.polesf:
    #         self.plot_pole(pole[0], pole[1])

    def on_click(self, event):
        pos = self.plot_widget.getViewBox().mapSceneToView(event.scenePos())

        if self.reflect_checkbox.isChecked():
            if event.button() == 1:  # Left mouse button for poles
                # self.polesf.append((pos.x(), pos.y()))
                self.poles.append((pos.x(), pos.y()))
                self.plot_pole(pos.x(), pos.y())

            elif event.button() == 2:  # Right mouse button for zeros
                # self.zerosf.append((pos.x(), pos.y()))
                self.zeros.append((pos.x(), pos.y()))
                self.plot_zero(pos.x(), pos.y())

        elif not self.reflect_checkbox.isChecked():
            # Add a new point at the clicked position
            if event.button() == 1:  # Left mouse button for poles
                self.poles.append((pos.x(), pos.y()))
                self.plot_pole(pos.x(), pos.y())

            elif event.button() == 2:  # Right mouse button for zeros
                self.zeros.append((pos.x(), pos.y()))
                self.plot_zero(pos.x(), pos.y())

        # Call the redraw_zeros_and_poles function after updating zeros and poles
        # self.redraw_zeros_and_poles()

    def on_double_click(self, event):
        if event.double() == True:
            pos = self.plot_widget.getViewBox().mapSceneToView(event.scenePos())

            # Check if the double click is near any zero or pole
            for zero_item in self.zero_items:
                if np.linalg.norm(np.array(zero_item.pos()) - np.array([pos.x(), pos.y()])) < 0.1:
                    self.plot_widget.removeItem(zero_item)
                    self.zero_items.remove(zero_item)
                    self.zeros.remove((pos.x(), pos.y()))
                    break

            for pole_item in self.pole_items:
                if np.linalg.norm(np.array(pole_item.pos()) - np.array([pos.x(), pos.y()])) < 0.1:
                    self.plot_widget.removeItem(pole_item)
                    self.pole_items.remove(pole_item)
                    self.poles.remove((pos.x(), pos.y()))
                    break

    def clear_zeros_and_poles(self):
        # Clear all zeros and their corresponding items
        for zero_item in self.zero_items:
            self.plot_widget.removeItem(zero_item)
        for zero_itemf in self.zero_itemsf:
            self.plot_widget.removeItem(zero_itemf)
        self.zero_items = []
        self.zeros = []
        self.zerosf = []
        self.zero_itemsf = []
        # Clear all poles and their corresponding items
        for pole_item in self.pole_items:
            self.plot_widget.removeItem(pole_item)
        for pole_itemf in self.pole_itemsf:
            self.plot_widget.removeItem(pole_itemf)
        self.pole_items = []
        self.poles = []
        self.polesf = []
        self.pole_itemsf = []

    def clear_poles(self):
        # Clear all poles and their corresponding items
        for pole_item in self.pole_items:
            self.plot_widget.removeItem(pole_item)
        for pole_itemf in self.pole_itemsf:
            self.plot_widget.removeItem(pole_itemf)
        self.pole_items = []
        self.poles = []
        self.polesf = []
        self.pole_itemsf = []

    def clear_zeros(self):
        # Clear all zeros and their corresponding items
        for zero_item in self.zero_items:
            self.plot_widget.removeItem(zero_item)
        for zero_itemf in self.zero_itemsf:
            self.plot_widget.removeItem(zero_itemf)
        self.zero_items = []
        self.zeros = []
        self.zerosf = []
        self.zero_itemsf = []

    def plot_pole(self, x, y):
        # Plot the pole
        target_pole = pg.TargetItem(pos=[x, y], size=20, symbol='x', pen='w', brush='w', movable=True)
        self.pole_items.append(target_pole)
        self.plot_widget.addItem(target_pole)

        # Plot the reflected pole if the reflect checkbox is checked
        if self.reflect_checkbox.isChecked():
            reflected_y = -y
            self.polesf.append((x, reflected_y))
            target_reflected_pole = pg.TargetItem(pos=[x, reflected_y], size=20, symbol='x', pen='g', brush='g', movable=True)
            self.pole_itemsf.append(target_reflected_pole)
            self.plot_widget.addItem(target_reflected_pole)

    def plot_zero(self, x, y):
        # Plot the zero
        # if not self.reflect_checkbox.isChecked():
        target_zero = pg.TargetItem(pos=[x, y], size=20, symbol='o', pen='w', brush='w', movable=True)
        self.zero_items.append(target_zero)
        self.plot_widget.addItem(target_zero)

        # Plot the reflected zero if the reflect checkbox is checked
        if self.reflect_checkbox.isChecked():
            reflected_y = -y
            self.zerosf.append((x, reflected_y))
            target_reflected_zero = pg.TargetItem(pos=[x, reflected_y], size=20, symbol='o', pen='g', brush='g', movable=True)
            self.zero_itemsf.append(target_reflected_zero)
            self.plot_widget.addItem(target_reflected_zero)

    def plot_frequency_response(self):
        # Extract zeros and poles
        zeros = [complex(z[0], z[1]) for z in self.zeros]
        poles = [complex(p[0], p[1]) for p in self.poles]

        # Call the function to plot frequency response
        self.plot_response(zeros, poles)

    def plot_response(self, zeros, poles, frequency_range=(0.1, 10), num_points=1000):
        # Generate frequencies for the frequency range
        frequencies = np.logspace(np.log10(frequency_range[0]), np.log10(frequency_range[1]), num_points)

        # Calculate the frequency response
        system = signal.TransferFunction(zeros, poles)
        magnitude, phase, _ = signal.bode(system, frequencies)

        # Plot the magnitude response
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.semilogx(frequencies, magnitude)
        plt.title('Magnitude Response')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.grid(True)

        # Plot the phase response
        plt.subplot(2, 1, 2)
        plt.semilogx(frequencies, phase)
        plt.title('Phase Response')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase (degrees)')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        central_widget = ZPlanePlot()
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Z-Plane Plotter')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
