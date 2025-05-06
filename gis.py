from PyQt5.QtWidgets import QApplication, QWidget
import folium
import sys
class MapPage(QWidget):
    def __init__(self):
        super(MapPage, self).__init__()
        self.setWindowTitle("Map Page")
        self.resize(800, 600)
        self.setupUi()

    def setupUi(self):
        # Create a folium map object
        self.map_widget = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
        # Save the map to an HTML file
        self.map_widget.save("map.html")

        # Load the HTML file into a QTextEdit or similar widget
        # For simplicity, we will just print the path to the saved map
        print("Map saved to map.html")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    mapObj = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
    window = MapPage()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())

 