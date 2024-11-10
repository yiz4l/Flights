import sys
from PyQt6.QtWidgets import QApplication
from db.database import Database
from models.account import Account
from widgets.login import loginWidget
from widgets.window import Window

if __name__ == '__main__':
    Database.create_tables()
    app = QApplication(sys.argv)
    login_window = loginWidget()

    def handle_login_success(account: Account):
        print("Login successful!")

        # 创建并显示主窗口
        main_window = Window(account)
        main_window.show()

        # 关闭登录窗口
        login_window.close()

    login_window.login_success.connect(handle_login_success)

    login_window.show()
    app.exec()
