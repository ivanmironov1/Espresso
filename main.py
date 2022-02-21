import sqlite3

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QTableWidget, QStatusBar, QDialog, \
    QMessageBox, QInputDialog


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('coffee.db')
        self.cursor = self.connection.cursor()


    def get_all_films(self):
        res = self.cursor.execute('''SELECT c.id, r.roast_name, s.sort_name, c.description, c.price, c.grains_or_ground FROM coffee c
                                     JOIN roast r on r.roast_id = c.roast_id
                                     JOIN sort s on s.sort_id = c.sort_id''').fetchall()

        return res


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('main.ui', self)

        self.temp_id = 0
        self.initUI()


    def update_table_films(self):
        table_films = data_base.get_all_films()

        for i, elem in enumerate(table_films):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


    def initUI(self):
        table_films = data_base.get_all_films()

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Год", "Жанр", "Продолжительность"])
        self.tableWidget.setRowCount(len(table_films))

        self.update_table_films()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    data_base = DataBase()
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
