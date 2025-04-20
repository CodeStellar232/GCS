<<<<<<< HEAD
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


class ConsoleUI:
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
=======

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GCA(object):
    def setupUi(self, GCA):
        GCA.setObjectName("GCA")
        GCA.resize(1131, 613)
        self.gridLayout = QtWidgets.QGridLayout(GCA)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(GCA)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        self.groupBox.setGeometry(QtCore.QRect(120, 120, 781, 441))
        self.groupBox.setObjectName("groupBox")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(10, 20, 101, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox_4 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_4.setGeometry(QtCore.QRect(520, 50, 101, 22))
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.addItem("")
        self.comboBox_5 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_5.setGeometry(QtCore.QRect(430, 50, 81, 22))
        self.comboBox_5.setObjectName("comboBox_5")
        self.comboBox_5.addItem("")
        self.comboBox_5.addItem("")
        self.send_Button = QtWidgets.QPushButton(self.groupBox)
        self.send_Button.setGeometry(QtCore.QRect(540, 20, 81, 21))
        self.send_Button.setObjectName("send_Button")
        self.send_Text = QtWidgets.QLineEdit(self.groupBox)
        self.send_Text.setGeometry(QtCore.QRect(120, 20, 411, 22))
        self.send_Text.setObjectName("send_Text")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setGeometry(QtCore.QRect(10, 50, 101, 20))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_2.setGeometry(QtCore.QRect(120, 50, 101, 20))
        self.checkBox_2.setObjectName("checkBox_2")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox)
        self.scrollArea.setGeometry(QtCore.QRect(10, 80, 611, 341))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 609, 339))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label.setObjectName("label")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_6.setGeometry(QtCore.QRect(630, 20, 141, 191))
        self.groupBox_6.setObjectName("groupBox_6")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_6)
        self.textBrowser.setGeometry(QtCore.QRect(0, 20, 141, 171))
        self.textBrowser.setObjectName("textBrowser")
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_7.setGeometry(QtCore.QRect(630, 220, 141, 201))
        self.groupBox_7.setObjectName("groupBox_7")
        self.textBrowser_3 = QtWidgets.QTextBrowser(self.groupBox_7)
        self.textBrowser_3.setGeometry(QtCore.QRect(0, 20, 141, 181))
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.clear_Button = QtWidgets.QPushButton(self.groupBox)
        self.clear_Button.setGeometry(QtCore.QRect(362, 50, 61, 21))
        self.clear_Button.setObjectName("clear_Button")
        self.groupBox_5 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_5.setGeometry(QtCore.QRect(910, 130, 191, 431))
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.textBrowser_4 = QtWidgets.QTextBrowser(self.groupBox_5)
        self.textBrowser_4.setGeometry(QtCore.QRect(0, 0, 191, 461))
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.label_2 = QtWidgets.QLabel(self.groupBox_5)
        self.label_2.setGeometry(QtCore.QRect(40, 10, 101, 20))
        self.label_2.setObjectName("label_2")
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
        self.page_3.setObjectName("page_3")
        self.toolBox.addItem(self.page_3, "")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.toolBox.addItem(self.page_4, "")
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setObjectName("page_5")
        self.toolBox.addItem(self.page_5, "")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")
        self.label_3 = QtWidgets.QLabel(self.page_6)
        self.label_3.setGeometry(QtCore.QRect(20, 370, 61, 31))
        self.label_3.setObjectName("label_3")
        self.toolBox.addItem(self.page_6, "")
        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)

        self.retranslateUi(GCA)
        self.toolBox.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(GCA)
        GCA.setTabOrder(self.comboBox, self.comboBox_4)
        GCA.setTabOrder(self.comboBox_4, self.comboBox_5)
        GCA.setTabOrder(self.comboBox_5, self.send_Button)
        GCA.setTabOrder(self.send_Button, self.send_Text)
        GCA.setTabOrder(self.send_Text, self.checkBox)
        GCA.setTabOrder(self.checkBox, self.checkBox_2)
        GCA.setTabOrder(self.checkBox_2, self.scrollArea)

    def retranslateUi(self, GCA):
        _translate = QtCore.QCoreApplication.translate
        GCA.setWindowTitle(_translate("GCA", "RECEIVER "))
        self.groupBox.setTitle(_translate("GCA", "CONSOLE"))
        self.comboBox.setItemText(0, _translate("GCA", "SIGNAL OFF"))
        self.comboBox.setItemText(1, _translate("GCA", "SIGNAL ON"))
        self.comboBox_4.setItemText(0, _translate("GCA", "PLAIN TEXT "))
        self.comboBox_5.setItemText(0, _translate("GCA", "NEWLINE "))
        self.comboBox_5.setItemText(1, _translate("GCA", "NEXT LINE "))
        self.send_Button.setText(_translate("GCA", "SEND"))
        self.checkBox.setText(_translate("GCA", "AUTOSCROLL"))
        self.checkBox_2.setText(_translate("GCA", "TIMESTAMP"))
        self.label.setText(_translate("GCA", "NOT CONNECTED"))
        self.groupBox_6.setTitle(_translate("GCA", "PACKET INFO "))
        self.groupBox_7.setTitle(_translate("GCA", "COMMAND HISTORY"))
        self.clear_Button.setText(_translate("GCA", "clear"))
        self.label_2.setText(_translate("GCA", "RAW TELEMETRY"))
        self.groupBox_8.setTitle(_translate("GCA", "TIME "))
        self.toolButton.setText(_translate("GCA", "DISCONNECTED"))
        self.groupBox_17.setTitle(_translate("GCA", "BATTERY"))
        self.toolButton_3.setText(_translate("GCA", "DISCONNECTED"))
        self.groupBox_18.setTitle(_translate("GCA", "BATTERY"))
        self.toolButton_4.setText(_translate("GCA", "DISCONNECTED"))
        self.groupBox_19.setTitle(_translate("GCA", "TIME "))
        self.toolButton_5.setText(_translate("GCA", "DISCONNECTED"))
        self.groupBox_20.setTitle(_translate("GCA", "SIGNAL"))
        self.toolButton_6.setText(_translate("GCA", "DISCONNECTED"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("GCA", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("GCA", "Page 2"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("GCA", "Page"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("GCA", "Page"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_5), _translate("GCA", "Page"))
        self.label_3.setText(_translate("GCA", "WELCOME"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_6), _translate("GCA", "Page"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    GCA = QtWidgets.QWidget()
    ui = Ui_GCA()
    ui.setupUi(GCA)
    GCA.show()
    sys.exit(app.exec_())
>>>>>>> dcffa7b7e9bddd0f066d2c1264ccd995432abdf6
