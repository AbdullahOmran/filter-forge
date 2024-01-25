import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
import numpy as np
import pyqtgraph as pg


class RealTimeGraph(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Real-Time Signal Input')

        # Create QGraphicsView and QGraphicsScene for the padding area
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Set up the QGraphicsView
        self.view.setSceneRect(0, 0, 200, 200)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create the pyqtgraph plot
        self.plotWidget = pg.PlotWidget(self)

        # Create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(self.plotWidget)

        # Initialize pyqtgraph plot
        self.curve = self.plotWidget.plot(pen='r')

        # Set up QTimer for real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGraph)
        self.timer.start(50)  # Set the interval (milliseconds)

        # Initialize mouse position and previous position
        self.mouseX = 0
        self.mouseY = 0
        self.prevMouseX = 0
        self.prevMouseY = 0

        # Flag to track mouse movement
        self.mouse_moving = False

        # Accumulated signal
        self.accumulated_signal = []

        # Connect mouse move event
        self.view.mouseMoveEvent = self.mouseMoveEvent

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
            amplitude = distance /10  # Adjust the scaling factor as needed

            # Determine the direction of movement
            direction = np.sign(delta_x)  # Use the x-direction for simplicity

            # Accumulate the signal based on the movement
            self.accumulated_signal.extend(amplitude * np.sin(
                0.02 * np.arange(len(self.accumulated_signal), len(self.accumulated_signal) + 100)) * direction)

            # Update the plot
            self.curve.setData(y=self.accumulated_signal)
            self.mouse_moving = False
        else:
            # If mouse is not moving, clear the plot
            self.curve.clear()


