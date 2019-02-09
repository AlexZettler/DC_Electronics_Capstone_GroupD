
from PyQt5.QtWidgets import QSizePolicy, QPushButton, QTabWidget, QTabBar, QLineEdit, QLabel, QDockWidget, QApplication, QWidget, QScrollArea

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import custom_logger as cl

import os
import os.path
import datetime
import random
from collections import deque


class TabDock(QTabWidget):
    def __init__(self, parent, colors):
        super().__init__(parent)
        #self.setCornerWidget(None, Qt.TopRightCorner)
        self.setTabsClosable(False)
        self.setTabShape(QTabWidget.Rounded)
        #self.setStyleSheet(f"background-color: {colors['light']}")


class ConfigureDock(QDockWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)

        text_box = QLineEdit('Drag this', self)
        text_box.setDragEnabled(True)
        text_box.move(0, 400)
        text_box.resize(140, 100)

        label = CustomLabel("Drop here", self)
        label.move(0, 500)
        label.resize(140, 100)


class VisualizeTab(QDockWidget):

    def __init__(self, parent, colors):
        super().__init__(parent)
        self.plot_list = PlotList(self, (500,400), colors=colors)

        #m = PlotCanvas(self, width=5, height=4, dpi=100, colors=colors)

        self.plot_list.add_plot()


        # Setup button
        btn_regather_data = QPushButton("Reload data!", self)
        # button.setToolTip("I'm a button!")
        btn_regather_data.clicked.connect(self.plot_list.managed_plots[0].plot_canvas.plot_temperatures)
        btn_regather_data.setStyleSheet(f"background-color: {colors['light']}")
        btn_regather_data.move(500,0)
        btn_regather_data.resize(140,100)


class PlotList(QScrollArea):
    def __init__(self, parent, size, colors):
        super().__init__(parent)
        self.colors = colors
        self.width,self.height = size
        self.managed_plots = []
        self.arrange_plots()

    def add_plot(self):
        self.index_to_add = len(self.managed_plots)
        p = PlotWidget(
            parent=self,
            size=(self.width, self.height),
            colors=self.colors
        )
        p.move(0, self.height*self.index_to_add)
        self.managed_plots.append(p)

    def arrange_plots(self):
        y_total = 0.0
        for i,p in zip(range(len(self.managed_plots)),self.managed_plots):
            p.move(0,y_total)
            y_total += self.height


class PlotWidget(QWidget):
    def __init__(self, parent, size, colors):
        super().__init__(parent)
        self.dpi = 100
        self.plot_canvas = PlotCanvas(self, width=size[0]/self.dpi, height=size[0]/self.dpi, dpi=self.dpi, colors=colors)

    @property
    def axes(self):
        return self.plot_canvas.axes

    @property
    def figure(self):
        return self.plot_canvas.figure


class PlotCanvas(FigureCanvasQTAgg):

    color_options = {
        "C0",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
    }

    def __init__(self, parent, width, height, dpi, colors):
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=colors["prim"])
        self.axes = self.figure.add_subplot(111, facecolor=colors["prim"])
        self.axes.set_title("LOL a title")

        FigureCanvasQTAgg.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(
            self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.updateGeometry()

        print(self.get_device_types())


    def plot(self, data, color):
        #ax = self.figure.add_subplot(111)
        self.axes.plot(data, color=color)

        self.draw()


    def plot_temperatures(self):
        self.axes.clear()
        data = self.get_rand_data()

        #Custom color cycling
        color_deque = deque(self.color_options)

        self.axes.set_title(f"Data({datetime.datetime.now().strftime('%H:%M:%S')})")
        for d in data:
            self.plot(d, color_deque[0])
            color_deque.rotate(1)

        #print(self.get_devices_from_log_directory("../log"))

    def get_rand_data(self):
        return [[random.random() for i in range(25)]for i in range(5)]


    def get_device_types(self):
        return cl.log_directories.keys()

    def get_device_files_of_type(self, device_type):
        return cl.iget_device_files_from_log_directory(device_type)


        #return {os.path.dirname(i):os.path.abspath(i) for i in glob.iglob(base_path, recursive=False)}


        #for name, path in cl.log_directories.items():
        #    pass

class CustomLabel(QLabel):

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        print("drag enter")
        if e.mimeData().hasFormat('text/plain'):

            e.accept()

        else:
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().text())
