from PyQt5.QtWidgets import QApplication, QMainWindow  # and other required widgets
import sys
from PyQt5 import uic


app = QApplication([])

# Create a QMainWindow
window = QMainWindow()

# Change the window title to "Signal View"
window.setWindowTitle("Signal View")

# Create a menu bar
menu_bar = window.menuBar()

# Create a menu
file_menu = menu_bar.addMenu("File")

# Add actions to the menu
action_new = file_menu.addAction("New")
action_open = file_menu.addAction("Open")
action_save = file_menu.addAction("Save")

# Load UI and StyleSheet
uic.loadUi('Signal Viewer.ui', window)
with open('stylesheet.qss', 'r') as file:
    window.setStyleSheet(file.read())

window.show()
sys.exit(app.exec_())
