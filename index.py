import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from ZPlane import ZPlaneSignalFilter
import pyqtgraph as pg
import numpy as np
import sys
from pathlib import Path
from res_rc import *  # Import the resource module
import pandas as pd
from PyQt5.uic import loadUiType
import urllib.request
import os
import login_window 
from os import path
import SignalViewer as sv
from all_pass_filter import AllPassFilter, AllPassFilterFeature, OnlineFilter
from conf import api
from workspace_dialog import WorkspaceDialog

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
        # The super() function in Python can take parameters to provide explicit context about which class's method is b
        # eing called. In the context of multiple inheritance or when dealing with complex inheritance chains, 
        # this helps ensure that the correct class's method is called.
        super(MainApp, self).__init__(parent)
        # QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1500, 900)

        self.Timer = QTimer(self)
        self.Timer.timeout.connect(self.draw_signal)

        self.plotted_signal = []
        self.curr_sample_index = 0
        self.curr_sample = 0
        self.z_plane_signal_filter  = None
        self.filters = []
        double_validator = QDoubleValidator(0.0, 1.0, 10)  # Arguments: bottom, top, decimals
        self.all_pass_real_lineEdit.setValidator(double_validator)
        self.all_pass_imag_lineEdit.setValidator(double_validator)

        self.all_pass_real_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.6]
        self.all_pass_imag_list = [0.1+0.5j, 0.2+0.2j, 0.3+0.7j, 0.4+1.3j, 0.5+1.5j, 0.6+0.4j, 0.7+0.5j, 0.8+0.9j,
                                   0.9+1.1j, 0.3+1.7j, 0.5+1.3j]

        for i in range(len(self.all_pass_real_list)):

            list_item1 = QListWidgetItem(f"a = {self.all_pass_real_list[i]}")
            list_item2 = QListWidgetItem(f"a = {self.all_pass_imag_list[i]}")
            list_item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            list_item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            list_item1.setCheckState(Qt.Unchecked)
            list_item2.setCheckState(Qt.Unchecked)
            self.all_pass_real_listWidget.addItem(list_item1)
            self.all_pass_imag_listWidget.addItem(list_item2)


        # Objects : signal

        self.unfiltered_signal_plot = sv.PlotSignal()
        self.filtered_signal_plot = sv.PlotSignal()

        self.unit_circle_graphics_views = [
            self.unit_circle,
            self.all_pass_unit_circle
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
            self.all_pass_phase_response, "all_pass_phase_response_plot_widget", "Frequency (rad/sec)", "Phase (degrees)",
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
        self.view.setStyleSheet("background-color: #19232D ;border: 2px solid #176B87; border-radius: 10px;")
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
        self.t_x = 1
        self.start_time=0
        # Accumulated signal
        self.accumulated_signal = []
        self.view.mouseMoveEvent = self.mouseMoveEvent
        self.view.mousePressEvent = self.mousePressEvent

#############################################For Connecting Function###################################################
        self.all_pass_radioButton.clicked.connect(self.toggle_side_bar)
        self.clear_btn.clicked.connect(self.clear_graph)
        self.workspace_btn.clicked.connect(self.manage_workspaces)
        self.show_all_pass_filter_btn.clicked.connect(self.show_all_pass_filter)
        self.all_pass_radioButton.clicked.connect(self.toggle_side_bar)
        self.clear_zeros_btn.clicked.connect(self.z_plane_signal_filter.clear_zeros)
        self.clear_poles_btn.clicked.connect(self.z_plane_signal_filter.clear_poles)
        self.clear_all_btn.clicked.connect(self.z_plane_signal_filter.clear_zeros_and_poles)
        self.clear_all_pass_filter_btn.clicked.connect(self.clear_all_pass_graph)
        self.all_pass_real_listWidget.itemClicked.connect(self.handleItemClicked)
        self.all_pass_imag_listWidget.itemClicked.connect(self.handleItemClicked)
        self.import_btn.clicked.connect(self.open_signal)
        self.apply_all_pass_filter_btn.clicked.connect(self.apply_all_pass_filter)
        self.online_filter = OnlineFilter(self.accumulated_signal, self.z_plane_signal_filter)
        self.online_filter2 = OnlineFilter([], self.z_plane_signal_filter)


    def open_signal(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Signal to Equalizer', '', '*.csv', options=options)
        data = pd.read_csv(file_name).to_numpy().transpose()[1].tolist()
        self.online_filter2.signal = data
        self.online_filter2.all_pass_filters = self.filters
        self.clear_graph()
        self.Timer.start(50)  # Set the interval (milliseconds)

    def draw_signal(self):

        if self.curr_sample_index < len(self.online_filter2.signal)-1:
            self.filtered_plot_widget.clear()
            self.unfiltered_plot_widget.clear()
            self.curr_sample_index += 1
            self.curr_sample = self.online_filter2.signal[self.curr_sample_index]
            self.plotted_signal.append(self.curr_sample)
            plot = pg.PlotDataItem(self.plotted_signal)
            self.unfiltered_plot_widget.addItem(plot)
            self.online_filter2.apply_filter()
            plot = pg.PlotDataItem(self.online_filter2.filtered_signal)
            self.filtered_plot_widget.addItem(plot)

    def show_all_pass_filter(self):
        checked_items = []
        for i in range(len(self.all_pass_real_list)):
            item1 = self.all_pass_real_listWidget.item(i)
            item2 = self.all_pass_imag_listWidget.item(i)
            if item1.checkState() == Qt.Checked:
                checked_items.append(self.all_pass_real_list[i])
            if item2.checkState() == Qt.Checked:
                checked_items.append(self.all_pass_imag_list[i])
        if self.all_pass_real_lineEdit.text() != "" and float(self.all_pass_real_lineEdit.text()) > 0:
            if self.all_pass_imag_lineEdit.text() != "":
                checked_items.append(float(self.all_pass_real_lineEdit.text()) +
                                     float(self.all_pass_imag_lineEdit.text()) * 1j)
            else:
                checked_items.append(float(self.all_pass_real_lineEdit.text()))

        # print(checked_items)
        if checked_items:
            self.filters = [AllPassFilter(a) for a in checked_items]
            self.feature = AllPassFilterFeature(filters=self.filters, phase_w=self.all_pass_phase_plot_widget,
                                                poles_zeros_w=self.all_pass_unit_circle_widget)
            self.feature.get_scene()
    def apply_all_pass_filter(self):
        self.online_filter.all_pass_filters = self.filters
        self.phase_plot_widget.clear()
        self.phase_plot_widget.addItem(self.feature.get_corrected_phase_plot(self.z_plane_signal_filter))

    def handleItemClicked(self, item):
        # Toggle the check state when an item is clicked
        current_state = item.checkState()
        item.setCheckState(Qt.Checked if current_state == Qt.Unchecked else Qt.Unchecked)
    def mousePressEvent(self, e):
        self.start_time = time.time()

    def mouseMoveEvent(self, event):
        # Update mouse coordinates
        pos = event.pos()
        self.prevMouseX = self.mouseX
        self.prevMouseY = self.mouseY
        self.mouseX = pos.x()
        self.mouseY = pos.y()
        self.t_x = time.time()
        self.mouse_moving = True

    def updateGraph(self):
        if self.mouse_moving:
            # Calculate the change in mouse coordinates
            delta_x = self.mouseX - self.prevMouseX
            # delta_y = self.mouseY - self.prevMouseY

            # Calculate the distance moved
            # distance = np.sqrt(delta_x ** 2 + delta_y ** 2)

            # Calculate the amplitude of the signal based on the distance and direction
            amplitude = 10  # Adjust the scaling factor as needed

            # Determine the direction of movement
            direction = np.sign(delta_x)  # Use the x-direction for simplicity

            delta_t = time.time() - self.t_x
            v = delta_x / delta_t if delta_t !=0 else 1
            omega = np.abs(v/ amplitude)*0.01

            curr_t = time.time()
            x = lambda t: amplitude* np.cos(omega * t)
            # print(delta_x, delta_t,amplitude,omega,x(curr_t-self.start_time))
            # print(omega)
            # Accumulate the signal based on the movement
            self.accumulated_signal.append(x(curr_t-self.start_time))

            self.online_filter.signal = self.accumulated_signal

            self.online_filter.apply_filter()
            filtered_sig_plot = pg.PlotDataItem(self.online_filter.filtered_signal)
            self.filtered_plot_widget.clear()
            self.filtered_plot_widget.addItem(filtered_sig_plot)
            # Update the plot
            self.curve.setData(y=self.accumulated_signal)
            self.mouse_moving = False
    def toggle_side_bar(self):
        if self.all_pass_radioButton.isChecked():
            # for slide activate_slider and disable the other buttons
            new_width = 450
        else:
            new_width = 0
        self.animation = QPropertyAnimation(self.right_frame, b"minimumWidth")
        self.animation.setDuration(40)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
        self.right_frame.update()
    def clear_graph(self):
        self.plotted_signal = []
        self.curr_sample_index = 0
        self.curr_sample = 0
        self.Timer.stop()
        self.unfiltered_plot_widget.clear()
        self.filtered_plot_widget.clear()

        self.online_filter.reset()
        self.online_filter2.reset()

        self.curve = self.unfiltered_plot_widget.plot(pen='r')
        self.accumulated_signal = []

    def clear_all_pass_graph(self):
        self.all_pass_phase_plot_widget.clear()
        self.all_pass_unit_circle_widget.clear()
    
    def manage_workspaces(self):
        dialog = WorkspaceDialog()
        global api
        if dialog.exec_() == QDialog.Accepted:
            if dialog.action_taken == 'open':
                selected_workspace = dialog.selected_workspace()
                if selected_workspace:
                    self._open_workspace(selected_workspace)
            elif dialog.action_taken == 'save':
                selected_workspace = dialog.selected_workspace_name()
                if selected_workspace:
                    api.delete_workspace_by_name(selected_workspace)
                    created_workspace = api.create_workspace(selected_workspace)
                    if created_workspace:
                        zeros_poles = self.change_zeros_poles_repr()
                        for vect in zeros_poles:
                            api.create_zeros_poles(created_workspace['id'], vect[0], vect[1], vect[2], vect[3])
                        

    def change_zeros_poles_repr(self):
        zeros_poles = []
        zeros = self.z_plane_signal_filter.zeros
        zerosf = self.z_plane_signal_filter.zerosf
        for zero in zeros:
            has_conj = self._has_conjugate(zero, zerosf)
            zeros_poles.append((zero[0], zero[1], has_conj, True))
        poles = self.z_plane_signal_filter.poles
        polesf = self.z_plane_signal_filter.polesf
        for pole in poles:
            has_conj = self._has_conjugate(pole, polesf)
            zeros_poles.append((pole[0], pole[1], has_conj, False))
        return zeros_poles

    def _has_conjugate(self, num, num_list):
        for n in num_list:
            if np.isclose(np.linalg.norm([num[0] - n[0], num[1] + n[1]]), 0):
                return True
        return False

    def _open_workspace(self, workspace):
        self.z_plane_signal_filter.clear_zeros_and_poles()
        for vect in workspace['zeros_poles']:
            if vect['is_zero']:
                self.z_plane_signal_filter.zeros.append((vect['x'], vect['y']))
                self.z_plane_signal_filter.plot_one_zero(vect['x'], vect['y'])
                if vect['has_conj']:
                    self.z_plane_signal_filter.zerosf.append((vect['x'], -vect['y']))
                    self.z_plane_signal_filter.plot_one_zero(vect['x'], -vect['y'], brush='g')
                
            else:
                self.z_plane_signal_filter.poles.append((vect['x'], vect['y']))
                self.z_plane_signal_filter.plot_one_pole(vect['x'], vect['y'])
                if vect['has_conj']:
                    self.z_plane_signal_filter.polesf.append((vect['x'], -vect['y']))
                    self.z_plane_signal_filter.plot_one_pole(vect['x'], -vect['y'], brush='g')
        self.z_plane_signal_filter.plot_frequency_response()
            

        
                    
                
        



def main():
    app = QApplication(sys.argv)
    # window = MainApp()
    # window.show()
    # app.exec_()
    global api
    if api.is_authenticated():
        window = MainApp()
        window.show()
    else:
        app.login_window = login_window.LoginWindow()
        app.login_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()