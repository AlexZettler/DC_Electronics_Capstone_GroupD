from PyQt5.QtWidgets import QMainWindow
import PyQt5.QtCore as QtCore

from visualization.settings import colors
from visualization.widgets import *


class VisApp(QMainWindow):
    """
    Main QT application window
    """
    def __init__(self):
        super().__init__()
        self.title = "Visualization!"

        # Define the initial position of the window
        self.left = 100
        self.top = 100

        # Define the window size
        self.width = 640
        self.height = 480

        # Setup tabs
        self.tab_widget = TabDock(self)

        self.init_ui()

    def init_ui(self):
        """
        Helper method for setting up UI
        """
        self.setWindowTitle(self.title)

        # Setup color
        self.setStyleSheet(f"background-color: {colors['prim']}")

        # Set positions
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage("status bar thing")

        # Setup configure widget
        configure = ConfigureTab(self)
        self.tab_widget.addTab(configure, "Configure")

        # Setup visualize widget
        visualize = VisualizeTab(self)
        self.tab_widget.addTab(visualize, "Visualize")

        # Display the app
        self.show()

    def resizeEvent(self, event):
        """
        Resize override method

        :param event:
        :return:
        """
        # Call parent resize event
        super().resizeEvent(event)

        # Define a content rectangle to handle resize events with
        cr = self.contentsRect()

        # Set the widget to fill the entire window
        self.tab_widget.setGeometry(
            QtCore.QRect(cr.left(), cr.top(), cr.width(), cr.height()))
