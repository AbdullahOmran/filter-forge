from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from main import ZPlaneSignalFilter
import pyqtgraph as pg
import numpy as np
import sys
from pathlib import Path
from res_rc import *  # Import the resource module

from PyQt5.uic import loadUiType
import urllib.request

import os
from os import path
import SignalViewer as sv
from all_pass_filter import AllPassFilter, AllPassFilterFeature

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
        self.z_plane_signal_filter  = None

        self.all_pass_list = [15, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for i in range(len(self.all_pass_list)):

            list_item = QListWidgetItem(f"a = {self.all_pass_list[i]}")
            list_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            list_item.setCheckState(Qt.Unchecked)
            self.all_pass_list_widget.addItem(list_item)


        # Objects : signal

        self.unfiltered_signal_plot = sv.PlotSignal()
        self.filtered_signal_plot = sv.PlotSignal()

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
            "Amplitude","UnFiltered Signal", self.unfiltered_signal_plot
        )
        # self.unfiltered_signal_viewer.linkTo(self.filtered_signal_viewer)

        self.all_pass_phase_plot_widget, _ = create_plot_widget(
            self.all_pass_phase_response, "all_pass_phase_response_plot_widget", "Frequency (Hz)", "Phase (degrees)",
            "All Pass Phase Response"
        )
        self.magnitude_plot_widget, _ = create_plot_widget(
            self.magnitude_response_view, "magnitude_response_plot_widget", "Frequency (Hz)", "Magnitude (degrees)",
            "Magnitude Response"
        )
        self.phase_plot_widget, _ = create_plot_widget(
            self.phase_response_view, "phase_response_plot_widget", "Frequency (Hz)", "Phase (degrees)",
            "Phase Response"
        )

#####################################################################################################################
        for i in range(len(self.unit_circle_graphics_views)):
            # Create the plot widget
            self.plot_widget = pg.PlotWidget(self.unit_circle_graphics_views[i], enableMenu=False)
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

            if i == 0:
                self.plot_widget.clear()
                self.z_plane_signal_filter = ZPlaneSignalFilter(self.plot_widget, self.magnitude_plot_widget,
                                                                self.phase_plot_widget, self.add_conjugates)
            else:
                self.all_pass_unit_circle_widget = self.plot_widget
            self.graphics_view_layout1 = QHBoxLayout(self.unit_circle_graphics_views[i])
            self.graphics_view_layout1.addWidget(self.plot_widget)
            self.unit_circle_graphics_views[i].setLayout(self.graphics_view_layout1)

############################################## For Mouse Pad ###########################################################
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setStyleSheet("background-color: lightGray;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.verticalLayout_2.addWidget(self.view)
        self.curve = self.unfiltered_plot_widget.plot(pen = "r")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGraph)
        self.timer.start(50)  # Set the interval (milliseconds)
        self.mouse_moving = False
        # Initialize mouse position and previous position
        self.mouseX = 0
        self.mouseY = 0
        self.prevMouseX = 0
        self.prevMouseY = 0

        # Accumulated signal
        self.accumulated_signal = []
        self.view.mouseMoveEvent = self.mouseMoveEvent

#############################################For Connecting Function###################################################
        self.all_pass_radioButton.clicked.connect(self.toggle_side_bar)
        self.clear_btn.clicked.connect(self.clear_graph)
        self.all_pass_list_widget.itemClicked.connect(self.handleItemClicked)
        self.show_all_pass_filter_btn.clicked.connect(self.show_all_pass_filter)
        self.all_pass_radioButton.clicked.connect(self.toggle_side_bar)
        self.clear_zeros_btn.clicked.connect(self.z_plane_signal_filter.clear_zeros)
        self.clear_poles_btn.clicked.connect(self.z_plane_signal_filter.clear_poles)
        self.clear_all_btn.clicked.connect(self.z_plane_signal_filter.clear_zeros_and_poles)
        self.import_btn.clicked.connect(self.open_signal)

    def open_signal(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '',
                                                       '*.csv', options=options)

        self.clear_graph()
        self.unfiltered_signal_viewer.load_dataset(file_name)
        self.unfiltered_signal_viewer.add_signal()
        self.play_pause_state = False
        self.play_pause_btn.setIcon(QIcon(f'icons/pause copy.svg'))


    def show_all_pass_filter(self):
        checked_items = []
        for i in range(len(self.all_pass_list)):
            item = self.all_pass_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                checked_items.append(self.all_pass_list[i])
        print(checked_items)
        self.filters = [AllPassFilter(a) for a in checked_items]
        self.feature = AllPassFilterFeature(filters=self.filters, phase_w=self.all_pass_phase_plot_widget,
                                            poles_zeros_w=self.all_pass_unit_circle_widget)
        self.feature.get_scene()

    def handleItemClicked(self, item):
        # Toggle the check state when an item is clicked
        current_state = item.checkState()
        item.setCheckState(Qt.Checked if current_state == Qt.Unchecked else Qt.Unchecked)

    def mouseMoveEvent(self, event):
        # Update mouse coordinates
        pos = event.pos()
        self.prevMouseX = self.mouseX
        self.prevMouseY = self.mouseY
        self.mouseX = pos.x()
        self.mouseY = pos.y()
        self.mouse_moving = True

    def updateGraph(self):
        if self.mouse_moving:
            # Calculate the change in mouse coordinates
            delta_x = self.mouseX - self.prevMouseX
            delta_y = self.mouseY - self.prevMouseY

            # Calculate the distance moved
            distance = np.sqrt(delta_x ** 2 + delta_y ** 2)

            # Calculate the amplitude of the signal based on the distance and direction
            amplitude = distance   # Adjust the scaling factor as needed

            # Determine the direction of movement
            direction = np.sign(delta_x)  # Use the x-direction for simplicity

            # Accumulate the signal based on the movement
            self.accumulated_signal.extend(amplitude * np.sin(
                0.02 * np.arange(len(self.accumulated_signal), len(self.accumulated_signal) + 100)) * direction)

            # Update the plot
            self.curve.setData(y=self.accumulated_signal)
            self.mouse_moving = False
    def toggle_side_bar(self):
        if self.all_pass_radioButton.isChecked():
            # for slide activate_slider and disable the other buttons
            new_width = 400
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.right_frame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.right_frame.update()
    def clear_graph(self):
        self.unfiltered_plot_widget.clear()
        self.curve = self.unfiltered_plot_widget.plot(pen='r')
        self.accumulated_signal = []


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()