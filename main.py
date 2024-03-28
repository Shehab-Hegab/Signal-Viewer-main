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



        # Initial Declerations on Openeing The App
        self.signal_widget1 = None
        self.signal_widget2 = None
        self.position_flag = 1
        self.timer1 = QTimer(self)
        self.timer2 = QTimer(self)

        # Two Browse Buttons
        self.BrowseButton.clicked.connect(lambda: self.open_dialog_box(self.Channel1Graphic, self.BrowseButton, self.timer1, self.RepeatCheck))
        self.BrowseButton2.clicked.connect(lambda: self.open_dialog_box(self.Channel2Graphic, self.BrowseButton2, self.timer2, self.RepeatCheck2))

        # Two Hide/Show Buttons
        self.HideButton.clicked.connect(lambda: self.hideButton_handler(self.signal_widget1))
        self.HideButton2.clicked.connect(lambda: self.hideButton_handler(self.signal_widget2))

        # Two Close Buttons
        self.CloseButton.clicked.connect(lambda: self.close_handler(self.Channel1Graphic, self.timer1))
        self.CloseButton2.clicked.connect(lambda: self.close_handler(self.Channel2Graphic, self.timer2))

        # Two Screenshot Buttons
        self.Screenshot.clicked.connect(lambda: self.screenshot_handler(self.signal_widget1))
        self.Screenshot2.clicked.connect(lambda: self.screenshot_handler(self.signal_widget2))

        # Two Play/Pause Buttons
        self.PlayPauseButton.clicked.connect(lambda: self.play_pause_handler(self.signal_widget1, self.PlayPauseButton, self.timer1))
        self.PlayPauseButton2.clicked.connect(lambda: self.play_pause_handler(self.signal_widget2, self.PlayPauseButton2, self.timer2))

        # Link Button - SPECIAL
        self.linked = False
        self.LinkButton.clicked.connect(self.link_controls)

        # Export PDF Button
        self.ExportPDF.triggered.connect(self.export_screenshots_to_pdf)

        # Color Buttons - Signal (1)
        self.Channel1Red.clicked.connect(lambda: self.change_color(self.signal_widget1, 'r'))
        self.Channel1Blue.clicked.connect(lambda: self.change_color(self.signal_widget1, 'b'))
        self.Channel1Green.clicked.connect(lambda: self.change_color(self.signal_widget1, 'g'))

        # Color Buttons - Signal (2)
        self.Channel2Red.clicked.connect(lambda: self.change_color(self.signal_widget2, 'r'))
        self.Channel2Blue.clicked.connect(lambda: self.change_color(self.signal_widget2, 'b'))
        self.Channel2Green.clicked.connect(lambda: self.change_color(self.signal_widget2, 'g'))
        
        # Signal Directions
        self.MoveSignalDownButton.clicked.connect(self.move_signal_down_handler)
        self.MoveSignalUpButton.clicked.connect(self.move_signal_up_handler)

        self.SwitchButton.clicked.connect(self.switch_handler)

        # Signal View Slider
        self.connect_slider()
        self.playing1 = False
        self.playing2 = False


    # [1] Adjust Speed Option
    # -----------------------
    def adjust_speed(self, timer, value):
        if timer:
            max_value = self.SpeedSlider.maximum()
            interval = max_value - value + 1
            timer.setInterval(interval)


    # [2] Change Color Options
    # ------------------------
    def change_color(self, signal_widget, color):
        if signal_widget:
            signal_widget.curve.setPen(color)


    # [3] Upload The Signal in Graphic View
    # -------------------------------------
    def open_dialog_box(self, graphic_channel,button, timer, repeat_checkbox):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", "DAT Files (*.dat);;CSV Files (*.csv)", options=options
        )

        if path:
            if button == self.BrowseButton:
                self.signal_widget1 = Signal(path, self.StatisticsField, self.StatisticsField2, self.position_flag)
                container_widget = QWidget()
                self.signal_widget1.pos_flag = 1

                layout = QVBoxLayout()
                layout.addWidget(self.signal_widget1.get_plot_widget())
                container_widget.setLayout(layout)

                if graphic_channel.layout():
                    while graphic_channel.layout().count():
                        item = graphic_channel.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.deleteLater()

                else:
                    graphic_channel.setLayout(layout)

                graphic_channel.setSceneRect(0, 0, container_widget.width(), container_widget.height())
                graphic_channel.setScene(QGraphicsScene())
                graphic_channel.layout().addWidget(container_widget)
                repeat_checkbox.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget1, state))
                if path.endswith('.dat'):
                    record = wfdb.rdrecord(path[:-4])
                    if record.sig_name:
                        self.ChannelsComboBox.clear()
                        self.ChannelsComboBox.addItems(record.sig_name)
                        self.ChannelsComboBox.setCurrentIndex(0)

                        def on_channel_change(index):
                            selected_channel_index = int(index)
                            if selected_channel_index >= 0:
                                if graphic_channel == self.Channel1Graphic and self.signal_widget1:
                                    self.signal_widget1.load_signal(path, selected_channel_index)

                        self.ChannelsComboBox.currentIndexChanged.connect(on_channel_change)

            if button == self.BrowseButton2:
                self.signal_widget2 = Signal(path, self.StatisticsField, self.StatisticsField2, self.position_flag)
                container_widget = QWidget()
                self.signal_widget2.pos_flag = 2

                layout = QVBoxLayout()
                layout.addWidget(self.signal_widget2.get_plot_widget())
                container_widget.setLayout(layout)

                if graphic_channel.layout():
                    while graphic_channel.layout().count():
                        item = graphic_channel.layout().takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.deleteLater()

                else:
                    graphic_channel.setLayout(layout)

                graphic_channel.setSceneRect(0, 0, container_widget.width(), container_widget.height())
                graphic_channel.setScene(QGraphicsScene())
                graphic_channel.layout().addWidget(container_widget)
                repeat_checkbox.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget2, state))

            elif path.endswith('.csv'):
                df = pd.read_csv(path)
                self.ChannelsComboBox.clear()
                self.ChannelsComboBox.addItems(df.columns[1:])
                self.ChannelsComboBox.setCurrentIndex(0)
                if self.signal_widget == self.signal_widget1:
                    repeat_checkbox.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget1, state))
                elif self.signal_widget == self.signal_widget2:
                    repeat_checkbox.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget2, state))
                
    
    # [4] Function to Repeat The Signal
    # ---------------------------------
    def set_repeat_enabled(self, signal_widget, state):
        signal_widget.repeat_enabled = state == Qt.Checked



    # [5] Hide Button Handling Function
    # ---------------------------------
    def hideButton_handler(self, signal_widget):
        if signal_widget:
            if signal_widget.get_plot_widget().isVisible():
                signal_widget.get_plot_widget().setVisible(False)
                self.HideButton.setText("Show")
            else:
                signal_widget.get_plot_widget().setVisible(True)
                self.HideButton.setText("Hide")



    # [6] Close Button Handling Function
    # ----------------------------------
    def close_handler(self, graphic_channel, timer):
        if graphic_channel.layout():
            old_widget = graphic_channel.layout().takeAt(0).widget()
            if old_widget:
                if timer.isActive():
                    timer.stop()
                    timer.timeout.disconnect()
                old_widget.setParent(None)
                old_widget.deleteLater()


    # [7] Screenshot Button Handling Function
    # ---------------------------------------
    def screenshot_handler(self, signal_widget):
        if signal_widget:
            image = signal_widget.get_plot_widget().grab()
            file_path_img = f"./data/images/screenshot_{signal_widget.ptr}_{id(signal_widget)}.png"
            image.save(file_path_img)
            stats_text = self.StatisticsField.toPlainText() if signal_widget == self.signal_widget1 else self.StatisticsField2.toPlainText()
            file_path_txt = f"./data/txt/screenshot_{signal_widget.ptr}_{id(signal_widget)}.txt"
            with open(file_path_txt, "w") as f:
                f.write(stats_text)
    


    # [8] Move The Signal in The Down Direction
    # -----------------------------------------
    def move_signal_down_handler(self):
        layout1 = self.Channel1Graphic.layout()
        layout2 = self.Channel2Graphic.layout()

        if layout1 and layout1.count() > 0:
            widget = layout1.takeAt(0).widget()
            if layout2:
                self.close_handler(self.Channel2Graphic, self.timer2)
            else:
                self.Channel2Graphic.setLayout(QVBoxLayout())

            container_widget = QWidget()
            layout2 = self.Channel2Graphic.layout()
            layout2.addWidget(widget)

            self.Channel2Graphic.setSceneRect(0, 0, container_widget.width(), container_widget.height())
            self.Channel2Graphic.setScene(QGraphicsScene())
            layout2.addWidget(container_widget)

            self.signal_widget2 = self.signal_widget1
            self.signal_widget2.statistics_field2.setText(self.signal_widget1.statistics_field1.toPlainText())
            self.signal_widget1.statistics_field1.setText("")
            self.signal_widget1 = None
            self.signal_widget2.pos_flag = 2

            self.update_button_connections()

    # [8] Move The Signal in The Up Direction
    # -----------------------------------------
    def move_signal_up_handler(self):
        layout1 = self.Channel1Graphic.layout()
        layout2 = self.Channel2Graphic.layout()

        if layout2 and layout2.count() > 0:
            widget = layout2.takeAt(0).widget()
            if layout1:
                self.close_handler(self.Channel1Graphic, self.timer1)
            else:
                self.Channel1Graphic.setLayout(QVBoxLayout())

            container_widget = QWidget()
            layout1 = self.Channel1Graphic.layout()
            layout1.addWidget(widget)

            self.Channel1Graphic.setSceneRect(0, 0, container_widget.width(), container_widget.height())
            self.Channel1Graphic.setScene(QGraphicsScene())
            layout1.addWidget(container_widget)

            self.signal_widget1 = self.signal_widget2
            self.signal_widget1.statistics_field1.setText(self.signal_widget2.statistics_field2.toPlainText())
            self.signal_widget2.statistics_field2.setText("")
            self.signal_widget2 = None
            self.signal_widget1.pos_flag = 1

            self.update_button_connections()

    # [8] Switch Function to Swap Plots Between Channel1Graphic and Channel2Graphic
    # ----------------------------------------------------------------------------
    def switch_handler(self):
        layout1 = self.Channel1Graphic.layout()
        layout2 = self.Channel2Graphic.layout()

        if layout1 and layout1.count() > 0 and layout2 and layout2.count() > 0:
            widget1 = layout1.takeAt(0).widget()
            widget2 = layout2.takeAt(0).widget()

            container_widget1 = QWidget()
            container_widget2 = QWidget()

            layout1 = self.Channel1Graphic.layout()
            layout2 = self.Channel2Graphic.layout()

            layout1.addWidget(widget2)
            layout2.addWidget(widget1)

            layout1.addWidget(container_widget2)
            layout2.addWidget(container_widget1)

            temp_signal_widget = self.signal_widget1
            self.signal_widget1 = self.signal_widget2
            self.signal_widget2 = temp_signal_widget

            temp_text = self.signal_widget1.statistics_field1.toPlainText()
            self.signal_widget1.statistics_field1.setText(self.signal_widget2.statistics_field2.toPlainText())
            self.signal_widget2.statistics_field2.setText(temp_text)

            self.signal_widget1.pos_flag = 1
            self.signal_widget2.pos_flag = 2

            self.update_button_connections()



    # [9] Update Some Buttons when moving up or down
    # -----------------------------------------------
    def update_button_connections(self):
        if self.signal_widget1:
            self.PlayPauseButton.clicked.disconnect()
            self.PlayPauseButton.clicked.connect(lambda: self.play_pause_handler(self.signal_widget1, self.PlayPauseButton, self.timer1))
            self.SpeedSlider.valueChanged.disconnect()
            self.SpeedSlider.valueChanged.connect(lambda value: self.adjust_speed(self.timer1, value))
        if self.signal_widget2:
            self.PlayPauseButton2.clicked.disconnect()
            self.PlayPauseButton2.clicked.connect(lambda: self.play_pause_handler(self.signal_widget2, self.PlayPauseButton2, self.timer2))
            self.SpeedSlider2.valueChanged.disconnect()
            self.SpeedSlider2.valueChanged.connect(lambda value: self.adjust_speed(self.timer2, value))



    # [10] Play/Pause Button Handling Function
    # ----------------------------------------
    def play_pause_handler(self, signal_widget, button, timer):
        if signal_widget:
            if not signal_widget.playing:
                button.setText("Pause")
                signal_widget.start_playback(timer)
                if self.linked:
                    self.playing1 = True
                    if button == self.PlayPauseButton:
                        self.PlayPauseButton2.setText("Pause")
                        if self.signal_widget2:
                            self.signal_widget2.start_playback(self.timer2)
                    elif button == self.PlayPauseButton2:
                        self.PlayPauseButton.setText("Pause")
                        if self.signal_widget1:
                            self.signal_widget1.start_playback(self.timer1)
            else:
                button.setText("Play")
                signal_widget.pause_playback(timer)
                if self.linked:
                    self.playing1 = False
                    if button == self.PlayPauseButton:
                        self.PlayPauseButton2.setText("Play")
                        if self.signal_widget2:
                            self.signal_widget2.pause_playback(self.timer2)
                    elif button == self.PlayPauseButton2:
                        self.PlayPauseButton.setText("Play")
                        if self.signal_widget1:
                            self.signal_widget1.pause_playback(self.timer1)


    # [11] Slider Connection Handling Function
    # ----------------------------------------
    def connect_slider(self):
        self.SpeedSlider.valueChanged.connect(lambda value: self.adjust_speed(self.timer1, value))
        self.SpeedSlider2.valueChanged.connect(lambda value: self.adjust_speed(self.timer2, value))


    # [12] Link Control Function
    # --------------------------
    def link_controls(self):
        self.linked = not self.linked
        if self.linked:
            self.LinkButton.setText("Unlink")
            self.SpeedSlider.valueChanged.connect(lambda value: self.SpeedSlider2.setValue(value))
            self.SpeedSlider2.valueChanged.connect(lambda value: self.SpeedSlider.setValue(value))
            self.RepeatCheck.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget1, state))
            self.RepeatCheck2.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget2, state))
            self.RepeatCheck.stateChanged.connect(lambda state: self.RepeatCheck2.setChecked(state))
            self.RepeatCheck2.stateChanged.connect(lambda state: self.RepeatCheck.setChecked(state))
        else:
            self.LinkButton.setText("Link")
            self.SpeedSlider.valueChanged.disconnect()
            self.SpeedSlider2.valueChanged.disconnect()
            self.RepeatCheck.stateChanged.disconnect()
            self.RepeatCheck2.stateChanged.disconnect()
            self.connect_slider()
            self.RepeatCheck.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget1, state))
            self.RepeatCheck2.stateChanged.connect(lambda state: self.set_repeat_enabled(self.signal_widget2, state))
    


    # [13] Export as PDF Function
    # ---------------------------
    def export_screenshots_to_pdf(self):
        screenshots_directory = "./data/images"
        txt_directory = "./data/txt"

        screenshots = [screenshot for screenshot in os.listdir(screenshots_directory) if
                    screenshot.startswith("screenshot_") and screenshot.endswith(".png")]

        if not screenshots:
            return

        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        pdf_filename = os.path.join('./data/reports', f"screenshots_{date}.pdf")

        c = canvas.Canvas(pdf_filename, pagesize=landscape(letter))

        x_offset = 50
        y_offset = landscape(letter)[1] - 100

        image_width = (landscape(letter)[0] - 150) / 2
        image_height = landscape(letter)[1] - 250

        for idx, screenshot in enumerate(screenshots):
            img = ImageReader(os.path.join(screenshots_directory, screenshot))
            text_path = os.path.join(txt_directory, screenshot.replace(".png", ".txt"))

            c.drawImage(img, x_offset, y_offset - image_height, width=image_width * 2, height=image_height,
                    preserveAspectRatio=True)
            with open(text_path, 'r') as f:
                stats = f.read()

            text_width = c.stringWidth(stats, "Helvetica", 12)
            text_height = 12

            c.drawCentredString(landscape(letter)[0] / 2, y_offset, stats)

            c.showPage()
            y_offset = landscape(letter)[1] - 100

            if os.path.exists(os.path.join(screenshots_directory, screenshot)):
                os.remove(os.path.join(screenshots_directory, screenshot))
            if os.path.exists(text_path):
                os.remove(text_path)

        c.save()



