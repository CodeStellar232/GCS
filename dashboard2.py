import sys
import threading
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QSizePolicy, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal


class SerialReader(QWidget):  # Change QObject to QWidget
    telemetry_received = pyqtSignal(dict)

    def __init__(self, port=None, baudrate=9600, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.alive = False
        self.thread = None
        self.ser = None

        # Add a layout and label for testing
        layout = QVBoxLayout(self)
        label = QLabel("Serial Reader Page", self)
        layout.addWidget(label)

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.port}: {e}")
            return False
        self.alive = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.alive = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_loop(self):
        """
        Reads lines from serial port.
        Expected each line in CSV format matching telemetry_fields order.
        Example line:
          AST123,2024-06-29 12:00:00,42,1234.5,101325,24.3,12.5,12:00:01,40.7128,-74.0060,10,7,0.01,0.02,0.98,0.1,0.0,-0.05,Nominal
        """
        telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]
        while self.alive:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == len(telemetry_fields):
                        # Map fields to values
                        telemetry_data = dict(zip(telemetry_fields, parts))
                        # Convert numerical fields to float or int as appropriate
                        for key in ["Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
                                    "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
                                    "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z"]:
                            try:
                                if key in telemetry_data:
                                    # Convert satellite count and packet count to int
                                    if key in ["Packet Count", "GNSS Satellites"]:
                                        telemetry_data[key] = int(telemetry_data[key])
                                    else:
                                        telemetry_data[key] = float(telemetry_data[key])
                            except ValueError:
                                pass  # keep original string if conversion fails

                        self.telemetry_received.emit(telemetry_data)
                    else:
                        print(f"Unexpected telemetry format: {line}")
            except Exception as e:
                print(f"Error reading serial data: {e}")


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        # Other initialization code...

    def update_data(self, data):
        """Update the dashboard with the received data."""
        print(f"DashboardPage received data: {data}")
        # Update the dashboard UI with the new data


class TelemetryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 1280, 720)
        self.resize(600, 550)

        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]

        self.serial_reader = None

        self.initUI()
        self.find_and_start_serial()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        label = QLabel("Dashboard", self)
        label.setAlignment(Qt.TopLeft)
        label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(label)

        # Create a grid layout for telemetry fields
        telemetry_group = QWidget(self)
        telemetry_layout = QGridLayout(telemetry_group)

        
        field_positions = [
            ("Team ID", 0, 1), ("Timestamp", 0, 3), ("Packet Count", 0, 5),
            ("Altitude", 1, 1), ("Pressure", 1, 3), ("Temperature", 1, 5),
            ("Voltage", 2, 1), ("GNSS Time", 2, 3), ("GNSS Latitude", 2, 5),
            ("GNSS Longitude", 3, 1), ("GNSS Altitude", 3, 3), ("GNSS Satellites", 3, 5),
            ("Accel X", 4, 1), ("Accel Y", 4, 3), ("Accel Z", 4, 5),
            ("Gyro X", 5, 1), ("Gyro Y", 5, 3), ("Gyro Z", 5, 5),
            ("Flight State", 6, 1)
        ]

        self.labels = {}
        self.values = {}

        for field, row, col in field_positions:
            label = QLabel(f"{field}:", self)
            value = QLabel("-", self)
            telemetry_layout.addWidget(label, row, col)
            telemetry_layout.addWidget(value, row, col + 1)
            self.labels[field] = label
            self.values[field] = value

        layout.addWidget(telemetry_group)

    def find_and_start_serial(self):
        """
        Tries to find a connected Arduino port and start reading.
        """
        ports = serial.tools.list_ports.comports()
        arduino_port = None
        for port in ports:
            if 'Arduino' in port.description or 'USB Serial Device' in port.description:
                arduino_port = port.device
                break

        if not arduino_port:
            QMessageBox.warning(self, "Port Not Found", "No Arduino or USB Serial Device detected.")
            return

        self.serial_reader = SerialReader(arduino_port)
        self.serial_reader.telemetry_received.connect(self.update_telemetry)
        started = self.serial_reader.start()
        if not started:
            QMessageBox.critical(self, "Error", f"Failed to open serial port {arduino_port}")

    def update_telemetry(self, data: dict):
        for field, value in data.items():
            if field in self.telemetry_fields:
                if field in self.values:
                    self.values[field].setText(str(value))

    def closeEvent(self, event):
        if self.serial_reader:
            self.serial_reader.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryWindow()
    window.show()
    sys.exit(app.exec_())

