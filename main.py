import sqlite3

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QTableWidget, QStatusBar, QDialog, \
    QMessageBox, QInputDialog


class TitleException(Exception):
    pass


class YearException(Exception):
    pass


class DurationException(Exception):
    pass


def check(sort, roast, description, price, grains_or_ground):
    if len(sort) == 0:
        raise TitleException('Заполните сорт')
    if len(roast) == 0:
        raise YearException('Заполните прожарку')
    if len(description) == 0:
        raise DurationException('Заполните описание')
    if int(price) < 0:
        raise YearException('Неверная цена')
    if int(grains_or_ground) not in (0, 1):
        raise DurationException('Молотый или нет?')


def check_genres(title):
    if len(title) == 0:
        raise TitleException('Заполните название жанра')


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('coffee.db')
        self.cursor = self.connection.cursor()

    def get_roasts(self):
        res = self.cursor.execute('''SELECT DISTINCT roast_name FROM roast''').fetchall()
        return res

    def get_sorts(self):
        res = self.cursor.execute('''SELECT DISTINCT sort_name FROM sort''').fetchall()
        return res

    def get_all_cofee(self):
        res = self.cursor.execute('''SELECT c.id, r.roast_name, s.sort_name, c.description, c.price, c.grains_or_ground FROM coffee c
                                     JOIN roast r on r.roast_id = c.roast_id
                                     JOIN sort s on s.sort_id = c.sort_id''').fetchall()

        return res

    def get_all_genres(self):
        res = self.cursor.execute('''SELECT * FROM genres
                                     ORDER BY genres.id DESC''').fetchall()

        return res

    def insert_coffee(self, sort_id, roast_id, description, price, grains_or_ground):
        self.cursor.execute('''INSERT INTO coffee(sort_id, roast_id, description, price, grains_or_ground)
               VALUES((SELECT sort_id FROM sort WHERE sort_name = ?),
                      (SELECT roast_id FROM roast WHERE roast_name = ?), ?, ?, ?)''', (sort_id, roast_id, description, price, grains_or_ground))

        self.connection.commit()

    def get_note(self, id):
        res = self.cursor.execute('''SELECT c.description, c.price, (SELECT r.roast_name FROM roast r WHERE r.roast_id = c.roast_id), c.grains_or_ground,
                                                                    (SELECT s.sort_name FROM sort s WHERE s.sort_id = c.sort_id)
                                     FROM coffee c
                                     WHERE id = ?''', (id,)).fetchall()

        return res

    def update_coffee(self, sort_id, roast_id, description, price, grains_or_ground, id):
        self.cursor.execute('''UPDATE coffee
SET sort_id = (SELECT sort_id FROM sort WHERE sort_name = ?),
    roast_id = (SELECT roast_id FROM roast WHERE roast_name = ?),
    description = ?, price = ?, grains_or_ground = ?
WHERE id = ?''', (sort_id, roast_id, description, price, grains_or_ground, id))
        self.connection.commit()

    def delete_films(self, ids):
        self.cursor.execute("DELETE FROM films WHERE id IN (" + ", ".join(
            '?' * len(ids)) + ")", ids)

        self.connection.commit()

    def insert_genre(self, genre):
        self.cursor.execute('''INSERT INTO genres(title) VALUES (?)''', (genre,))

        self.connection.commit()

    def update_genre(self, title, id):
        self.cursor.execute('''UPDATE genres
                               SET title = ?
                               WHERE id = ?''', (title, id))

    def delete_genres(self, ids):
        self.cursor.execute("DELETE FROM genres WHERE id IN (" + ", ".join(
            '?' * len(ids)) + ")", ids)

        self.connection.commit()


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('main.ui', self)

        self.temp_id = 0
        self.initUI()

    def update_table_films(self):
        table_films = data_base.get_all_cofee()

        for i, elem in enumerate(table_films):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


    def initUI(self):
        table_films = data_base.get_all_cofee()

        self.pushButton.clicked.connect(self.on_click_new)
        self.pushButton_2.clicked.connect(self.on_click_edit)
        self.pushButton_3.clicked.connect(self.on_click_delete)

        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Обжарка", "Сорт", "Описание", "Стоимость", "Молотый"])
        self.tableWidget.setRowCount(len(table_films))

        self.update_table_films()

    def on_click_new(self):
        self.dialog_new = DialogNew(self)
        self.dialog_new.exec_()

    def on_click_edit(self):
        self.dialog_edit = DialogEdit(self)
        if len([i.row() for i in self.tableWidget.selectedItems()]) == 1:
            self.dialog_edit.exec_()
        else:
            self.statusBar().showMessage('Выделите 1 запись :)')

    def on_click_delete(self):
        # Получаем список элементов без повторов и их id
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        # Спрашиваем у пользователя подтверждение на удаление элементов
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        # Если пользователь ответил утвердительно, удаляем элементы.
        # Не забываем зафиксировать изменения
        if valid == QMessageBox.Yes:
            data_base.delete_films(ids)

            self.update_table_films()


