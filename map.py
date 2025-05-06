import sys
import time
import threading
import requests
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, QCoreApplication, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

TWO_MINUTES = 120000  # milliseconds
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

class Location:
    def __init__(self, lat, lon, accuracy=10, provider="mock", timestamp=None):
        self.latitude = lat
        self.longitude = lon
        self.accuracy = accuracy
        self.provider = provider
        self.time = timestamp or int(time.time() * 1000)

class LocationService(QObject):
    location_updated = pyqtSignal(Location)

    def __init__(self):
        super().__init__()
        self.previous_best_location = None
        self.is_running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_location)

    def start(self):
        self.is_running = True
        self.timer.start(TWO_MINUTES)

    def stop(self):
        self.timer.stop()
        self.is_running = False
        
# try to fetch coordinates from gps
    def get_current_location(self):
        # Placeholder for real GPS data
        # Use geopy or gpsd here in real implementation
        lat, lon = 23.0225, 72.5714  # Example: Ahmedabad coords
        return Location(lat, lon)

    def check_location(self):
        if not self.is_running:
            self.start()

        new_location = self.get_current_location()

        if self.is_better_location(new_location, self.previous_best_location):
            self.previous_best_location = new_location
            self.post_location_to_server(new_location)
            self.stop()

    def post_location_to_server(self, location):
        try:
            device_key = "mock-device-id"  # Replace with real device ID logic
            url = "https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d13961.993727457553!2d77.64214655!3d28.972597699999998!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sin!4v1745406415227!5m2!1sen!2sin"
            data = {
                'device_key': device_key,
                'latitude': str(location.latitude),
                'longitude': str(location.longitude),
            }
            response = requests.post(url, data=data)
            print("Server Response:", response.status_code)
        except Exception as e:
            print("Error posting location:", e)

    def is_better_location(self, location, current_best_location):
        if current_best_location is None:
            return True

        time_delta = location.time - current_best_location.time
        is_significantly_newer = time_delta > TWO_MINUTES
        is_significantly_older = time_delta < -TWO_MINUTES
        is_newer = time_delta > 0

        if is_significantly_newer:
            return True
        elif is_significantly_older:
            return False

        accuracy_delta = location.accuracy - current_best_location.accuracy
        is_less_accurate = accuracy_delta > 0
        is_more_accurate = accuracy_delta < 0
        is_significantly_less_accurate = accuracy_delta > 200

        is_from_same_provider = location.provider == current_best_location.provider

        if is_more_accurate:
            return True
        elif is_newer and not is_less_accurate:
            return True
        elif is_newer and not is_significantly_less_accurate and is_from_same_provider:
            return True

        return False

def main():
    app = QCoreApplication(sys.argv)
    service = LocationService()
    service.start()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    app = QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()  
    ui = Ui_GCA()
    ui.setupUi(MainWindow)    