# SIGNAL CLASS
# ------------

class Signal:
    def __init__(self, path, statistics_field1, statistics_field2, pos_flag):
        self.ptr = 0
        self.playing = False
        self.deleted = False
        self.repeat_enabled = False
        self.curve_deleted = False
        self.pos_flag = pos_flag
        self.statistics_field1 = statistics_field1
        self.statistics_field2 = statistics_field2
        try:
            fs = ', Sampling Rate = ' + str(wfdb.rdrecord(path[:-4], channels=[0]).fs)
        except:
            self.record_header = ''
        try:
            header = list(wfdb.rdheader(path[:-4]).comments)
            self.record_header = header[0] + ', ' + header[1] + ', ' + header[2] + fs
        except:
            self.record_header = ''
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=True, y=True)

        self.plot_item = self.plot_widget.getPlotItem()
        self.curve = self.plot_item.plot(pen='w')
        self.plot_item.setTitle(self.record_header)

        self.ecg_signal = []
        self.time = []
        self.fixed_x_range = 5
        self.initial_x_max = self.fixed_x_range
        self.load_signal(path, 0)

    def load_signal(self, path, selected_channel_index):
        if path.endswith('.dat'):
            record = wfdb.rdrecord(path[:-4], channels=[0])
            sampling_rate = record.fs
            self.ecg_signal = record.p_signal.flatten()
            self.duration = len(self.ecg_signal) / self.sampling_rate
            self.time = np.linspace(0, self.duration, len(self.ecg_signal))
        elif path.endswith('.csv'):
            data = pd.read_csv(path)
            self.ecg_signal = np.array(pd.to_numeric(data.iloc[:, selected_channel_index + 1].values, downcast="float"))
            self.time = np.array(pd.to_numeric(data.iloc[:, 0].values, downcast="float"))

        if self.plot_data_items:
            for item in self.plot_data_items:
                self.plot_item.removeItem(item)
            self.plot_data_items.clear()
            self.legend.clear()

        plot_data_item = self.plot_item.plot(pen=(255, 255, 255))
        self.plots.append(self.ecg_signal)
        self.plot_data_items.append(plot_data_item)

        self.legend.addItem(plot_data_item, f'Signal {selected_channel_index}')

    def calculate_statistics(self, data):
        mean = np.mean(data)
        variance = np.var(data)
        peak = np.max(data)
        trough = np.min(data)
        return mean, variance, peak, trough

    def update(self, timer):
        if self.deleted or not self.playing or self.ptr >= len(self.time):
            return
        x_max = self.time[self.ptr]
        x_min = max(0, x_max - self.fixed_x_range)
        signal_slice = self.ecg_signal[:self.ptr + 1]
        mean, variance, peak, trough = self.calculate_statistics(signal_slice)
        if self.pos_flag == 1:
            self.statistics_field1.setText(f"Mean: {mean:.2f}\nVariance: {variance:.2f}\nPeak: {peak:.2f}\nTrough: {trough:.2f}")
        if self.pos_flag == 2:
            self.statistics_field2.setText(f"Mean: {mean:.2f}\nVariance: {variance:.2f}\nPeak: {peak:.2f}\nTrough: {trough:.2f}")
        if not self.curve_deleted and self.curve is not None:
            self.curve.setData(self.time[:self.ptr + 1], signal_slice)
            if self.plot_item is not None:
                self.plot_item.setXRange(x_min, x_min + self.fixed_x_range, padding=0)
        if self.ptr >= len(self.time) and self.repeat_enabled:
            self.ptr = 0
        y_min, y_max = np.min(self.ecg_signal), np.max(self.ecg_signal)
        y_padding = 0.5
        self.plot_widget.setLimits(xMin=0, xMax=max(self.fixed_x_range, self.time[self.ptr] + 0.5), yMin=y_min - y_padding, yMax=y_max + y_padding)
        self.ptr += 1

    def start_playback(self, timer):
        if not self.playing:
            self.playing = True
            timer.timeout.connect(lambda: self.update(timer))
            timer.start(10)

    def pause_playback(self, timer):
        if self.playing:
            self.playing = False
            timer.stop()

    def get_plot_widget(self):
        return self.plot_widget



# MAIN PROGRAM
# ------------
def main():
    app = QApplication([])
    window = SignalViewer()
    app.aboutToQuit.connect(window.export_screenshots_to_pdf)
    app.exec_()

if __name__ == "__main__":
    main()
