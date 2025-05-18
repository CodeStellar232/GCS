from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLineEdit, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QGroupBox, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
import serial
import serial.tools.list_ports
import sys

class ConsolePage(QWidget):
    def __init__(self):
        super().__init__()
        # self.serial_manager = serial_manager  # Store the SerialManager instance
        self.serial_port = None
        # Packet info tracking
        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        
        self.headers = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]

        self.value_labels = {}
        self.packet_labels = {}

        self.setup_ui()
        self.auto_find_serial_port()

        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.read_serial_data)
        self.serial_timer.start(200)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        console_group = QGroupBox("Console Dashboard")
        console_layout = QVBoxLayout(console_group)

        command_layout = QHBoxLayout()
        command_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter Command")

        self.send_button = QPushButton("Send")
        self.send_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.send_button.setMinimumWidth(100)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.clear_button.setMinimumWidth(100) 

        self.timestamp_checkbox = QCheckBox("Timestamp")
        self.timestamp_checkbox.setChecked(True)
        self.send_button.setMinimumWidth(100)

        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        command_layout.addWidget(self.clear_button)
        command_layout.addWidget(self.timestamp_checkbox)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add raw telemetry display widget
        self.raw_telemetry_display = QTextEdit()  # Define the raw telemetry display
        self.raw_telemetry_display.setReadOnly(True)
        self.raw_telemetry_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        split_layout = QHBoxLayout()
        split_layout.addWidget(self.console_output, 7)
        split_layout.addWidget(self.raw_telemetry_display, 3)  # Add it to the layout

        right_side_layout = QVBoxLayout()

        self.command_history_list = QListWidget()
        command_history_group = QGroupBox("Command History")
        command_history_layout = QVBoxLayout(command_history_group)
        command_history_layout.addWidget(self.command_history_list)

        packet_info_group = QGroupBox("Packet Info")
        packet_info_layout = QGridLayout()
        packet_info_group.setLayout(packet_info_layout)
        packet_info_group.setFixedHeight(300)

        packet_headers = [
            "Total Packets", "Missing Packets", "Packet Loss %", 
            "Corrupt Packets", "Last Packet ID", "Last Packet Time"
        ]
        for row, name in enumerate(packet_headers):
            packet_info_layout.addWidget(QLabel(f"{name}:"), row, 0)
            label = QLabel("-")
            self.packet_labels[name] = label
            packet_info_layout.addWidget(label, row, 1)

        right_side_layout.addWidget(command_history_group)
        right_side_layout.addWidget(packet_info_group)
        split_layout.addLayout(right_side_layout, 3)

        console_layout.addLayout(command_layout)
        console_layout.addLayout(split_layout)

        main_layout.addWidget(console_group, 3)

        telemetry_group = QGroupBox("Raw Telemetry")
        telemetry_layout = QVBoxLayout(telemetry_group)
        telemetry_values_layout = QGridLayout()
        for i, header in enumerate(self.headers):
            telemetry_values_layout.addWidget(QLabel(f"{header}:"), i, 0)
            value_label = QLabel("-")
            self.value_labels[header] = value_label
            telemetry_values_layout.addWidget(value_label, i, 1)
        telemetry_layout.addLayout(telemetry_values_layout)

        main_layout.addWidget(telemetry_group, 1)

        self.send_button.clicked.connect(self.send_command)
        self.clear_button.clicked.connect(self.clear_console)
        self.command_input.returnPressed.connect(self.send_command)
        self.command_history_list.itemClicked.connect(lambda item: self.command_input.setText(item.text()))

    def auto_find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "USB" in port.description or "COM" in port.device:
                try:
                    self.serial_port = serial.Serial(port.device, 9600, timeout=1)
                    print(f"Connected to {port.device}")
                    return
                except Exception as e:
                    print(f"Failed to connect to {port.device}: {e}")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self.append_console(line)
                    self.raw_telemetry_display.append(line)
                    self.update_telemetry(line)

                    packet_id = self.extract_packet_id(line)
                    is_corrupt = "FAIL" in line
                    self.update_packet_info(packet_id, is_corrupt)
            except Exception as e:
                self.append_console(f"[ERROR]: {e}")

    def append_console(self, text):
        if self.timestamp_checkbox.isChecked():
            timestamp = datetime.now().strftime("%H:%M:%S")
            text = f"[{timestamp}] {text}"
        self.console_output.append(text)
        self.console_output.moveCursor(QTextCursor.End)

    def update_telemetry(self, line):
        parts = line.split(',')
        if len(parts) != len(self.headers):
            return
        for header, value in zip(self.headers, parts):
            self.value_labels[header].setText(value)

    def update_packet_info(self, packet_id, is_corrupt=False):
        self.total_packets += 1

        if self.last_packet_id != -1:
            gap = packet_id - self.last_packet_id
            if gap > 1:
                self.missing_packets += gap - 1
        self.last_packet_id = packet_id
        self.last_packet_time = datetime.now().strftime("%H:%M:%S")

        if is_corrupt:
            self.corrupt_packets += 1

        total_expected = self.total_packets + self.missing_packets
        packet_loss = (self.missing_packets / total_expected) * 100 if total_expected else 0

        self.packet_labels["Total Packets"].setText(str(self.total_packets))
        self.packet_labels["Missing Packets"].setText(str(self.missing_packets))
        self.packet_labels["Packet Loss %"].setText(f"{packet_loss:.2f}")
        self.packet_labels["Corrupt Packets"].setText(str(self.corrupt_packets))
        self.packet_labels["Last Packet ID"].setText(str(packet_id))
        self.packet_labels["Last Packet Time"].setText(self.last_packet_time)

    def extract_packet_id(self, line):
        for part in line.split(','):
            if part.isdigit():
                return int(part)
        return self.last_packet_id + 1

    def send_command(self):
        command = self.command_input.text().strip()
        if command:
            self.append_console(f"SENT: {command}")
            self.command_history_list.addItem(command)
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write((command + '\n').encode())
            self.command_input.clear()

    def clear_console(self):
        self.console_output.clear()
        self.command_history_list.clear()
        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        for label in self.packet_labels.values():
            label.setText("-")
        for label in self.value_labels.values():
            label.setText("-")

    def update_data(self, data):
        """
        Update the console with new data.
        :param data: A string containing the new data.
        """
        self.console_output.append(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsolePage(None)
    window.show()
    sys.exit(app.exec_())
