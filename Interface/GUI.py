import sys
from DatabaseConnection import get_connection
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGridLayout, QSizePolicy, QTabWidget, QPushButton,
    QScrollArea, QPlainTextEdit, QStackedWidget, QTabBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton,
)

# Temporary hardcoded logins for testing
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
    login_succeeded = pyqtSignal(str, str)  # username, role

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
        logout_button.clicked.connect(self.logout_requested.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.addStretch()
        layout.addWidget(self.welcome)
        layout.addSpacing(16)
        layout.addWidget(logout_button)
        layout.addStretch()

    def set_user(self, username, role):
        self.welcome.setText(f"Welcome, {username} ({role})")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(420, 340)

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
        self.stack.setCurrentWidget(self.role_page)

    def show_login(self, role):
        self.login_page.set_role(role)
        self.stack.setCurrentWidget(self.login_page)

    def show_home(self, username, role):
        self.home_page.set_user(username, role)
        self.stack.setCurrentWidget(self.home_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())