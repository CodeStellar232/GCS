
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QSizePolicy, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, pyqtSignal
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtGui import QFont

class TelemetryDashboard(QMainWindow):
    update_graphs_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph")
        self.setGeometry(100, 100, 1100, 650)
        self.update_graphs_signal.connect(self.update_graphs)  

        self.arduino_connected = False
        self.x_data = []
        self.serial_data = []
        self.arduino_port = None

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        self.graph_specs = [
            ("Pressure [Pa]", ["Pressure"]),
            ("Altitude [m]", ["Altitude"]),
            ("Voltage [V]", ["Voltage"]),
            ("Current [A]", ["Current"]),
            ("Accelerometer [m/s²]", ["AccX", "AccY", "AccZ"]),
            ("Gyroscope [rad/s]", ["GyroX", "GyroY", "GyroZ"]),
            ("Orientation [Degree]", ["Orientation"]),
            ("Temperature [°C]", ["Temperature"])
        ]

        self.graphs = {}
        self.curves = {}
        self.data = {}

        positions = [(i // 4, i % 4) for i in range(len(self.graph_specs))]

        for pos, (title, label) in zip(positions, self.graph_specs):
            graph = self.create_graph(title, label)
            graph.setStyleSheet("border: 2px solid gray;")
            grid_layout.addWidget(graph, *pos)

        self.serial_monitor = QLabel("Serial Monitor:\n")
        self.serial_monitor.setStyleSheet("color: black; background-color: white; padding: 6px;")
        self.serial_monitor.setFont(QFont('Arial', 10))

        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.serial_monitor)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.detect_arduino()

        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start()

    def create_graph(self, title, label):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.setBackground("black")
        plot_widget.showGrid(x=True, y=True)
        plot_widget.legeng = pg.LegendItem(offset=(70, 30))
        plot_widget.legeng.setParentItem(plot_widget.getPlotItem())

        self.graphs[label[0]] = plot_widget
        self.data[label[0]] = {'x': [], 'y': []}
        self.curves[label[0]] = plot_widget.plot([], [], pen=pg.mkPen(color='w', width=2))

        return plot_widget


    def read_serial_data(self):
        ser = None
        try:
            if self.arduino_port is not None:
                ser = serial.Serial(self.arduino_port, 9600, timeout=1)
                print(f"Connected to {self.arduino_port}")

                while self.arduino_connected:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            print(f"Received data: {line}")
                            self.serial_data.append(line)
                            self.serial_data = self.serial_data[-2:]  # Keep only last 2 entries
                            new_data = self.parse_serial_data(line)
                            self.update_graphs_signal.emit(new_data)  # Emit safely to main thread
                    except serial.SerialException:
                        print("Serial connection lost. Reconnecting...")
                        self.arduino_connected = False
        finally:
            if ser and ser.is_open:
                ser.close()
                print("Serial connection closed.")

    def parse_serial_data(self, line):
        data_dict = {}
        try:
            data_pairs = line.split(',')
            for pair in data_pairs:
                key, value = pair.split(':')
                key = key.strip()
                value = value.strip()
                if key in self.data:
                    self.data[key]['x'].append(len(self.data[key]['x']) + 1)
                    self.data[key]['y'].append(float(value))
                    data_dict[key] = {'x': self.data[key]['x'], 'y': self.data[key]['y']}
        except Exception as e:
            print(f"Error parsing data '{line}': {e}")
        return data_dict

    def update_graphs(self, new_data=None):
        if not self.arduino_connected or new_data is None:
            return

        for title, values in new_data.items():
            if title in self.graphs:
                x_data = values['x'][-50:]  
                y_data = values['y'][-50:]

                self.data[title]['x'] = x_data
                self.data[title]['y'] = y_data

                self.curves[title].setData(x_data, y_data) 

            self.update_serial_monitor()

    def update_serial_monitor(self):
        if len(self.serial_data) >= 2:
            self.serial_monitor.setText(f"Serial Monitor:\n{self.serial_data[-2]}\n{self.serial_data[-1]}")
        elif len(self.serial_data) == 1:
            self.serial_monitor.setText(f"Serial Monitor:\n{self.serial_data[-1]}")
        else:
            self.serial_monitor.setText("Serial Monitor:\nNo data received yet.")

    def detect_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'USB Serial' in port.description:
                self.arduino_port = port.device
                self.arduino_connected = True
                self.serial_monitor.setText(f"Serial Monitor:\nArduino detected on port: {self.arduino_port}")
                print(f"Arduino detected on port: {self.arduino_port}")
                self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
                self.serial_thread.start()  
                return

        self.serial_monitor.setText("Serial Monitor:\nNo Arduino detected. Please connect it via USB.")
        print("No Arduino detected. Please connect it via USB.")


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetryDashboard()
    window.show()
    sys.exit(app.exec_())
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QSizePolicy, QLabel
from PyQt5.QtCore import QTimer, QMetaObject, Qt
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtGui import QFont

class Graph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph")
        self.setGeometry(100, 100, 1100, 650)

        self.arduino_connected = True
        self.arduino_port = None
        self.serial_data = []
        self.x_data = []

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(14)

        self.graph_specifications = [
            ("Pressure [Pa]", ["Pressure"]),
            ("Altitude [m]", ["Altitude"]),
            ("Voltage [V]", ["Voltage"]),
            ("Current [A]", ["Current"]),
            ("Accelerometer [m/s²]", ["AccX", "AccY", "AccZ"]),
            ("Gyroscope [rad/s]", ["GyroX", "GyroY", "GyroZ"]),
            ("Orientation [Degree]", ["Orientation"]),
            ("Temperature [°C]", ["Temperature"])
        ]

        self.graphs = {}
        self.data = {}

        positions = [(i // 4, i % 4) for i in range(len(self.graph_specifications))]

        for pos, (title, labels) in zip(positions, self.graph_specifications):
            graph = self.create_graph(title, labels)
            graph.setStyleSheet("border: 2px solid gray;")
            grid_layout.addWidget(graph, *pos)

        self.serial_monitor = QLabel("Serial Monitor:\n")
        self.serial_monitor.setStyleSheet("color: black; background-color: white; padding: 6px;")
        self.serial_monitor.setFont(QFont('Arial', 10))

        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.serial_monitor)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000)

        self.detect_arduino()

        if self.arduino_connected:
            self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.serial_thread.start()
        else:
            self.serial_monitor.setText("Serial Monitor:\nArduino not detected.")
            print("Arduino not detected.")

    def create_graph(self, title, labels):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.setBackground("black")
        plot_widget.showGrid(x=True, y=True)

        plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plot_widget.setMinimumSize(300, 310)
        plot_widget.setMaximumSize(300, 310)

        self.graphs[title] = plot_widget
        self.data[title] = {label: ([], []) for label in labels}

        font = QFont('Arial', 12)
        font.setWeight(QFont.Bold)

        plot_widget.getAxis('left').setFont(font)
        plot_widget.getAxis('bottom').setFont(font)

        return plot_widget

    def update_graphs(self, new_data=None):
        if not self.arduino_connected or new_data is None:
            return

        for title, values in new_data.items():
            if title in self.graphs:
                plot_widget = self.graphs[title]
                plot_widget.clear()

                for label, (x_data, y_data) in values.items():
                    if len(x_data) > 5:
                        x_data = x_data[-5:]
                        y_data = y_data[-5:]

                    self.data[title][label] = (x_data, y_data)
                    plot_widget.plot(x_data, y_data, pen=pg.mkPen(width=2))

                y_min, y_max = min(y_data, default=0), max(y_data, default=10)
                plot_widget.setYRange(y_min - 1, y_max + 1, padding=0)

                if self.x_data:
                    x_min = min(self.x_data)
                    x_max = max(self.x_data)
                    plot_widget.setXRange(x_min, x_max, padding=0)

        self.update_serial_monitor()

    def read_serial_data(self):
        try:
            with serial.Serial(self.arduino_port, 9600, timeout=1) as ser:
                print(f"Connected to {self.arduino_port}")
                while self.arduino_connected:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"Received data: {line}")
                        values = line.split(",")
                        if len(values) == 8:
                            try:
                                pressure = float(values[0])
                                altitude = float(values[1])
                                voltage = float(values[2])
                                current = float(values[3])
                                acc_x = float(values[4])
                                acc_y = float(values[5])
                                acc_z = float(values[6])
                                temperature = float(values[7])

                                self.serial_data.append(line)

                                new_data = {
                                    "Pressure [Pa]": {"Pressure": (self.x_data, [pressure])},
                                    "Altitude [m]": {"Altitude": (self.x_data, [altitude])},
                                    "Voltage [V]": {"Voltage": (self.x_data, [voltage])},
                                    "Current [A]": {"Current": (self.x_data, [current])},
                                    "Accelerometer [m/s²]": {
                                        "AccX": (self.x_data, [acc_x]),
                                        "AccY": (self.x_data, [acc_y]),
                                        "AccZ": (self.x_data, [acc_z])
                                    },
                                    "Temperature [°C]": {"Temperature": (self.x_data, [temperature])}
                                }

                                QMetaObject.invokeMethod(
                                    self, "update_graphs",
                                    Qt.QueuedConnection,
                                    Qt.Q_ARG(dict, new_data)
                                )

                            except ValueError:
                                print("Error: Could not convert values to float")

                        if len(self.serial_data) > 5:
                            self.serial_data.pop(0)

        except serial.SerialException as e:
            print(f"Error reading serial data: {e}")
            self.serial_monitor.setText(f"Serial Monitor:\nError reading data: {e}")

    def update_serial_monitor(self):
        if len(self.serial_data) >= 2:
            self.serial_monitor.setText(f"Serial Monitor:\n{self.serial_data[-2]}\n{self.serial_data[-1]}")
        elif len(self.serial_data) == 1:
            self.serial_monitor.setText(f"Serial Monitor:\n{self.serial_data[-1]}")
        else:
            self.serial_monitor.setText("Serial Monitor:\nNo data received yet.")

    def detect_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'USB Serial Device' in port.description:
                self.arduino_port = port.device
                self.arduino_connected = True
                self.serial_monitor.setText(f"Serial Monitor:\nArduino detected on port: {self.arduino_port}")
                return
        self.serial_monitor.setText("Serial Monitor:\nNo Arduino detected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Graph()
    window.show()
    sys.exit(app.exec_())
