from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from main import ZPlaneSignalFilter
import pyqtgraph as pg

import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request

import os
from os import path
import SignalViewer as sv
from touch_pad import RealTimeGraph

ui, _ = loadUiType('main.ui')
def create_plot_widget(graphics_view, object_name="", bottom_label="", left_label="", signal_viewer_title=None,
                       signal_plot=None):
    widget = pg.PlotWidget(graphics_view)
    graphics_view_layout = QHBoxLayout(graphics_view)
    graphics_view_layout.addWidget(widget)
    graphics_view.setLayout(graphics_view_layout)
    widget.setObjectName(object_name)

    signal_viewer = sv.SignalViewerLogic(widget)

    signal_viewer.view.setLabel("bottom", text=bottom_label)
    signal_viewer.view.setLabel("left", text=left_label)
    if signal_viewer_title:
        signal_viewer.view.setTitle(signal_viewer_title)
    if signal_plot:
        signal_viewer.signal = signal_plot

    return widget, signal_viewer


class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1500, 900)

        self.mouse_pad = RealTimeGraph()
        self.verticalLayout_2.addWidget(self.mouse_pad.view)
        # self.unfiltered_signal_view.addWidget(self.mouse_pad.plotWidget)

        # Objects : signal
        
        self.unfiltered_signal_plot = sv.PlotSignal()
        self.filtered_signal_plot = sv.PlotSignal()

        self.all_pass_radioButton.clicked.connect(self.toggle_side_bar)

        self.response_graphics_views = [
            self.magnitude_response_view,
            self.phase_response_view,
            self.all_pass_phase_response
        ]

        self.response_graphics_view = [
                ["phase_response_plot_widget", "Frequency (Hz)", "Phase (degrees)", "Phase Response"],
                ["magnitude_response_plot_widget", "Frequency (Hz)", "Magnitude (degrees)", "Magnitude Response"],
                ["all_pass_phase_response_plot_widget", "Frequency (Hz)", "Phase (degrees)", "All Pass Phase Response"]
        ]
        self.unit_circle_graphics_views = [
            self.unite_circle,
            self.all_pass_unite_circle
        ]

        self.filtered_plot_widget, self.filtered_signal_viewer = create_plot_widget(
            self.filtered_signal_view, "filtered_plot_widget", "Time (sec)",
            "Amplitude","Filtered Signal", self.filtered_signal_plot
        )
        self.unfiltered_plot_widget, self.unfiltered_signal_viewer = create_plot_widget(
            self.unfiltered_signal_view, "unfiltered_plot_widget", "Time (sec)",
            "Amplitude","UnFiltered Signal", self.filtered_signal_plot
        )
        self.z_plane_signal_filter  = None

#####################################################################################################################
        for i in range(len(self.response_graphics_views)):
            # for the first two graphics views which include response
            self.plot_widget = pg.PlotWidget(self.response_graphics_views[i])
            self.graphics_view_layout = QHBoxLayout()
            self.graphics_view_layout.addWidget(self.plot_widget)
            self.response_graphics_views[i].setLayout(self.graphics_view_layout)

            # Assuming 'response_graphics_view' is a valid variable in your code
            self.plot_widget.setObjectName(self.response_graphics_view[i][0])
            self.plot_widget.setBackground((25, 35, 45))
            self.plot_widget.setLabel("bottom", text=self.response_graphics_view[i][1])
            self.plot_widget.setLabel("left", text=self.response_graphics_view[i][2])
            self.plot_widget.showGrid(x=True, y=True)
            self.plot_widget.setTitle(self.response_graphics_view[i][3])


#####################################################################################################################
        # for i in range(len(self.unit_circle_graphics_views)):
            # Create the plot widget
        self.plot_widget = pg.PlotWidget(self.unit_circle_graphics_views[0])
        self.plot_widget.setAspectLocked()
        self.plot_widget.showGrid(x=False, y=False)
        # Draw the unit circle as a CircleROI
        self.unit_circle = pg.CircleROI([-1, -1], size=[2, 2], movable=False, pen=(0, 0, 255))
        self.plot_widget.addItem(self.unit_circle)
        self.plot_widget.setBackground((25, 35, 45))
        # Draw x-axis and y-axis at the center of the circle
        self.x_axis = pg.InfiniteLine(pos=0, angle=0, pen=(255, 0, 0), movable=False)
        self.y_axis = pg.InfiniteLine(pos=0, angle=90, pen=(0, 255, 0), movable=False)
        self.plot_widget.addItem(self.x_axis)
        self.plot_widget.addItem(self.y_axis)
        self.plot_widget.clear()
        self.z_plane_signal_filter = ZPlaneSignalFilter(self.plot_widget)
        self.graphics_view_layout1 = QHBoxLayout(self.unit_circle_graphics_views[0])
        self.graphics_view_layout1.addWidget(self.plot_widget)
        self.unit_circle_graphics_views[0].setLayout(self.graphics_view_layout1)
        
#####################################################################################################################

    def toggle_side_bar(self):
        if self.all_pass_radioButton.isChecked():
            # for slide activate_slider and disable the other buttons
            new_width = 500
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.right_frame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.right_frame.update()



def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()