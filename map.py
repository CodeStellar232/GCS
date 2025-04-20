import sys, random, time, datetime
import numpy as np
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from threading import *

class Ui_MainWindow:
    def setupUi(self, parent_widget):
        parent_widget.setObjectName("MapPage")
        parent_widget.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent_widget)
        self.centralwidget.setObjectName("centralwidget")
        layout = QtWidgets.QVBoxLayout(self.centralwidget)
        label = QtWidgets.QLabel("Map Page Content Here")
        layout.addWidget(label)
        parent_widget.setLayout(layout)

    
class Ui_GCA(object):
    def update_data(self, data):
        # Update the page with Arduino data
        print(f"Updating page with data: {data}")



gps_list = []
gps_n_list = []  # Nested list for GPS values
temp_list = []
delay = 1  # Delay for data generation

class dataGeneration:
    def tempSensor(self):
        """
        Generates random temperature data.
        This method runs indefinitely in a separate thread,
        generating random temperature values between 5 and 50
        every second.
        """
        global temp, temp_array
        while True:
            QApplication.processEvents()
            temp = random.randint(5, 50)
            temp_list.append(temp)
            temp_array = np.array(temp_list)
            time.sleep(delay)

    def input_gps(self):
        """
        Generates random GPS coordinates.
        This method runs indefinitely in a separate thread,
        generating random longitude and latitude values within
        predefined ranges every second. It also formats the
        data into a nested list for plotting purposes.
        """
        global gps_n_list, Current_DateTime, lat, long
        while True:
            QApplication.processEvents()
            long = random.randint(7585707193, 7585898276) / 100000000
            lat = random.randint(3086340228, 3086405821) / 100000000
            gps_list.extend([long, lat])
            gps_n_list.append(gps_list[-2:])
            dt = datetime.datetime.now()
            Current_DateTime = dt.strftime('%d-%b-%Y & %H:%M:%S')
            time.sleep(delay)
            
def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_2.setTitle(_translate("MainWindow", "MAP"))
        self.groupBox_8.setTitle(_translate("MainWindow", "TIME "))
        self.toolButton.setText(_translate("MainWindow", "DISCONNECTED"))
        self.groupBox_17.setTitle(_translate("MainWindow", "BATTERY"))
        self.toolButton_3.setText(_translate("MainWindow", "DISCONNECTED"))
        self.groupBox_18.setTitle(_translate("MainWindow", "BATTERY"))
        self.toolButton_4.setText(_translate("MainWindow", "DISCONNECTED"))
        self.groupBox_19.setTitle(_translate("MainWindow", "TIME "))
        self.toolButton_5.setText(_translate("MainWindow", "DISCONNECTED"))
        self.groupBox_20.setTitle(_translate("MainWindow", "SIGNAL"))
        self.toolButton_6.setText(_translate("MainWindow", "DISCONNECTED"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("MainWindow", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("MainWindow", "Page 2"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("MainWindow", "Page 3"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("MainWindow", "Page"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_5), _translate("MainWindow", "Page"))
        self.label_4.setText(_translate("MainWindow", "WELCOME"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_6), _translate("MainWindow", "Page"))
if __name__ == "_main_":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

        