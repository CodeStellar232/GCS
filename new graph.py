import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QDialog, QWidget, QStackedWidget, QPushButton, QLabel, QHBoxLayout, QComboBox, QGroupBox, QRadioButton
from PyQt5.QtCore import QMetaObject, Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QTextCursor
import serial.tools.list_ports
import serial
import threading


class SerialManager(QDialog):
    def __init__(self):
        super(SerialManager, self).__init__()
        self.setWindowTitle("Serial Manager")
        self.resize(300, 120)

        layout = QVBoxLayout(self)
        self.port_combo = QComboBox()
        self.refresh_ports()
        layout.addWidget(QLabel("Select Serial Port:"))
        layout.addWidget(self.port_combo)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")

    def selected_port(self):
        """Return the selected port."""
        if self.port_combo.count() > 0:
            return self.port_combo.currentText().split(" - ")[0]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Navigation")
        self.resize(799, 600)
        self.arduino_connected = False
        self.arduino_port = None

        self.setupUi()

        # Show SerialManager after a delay of 1 second
        QTimer.singleShot(1000, self.show_serial_manager)

    def setupUi(self):
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.main_layout = QHBoxLayout(self.centralwidget)

        self.nav_widget = QWidget(self.centralwidget)
        self.nav_widget.setMaximumSize(QSize(50, 16777215))
        self.nav_layout = QVBoxLayout(self.nav_widget)

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

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.main_layout.addWidget(self.stackedWidget)

        self.init_pages()

        self.db_btn.clicked.connect(lambda: self.navigate_to(0))
        self.console_btn.clicked.connect(lambda: self.navigate_to(1))
        self.graph_btn.clicked.connect(lambda: self.navigate_to(2))
        self.map_btn.clicked.connect(lambda: self.navigate_to(3))
        self.tjct_btn.clicked.connect(lambda: self.navigate_to(4))
        self.abt_btn.clicked.connect(lambda: self.navigate_to(5))

    def init_pages(self):
        self.dashboard_ui = QLabel("Dashboard Page Placeholder")
        self.stackedWidget.addWidget(self.dashboard_ui)

        self.console_ui = QTextCursor()
        self.stackedWidget.addWidget(QLabel("Console Page Placeholder"))

        self.graph_page = QLabel("Graph Page Placeholder")
        self.stackedWidget.addWidget(self.graph_page)

        self.map_page = QLabel("Map Page Placeholder")
        self.stackedWidget.addWidget(self.map_page)

        self.create_placeholder_page("TRAJECTORY PAGE")
        self.create_about_page()

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
        placeholder_page = QLabel(text)
        placeholder_page.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(placeholder_page)

    def create_about_page(self):
        about_page = QLabel("About Page Placeholder")
        about_page.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(about_page)

    def navigate_to(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def show_serial_manager(self):
        """Show the SerialManager dialog."""
        self.serial_manager = SerialManager()
        self.serial_manager.show()  # Use show() instead of exec_() to make it non-blocking

    def start_serial_thread(self):
        """Start a thread to read serial data."""
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()

    def read_serial_data(self):
        """Read data from the serial port."""
        try:
            print(f"Attempting to open port: {self.arduino_port}")
            with serial.Serial(self.arduino_port, 9600, timeout=1) as ser:
                while self.arduino_connected:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"Received data: {line}")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.arduino_connected = False
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
