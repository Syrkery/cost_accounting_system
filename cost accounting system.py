import sys, sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QTextBrowser, QDateEdit, QComboBox
from datetime import datetime


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
        uname = mail = passw = False
        username = self.user_name.toPlainText()
        e_mail = self.email.toPlainText()
        pasw = self.password.text()

        try:
            u_name_check = cur.execute("SELECT username FROM Users").fetchall()
            email_check = cur.execute("SELECT email FROM Users WHERE username = ?", (username,)).fetchall()
            pasw_check = cur.execute("SELECT password FROM Users WHERE username = ?", (username,)).fetchall()
        except sqlite3.Error as e:
            self.problems.append(f"Database error: {str(e)}")
            return
        if (username,) in u_name_check:
            uname = True
        else:
            self.problems.append('Invalid username')
            self.user_name.clear()

        if (e_mail,) in email_check:
            mail = True
        else:
            self.problems.append('Invalid e-mail')
            self.email.clear()

        if (pasw,) in pasw_check:
            passw = True
        else:
            self.problems.append('Invalid password')
            self.password.clear()

        if uname and mail and passw:
            self.problems.append('OK!')
            self.open_main_window()
        con.close()

    def open_main_window(self):
        self.main_window = Main()
        self.main_window.show()
        self.close()

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
        self.problems = self.findChild(QTextBrowser, 'problems')
        self.OK.clicked.connect(self.cont)

    def cont(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        username = self.user_name.toPlainText()
        e_mail = self.email.toPlainText()
        pasw = self.password.text()
        pasw_rep = self.password_repeat.text()

        def pass_check(parol, repeat):
            up = sym = num = 0
            if len(parol) < 8:
                self.problems.append('Length should ba at least 8 symbols')
            if parol != repeat:
                self.problems.append("Passwords aren't matching")
            for i in parol:
                if i.isdigit():
                    num += 1
                elif i.isupper():
                    up += 1
                elif not i.isalnum():
                    sym += 1
            if up < 1:
                self.problems.append('There should be at least 1 upper character')
            if sym < 1:
                self.problems.append('There should be at least 1 special symbol')
            if num < 1:
                self.problems.append('There should be at least 1 number')
            return all([len(parol) >= 8, parol == repeat, up >= 1, sym >= 1, num >= 1])

        try:
            u_name_check = cur.execute("SELECT username FROM Users").fetchall()
            email_check = cur.execute("SELECT email FROM Users").fetchall()
        except sqlite3.Error as e:
            self.problems.append(f"Database error: {str(e)}")
            return

        usern = (username,) not in u_name_check
        mail = (e_mail,) not in email_check
        passw = pass_check(pasw, pasw_rep)

        if usern and mail and passw:
            cur.execute(
                "INSERT INTO Users(username, password, email, created_at) VALUES(?, ?, ?, ?)",
                (username, pasw, e_mail, datetime.now().strftime("%d-%m-%Y"))
            )
            con.commit()
            self.problems.append('OK!')
            self.open_main_window()
        con.close()

    def open_main_window(self):
        self.main_window = Main()
        self.main_window.show()
        self.close()

    def go_back(self):
        self.parent.show()
        self.close()


from PyQt6.QtWidgets import QTableWidgetItem

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Main_window.ui', self)
        self.add_transaction.clicked.connect(self.Add_transaction)
        self.edit_transaction.clicked.connect(self.Edit_transaction)
        self.Del.clicked.connect(self.Delete)
        self.Back.clicked.connect(self.go_back)
        self.GetRep.clicked.connect(self.rep)
        self.load_data()

    def load_data(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        transactions = cur.execute("SELECT date, amount, category, type, description FROM Transactions").fetchall()
        con.close()

        try:
            self.table.setRowCount(0)
            for row_index, row_data in enumerate(transactions):
                self.table.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))
        except Exception as e:
            print(e)

    def Add_transaction(self):
        self.new_tran = New_transaction()
        self.new_tran.show()

    def Edit_transaction(self):
        self.edit_tran = Edit()
        self.edit_tran.show()

    def Delete(self):
        self.edit_tran = Delete()
        self.edit_tran.show()

    def rep(self):
        self.rep = Report()
        self.rep.show()

    def go_back(self):
        self.first = LoginOrRegistration()
        self.first.show()
        self.close()



class New_transaction(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('New_Transaction.ui', self)
        tran_date = self.findChild(QDateEdit, 'date_of_trans')
        summ = self.findChild(QTextEdit, 'summ')
        category = self.findChild(QTextEdit, 'category')
        type = self.findChild(QComboBox, 'type')
        description = self.findChild(QTextEdit, 'description')
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        cur.execute(
            """INSERT INTO Transaction(amount, date, category, type, description) VALUES(?, ?, ?, ?, ?)""",
        (summ, tran_date, category, type, description))


class Edit(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Edit_Transaction.ui', self)


class Delete(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Delete.ui', self)


class Report(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('REPORTS.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = LoginOrRegistration()
    main_window.show()
    sys.exit(app.exec())
