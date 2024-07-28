from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from index import MainApp
from conf import api


login_ui, _ = loadUiType('login.ui')


class LoginWindow(QWidget, login_ui):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        self.login_label.setAlignment(Qt.AlignCenter)
        self.submit_btn.clicked.connect(self.handle_login)
        self.main_window = None
      
        

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        global api

        if api.login(username, password):
            self.accept_login()

        else:
            QMessageBox.warning(self, 'Error', 'Bad user or password')
        

    def accept_login(self):
        self.main_window = MainApp()
        self.main_window.show()
        self.close()
        