class DialogNew(QDialog):
    def __init__(self, parent):
        super(DialogNew, self).__init__()
        self.parent = parent
        uic.loadUi('dialog_film.ui', self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.on_click)

        for i in data_base.get_roasts():
            self.comboBox.addItem(i[0])

        for i in data_base.get_sorts():
            self.comboBox_2.addItem(i[0])

    def on_click(self):
        description = self.lineEdit.text()
        price = self.lineEdit_4.text()
        roast = self.comboBox.currentText()
        sort = self.comboBox_2.currentText()
        grains_or_ground = self.checkBox.checkState()
        grains_or_ground = 1 if grains_or_ground == 2 else 0
        try:
            check(sort, roast, description, price, grains_or_ground)
            print(sort, roast, description, price, grains_or_ground)
            data_base.insert_coffee(sort, roast, description, price, grains_or_ground)
            self.hide()

            table = data_base.get_all_cofee()
            for i, elem in enumerate(table):
                for j, val in enumerate(elem):
                    self.parent.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))


        except Exception as e:
            print(e)
            self.label_5.setText(str(e))


class DialogEdit(QDialog):
    def __init__(self, parent):
        super(DialogEdit, self).__init__()
        self.parent = parent
        uic.loadUi('dialog_film.ui', self)
        self.initUI()

    def initUI(self):
        res = [i.row() for i in self.parent.tableWidget.selectedItems()]
        self.id = self.parent.tableWidget.item(*res, 0).text()
        temp_res = data_base.get_note(self.id)[0]
        print(temp_res)

        self.lineEdit.setText(temp_res[0])
        self.lineEdit_4.setText(str(temp_res[1]))
        for i in data_base.get_roasts():
            self.comboBox.addItem(i[0])

        for i in data_base.get_sorts():
            self.comboBox_2.addItem(i[0])

        self.comboBox.setCurrentText(temp_res[2])
        self.comboBox_2.setCurrentText(temp_res[4])
        if temp_res[3] == 1:
            self.checkBox.setChecked(True)

        self.label_5.setText('Редактирование записи')

        self.pushButton.clicked.connect(self.on_click)

    def on_click(self):
        description = self.lineEdit.text()
        price = self.lineEdit_4.text()
        roast = self.comboBox.currentText()
        sort = self.comboBox_2.currentText()
        grains_or_ground = self.checkBox.checkState()
        grains_or_ground = 1 if grains_or_ground == 2 else 0

        try:
            check(sort, roast, description, price, grains_or_ground)
            data_base.update_coffee(sort, roast, description, price, grains_or_ground, self.id)
            self.hide()
            table = data_base.get_all_cofee()
            for i, elem in enumerate(table):
                for j, val in enumerate(elem):
                    self.parent.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        except Exception as e:
            print(e)
            self.label_5.setText(str(e))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    data_base = DataBase()
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
