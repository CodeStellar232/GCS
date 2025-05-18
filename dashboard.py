from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QLineEdit, QMessageBox, QRadioButton, QLabel
import serial
import serial.tools.list_ports
import threading

class Ui_GCA(QtCore.QObject):
    data_received = QtCore.pyqtSignal(str)

    def setupUi(self, GCA):
        GCA.setObjectName("GCA")
        GCA.resize(1132, 650)
        self.gridLayout = QtWidgets.QGridLayout(GCA)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(GCA)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # Dashboard
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_2.setGeometry(QtCore.QRect(200,200,1400,900))
        self.groupBox_2.setObjectName("groupBox_2")
        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z", "Flight State"
        ]

        # Clear Button
        self.clear_btn = QPushButton("Clear", self.groupBox_2)
        self.clear_btn.setGeometry(QtCore.QRect(660, 10, 80, 30))
        self.clear_btn.clicked.connect(self.clear_display)

        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_2)
        self.textBrowser.setGeometry(QtCore.QRect(0, 50, 741, 410))
        self.textBrowser.setObjectName("textBrowser")

        # Serial Port Settings
        self.groupBox_3 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_3.setGeometry(QtCore.QRect(1100, 120, 221, 211))
        self.groupBox_3.setObjectName("groupBox_3")

        self.label_2 = QtWidgets.QLabel("PORT", self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 55, 16))
########
        self.label_3 = QtWidgets.QLabel("BAUD RATE", self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(10, 90, 61, 16))
        
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_2.setGeometry(QtCore.QRect(10, 60, 201, 22))

        self.comboBox_3 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_3.setGeometry(QtCore.QRect(10, 110, 201, 22))
        self.comboBox_3.addItems(["1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200"])

        self.pushButton_2 = QtWidgets.QPushButton("CONNECT", self.groupBox_3)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 150, 171, 28))
        self.pushButton_2.clicked.connect(self.connect_serial)

        # Data Logger Section
        self.groupBox_4 = QtWidgets.QGroupBox(self.frame)
        self.groupBox_4.setGeometry(QtCore.QRect(1100, 350, 221, 100))
        self.groupBox_4.setObjectName("groupBox_4")
        self.groupBox_4.setTitle("Data Logger")

        self.radio_log = QRadioButton("Log Data", self.groupBox_4)
        self.radio_log.setGeometry(QtCore.QRect(20, 30, 100, 20))

        self.radio_disable = QRadioButton("Disable Data", self.groupBox_4)
        self.radio_disable.setGeometry(QtCore.QRect(20, 60, 100, 20))
        self.radio_disable.setChecked(True)
        self.radio_disable.toggled.connect(self.disable_data_logging)

        self.radio_log.toggled.connect(self.toggle_data_logging)
        self.radio_disable.toggled.connect(self.toggle_data_logging)

        # Command Sending Section
        self.command_input = QLineEdit(self.frame)
        self.command_input.setGeometry(QtCore.QRect(120, 590, 500, 30))
        self.command_input.setPlaceholderText("Enter command to send...")

        self.send_btn = QPushButton("Send", self.frame)
        self.send_btn.setGeometry(QtCore.QRect(630, 590, 100, 30))
        self.send_btn.clicked.connect(self.send_command)

        self.clear_command_btn = QPushButton("Clear", self.frame)
        self.clear_command_btn.setGeometry(QtCore.QRect(740, 590, 100, 30))
        self.clear_command_btn.clicked.connect(self.clear_command_input)
        
        self.status_label = QLabel(GCA)
        self.status_label.setGeometry(QtCore.QRect(10, 10, 300, 30))
        self.status_label.setText("Arduino Status: Waiting...")

        self.gridLayout.addWidget(self.frame, 0, 1, 1, 1)

        self.retranslateUi(GCA)
        QtCore.QMetaObject.connectSlotsByName(GCA)

        self.data_received.connect(self.update_text_browser)

        self.serial_connection = None
        self.refresh_ports()
        self.data_logging_enabled = False

    def retranslateUi(self, GCA):
        _translate = QtCore.QCoreApplication.translate
        GCA.setWindowTitle(_translate("GCA", "RECEIVER"))
        self.groupBox_2.setTitle(_translate("GCA", "Dashboard"))
        self.groupBox_3.setTitle(_translate("GCA", "Serial Port Settings"))
        self.groupBox_4.setTitle(_translate("GCA", "Data Logger"))
        self.clear_btn.setText(_translate("GCA", "Clear"))
        self.pushButton_2.setText(_translate("GCA", "CONNECT"))
        self.radio_log.setText(_translate("GCA", "Log Data"))
        self.radio_disable.setText(_translate("GCA", "Disable Data"))
        self.send_btn.setText(_translate("GCA", "Send"))
        self.clear_command_btn.setText(_translate("GCA", "Clear"))

    def connect_serial(self):
        port = self.comboBox_2.currentText()
        baud_rate = int(self.comboBox_3.currentText())
        if not port:
            QMessageBox.warning(None, "Warning", "No COM port selected!")
            return
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            self.textBrowser.append(f"✅ Connected to {port} at {baud_rate} baud.")
            self.start_reading_thread()
        except Exception as e:
            self.textBrowser.append(f"❌ Failed to connect: {str(e)}")

    def start_reading_thread(self):
        self.reading_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.reading_thread.start()

    def read_serial_data(self):
        try:
            while self.serial_connection.is_open:
                line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line and self.data_logging_enabled:
                    self.data_received.emit(line)
        except Exception as e:
            self.textBrowser.append(f"❌ Error reading data: {str(e)}")

    def update_text_browser(self, data):
        # Try to parse CSV data and display as field: value
        parts = data.split(',')
        if len(parts) == len(self.telemetry_fields):
            formatted = "<b>Telemetry Data:</b><br>"
            for field, value in zip(self.telemetry_fields, parts):
                formatted += f"<b>{field}:</b> {value}<br>"
            self.textBrowser.append(formatted)
        else:
            # Fallback: just display the raw data
            self.textBrowser.append(data)

    def refresh_ports(self):
        self.comboBox_2.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboBox_2.addItem(port.device)

    def disable_data_logging(self):
        if self.radio_disable.isChecked():
            self.data_logging_enabled = False
            self.textBrowser.append("⛔ Data logging disabled.")

    def toggle_data_logging(self):
        if self.radio_log.isChecked():
            self.data_logging_enabled = True
            self.textBrowser.append("▶️ Data logging enabled.")
        elif self.radio_disable.isChecked():
            self.data_logging_enabled = False
            self.textBrowser.append("⛔ Data logging disabled.")

    def send_command(self):
        command = self.command_input.text().strip()
        if not command:
            QMessageBox.warning(None, "Warning", "Command cannot be empty!")
            return
        self.textBrowser.append(f"📤 <b>Sent:</b> {command}")
        self.command_input.clear()

    def clear_display(self):
        self.textBrowser.clear()

    def clear_command_input(self):
        self.command_input.clear()

    def update_status(self, message):
        self.status_label.setText(f"Arduino Status: {message}")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = Ui_GCA()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
