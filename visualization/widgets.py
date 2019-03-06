from PyQt5.QtWidgets import QPushButton, QTabWidget, QLineEdit, QLabel, QWidget, QFrame, QScrollArea, QVBoxLayout, \
    QHBoxLayout

from visualization.MPLWidget import MPLWidget
from data_handling.data_retrieval import get_rand_data
import PyQt5.sip as sip

import datetime


class TabDock(QTabWidget):
    """
    The primary widget holding the configure and visualization tabs
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setTabsClosable(False)
        self.setTabShape(QTabWidget.Rounded)

        # Todo: Add tab redraw event to achieve a consistent style

        # self.setStyleSheet(f"background-color: {colors['light']}")


class ConfigureTab(QWidget):
    """
    The main configuration tab used to configure aspects of the system
    """

    # Todo: Look at celery & redis to see if this would be a good application for the tools, if not a database may be the best wat of managing settings

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
    """
    A tab for visualizing data over a period of time
    """

    # https://www.youtube.com/watch?v=ykUhAp8yTFE
    def __init__(self, parent):
        super().__init__(parent)
        self.h_layout = QHBoxLayout()

        # Setup the graph scroll widget in the left hand side of the window
        self.graph_area = GraphScrollWidget(self)
        self.h_layout.addWidget(self.graph_area)

        # Setup the graph configuration widget in the right hand side of the window
        self.graph_config_layout = GraphSetupWidget(self, self.graph_area.scroll_content)
        self.h_layout.addWidget(self.graph_config_layout)

        # Apply layout
        self.setLayout(self.h_layout)


class GraphSetupWidget(QFrame):
    """
    A widget for setting up the graphs
    """
    frame_width = 3

    def __init__(self, parent, glw):
        super().__init__(parent)
        self.b_layout = QVBoxLayout()
        self.graph_list_widget = glw

        # Set QFrame style
        self.setFrameStyle(QFrame.Box + QFrame.Raised)
        self.setLineWidth(self.frame_width)

        # Add new Graph button
        self.btn_add_graph = QPushButton("Add another graph!")
        self.btn_add_graph.clicked.connect(lambda: self.graph_list_widget.add_graph_plot_instance())
        self.b_layout.addWidget(self.btn_add_graph)

        # Add new Graph button
        self.regather_data = QPushButton("Regather Data!")
        self.regather_data.clicked.connect(lambda: self.graph_list_widget.regather_graph_data())
        self.b_layout.addWidget(self.regather_data)

        # Apply layout
        self.setLayout(self.b_layout)


class GraphScrollWidget(QScrollArea):
    """
    A widget to enable scroll functionality
    """

    def __init__(self, parent):
        super().__init__(parent)
        # DOES NOT WORK WITHOUT THIS LINE OF CODE!
        self.setWidgetResizable(True)

        # Define our internal scroll contents
        self.scroll_content = GraphListWidget(self)
        scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(scroll_layout)

        self.setWidget(self.scroll_content)

    @property
    def graphs(self):
        return self.graph_list_widget.graphs


class GraphListWidget(QWidget):
    """
    A widget for managing many different graphs
    """

    def __init__(self, parent):
        super().__init__(parent)
        # An ID to assign to next value given to graph instances
        self._next_id = 0
        # A dictionary of graphs currently being displayed
        self.graphs = dict()

        # Define and set our layout
        self.box = QVBoxLayout()
        self.setLayout(self.box)

    def add_graph_plot_instance(self):
        # Get the next id to be used
        current_id = self.next_id

        # Create an instance of the graph
        graph_with_menu = PlotWithCommands(self, current_id)

        # Retrieves the next graph ID
        self.graphs[current_id] = graph_with_menu

        # Plot some dummy data when graph is added
        graph_with_menu.graph_widget.multi_plot(get_rand_data())

        # Bind the remove button to a function to remove the graph from the managed graphs and erase it from the canvas
        graph_with_menu.btn_remove_plot.clicked.connect(lambda: self.remove_plot(graph_with_menu))

        # Add the widget to the layout and assign the new layout
        self.box.addWidget(graph_with_menu)
        self.setLayout(self.box)

    @property
    def next_id(self):
        """
        Gets the next value of the ID
        """
        _id = self._next_id
        self._next_id += 1
        return _id

    def remove_plot(self, graph_with_menu):
        # Delete the dictionary entery for the graph key
        del self.graphs[graph_with_menu._id]

        # Remove the widget from the layout
        self.box.removeWidget(graph_with_menu)

        # PyQt5 delete statement for managing object cleanup
        sip.delete(graph_with_menu)

        # Just to make sure
        graph_with_menu = None

    def regather_graph_data(self):
        # Iterate through values in the dictionary
        for graph in self.graphs.values():
            # Fill the graphs with dummy data
            data = get_rand_data()

            # Plot all graphs returned in the data variable
            graph.graph_widget.multi_plot(data)


class PlotWithCommands(QWidget):
    """
    A widget that contains a graph with controls located on the right hand panel.
    These options currently only include a remove button
    """

    def __init__(self, parent, _id):
        super().__init__(parent)
        self._id = _id
        self.linked_logs = []

        # Define our layout
        h_layout = QHBoxLayout()

        # Define our left side graph section
        self.graph_widget = MPLWidget()
        h_layout.addWidget(self.graph_widget)

        # Define our right side menu
        button_menu_area = QWidget()
        button_menu_layout = QVBoxLayout()

        # Add a remove plot button. Functionality is not created here.
        # This is because the function would remove this widget and the key in the graph manager would lose the relation
        self.btn_remove_plot = QPushButton("Remove")
        button_menu_layout.addWidget(self.btn_remove_plot)

        # Finalize menu layout
        button_menu_area.setLayout(button_menu_layout)
        h_layout.addWidget(button_menu_area)

        # Apply layout
        self.setLayout(h_layout)

    def graph_log_files(self)->None:
        """
        This method plots a list of log files and data points logged within the last minute
        """

        # Get the start and end times
        time_delta = datetime.timedelta(minutes=1)
        end_time = datetime.datetime.now()
        start_time = end_time - time_delta

        # Plot the time plotted graph
        self.graph_widget.create_time_axis(start_time, end_time)

        # Gather dummy data for now
        data = (range(20))

        # Plot all graphs
        self.graph_widget.multi_plot(data)

    def add_linked_log_files(self):
        pass


class CustomLabel(QLabel):
    """
    A dummy label to test drag and drop functionality with
    """

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
