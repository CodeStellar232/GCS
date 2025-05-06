import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QColor, QVector3D
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import (
    Qt3DWindow, QOrbitCameraController, QPhongMaterial,
    QPlaneMesh, QCuboidMesh
)
from PyQt5.Qt3DRender import QCamera, QDirectionalLight, QMesh


class InfoPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.coord_label = QLabel("Coordinates:\nX: 0.00\nY: 0.00\nZ: 0.00")
        self.rpy_label = QLabel("Orientation:\nRoll: 0°\nPitch: 0°\nYaw: 0°")

        layout.addWidget(QLabel("<b>Object Info</b>"))
        layout.addSpacing(10)
        layout.addWidget(self.coord_label)
        layout.addSpacing(10)
        layout.addWidget(self.rpy_label)
        layout.addStretch()

    def update_info(self, pos: QVector3D, rotation: QVector3D):
        self.coord_label.setText(
            f"Coordinates:\nX: {pos.x():.2f}\nY: {pos.y():.2f}\nZ: {pos.z():.2f}"
        )
        self.rpy_label.setText(
            f"Orientation:\nRoll: {rotation.x():.0f}°\nPitch: {rotation.y():.0f}°\nYaw: {rotation.z():.0f}°"
        )


class TrajectoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Trajectory Viewer")
        self.resize(1200, 700)

        self.view = Qt3DWindow()
        self.container = self.createWindowContainer(self.view)
        self.container.setMinimumSize(800, 600)

        self.info_panel = InfoPanel()

        layout = QHBoxLayout()
        layout.addWidget(self.info_panel)
        layout.addWidget(self.container)
        self.setLayout(layout)

        self.root_entity = QEntity()

        self._setup_grid()
        self._load_model()
        self._setup_camera()

        self.view.setRootEntity(self.root_entity)

        # Timer to update panel (simulate real-time)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_info)
        self.timer.start(1000)

    def _load_model(self):
        self.model_entity = QEntity(self.root_entity)

        mesh = QMesh()
        mesh.setSource(QUrl.fromLocalFile(r"C:\Users\AYUSHI\Desktop\RESTART\PRARAMBH\.qodo\Main\assets\rocket.obj"))  #Change path to your model

        material = QPhongMaterial()
        material.setDiffuse(QColor(200, 100, 200))

        self.transform = QTransform()
        self.transform.setScale(1.5)
        self.transform.setTranslation(QVector3D(0, 1, 0))
        self.transform.setRotationX(15)
        self.transform.setRotationY(25)

        self.model_entity.addComponent(mesh)
        self.model_entity.addComponent(material)
        self.model_entity.addComponent(self.transform)

        # Light
        light_entity = QEntity(self.root_entity)
        light = QDirectionalLight(light_entity)
        light.setColor(QColor(255, 255, 255))
        light.setIntensity(0.9)
        light_transform = QTransform()
        light_transform.setTranslation(QVector3D(10, 10, 10))
        light_entity.addComponent(light)
        light_entity.addComponent(light_transform)

    def _setup_camera(self):
        camera = self.view.camera()
        camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
        camera.setPosition(QVector3D(0, 8, 20))
        camera.setViewCenter(QVector3D(0, 0, 0))

        cam_controller = QOrbitCameraController(self.root_entity)
        cam_controller.setLinearSpeed(50)
        cam_controller.setLookSpeed(180)
        cam_controller.setCamera(camera)

    def _setup_grid(self):
        for axis in range(-10, 11):
            if axis == 0:
                continue
            # X-axis lines
            x_line = QEntity(self.root_entity)
            mesh = QPlaneMesh()
            mesh.setWidth(0.02)
            mesh.setHeight(20.0)
            transform = QTransform()
            transform.setTranslation(QVector3D(axis, 0, 0))
            material = QPhongMaterial()
            material.setDiffuse(QColor(180, 180, 180))
            x_line.addComponent(mesh)
            x_line.addComponent(material)
            x_line.addComponent(transform)

            # Z-axis lines
            z_line = QEntity(self.root_entity)
            mesh2 = QPlaneMesh()
            mesh2.setWidth(20.0)
            mesh2.setHeight(0.02)
            transform2 = QTransform()
            transform2.setTranslation(QVector3D(0, 0, axis))
            material2 = QPhongMaterial()
            material2.setDiffuse(QColor(180, 180, 180))
            z_line.addComponent(mesh2)
            z_line.addComponent(material2)
            z_line.addComponent(transform2)

    def _update_info(self):
        pos = self.transform.translation()
        rot = QVector3D(self.transform.rotationX(), self.transform.rotationY(), self.transform.rotationZ())
        self.info_panel.update_info(pos, rot)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TrajectoryPage()
    viewer.show()
    sys.exit(app.exec_())

