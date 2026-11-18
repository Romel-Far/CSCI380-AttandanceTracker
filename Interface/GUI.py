import sys
import os
from datetime import datetime

import cv2
from DatabaseConnection import get_connection, record_attendance, session_attendance_list

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFormLayout, QLineEdit,
    QPlainTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap

# import the qr files from the other folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from QR.qr_generator import (
    create_student_qr_data,
    generate_qr_image,
    parse_student_qr_data,
    pil_image_to_qpixmap,
)
from QR.qr_scanner import ScanCooldown, draw_qr_box, scan_frame


# test accounts for now
TEST_ACCOUNTS = {
    "Student": ("abc", "123"),
    "Professor": ("abc", "123"),
    "Admin": ("abc", "123"),
}


def check_credentials(username, password, role):
    """Return True if the username/password match the test account for this role."""
    return TEST_ACCOUNTS.get(role) == (username, password)


class RolePage(QWidget):
    role_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        title = QLabel("Please select account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(12)
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(16)

        for role in ("Student", "Professor", "Admin"):
            button = QPushButton(role)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda _, r=role: self.role_selected.emit(r))
            layout.addWidget(button)

        layout.addStretch()


class LoginPage(QWidget):
    back_requested = pyqtSignal()
    login_succeeded = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.role = ""

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setStyleSheet("color: #c0392b;")

        back_button = QPushButton("Back")
        login_button = QPushButton("Log in")
        login_button.setDefault(True)

        buttons = QHBoxLayout()
        buttons.addWidget(back_button)
        buttons.addWidget(login_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(12)
        layout.addStretch()
        layout.addWidget(self.title)
        layout.addSpacing(16)
        layout.addLayout(form)
        layout.addWidget(self.message)
        layout.addLayout(buttons)
        layout.addStretch()

        back_button.clicked.connect(self.back_requested.emit)
        login_button.clicked.connect(self.attempt_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.attempt_login)

    def set_role(self, role):
        self.role = role
        self.title.setText(f"{role} Login")
        self.username_input.clear()
        self.password_input.clear()
        self.message.clear()
        self.username_input.setFocus()

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.message.setText("Enter your username and password.")
            return

        if check_credentials(username, password, self.role):
            self.login_succeeded.emit(username, self.role)
        else:
            self.message.setText("Incorrect username or password.")
            self.password_input.clear()
            self.password_input.setFocus()


class HomePage(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.welcome = QLabel()
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome.setStyleSheet("font-size: 18px;")

        logout_button = QPushButton("Log out")
        logout_button.clicked.connect(self.handle_logout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.addWidget(self.welcome)
        layout.addSpacing(10)

        # student qr code generator below
        self.student_box = QWidget()
        s_layout = QVBoxLayout(self.student_box)
        s_form = QFormLayout()
        self.s_id_input = QLineEdit("1")
        self.s_name_input = QLineEdit("James Wilson")
        s_form.addRow("Student ID:", self.s_id_input)
        s_form.addRow("Name:", self.s_name_input)
        
        btn_gen_qr = QPushButton("Generate My QR Badge")
        btn_gen_qr.clicked.connect(self.generate_qr)
        self.qr_label = QLabel("QR will show here")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(180, 180)
        
        btn_save_qr = QPushButton("Save QR Image")
        btn_save_qr.clicked.connect(self.save_qr)
        self.qr_status = QLabel("")

        s_layout.addLayout(s_form)
        s_layout.addWidget(btn_gen_qr)
        s_layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(btn_save_qr)
        s_layout.addWidget(self.qr_status)
        layout.addWidget(self.student_box)

        # this is where the webcam runs
        self.prof_box = QWidget()
        p_layout = QVBoxLayout(self.prof_box)

        self.cam_status = QLabel("Camera is idle")
        cam_btns = QHBoxLayout()
        self.btn_cam_start = QPushButton("Start Camera")
        self.btn_cam_stop = QPushButton("Stop Camera")
        self.btn_cam_stop.setEnabled(False)
        self.btn_cam_start.clicked.connect(self.start_camera)
        self.btn_cam_stop.clicked.connect(self.stop_camera)
        cam_btns.addWidget(self.btn_cam_start)
        cam_btns.addWidget(self.btn_cam_stop)

        self.cam_label = QLabel("Camera Off")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_label.setFixedSize(320, 220)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(80)

        p_layout.addWidget(self.cam_status)
        p_layout.addLayout(cam_btns)
        p_layout.addWidget(self.cam_label, alignment=Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(QLabel("Today's Attendance:"))
        p_layout.addWidget(self.log_box)
        layout.addWidget(self.prof_box)

        # admin box just to see who checked in
        self.admin_box = QWidget()
        a_layout = QVBoxLayout(self.admin_box)
        self.admin_log = QPlainTextEdit()
        self.admin_log.setReadOnly(True)
        a_layout.addWidget(QLabel("Session Check-in Records:"))
        a_layout.addWidget(self.admin_log)
        layout.addWidget(self.admin_box)

        layout.addSpacing(10)
        layout.addWidget(logout_button)

        # stuff for the camera feed
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_camera_frame)
        self.cooldown = ScanCooldown(cooldown_seconds=4)
        self.saved_pil_qr = None

    def set_user(self, username, role):
        self.welcome.setText(f"Welcome, {username} ({role})")
        self.student_box.setVisible(role == "Student")
        self.prof_box.setVisible(role == "Professor")
        self.admin_box.setVisible(role == "Admin")

        if role == "Student":
            self.s_name_input.setText(username if username != "abc" else "James Wilson")
        elif role == "Admin":
            self.admin_log.clear()
            for item in session_attendance_list:
                self.admin_log.appendPlainText(f"{item['time']} - {item['student_name']} (ID: {item['student_id']})")

    # makes student qr code
    def generate_qr(self):
        try:
            s_id = int(self.s_id_input.text().strip())
            s_name = self.s_name_input.text().strip()
            text = create_student_qr_data(s_id, s_name)
            self.saved_pil_qr = generate_qr_image(text)
            pix = pil_image_to_qpixmap(self.saved_pil_qr)
            self.qr_label.setPixmap(pix.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio))
            self.qr_status.setText(f"Generated QR for {s_name}!")
        except Exception as e:
            self.qr_status.setText(f"Error: {e}")

    # saves the qr code image to file
    def save_qr(self):
        if self.saved_pil_qr:
            filename = f"qr_student_{self.s_id_input.text().strip()}.png"
            self.saved_pil_qr.save(filename)
            self.qr_status.setText(f"Saved to {filename}")

    # turn on camera
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.cam_status.setText("Could not open camera")
            return
        self.timer.start(30)
        self.btn_cam_start.setEnabled(False)
        self.btn_cam_stop.setEnabled(True)
        self.cam_status.setText("Camera scanning for QR...")

    # turn off camera
    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_cam_start.setEnabled(True)
        self.btn_cam_stop.setEnabled(False)
        self.cam_label.setText("Camera Off")
        self.cam_status.setText("Camera is idle")

    # read frame, scan qr, and mark present
    def read_camera_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        # check for qr
        data, points = scan_frame(frame)
        if points is not None:
            draw_qr_box(frame, points)

        if data:
            info = parse_student_qr_data(data)
            if info and self.cooldown.can_scan(info["student_id"]):
                # connect here twin
                entry = record_attendance(info["student_id"], info["student_name"])
                self.log_box.appendPlainText(f"Checked in: {entry['student_name']} (ID: {entry['student_id']})")
                self.cam_status.setText(f"Recorded: {entry['student_name']}!")

        # display frame on screen
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(qimg).scaled(320, 220, Qt.AspectRatioMode.KeepAspectRatio))

    def handle_logout(self):
        self.stop_camera()
        self.logout_requested.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance Tracker")
        self.resize(460, 480)

        self.role_page = RolePage()
        self.login_page = LoginPage()
        self.home_page = HomePage()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.role_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.home_page)
        self.setCentralWidget(self.stack)

        self.role_page.role_selected.connect(self.show_login)
        self.login_page.back_requested.connect(self.show_roles)
        self.login_page.login_succeeded.connect(self.show_home)
        self.home_page.logout_requested.connect(self.show_roles)

    def show_roles(self):
        self.resize(440, 360)
        self.stack.setCurrentWidget(self.role_page)

    def show_login(self, role):
        self.resize(440, 360)
        self.login_page.set_role(role)
        self.stack.setCurrentWidget(self.login_page)

    def show_home(self, username, role):
        self.resize(460, 500)
        self.home_page.set_user(username, role)
        self.stack.setCurrentWidget(self.home_page)

    def closeEvent(self, event):
        self.home_page.stop_camera()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
