import requests
import folium
import datetime
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
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

def gps_locator():
    location = locationCoordinates()
    if location:
        lat, long, city, state = location
        map_obj = folium.Map(location=[lat, long], zoom_start=15)
        folium.Marker([lat, long], popup=f"Current Location: {city}, {state}").add_to(map_obj)
        file_name = f"Location_{datetime.date.today()}.html"
        map_obj.save(file_name)
        return file_name
    else:
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
        file_path = gps_locator()
        if file_path:
            self.mapView.setUrl(QUrl.fromLocalFile(file_path))
            self.label.setText("Map Loaded Successfully!")
        else:
            self.label.setText("Unable to generate map. Please check your internet connection.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LocationApp()
    window.show()
    sys.exit(app.exec_())