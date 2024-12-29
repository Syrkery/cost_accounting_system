import sys, sqlite3
from PyQt6 import uic
from PyQt6.QtGui import QPen, QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QTextBrowser, QDateEdit, QComboBox, \
    QTableWidgetItem, QGraphicsScene, QGraphicsView, QGraphicsTextItem
from datetime import datetime
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt


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
            self.problems.append(f'Database error: {str(e)}')
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
            self.problems.append(f'Database error: {str(e)}')
            return

        usern = (username,) not in u_name_check
        mail = (e_mail,) not in email_check
        passw = pass_check(pasw, pasw_rep)

        if usern and mail and passw:
            cur.execute(
                "INSERT INTO Users(username, password, email, created_at) VALUES(?, ?, ?, ?)",
                (username, pasw, e_mail, datetime.now().strftime('%d-%m-%Y'))
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

    def update_transactions(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        transactions = cur.execute("SELECT date, amount, category, type, description FROM Transactions").fetchall()
        con.close()

        self.table.setRowCount(0)
        for row_index, row_data in enumerate(transactions):
            self.table.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

    def Add_transaction(self):
        self.new_tran = New_transaction(self)
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
    def __init__(self, parent):
        try:
            super().__init__()
            self.parent = parent
            uic.loadUi('New_Transaction.ui', self)
            self.tran = self.findChild(QDateEdit, 'date_of_trans')
            self.sum = self.findChild(QTextEdit, 'summ')
            self.categ = self.findChild(QTextEdit, 'category')
            self.ty = self.findChild(QComboBox, 'type')
            self.desc = self.findChild(QTextEdit, 'description')
            self.Close.clicked.connect(self.close)
            self.confirm.clicked.connect(self.cont)
        except Exception as e:
            print(e)

    def close(self):
        self.parent.update_transactions()
        self.close()

    def cont(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        summ = self.sum.toPlainText()
        tran_date = self.tran.date().toString('dd-MM-yyyy')
        category = self.categ.toPlainText()
        if self.ty.currentText() == 'Income':
            type = 'доход'
        else:
            type = 'расход'
        description = self.desc.toPlainText()

        cur.execute(
            "INSERT INTO Transactions(amount, date, category, type, description) VALUES(?, ?, ?, ?, ?)",
            (summ, tran_date, category, type, description)
        )
        con.commit()
        super().close()
        self.parent.update_transactions()


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
        self.graph = self.findChild(QGraphicsView, 'graph')
        self.init_graph()

    def init_graph(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        transactions = cur.execute("SELECT amount, type, date FROM Transactions").fetchall()
        con.close()

        if not transactions:
            return

        balances = []
        dates = []

        total_balance = 0
        for transaction in transactions:
            amount, trans_type, date = transaction
            if trans_type.lower() == 'income':
                total_balance += amount
            elif trans_type.lower() == 'expense':
                total_balance -= amount
            else:
                continue

            balances.append(total_balance)
            dates.append(datetime.strptime(date, '%d-%m-%Y'))

        if not balances or not dates:
            return

        min_date = min(dates)
        max_date = max(dates)
        min_balance = min(balances)
        max_balance = max(balances)

        date_range = (max_date - min_date).days or 1
        balance_range = max_balance - min_balance or 1

        normalized_dates = [(date - min_date).days / date_range * 800 for date in dates]
        normalized_balances = [(balance - min_balance) / balance_range * 400 for balance in balances]

        scene = QGraphicsScene()
        pen = QPen(Qt.GlobalColor.blue)
        pen.setWidth(2)

        x_axis_y = 400 - ((0 - min_balance) / balance_range * 400)
        scene.addLine(0, x_axis_y, 800, x_axis_y, QPen(Qt.GlobalColor.black))

        for i in range(1, len(normalized_dates)):
            scene.addLine(
                normalized_dates[i - 1], 400 - normalized_balances[i - 1],
                normalized_dates[i], 400 - normalized_balances[i],
                pen
            )

        for x, y in zip(normalized_dates, normalized_balances):
            scene.addEllipse(x - 3, 400 - y - 3, 6, 6, pen)

        self.graph.setScene(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = LoginOrRegistration()
    main_window.show()
    sys.exit(app.exec())
