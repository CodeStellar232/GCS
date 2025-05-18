import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import threading
from PyQt5.QtGui import QFont, QColor, QPalette
import time

class GraphsPage(QMainWindow):
    update_graphs_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telemetry Graphs")
        self.setGeometry(100, 100, 1100, 650)
        self.update_graphs_signal.connect(self.update_graphs)

        self.arduino_connected = False
        self.serial_data = []
        self.arduino_port = None

        self.telemetry_fields = [
            "Team ID", "Timestamp", "Packet Count", "Altitude", "Pressure", "Temperature", "Voltage",
            "GNSS Time", "GNSS Latitude", "GNSS Longitude", "GNSS Altitude", "GNSS Satellites",
            "AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ", "Flight State"
        ]

        # Adjust graph_specs to fit into six boxes
        self.graph_specs = [
            ("Pressure [Pa]", ["Pressure"]),
            ("Altitude [m]", ["Altitude"]),
            ("Voltage [V]", ["Voltage"]),
            ("Accelerometer [m/s²]", ["AccX", "AccY", "AccZ"]),
            ("Gyroscope [rad/s]", ["GyroX", "GyroY", "GyroZ"]),
            ("Temperature [°C]", ["Temperature"])
        ]
 
        self.graphs = {}
        self.curves = {}
        self.data = {}

        # Create the main layout
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # Arrange graphs in a 2x3 grid (6 boxes)
        positions = [(i // 3, i % 3) for i in range(len(self.graph_specs))]
        for pos, (title, labels) in zip(positions, self.graph_specs):
            graph = self.create_graph(title, labels)
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

    def create_graph(self, title, labels):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.setBackground("black")
        plot_widget.showGrid(x=True, y=True)

        legend = pg.LegendItem(offset=(70, 30))
        legend.setParentItem(plot_widget.getPlotItem())

        colors = ['r', 'g', 'b', 'y', 'c', 'm', 'w']

        for i, label in enumerate(labels):
            color = colors[i % len(colors)]
            self.graphs[label] = plot_widget
            self.data[label] = {'x': [], 'y': []}
            curve = plot_widget.plot([], [], pen=pg.mkPen(color=color, width=2), name=label)
            self.curves[label] = curve
            legend.addItem(curve, label)

        return plot_widget

    def read_serial_data(self):
        ser = None
        try:
            if self.arduino_port is not None:
                ser = serial.Serial(self.arduino_port, 9600, timeout=1)
                print(f"Connected to {self.arduino_port}")

                try:
                    while self.arduino_connected:
                        try:
                            line = ser.readline().decode('utf-8').strip()
                            if line:
                                print(f"Received data: {line}")
                                self.serial_data.append(line)
                                self.serial_data = self.serial_data[-2:]
                                new_data = self.parse_serial_data(line)
                                self.update_graphs_signal.emit(new_data)
                            time.sleep(0.1)  # Add a small delay to prevent overload
                        except serial.SerialException:
                            print("Serial connection lost. Reconnecting...")
                            self.arduino_connected = False
                except Exception as e:
                    print(f"Error in serial thread: {e}")
                    self.arduino_connected = False
        finally:
            if ser and ser.is_open:
                ser.close()
                print("Serial connection closed.")

    def parse_serial_data(self, line):
        data_dict = {}
        try:
            values = line.split(',')
            if len(values) != len(self.telemetry_fields):
                print(f"Malformed line: {line}")
                return {}

            telemetry = dict(zip(self.telemetry_fields, values))

            for key in telemetry:
                if key not in self.data:
                    continue  # Skip untracked values

                try:
                    x_val = len(self.data[key]['x']) + 1
                    y_val = float(telemetry[key])
                    self.data[key]['x'].append(x_val)
                    self.data[key]['y'].append(y_val)
                    data_dict[key] = {
                        'x': self.data[key]['x'],
                        'y': self.data[key]['y']
                    }
                except ValueError:
                    print(f"Non-numeric value for {key}: {telemetry[key]}")

        except Exception as e:
            print(f"Error parsing line: {line}, Error: {e}")

        return data_dict

    def update_graphs(self, new_data=None):
        if not self.arduino_connected or new_data is None:
            return

        for key, values in new_data.items():
            if key in self.curves:
                x_data = values['x'][-1000:]
                y_data = values['y'][-1000:]

                self.data[key]['x'] = self.data[key]['x'][-1000:]
                self.data[key]['y'] = self.data[key]['y'][-1000:]

                self.curves[key].setData(x_data, y_data)

                self.graphs[key].enableAutoRange(axis='x', enable=True)
                self.graphs[key].enableAutoRange(axis='y', enable=True)

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
            print(f"Port: {port.device}, Description: {port.description}")
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

    def update_data(self, data):
        """Update the graphs with the received data."""
        print(f"GraphsPage received data: {data}")
        self.update_graphs(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphsPage()
    window.show()

    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    sys.exit(app.exec_())
