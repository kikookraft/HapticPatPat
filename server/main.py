from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt
from server import Server

import sys

"""Main window of the application
This file contains the main window of the application. It is used to create the UI and handle the user interactions.
There is not much logic in this file, it is mostly used to create the UI and call the server when needed.
"""

class MainWindow(QWidget):
    """Main window of the application"""
    def __init__(self):
        super().__init__()

        self.slider_strength = None

        self.prev_patstrap_status = False
        self.prev_vrchat_status = False

        self.setWindowTitle("PatPatHaptic Server")
        # Load the global css file if it exists, otherwise create it with the default values
        try: 
            with open("global.css","r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            # write the default file
            with open("global.css","w") as file:
                a = """QLabel {    color: #ffffff;    font-weight: 300;    font-size: 25px;}QPushButton {    background: #109960;    border: none;    padding: 12px 15px;    text-decoration: none;    font-size: 20px;    margin: 0px 10px 0px 10px;    border-radius: 5px;    font-weight: 500;    color: white;}QPushButton::hover {    background: #49d196;}QPushButton::disabled {    color: #c0c0c0;    background: #1c1927;}#mainbackground {    background: #24202f;}#section {    background: rgba(44, 40, 54, 1);    border-radius: 10px;    margin-bottom: 5px;}QSlider {    height: 15px;}QSlider::add-page:horizontal {    background: white;}QSlider::sub-page:horizontal {    background: #29b980;}QSlider::handle:horizontal {    height: 10px;    width: 10px;    background: #109960;}QSlider::handle:horizontal:hover {    background: #29b980;}"""
                file.write(a)
            self.setStyleSheet(a)
        layoutMain = QVBoxLayout()
        layoutMain.setContentsMargins(0, 0, 0, 0)

        box = QWidget()
        box.setObjectName("mainbackground")

        # Create the sections
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.create_patstrap_status())
        layout.addWidget(self.create_vrchat_status())
        layout.addWidget(self.create_settings())
        layout.addWidget(self.create_test())
        
        self.server = Server(self)

        box.setLayout(layout)
        layoutMain.addWidget(box)

        self.setLayout(layoutMain)

    def create_patstrap_status(self):
        """Create the patstrap status section"""
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Patstrap connection")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        self.status_hardware_connection = QLabel(" ⬤")
        self.status_hardware_connection.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_hardware_connection.setStyleSheet("color: #b94029; font-size: 30px;")
        layout.addWidget(self.status_hardware_connection)

        box.setLayout(layout)
        return box

    def create_vrchat_status(self):
        """Create the vrchat status section"""
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("VRChat connection")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        self.status_vrchat_connection = QLabel("  ⬤")
        self.status_vrchat_connection.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_vrchat_connection.setStyleSheet("color: #b94029; font-size: 30px;")
        layout.addWidget(self.status_vrchat_connection)

        box.setLayout(layout)
        return box

    def create_settings(self):
        """Create the settings section"""
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(85)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Intensity")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)

        self.slider_strength = QSlider(Qt.Orientation.Horizontal)
        self.slider_strength.setMaximumWidth(200)
        self.slider_strength.setMinimum(0)
        self.slider_strength.setMaximum(100)
        self.slider_strength.setValue(50)
        layout.addWidget(self.slider_strength)

        box.setLayout(layout)
        return box

    def get_intensity(self) -> float:
        """Get the intensity from the slider and return it as a float between 0 and 1"""
        if self.slider_strength is None:
            return 0
        return self.slider_strength.value() / 100.0

    def create_test(self):
        """Create the test section with the two buttons to test the hardware"""
        box = QWidget()
        box.setObjectName("section")
        box.setFixedHeight(140)

        layoutH = QHBoxLayout()
        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(20, 20, 20, 20)

        self.test_left_button = QPushButton("Pat left")
        self.test_left_button.clicked.connect(self.pat_left)
        self.test_left_button.setDisabled(True)
        layoutH.addWidget(self.test_left_button)

        self.test_right_button = QPushButton("Pat right")
        self.test_right_button.clicked.connect(self.pat_right)
        self.test_right_button.setDisabled(True)
        layoutH.addWidget(self.test_right_button)

        info_label = QLabel("Test hardware")
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_label.setFixedHeight(40)
        layoutV.addWidget(info_label)
        layoutV.addItem(layoutH)

        box.setLayout(layoutV)
        return box

    def pat_left(self):
        """Send a pat to the left side of the patstrap"""
        self.server.strength_left = 2

    def pat_right(self):
        """Send a pat to the right side of the patstrap"""
        self.server.strength_right = 2

    def set_patstrap_status(self, status: bool):
        """Set the status of the patstrap connection and update the UI accordingly"""
        if self.prev_patstrap_status != status:
            self.prev_patstrap_status = status
            self.status_hardware_connection.setStyleSheet("color: #29b980; font-size: 30px;" if status else "color: #b94029; font-size: 30px;")

            # Enable or disable the test buttons
            self.test_right_button.setDisabled(not status)
            self.test_left_button.setDisabled(not status)

    def set_vrchat_status(self, status: bool):
        """Set the status of the vrchat connection and update the UI accordingly"""
        if self.prev_vrchat_status != status:
            self.prev_vrchat_status = status
            self.status_vrchat_connection.setStyleSheet("color: #29b980; font-size: 30px;" if status else "color: #b94029; font-size: 30px;")

    def closeEvent(self, _):
        """Stop the server when the window is closed"""
        self.server.shutdown()
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setFixedSize(400, 425)
    window.show()
    sys.exit(app.exec())
