
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, QDateTime
import psutil
import serial.tools.list_ports
import random  # Temporary for fake GNSS Signal Strength
import sys

class StatusHeaderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Real-Time Status Header")
        self.setFixedSize(900, 100)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(20)

        # Battery
        self.battery_label = QLabel("Battery:")
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(0)
        self.battery_bar.setFormat("%p%")

        # GNSS Signal Strength
        self.gnss_label = QLabel("Signal: N/A")

        # Serial Port Connection Status
        self.serial_label = QLabel("Serial: Disconnected")

        # Date & Time
        self.datetime_label = QLabel("DateTime: --:--:--")

        # Add all widgets
        self.layout.addWidget(self.battery_label)
        self.layout.addWidget(self.battery_bar)
        self.layout.addWidget(self.gnss_label)
        self.layout.addWidget(self.serial_label)
        self.layout.addWidget(self.datetime_label)

        self.setLayout(self.layout)

        # Timer to update every 1 second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 1 second

        self.update_status()  # Update immediately on start

    def update_status(self):
        self.update_battery_status()
        self.update_gnss_signal()
        self.update_serial_status()
        self.update_datetime()

    def update_battery_status(self):
        battery = psutil.sensors_battery()
        if battery is not None:
            percent = battery.percent
            self.battery_bar.setValue(percent)

            if battery.power_plugged:
                self.battery_bar.setFormat(f"Charging ({percent}%)")
            else:
                self.battery_bar.setFormat(f"{percent}%")
        else:
            self.battery_bar.setFormat("Battery Info N/A")
            self.battery_bar.setValue(0)

    def update_gnss_signal(self):
        # Here you should parse real GNSS data instead of random
        fake_signal_strength = random.randint(0, 100)  # Simulate GNSS strength
        self.gnss_label.setText(f"GNSS Signal: {fake_signal_strength}%")
        if fake_signal_strength > 70:
            self.gnss_label.setStyleSheet("color: green;")
        elif fake_signal_strength > 40:
            self.gnss_label.setStyleSheet("color: orange;")
        else:
            self.gnss_label.setStyleSheet("color: red;")

    def update_serial_status(self):
        ports = list(serial.tools.list_ports.comports())
        if ports:
            self.serial_label.setText("Serial: Connected")
            self.serial_label.setStyleSheet("color: green;")
        else:
            self.serial_label.setText("Serial: Disconnected")
            self.serial_label.setStyleSheet("color: red;")

    def update_datetime(self):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.datetime_label.setText(f"DateTime: {current_time}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatusHeaderWidget()
    window.show()
    sys.exit(app.exec_())


    def update_battery_status(self):
        battery = psutil.sensors_battery()
        if battery:
            battery_percentage = battery.percent
            is_charging = battery.power_plugged

            self.battery_bar.setValue(battery_percentage)

            # Dynamic text depending on charging
            if is_charging:
                self.battery_label.setText(f"Battery: {battery_percentage}% (Charging)")
            else:
                self.battery_label.setText(f"Battery: {battery_percentage}%")

            # Dynamic Color
            if battery_percentage >= 75:
                color = "green"
            elif 30 <= battery_percentage < 75:
                color = "orange"
            else:
                color = "red"

            self.battery_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
        else:
            self.battery_label.setText("Battery: N/A")
            self.battery_bar.setValue(0)

