import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.uic import loadUi
import resource_rc




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        # Set up the main window
        self.setObjectName("MainWindow")
        self.resize(799, 600)

        # Central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Layouts
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        # Left navigation widget
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMaximumSize(QtCore.QSize(50, 16777215))

        # Navigation buttons
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.db_btn = self.create_nav_button(":/icons/layout.png")
        self.verticalLayout.addWidget(self.db_btn)
        
        self.console_btn = self.create_nav_button(":/icons/command-line.png")
        self.verticalLayout.addWidget(self.console_btn)

        self.graph_btn = self.create_nav_button(":/icons/graph.png")
        self.verticalLayout.addWidget(self.graph_btn)

        self.map_btn = self.create_nav_button(":/icons/placeholder.png")
        self.verticalLayout.addWidget(self.map_btn)

        self.tjct_btn = self.create_nav_button(":/icons/heading.png")
        self.verticalLayout.addWidget(self.tjct_btn)

        self.abt_btn = self.create_nav_button(":/icons/id-card.png")
        self.verticalLayout.addWidget(self.abt_btn)

        self.horizontalLayout.addWidget(self.widget)

        # Stacked widget for pages
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.stackedWidget)

        # Pages
        self.create_page("DASHBOARD PAGE")
        self.create_page("CONSOLE PAGE")
        self.create_page("GRAPH PAGE")
        self.create_page("MAP PAGE")
        self.create_page("TRAJECTORY PAGE")
        self.create_page("ABOUT PAGE")

        # Connect buttons to page navigation
        self.db_btn.clicked.connect(lambda: self.navigate_to(0))
        self.console_btn.clicked.connect(lambda: self.navigate_to(1))
        self.graph_btn.clicked.connect(lambda: self.navigate_to(2))
        self.map_btn.clicked.connect(lambda: self.navigate_to(3))
        self.tjct_btn.clicked.connect(lambda: self.navigate_to(4))
        self.abt_btn.clicked.connect(lambda: self.navigate_to(5))

    def create_nav_button(self, icon_path):
        button = QtWidgets.QPushButton()
        button.setMinimumSize(QtCore.QSize(35, 35))
        button.setMaximumSize(QtCore.QSize(35, 35))
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(30, 30))
        button.setCheckable(True)
        button.setAutoExclusive(True)
        return button

    def create_page(self, text):
        page = QtWidgets.QWidget()
        label = QtWidgets.QLabel(page)
        label.setGeometry(QtCore.QRect(50, 50, 400, 50))
        label.setText(f"{text}")
        self.stackedWidget.addWidget(page)

    def navigate_to(self, index):
        self.stackedWidget.setCurrentIndex(index)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
