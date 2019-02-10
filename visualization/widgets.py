from PyQt5.QtWidgets import QSizePolicy, QPushButton, QAction, QTabWidget, QTabBar, QLineEdit, QLabel, QDockWidget, QApplication, QWidget, QFrame, QScrollArea, QVBoxLayout,QHBoxLayout

from visualization.MPLWidget import MPLWidget
from visualization.settings import colors

import custom_logger as cl

import os
import os.path
import datetime
import random
from collections import deque




class TabDock(QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        #self.setCornerWidget(None, Qt.TopRightCorner)
        self.setTabsClosable(False)
        self.setTabShape(QTabWidget.Rounded)
        #self.setStyleSheet(f"background-color: {colors['light']}")


class ConfigureTab(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        text_box = QLineEdit('Drag this', self)
        text_box.setDragEnabled(True)
        text_box.move(10, 10)
        text_box.resize(100, 60)

        label = CustomLabel("Drop here", self)
        label.move(10, 70)
        label.resize(100, 60)


class VisualizeTab(QWidget):
     #https://www.youtube.com/watch?v=ykUhAp8yTFE

    def __init__(self, parent):
        super().__init__(parent)
        self.h_layout = QHBoxLayout()
        self.graph_area = GraphScrollArea(self)
        self.graph_config_layout = GraphSetupWidget()

        self.h_layout.addWidget(self.graph_area)
        self.h_layout.addWidget(self.graph_config_layout)
        self.setLayout(self.h_layout)

        #GraphScrollArea

        #m.move(0,0)

        #n = GraphWidget(self,400,300,colors)
        #n.resize(640,480)
        #n.move(20,20)

        #gsa = GraphScrollArea(self, colors)
        #gsa.resize(500,500)

        #gsa.add_graph(MPLWidget(self, 400, 300, colors))
        #gsa.add_graph(MPLWidget(self, 400, 300, colors))

        #gsa.add_graph(GraphWidget(self, 400, 300, colors))
        #gsa.add_graph(GraphWidget(self, 400, 300, colors))
        #gsa.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)



    def add_graph(self):
        m = MPLWidget(self)
        #self.
        pass


class GraphSetupWidget(QFrame):
    frame_width=3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.b_layout = QVBoxLayout()

        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)

        # Add new Graph button
        self.btn_add_graph = QPushButton("Add another graph!")
        self.b_layout.addWidget(self.btn_add_graph)

        # Add new Graph button
        self.regather_data = QPushButton("Regather Data!")
        self.b_layout.addWidget(self.regather_data)

        self.setLayout(self.b_layout)

        #Setup button
        #btn_regather_data = QPushButton("Reload data!", self)
        #btn_regather_data.setToolTip("Lets reload some data!")

        #btn_regather_data.clicked.connect(n.graph.plot_temperatures)
        #btn_regather_data.clicked.connect(gsa.graph_list.regather_graph_data)

        #btn_regather_data.setStyleSheet(f"background-color: {colors['light']}")
        #btn_regather_data.move(500,0)
        #btn_regather_data.resize(140,100)


class GraphScrollArea(QWidget):
    #todo: scroll no longer feels like an english word, I should come back to this later
    def __init__(self, parent):
        super().__init__(parent)

        self.scroll_area = QScrollArea(self)

        scroll_box = QVBoxLayout(self)
        scroll_box.addWidget(self.scroll_area)


        self.setLayout(scroll_box)

        self.scroll_area_layout = QVBoxLayout(scroll_box)

        self.scroll_area_layout.addWidget(MPLWidget(self))
        #scroll_box.

        self.graph_list_widget = GraphListWidget(self)

        #self.scroll_area.setVerticalScrollBar()

        #self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.resize(500,500)
        self.scroll_area.setWidget(self.graph_list_widget)

    def add_graph(self, graph):
        self.graph_list_widget.add_graph(graph)
        #self.scroll_area.setWidget(self.graph_list_widget)

    @property
    def graphs(self):
        return self.graph_list_widget.graphs


class GraphListWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.graphs = []

        self.box = QVBoxLayout()
        #self.setLayout(self.box)

        #btn_lol = QPushButton("LOL", self)
        #sample_graph = MPLWidget(self)

        #self.box.addWidget(btn_lol)
        #self.box.addWidget(sample_graph)

        self.setLayout(self.box)

    def add_graph(self, graph):
        if isinstance(graph, MPLWidget):
            self.graphs.append(graph)
            self.box.addWidget(graph)
            self.setLayout(self.box)

            print(len(self.graphs))
        else:
            raise TypeError

    def regather_graph_data(self):
        for graph in self.graphs:
            graph.plot_temperatures()




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

