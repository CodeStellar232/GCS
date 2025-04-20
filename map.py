<<<<<<< HEAD
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

        
=======



from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1135, 665)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(10, 10, 1110, 592))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_2.setGeometry(QtCore.QRect(120, 120, 981, 461))
        self.groupBox_2.setObjectName("groupBox_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setGeometry(QtCore.QRect(0, 20, 981, 441))
        self.textBrowser.setObjectName("textBrowser")
        self.graphicsView = QtWidgets.QGraphicsView(self.groupBox_2)
        self.graphicsView.setGeometry(QtCore.QRect(370, 60, 571, 361))
        self.graphicsView.setObjectName("graphicsView")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(120, 0, 991, 101))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.groupBox_8 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_8.setGeometry(QtCore.QRect(10, 0, 171, 51))
        self.groupBox_8.setObjectName("groupBox_8")
        self.toolButton = QtWidgets.QToolButton(self.groupBox_8)
        self.toolButton.setGeometry(QtCore.QRect(10, 20, 161, 21))
        self.toolButton.setObjectName("toolButton")
        self.groupBox_17 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_17.setGeometry(QtCore.QRect(10, 50, 171, 41))
        self.groupBox_17.setObjectName("groupBox_17")
        self.toolButton_3 = QtWidgets.QToolButton(self.groupBox_17)
        self.toolButton_3.setGeometry(QtCore.QRect(10, 20, 161, 21))
        self.toolButton_3.setObjectName("toolButton_3")
        self.groupBox_18 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_18.setGeometry(QtCore.QRect(820, 0, 171, 51))
        self.groupBox_18.setObjectName("groupBox_18")
        self.toolButton_4 = QtWidgets.QToolButton(self.groupBox_18)
        self.toolButton_4.setGeometry(QtCore.QRect(10, 20, 161, 21))
        self.toolButton_4.setObjectName("toolButton_4")
        self.groupBox_19 = QtWidgets.QGroupBox(self.groupBox_18)
        self.groupBox_19.setGeometry(QtCore.QRect(10, 50, 171, 51))
        self.groupBox_19.setObjectName("groupBox_19")
        self.toolButton_5 = QtWidgets.QToolButton(self.groupBox_19)
        self.toolButton_5.setGeometry(QtCore.QRect(10, 20, 161, 21))
        self.toolButton_5.setObjectName("toolButton_5")
        self.groupBox_20 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_20.setGeometry(QtCore.QRect(820, 50, 171, 51))
        self.groupBox_20.setObjectName("groupBox_20")
        self.toolButton_6 = QtWidgets.QToolButton(self.groupBox_20)
        self.toolButton_6.setGeometry(QtCore.QRect(10, 20, 161, 21))
        self.toolButton_6.setObjectName("toolButton_6")
        self.toolBox = QtWidgets.QToolBox(self.frame)
        self.toolBox.setGeometry(QtCore.QRect(0, 0, 111, 591))
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page.setObjectName("page")
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page_2.setObjectName("page_2")
        self.toolBox.addItem(self.page_2, "")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page_3.setObjectName("page_3")
        self.toolBox.addItem(self.page_3, "")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page_4.setObjectName("page_4")
        self.toolBox.addItem(self.page_4, "")
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page_5.setObjectName("page_5")
        self.toolBox.addItem(self.page_5, "")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setGeometry(QtCore.QRect(0, 0, 111, 405))
        self.page_6.setObjectName("page_6")
        self.label_4 = QtWidgets.QLabel(self.page_6)
        self.label_4.setGeometry(QtCore.QRect(20, 370, 61, 31))
        self.label_4.setObjectName("label_4")
        self.toolBox.addItem(self.page_6, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1135, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.toolBox.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

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
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("MainWindow", "Page"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("MainWindow", "Page"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_5), _translate("MainWindow", "Page"))
        self.label_4.setText(_translate("MainWindow", "WELCOME"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_6), _translate("MainWindow", "Page"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
>>>>>>> dcffa7b7e9bddd0f066d2c1264ccd995432abdf6
