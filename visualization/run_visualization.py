from PyQt5 import QtWidgets, QtCore
from visualization.visualization_app import VisApp

import sys

app = QtWidgets.QApplication(sys.argv)
#settings = QtCore.QSettings('Alex Zettler', 'Data visualization')


visualization = VisApp()
sys.exit(app.exec_())