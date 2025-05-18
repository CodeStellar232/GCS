import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QComboBox, QVBoxLayout, QWidget, QStackedWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import QMetaObject, Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from dashboard import Ui_GCA as DashboardPage
from console import ConsolePage as ConsolePage
from graphs import GraphsPage as GraphsPage
from trajectory import InfoPanel as InfoPanel

import serial.tools.list_ports
import threading
import serial
import resource_rc

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navigation Example")
        self.resize(799, 600)
        self.setupUi()

    def setupUi(self):
        # Central widget and layout
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.main_layout = QHBoxLayout(self.centralwidget)

        # Stacked widget for pages
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.main_layout.addWidget(self.stackedWidget)

        # Initialize the pages
        self.init_pages()

    def init_pages(self):
        # Dashboard Page
        self.dashboard_widget = QWidget()
        self.dashboard_ui = DashboardPage()
        self.dashboard_ui.setupUi(self.dashboard_widget)
        self.stackedWidget.addWidget(self.dashboard_widget)

        # Console Page
        self.console_ui = ConsolePage()
        self.console_ui.setup_ui()  # Only if setup_ui exists and takes no arguments
        self.stackedWidget.addWidget(self.console_ui)

        # Graph Page
        self.graph_ui = GraphsPage()  # Instantiate directly
        self.stackedWidget.addWidget(self.graph_ui)

        # Trajectory/Info Panel Page (optional)
        self.trajectory_widget = QWidget()
        serial_manager = None  # Placeholder for serial_manager instance
        self.trajectory_ui = InfoPanel(serial_manager)
        
        if hasattr(self.trajectory_ui, "setupUi"):
            self.trajectory_ui.setupUi(self.trajectory_widget)
        self.stackedWidget.addWidget(self.trajectory_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())