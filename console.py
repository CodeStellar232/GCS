from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLineEdit, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGroupBox, QGridLayout, QComboBox
)
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
import sys
import serial
import serial.tools.list_ports



class ConsoleUI(QWidget):
    def __init__(self):  # Corrected method name
        super().__init__()
        self.setWindowTitle("GCS Console")

        main_layout = QGridLayout()
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setPlaceholderText("Console Output...")
        main_layout.addWidget(QLabel("Console Output"), 0, 0)
        main_layout.addWidget(self.console_output, 1, 0, 2, 1)

        command_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter Command")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_command)
        self.command_input.returnPressed.connect(self.send_command)
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        main_layout.addLayout(command_layout, 3, 0)

        self.command_history_list = QListWidget()
        main_layout.addWidget(QLabel("Command History"), 0, 1)
        main_layout.addWidget(self.command_history_list, 1, 1)


        packet_group = QGroupBox("Packet Info")
        packet_layout = QVBoxLayout()

        self.packet_info_widget = QWidget()
        self.packet_info_layout = QVBoxLayout(self.packet_info_widget)

        self.packet_scroll_area = QScrollArea()
        self.packet_scroll_area.setWidgetResizable(True)
        self.packet_scroll_area.setWidget(self.packet_info_widget)

        packet_layout.addWidget(self.packet_scroll_area)

        self.packet_info_display = QTextEdit()
        self.packet_info_display.setReadOnly(True)
        self.packet_info_display.setPlaceholderText("Packet Info Summary...")
        packet_layout.addWidget(self.packet_info_display)

        packet_group.setLayout(packet_layout)
        main_layout.addWidget(packet_group, 2, 1, 2, 1)

        serial_layout = QHBoxLayout()
        self.port_selector = QComboBox()
        self.refresh_ports()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        serial_layout.addWidget(QLabel("Serial Port:"))
        serial_layout.addWidget(self.port_selector)
        serial_layout.addWidget(self.connect_button)
        main_layout.addLayout(serial_layout, 4, 0, 1, 2)

        self.setLayout(main_layout)

        self.command_history = []

        # Packet Tracking Variables
        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        self.serial_port = None
        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.read_serial_data)

    def refresh_ports(self):
        self.port_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_selector.addItem(port.device)

    def connect_serial(self):
        port = self.port_selector.currentText()
        if port:
            try:
                self.serial_port = serial.Serial(port, 9600, timeout=0.1)
                self.serial_timer.start(200)
                self.console_output.append(f"[INFO] Connected to {port} at 9600 baud.")
            except Exception as e:
                self.console_output.append(f"[ERROR] Could not open serial port: {str(e)}")

    def read_serial_data(self):
        if self.serial_port and self.serial_port.in_waiting:
            try:
                raw_line = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                if raw_line:
                    self.console_output.append(raw_line)
                    self.console_output.moveCursor(QTextCursor.End)

                    packet_id = self.extract_packet_id(raw_line)
                    is_corrupt = "FAIL" in raw_line
                    self.add_packet_info(raw_line)
                    self.update_packet_info(packet_id, is_corrupt=is_corrupt)
            except Exception as e:
                self.console_output.append(f"[ERROR] Failed to read serial: {str(e)}")

    def send_command(self):
        try:
            command = self.command_input.text().strip()
            if command:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] SENT: {command}"
                self.console_output.append(log_entry)
                self.console_output.moveCursor(QTextCursor.End)

                self.command_history.append(command)
                self.command_history_list.addItem(command)
                self.command_input.clear()

                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.write((command + '\n').encode())

                packet_id = self.extract_packet_id(command)
                self.add_packet_info(log_entry)
                self.update_packet_info(packet_id)
        except Exception as e:
            self.console_output.append(f"[ERROR] {str(e)}")

    def extract_packet_id(self, text: str):
        try:
            parts = text.strip().split()
            for part in parts:
                if part.isdigit():
                    return int(part)
            return self.last_packet_id + 1
        except:
            return self.last_packet_id + 1

    def add_packet_info(self, message):
        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet("background-color: #e8f0ff; padding: 4px; border: 1px solid #ccc;")
        self.packet_info_layout.addWidget(label)

        max_labels = 100
        if self.packet_info_layout.count() > max_labels:
            widget_to_remove = self.packet_info_layout.takeAt(0).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()

    def update_packet_info(self, packet_id, is_corrupt=False):
        self.total_packets += 1

        if self.last_packet_id != -1 and (packet_id - self.last_packet_id) > 1:
            self.missing_packets += (packet_id - self.last_packet_id - 1)
        elif self.last_packet_id == -1:
            self.missing_packets = 0

        self.last_packet_id = packet_id
        self.last_packet_time = datetime.now().strftime("%H:%M:%S")

        if is_corrupt:
            self.corrupt_packets += 1

        total_expected = self.total_packets + self.missing_packets
        packet_loss = (self.missing_packets / total_expected) * 100 if total_expected > 0 else 0

        self.packet_info_display.setPlainText(f"""
Total Packets Received : {self.total_packets}
Missing Packets        : {self.missing_packets}
Packet Loss Percentage : {packet_loss:.2f}%
Corrupt Packets        : {self.corrupt_packets}
Last Packet ID         : {self.last_packet_id}
Last Packet Time       : {self.last_packet_time}
        """.strip())

    def clear_packet_info(self):
        self.total_packets = 0
        self.missing_packets = 0
        self.corrupt_packets = 0
        self.last_packet_id = -1
        self.last_packet_time = "N/A"
        self.packet_info_display.clear()

        while self.packet_info_layout.count():
            widget_to_remove = self.packet_info_layout.takeAt(0).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()


class ConsolePageUI:
    def setupUi(self, parent_widget):
        parent_widget.setObjectName("ConsolePage")
        layout = QVBoxLayout(parent_widget)
        label = QLabel("Console Page Content Here")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsoleUI()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())

