import requests
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

def locationCoordinates():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        loc = data['loc'].split(',')
        lat, long = float(loc[0]), float(loc[1])
        city = data.get('city', 'Unknown')
        state = data.get('region', 'Unknown')
        return lat, long, city, state
    except:
        return None

class LocationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Location Finder")
        self.resize(800, 600)
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Click the button to get your location!")
        self.layout.addWidget(self.label)
        
        self.button = QPushButton("Get Location")
        self.button.clicked.connect(self.showLocation)
        self.layout.addWidget(self.button)
        
        self.mapButton = QPushButton("Show Map")
        self.mapButton.clicked.connect(self.showMap)
        self.layout.addWidget(self.mapButton)
        
        self.mapView = QWebEngineView()
        self.layout.addWidget(self.mapView)
        
        self.setLayout(self.layout)
        
    def showLocation(self):
        location = locationCoordinates()
        if location:
            lat, long, city, state = location
            self.label.setText(f"Latitude: {lat}\nLongitude: {long}\nCity: {city}\nState: {state}")
        else:
            self.label.setText("Unable to fetch location. Please check your internet connection.")
            
    def showMap(self):
        location = locationCoordinates()
        if location:
            lat, long, city, state = location
            # Generate OpenStreetMap embed link
            openstreet_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={long}#map=15/{lat}/{long}"
            self.mapView.setUrl(QUrl(openstreet_url))
        else:
            self.label.setText("Unable to display map. Please check your internet connection.")

if __name__ == '__main__':
    from PyQt5.QtCore import QUrl

    app = QApplication(sys.argv)
    window = LocationApp()
    window.show()
    sys.exit(app.exec_())