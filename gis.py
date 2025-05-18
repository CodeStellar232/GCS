from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QStackedWidget, QLabel
from PyQt5.QtCore import QMetaObject, Qt, QSize
from PyQt5.QtGui import QIcon
import serial.tools.list_ports
import threading
import resource_rc
from dashboard import Ui_GCA as DashboardPage
from console import ConsolePage as ConsolePage
from graphs import GraphsPage as TelemetryDashboard
from trajectory import InfoPanel as InfoPanel
from manager import SerialManager as SerialManager
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Navigation Example")
        self.resize(799, 600)
        
        # Initialize SerialManager
        self.serial_manager = SerialManager()  # Create an instance of SerialManager
        self.arduino_connected = False
        self.setupUi()

    def setupUi(self):
        # Central widget and layout
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.main_layout = QHBoxLayout(self.centralwidget)

        # Left navigation buttons
        self.nav_widget = QWidget(self.centralwidget)
        self.nav_widget.setMaximumSize(QSize(50, 16777215))
        self.nav_layout = QVBoxLayout(self.nav_widget)

        # Navigation buttons with icons
        self.db_btn = self.create_nav_button(":/icons/layout.png")
        self.nav_layout.addWidget(self.db_btn)

        self.console_btn = self.create_nav_button(":/icons/command-line.png")
        self.nav_layout.addWidget(self.console_btn)

        self.graph_btn = self.create_nav_button(":/icons/graph.png")
        self.nav_layout.addWidget(self.graph_btn)

        self.map_btn = self.create_nav_button(":/icons/placeholder.png")
        self.nav_layout.addWidget(self.map_btn)

        self.tjct_btn = self.create_nav_button(":/icons/heading.png")
        self.nav_layout.addWidget(self.tjct_btn)

        self.abt_btn = self.create_nav_button(":/icons/id-card.png")
        self.nav_layout.addWidget(self.abt_btn)

        self.main_layout.addWidget(self.nav_widget)

        # Stacked widget for pages
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.main_layout.addWidget(self.stackedWidget)

        # Initialize the pages
        self.init_pages()

        # Connect navigation buttons to corresponding pages
        self.db_btn.clicked.connect(lambda: self.navigate_to(0))
        self.console_btn.clicked.connect(lambda: self.navigate_to(1))
        self.graph_btn.clicked.connect(lambda: self.navigate_to(2))
        self.map_btn.clicked.connect(lambda: self.navigate_to(3))
        self.tjct_btn.clicked.connect(lambda: self.navigate_to(4))
        self.abt_btn.clicked.connect(lambda: self.navigate_to(5))

    def init_pages(self):
        # Dashboard Page
        self.dashboard_page = QWidget()
        self.dashboard_ui = DashboardPage()
        self.dashboard_ui.setupUi(self.dashboard_page)
        self.stackedWidget.addWidget(self.dashboard_page)

        # Console Page
        self.console_ui = ConsolePage()  # Directly use ConsoleUI
        self.stackedWidget.addWidget(self.console_ui)

        # Graph Page
        self.graph_page = TelemetryDashboard()
        self.stackedWidget.addWidget(self.graph_page)

        # Map Page (Placeholder for now)
        self.map_page = QWidget()
        self.map_ui = QLabel("Map Page Placeholder", self.map_page)
        self.map_ui.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(self.map_page)

        # Placeholder Pages
        self.create_placeholder_page("TRAJECTORY PAGE")
        self.create_placeholder_page("ABOUT PAGE")

        # Detect Arduino AFTER all UI elements are ready
        self.detect_arduino()

        # Start Serial Reading Thread if Arduino is connected
        if self.arduino_connected:
            self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.serial_thread.start()

    def create_nav_button(self, icon_path):
        button = QPushButton()
        button.setMinimumSize(QSize(35, 35))
        button.setMaximumSize(QSize(35, 35))
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(30, 30))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        return button

    def create_placeholder_page(self, text):
        placeholder_page = QWidget()
        label = QLabel(placeholder_page)
        label.setText(text)
        label.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(placeholder_page)

    def navigate_to(self, index):
        print(f"Navigating to page index: {index}")
        self.stackedWidget.setCurrentIndex(index)

    def detect_arduino(self):
        """Detect Arduino and update the console output."""
        self.serial_manager.detect_serial_port()  # Use SerialManager to detect Arduino
        if self.serial_manager.serial_port:
            self.arduino_connected = True
            print(f"Arduino detected on port: {self.serial_manager.serial_port.portstr}")
            if hasattr(self.console_ui, 'console_output') and self.console_ui.console_output is not None:
                self.console_ui.console_output.append(f"Arduino detected on port: {self.serial_manager.serial_port.portstr}\n")
        else:
            self.arduino_connected = False
            print("No Arduino detected.")
            if hasattr(self.console_ui, 'console_output') and self.console_ui.console_output is not None:
                self.console_ui.console_output.append("No Arduino detected.")

    def read_serial_data(self):
        """Read serial data from Arduino and update the console output."""
        while self.arduino_connected:
           # data = self.serial_manager.get_latest_data()
            data = self.serial_manager.get_latest_data()
            print(f"Received data: {data}")  # Debugging output
            if data:
                print(f"Received data: {data}")
                QMetaObject.invokeMethod(
                    self.console_ui.console_output,
                    "append",
                    Qt.QueuedConnection,
                    Qt.Q_ARG(str, data)
                )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
