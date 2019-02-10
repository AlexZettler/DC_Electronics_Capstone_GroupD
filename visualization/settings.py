from PyQt5.QtGui import QColor

main_color = "#6e7f59"
colors = {
    "prim": main_color,
    "light": QColor(main_color).lighter(125).name(),
    "dark": QColor(main_color).darker(125).name()
}