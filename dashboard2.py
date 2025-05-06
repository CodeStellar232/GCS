import sys
import threading
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QComboBox, QPushButton, QFileDialog, QCheckBox, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from status_header import StatusHeaderWidget  

class TelemetryHandler(QObject):
    telemetry_received = pyqtSignal(dict)

class DashboardPage(QWidget):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 1280, 720)

        # Serial & Logging Vars
        self.serial_port = None
        self.logging_enabled = False
        self.log_file_path = ""

        # Telemetry Fields
        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]
        self.labels = {f: QLabel(f"{f}:") for f in self.telemetry_fields}
        self.values = {f: QLabel("-") for f in self.telemetry_fields}

        # Setup UI
        self.setupUI()
        self.start_port_refresh()

        # Timer for updating UI every second
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_telemetry_ui_periodically)
        self.update_timer.start(1000)  # Update every second

        # Initialize telemetry storage
        self.latest_telemetry = {}

        # Create a handler to signal updates to the main thread
        self.telemetry_handler = TelemetryHandler()
        self.telemetry_handler.telemetry_received.connect(self.update_telemetry_ui)

    def setupUI(self):
        main_layout = QHBoxLayout(self)
        telemetry_group = QGroupBox("Dashboard")
        telemetry_layout = QGridLayout()

        for i, key in enumerate(self.telemetry_fields):
            row, col = i // 3, i % 3
            telemetry_layout.addWidget(self.labels[key], row, col * 2)
            telemetry_layout.addWidget(self.values[key], row, col * 2 + 1)

        telemetry_group.setLayout(telemetry_layout)

        # Right layout for serial/log controls
        right_layout = QVBoxLayout()

        # Serial group
        self.combobox_ports = QComboBox()
        self.baud_rate_selector = QComboBox()
        self.baud_rate_selector.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_rate_selector.setCurrentIndex(4)  # Default to 115200

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_serial_connection)

        serial_group = QGroupBox("Serial Port Settings")
        serial_layout = QVBoxLayout()
        serial_layout.addWidget(QLabel("Port:"))
        serial_layout.addWidget(self.combobox_ports)
        serial_layout.addWidget(QLabel("Baud Rate:"))
        serial_layout.addWidget(self.baud_rate_selector)
        serial_layout.addWidget(self.connect_button)
        serial_group.setLayout(serial_layout)

        # Logging group
        self.checkbox_logging = QCheckBox("Enable Logging")
        self.checkbox_logging.stateChanged.connect(self.toggle_logging)

        self.save_button = QPushButton("Log File")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.select_log_file)

        logging_group = QGroupBox("Data Logging Settings")
        logging_layout = QVBoxLayout()
        logging_layout.addWidget(self.checkbox_logging)
        logging_layout.addWidget(self.save_button)
        logging_group.setLayout(logging_layout)

        # Clear Button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_telemetry)

        # Status Button
        self.status_button = QPushButton("Status Window")
        self.status_button.clicked.connect(self.toggle_status_window)

        # Add to right layout
        right_layout.addWidget(serial_group)
        right_layout.addWidget(logging_group)
        right_layout.addWidget(self.clear_button)
        right_layout.addWidget(self.status_button)

        main_layout.addWidget(telemetry_group, 3)
        main_layout.addLayout(right_layout, 1)

    def toggle_status_window(self):
        if hasattr(self, 'status_window') and self.status_window.isVisible():
            self.status_window.close()
        self.status_window = StatusHeaderWidget()
        self.status_window.show()

    def start_port_refresh(self):
        self.refresh_ports()
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(3000)

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        current = self.combobox_ports.currentText()
        self.combobox_ports.clear()
        self.combobox_ports.addItems(ports)
        if current in ports:
            self.combobox_ports.setCurrentText(current)

    def toggle_serial_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.connect_button.setText("Connect")
        else:
            try:
                port = self.combobox_ports.currentText()
                baud = int(self.baud_rate_selector.currentText())
                self.serial_port = serial.Serial(port, baud, timeout=1)
                threading.Thread(target=self.read_serial_data, daemon=True).start()
                self.connect_button.setText("Disconnect")
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))

    def read_serial_data(self):
        try:
            while self.serial_port and self.serial_port.is_open:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.handle_telemetry_line(line)
        except Exception as e:
            print(f"Serial error: {e}")
            self.serial_port = None
            self.connect_button.setText("Connect")

    def handle_telemetry_line(self, line):
        print(f"Raw telemetry packet: {line}")  # Debugging line

        parts = line.split(',')
        if len(parts) != len(self.telemetry_fields):
            print(f"Invalid telemetry packet (expected {len(self.telemetry_fields)} fields, got {len(parts)})")
            return  # Skip this packet or handle it accordingly

        data = dict(zip(self.telemetry_fields, parts))
        self.latest_telemetry = data  # Store the latest telemetry data
        self.telemetry_handler.telemetry_received.emit(data)  # Emit the signal to update the UI

        # If logging enabled, save the telemetry line to the file
        if self.logging_enabled and self.log_file_path:
            threading.Thread(target=self.save_log, args=(line,), daemon=True).start()

    def update_telemetry_ui(self, data):
        # Update UI labels with new data
        for key, value in data.items():
            self.values[key].setText(value)

    def update_telemetry_ui_periodically(self):
        # This function will be called every second to update the telemetry UI.
        if self.latest_telemetry:
            self.update_telemetry_ui(self.latest_telemetry)

    def toggle_logging(self, state):
        self.logging_enabled = state == Qt.Checked
        self.save_button.setEnabled(self.logging_enabled)
        if self.logging_enabled and not self.log_file_path:
            self.select_log_file()

    def select_log_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log File", "", "CSV Files (.csv);;Text Files (.txt)")
        if file_path:
            self.log_file_path = file_path
            QMessageBox.information(self, "Log File Selected", f"Telemetry will be saved to:\n{file_path}")
        else:
            self.logging_enabled = False
            self.checkbox_logging.setChecked(False)

    def save_log(self, line):
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(line + '\n')
        except Exception as e:
            print(f"Logging error: {e}")

    def clear_telemetry(self):
        for label in self.values.values():
            label.setText("-")