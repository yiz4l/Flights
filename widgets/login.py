import sys, hashlib
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QStackedWidget
from qfluentwidgets import LineEdit, PasswordLineEdit, PushButton, SegmentedWidget, Dialog
from db.database import Database

from models.account import Account
from models.passenger import Passenger

class loginWidget(QWidget):
    login_success = pyqtSignal(Account)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login/Register")
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.title_segmented_widget = SegmentedWidget(self)
        # title_segmented_widget.setText("Login")
        self.stacked_widget = QStackedWidget(self)

        self.login_widget = QWidget()
        self.register_widget = QWidget()


        self.usernameEdit = LineEdit()
        self.usernameEdit.setPlaceholderText("example@example.com")
        self.usernameEdit.setClearButtonEnabled(True)

        self.passwordEdit = PasswordLineEdit()
        self.passwordEdit.setClearButtonEnabled(True)

        self.registerUsernameEdit = LineEdit()
        self.registerUsernameEdit.setPlaceholderText("example@example.com")
        self.registerUsernameEdit.setClearButtonEnabled(True)

        self.registerPasswordEdit = PasswordLineEdit()
        self.registerPasswordEdit.setClearButtonEnabled(True)

        self.nameEdit = LineEdit()
        self.nameEdit.setPlaceholderText("Real Name")
        self.nameEdit.setClearButtonEnabled(True)

        self.idEdit = LineEdit()
        self.idEdit.setPlaceholderText("ID Number")
        self.idEdit.setClearButtonEnabled(True)

        loginButton = PushButton("Login")
        registerButton = PushButton("Register")

        login_widget_layout = QVBoxLayout()
        register_widget_layout = QVBoxLayout()
        login_widget_layout.addWidget(self.usernameEdit)
        login_widget_layout.addWidget(self.passwordEdit)
        login_widget_layout.addWidget(loginButton)

        register_widget_layout.addWidget(self.registerUsernameEdit)
        register_widget_layout.addWidget(self.registerPasswordEdit)
        register_widget_layout.addWidget(self.nameEdit)
        register_widget_layout.addWidget(self.idEdit)
        register_widget_layout.addWidget(registerButton)

        loginButton.clicked.connect(self.on_login_button_click)
        registerButton.clicked.connect(self.on_register_button_click)

        self.login_widget.setLayout(login_widget_layout)
        self.register_widget.setLayout(register_widget_layout)

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        self.stacked_widget.setCurrentIndex(0)

        self.title_segmented_widget.addItem(
            routeKey="login",
            text="Login",
            onClick=lambda: self.stacked_widget.setCurrentWidget(self.login_widget)
        )
        self.title_segmented_widget.addItem(
            routeKey="register",
            text="Register",
            onClick=lambda: self.stacked_widget.setCurrentWidget(self.register_widget)
        )
        self.title_segmented_widget.setCurrentItem("login")

        self.layout.addWidget(self.title_segmented_widget)
        self.layout.addWidget(self.stacked_widget)

        self.setLayout(self.layout)

    def on_login_button_click(self):
        # print(self.usernameEdit.text())
        pwd = Database.query_password(self.usernameEdit.text())
        input_pwd = hashlib.sha256(self.passwordEdit.text().encode('utf-8')).hexdigest()
        if pwd and pwd == input_pwd:
            self.login_success.emit(Database.query_userinfo(self.usernameEdit.text()))
            self.close()
        else:
            print("User not found or wrong password.")

    def on_register_button_click(self):

        pwd = hashlib.sha256(self.registerPasswordEdit.text().encode('utf-8')).hexdigest()
        try:
            if len(self.nameEdit.text()) != 0 and self.validate_id():
                Database.add_user(self.registerUsernameEdit.text(), pwd, self.nameEdit.text(), self.idEdit.text())
                Database.add_passenger(Database.query_userinfo(self.registerUsernameEdit.text()), Passenger(
                    id=self.idEdit.text(),
                    name=self.nameEdit.text(),
                    phone=None
                ))
                self.login_success.emit(Database.query_userinfo(self.registerUsernameEdit.text()))
                self.close()
        except Exception as e:
            print(f"Error: {e}")
            w = Dialog("Error", f"{e}", self)
            if w.exec():
                pass

    def validate_id(self) -> bool:
        if len(self.idEdit.text()) != 18:
            return False

        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_digits = '10X98765432'

        total_sum = sum(int(self.idEdit.text()[i]) * weights[i] for i in range(17))
        check_digit = check_digits[total_sum % 11]

        if self.idEdit.text()[-1] != check_digit:
            return False

        return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = loginWidget()
    w.login_success.connect(lambda x: print(x))
    w.show()
    app.exec()