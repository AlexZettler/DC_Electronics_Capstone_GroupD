from PyQt5 import QtWidgets, QtCore
from visualization.visualization_app import VisApp

import sys

app = QtWidgets.QApplication(sys.argv)
#settings = QtCore.QSettings('Alex Zettler', 'Data visualization')

main_color = "#6e7f59"

visualization = VisApp(color=main_color)
sys.exit(app.exec_())