import sys, sqlite3
from PyQt6 import uic
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QTextBrowser, QDateEdit, QComboBox, \
    QTableWidgetItem, QGraphicsScene, QGraphicsView
from datetime import datetime, timedelta
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
        transactions = cur.execute("SELECT id, date, amount, category, type, description FROM Transactions").fetchall()
        con.close()

        self.table.setRowCount(0)
        for row_index, row_data in enumerate(transactions):
            self.table.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

        self.table.setSortingEnabled(True)

    def update_transactions(self):
        self.load_data()

    def Add_transaction(self):
        self.new_tran = New_transaction(self)
        self.new_tran.show()

    def Edit_transaction(self):
        self.edit_tran = Edit()
        self.edit_tran.show()

    def Delete(self):
        self.del_tran = Delete(self)
        self.del_tran.show()

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
            """INSERT INTO Transactions(amount, date, category, type, description) VALUES(?, ?, ?, ?, ?)""",
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
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('Delete.ui', self)
        self.confirm.clicked.connect(self.delete_transaction)
        self.cancel.clicked.connect(self.close)

    def delete_transaction(self):
        selected_row = self.parent.table.currentRow()
        if selected_row == -1:
            return

        transaction_id = self.parent.table.item(selected_row, 0).text()
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM Transactions WHERE id = ?", (transaction_id,))
            con.commit()
        except sqlite3.Error as e:
            print(f"Error while deleting: {e}")
        finally:
            con.close()
            self.parent.update_transactions()
            self.close()


class Report(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            uic.loadUi('REPORTS.ui', self)
            self.graph = self.findChild(QGraphicsView, 'graph')
            self.init_graph()
        except Exception as e:
            print(e)

    def init_graph(self):
        con = sqlite3.connect('cost accounting system.sqlite')
        cur = con.cursor()
        transactions = cur.execute("SELECT amount, date, type FROM Transactions").fetchall()
        con.close()

        dates = []
        amounts = []
        types = []

        for transaction in transactions:
            amount, date, type_ = transaction
            dates.append(datetime.strptime(date, '%d-%m-%Y'))
            amounts.append(float(amount))
            types.append(type_)

        if not dates or not amounts:
            return

        min_date = min(dates)
        max_date = max(dates)
        min_amount = min(amounts)
        max_amount = max(amounts)

        date_range = (max_date - min_date).days or 1
        amount_range = max_amount - min_amount or 1

        normalized_dates = [(date - min_date).days / date_range * 800 for date in dates]
        normalized_amounts = [(amount - min_amount) / amount_range * 400 for amount in amounts]

        scene = QGraphicsScene()
        pen = QPen(Qt.GlobalColor.blue)
        pen.setWidth(2)

        self.add_axes(scene, min_date, max_date, min_amount, max_amount)

        for i in range(1, len(normalized_dates)):
            scene.addLine(
                normalized_dates[i - 1], 400 - normalized_amounts[i - 1],
                normalized_dates[i], 400 - normalized_amounts[i],
                pen
            )

        for x, y, type_ in zip(normalized_dates, normalized_amounts, types):
            pen.setColor(QColor('red') if type_ == "expense" else QColor('green'))
            scene.addEllipse(x - 3, 400 - y - 3, 6, 6, pen)

        self.graph.setScene(scene)

    def add_axes(self, scene, min_date, max_date, min_amount, max_amount):
        pen = QPen(Qt.GlobalColor.black)
        scene.addLine(0, 400, 800, 400, pen)
        scene.addText("Date", QFont('Arial', 10)).setPos(800, 380)

        scene.addLine(0, 0, 0, 400, pen)
        scene.addText("Amount", QFont('Arial', 10)).setPos(10, 10)

        for i in range(0, 5):
            y_pos = i * 80
            scene.addText(str(round(min_amount + (max_amount - min_amount) * (i / 4), 2)),
                            QFont('Arial', 8)).setPos(-50, 400 - y_pos)

        for i in range(0, 6):
            x_pos = i * 160
            current_date = min_date + timedelta(days=(max_date - min_date).days * i // 5)
            scene.addText(current_date.strftime('%d-%m-%Y'), QFont('Arial', 8)).setPos(x_pos, 410)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = LoginOrRegistration()
    main_window.show()
    sys.exit(app.exec())
