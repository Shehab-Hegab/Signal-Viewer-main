# First: LIBRARIES SECTION
# ------------------------
# uic is a command-line tool provided by PyQt5 (and PyQt6) that allows you to convert Qt Designer .ui files into Python code. 
from PyQt5 import uic
# A Library to plot the graph for each channel
import pyqtgraph as pg
# Import all the widget pf PyQt to be able to use them
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGraphicsScene, \
    QFileDialog, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
# The uic module in PyQt5 is used to dynamically load user interface files created with Qt Designer
from PyQt5 import uic
# WFDB (Waveform Database) is a software package and a standardized format for storing and managing physiological signals
import wfdb
# NumPy is a fundamental Python library for numerical and scientific computing
import numpy as np
# pandas is a popular open-source Python library used for data manipulation and analysis
import pandas as pd
# Classes are typically used to handle date and time. 
import datetime
# This application allows users to navigate through their file system and display the content of a directory in a QListWidget
import os
# ReportLab is a widely-used Python library for programmatically creating PDFs. 
# It provides a robust set of tools for generating reports, creating forms, drawing graphics, and more within a PDF document.
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# MAIN CLASS OF SIGNAL VIEWER - MAIN WINDOW
# -----------------------------------------
class SignalViewer(QMainWindow):
    def __init__(self):
        super(SignalViewer, self).__init__()
        uic.loadUi("./Signal Viewer.ui", self)
        # Change Applicayion Main Window Title
        self.setWindowTitle("Bio-Signal Viewer")
        # Create and set the application icon
        icon = QIcon("./ApplicationFiles/Main_App_Icon.png")  # Replace with your icon file path
        self.setWindowIcon(icon)
        self.show()




# MAIN PROGRAM
# ------------
def main():
    app = QApplication([])
    window = SignalViewer()
    app.exec_()

if __name__ == "__main__":
    main()