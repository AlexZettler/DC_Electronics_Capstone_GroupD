from PyQt5.QtWidgets import QSizePolicy, QPushButton, QAction, QTabWidget, QTabBar, QLineEdit, QLabel, QDockWidget, QApplication, QWidget, QFrame, QScrollArea, QVBoxLayout,QHBoxLayout

from visualization.MPLWidget import MPLWidget
from visualization.settings import colors
from visualization.visualization_data_gather import get_rand_data



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

        self.graph_area = GraphScrollWidget(self)
        self.h_layout.addWidget(self.graph_area)

        self.graph_config_layout = GraphSetupWidget(self, self.graph_area.scroll_content)
        self.h_layout.addWidget(self.graph_config_layout)

        self.setLayout(self.h_layout)


class GraphSetupWidget(QFrame):
    frame_width=3

    def __init__(self, parent, glw):
        super().__init__(parent)
        self.b_layout = QVBoxLayout()
        self.graph_list_widget = glw

        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)

        # Add new Graph button
        self.btn_add_graph = QPushButton("Add another graph!")
        self.btn_add_graph.clicked.connect(lambda: self.graph_list_widget.add_graph(MPLWidget()),)
        self.b_layout.addWidget(self.btn_add_graph)

        # Add new Graph button
        self.regather_data = QPushButton("Regather Data!")
        self.regather_data.clicked.connect(lambda: self.graph_list_widget.regather_graph_data())
        self.b_layout.addWidget(self.regather_data)

        #Apply layout
        self.setLayout(self.b_layout)


class GraphScrollWidget(QScrollArea):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)

        self.scroll_content = GraphListWidget(self)
        scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(scroll_layout)

        self.setWidget(self.scroll_content)

    def add_graph(self, graph):
        self.scroll_area_layout.add_graph(graph)
        #self.scroll_area.setWidget(self.graph_list_widget)

    @property
    def graphs(self):
        return self.graph_list_widget.graphs


class GraphListWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.graphs = []
        self.box = QVBoxLayout()
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
            data = get_rand_data()
            graph.multi_plot(data)

    def plot_graph_index_0(self):
        self.graphs[0].plot([i for i in range(10)])


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

