import sys, sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QTextBrowser


class LoginOrRegistration(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Login or registraation.ui', self)
        self.LOGIN.clicked.connect(self.open_login_window)
        self.REGISTRATION.clicked.connect(self.open_register_window)

    def open_login_window(self):
        self.login_window = Login(self)
        self.login_window.show()
        self.close()

    def open_register_window(self):
        self.register_window = Register(self)
        self.register_window.show()
        self.close()


class Login(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('Login.ui', self)
        self.Back.clicked.connect(self.go_back)
        self.user_name = self.findChild(QTextEdit, 'user_name')
        self.email = self.findChild(QTextEdit, 'email')
        self.password = self.findChild(QLineEdit, 'password')
        self.problems = self.findChild(QTextBrowser, 'problems')
        self.OK.clicked.connect(self.cont)

    def cont(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        u_name_check = cur.execute("""Select username FROM Users""").fetchall()
        email_check = cur.execute("""SELECT email FROM Users""").fetchall()
        pasw_ckeck = cur.execute("""SELECT password FROM Users""").fetchall()
        username = self.user_name.toPlainText()
        e_mail = self.email.toPlainText()
        pasw = self.password.text()

        if username in u_name_check:
            print(1)
        else:
            self.problems.append('Invalid username')
            self.user_name.clear()
        if e_mail in email_check:
            print(1)
        else:
            self.problems.append('Invalid e-mail')
            self.email.clear()
        if pasw in pasw_ckeck:
            print(1)
        else:
            self.problems.append('Invalid password')
            self.password.clear()

    def go_back(self):
        self.parent.show()
        self.close()


class Register(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('Register.ui', self)
        self.Back.clicked.connect(self.go_back)
        self.user_name = self.findChild(QTextEdit, 'user_name')
        self.email = self.findChild(QTextEdit, 'email')
        self.password = self.findChild(QLineEdit, 'password')
        self.password_repeat = self.findChild(QLineEdit, 'password_repeat')
        self.OK.clicked.connect(self.cont)

    def cont(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        usern = False
        mail = False
        pasw = False
        u_name_check = cur.execute("""SELECT username FROM Users""").fetchall()
        email_check = cur.execute("""SELECT email FROM Users""").fetchall()
        pasw_ckeck = cur.execute("""SELECT password FROM Users""").fetchall()
        username = self.user_name.toPlainText()
        e_mail = self.email.toPlainText()
        pasw = self.password.text()
        pasw_rep = self.password_repeat.text()

        if username not in u_name_check:
            usern = True
        else:
            self.problems.append('Invalid username')
            self.user_name.clear()
        if e_mail not in email_check:
            mail = True
        else:
            self.problems.append('Invalid e-mail')
            self.email.clear()
        if pasw not in pasw_ckeck and pasw == pasw_rep and len(pasw) >= 7:
            pasw = True
        else:
            self.problems.append('Invalid password')
            self.password.clear()
            if pasw != pasw_rep:
                self.password_repeat.clear()

        if usern and mail and pasw:
            cur.execute("""INSERT INTO Users(username, password, email, created_at) VALUES(?, ?, ?, ?)""",
                        (username, pasw, e_mail, ''))
            con.commit()

    def go_back(self):
        self.parent.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = LoginOrRegistration()
    main_window.show()
    sys.exit(app.exec())
