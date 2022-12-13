import sys
import shutil
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QFileDialog, QListWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('books.ui', self)
        self.con = sqlite3.connect("data/library.sqlite")
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.fl = True
        self.bpp = 1
        self.listc = QListWidget()
        self.listtc = QListWidget()
        self.btn.clicked.connect(self.get_list)
        self.addcb.clicked.connect(self.addcat)
        self.delcb.clicked.connect(self.delcat)
        self.allb.clicked.connect(self.get_list)
        self.delcatfilt()
        self.filter()
        self.bp.clicked.connect(self.getpic)
        self.addbb.clicked.connect(self.addbook)
        self.get_list()
        self.delbb.clicked.connect(self.delblist)
        self.pl.clicked.connect(self.plbtocat)
        self.min.clicked.connect(self.minbfromcat)
        self.px = QPixmap('data/contacts.png')
        self.conts = self.px.scaled(260, 260, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.image = QLabel(self)
        self.image.setGeometry(380, 300, 300, 150)
        self.image.setPixmap(self.conts)

    def keyPressEvent(self, e):
        if e.key() == 16777220:
            self.flagger()
            self.get_list()

    def flagger(self):
        self.fl = True

    def getpic(self):
        self.bpp = QFileDialog.getOpenFileName(self, 'Select a file', os.getcwd(), 'Image file (*.jpg *.png)')[0]
        if self.bpp == '':
            self.bpp = 'data/defpic.jpg'

    def minbfromcat(self):
        self.flagger()
        self.listc.clear()
        self.cat = self.filt.currentText()
        if self.cat == 'books':
            return
        self.book_list_cat = self.cur.execute(f"""SELECT * FROM {self.cat}""").fetchall()
        book_list = []
        for i in range(len(self.book_list_cat)):
            z = self.cur.execute(f"""SELECT * FROM books WHERE id = {self.book_list_cat[i][1]}""").fetchall()[0][1]
            book_list.append(z)
        for i in book_list:
            self.listc.addItem(i)
        self.listc.itemClicked.connect(self.minb)
        self.listc.show()

    def minb(self, item):
        if self.fl:
            t = item.text()
            id = self.cur.execute(f"""SELECT id FROM books WHERE name = '{t}'""").fetchall()[0][0]
            for i in range(len(self.book_list_cat)):
                if id == self.book_list_cat[i][1]:
                    id = self.book_list_cat[i][0]
            self.cur.execute(f"""DELETE FROM {self.cat} WHERE id = {id}""")
            self.con.commit()
            self.listc.clear()
            self.listc.close()
            self.fl = False

    def plbtocat(self):
        self.flagger()
        self.listtc.clear()
        self.cat = self.filt.currentText()
        if self.cat == 'books':
            return
        self.book_listt_cat = self.cur.execute(f"""SELECT * FROM {self.cat}""").fetchall()
        ch = []
        for i in self.book_listt_cat:
            ch.append(i[1])
        book_list = []
        z = self.cur.execute(f"""SELECT * FROM books""").fetchall()
        for i in z:
            if i[0] not in ch:
                book_list.append(i[1])
        for i in book_list:
            self.listtc.addItem(i)
        self.listtc.itemClicked.connect(self.plb)
        self.listtc.show()

    def plb(self, item):
        if self.fl:
            t = item.text()
            id = self.cur.execute(f"""SELECT id FROM books WHERE name = '{t}'""").fetchall()[0][0]
            self.cur.execute(f"""INSERT INTO {self.cat} (book_id)
            VALUES ({id})""")
            self.con.commit()
            self.listtc.clear()
            self.listtc.close()
            self.fl = False

    def delblist(self):
        self.list1 = QListWidget()
        book_list = self.cur.execute(f"""SELECT * FROM books""").fetchall()
        for i in book_list:
            self.list1.addItem(i[1])
        self.list1.itemClicked.connect(self.delbook)
        self.list1.show()

    def delbook(self, item):
        self.flagger()
        t = item.text()
        qstn = QMessageBox.question(self, 'Удаление книги', 'Вы действительно хотите удалить эту книгу?')
        if qstn == 16384 and self.fl:
            id = self.cur.execute(f"""SELECT * FROM books WHERE name = '{t}'""").fetchall()
            self.cur.execute(f"""DELETE FROM books
                        WHERE name = '{t}'""")
            tables = self.cur.execute("""SELECT * FROM sqlite_master WHERE type='table'""").fetchall()
            for i in tables:
                if i[1] != 'books' and i[1] != 'sqlite_sequence':
                    self.cur.execute(f"""DELETE FROM {i[1]}
                                WHERE book_id = {id[0][0]}""")
            self.con.commit()
            self.list1.clear()
            self.list1.close()
            self.fl = False

    def addbook(self):
        print(self.bpp)
        if type(self.bpp) != type('str'):
            self.bpp = 'data/defpic.jpg'
        img = self.bpp.split('/')[-1]
        shutil.copyfile(self.bpp, f'data/images/{img}')
        bn = self.bn.text()
        ba = self.ba.text()
        if self.by.text() != '':
            by = int(self.by.text())
        bg = self.bg.text()
        bpn = self.bpn.text()
        if bn == '' or ba == '' or str(by) == '' or bg == '':
            return
        else:
            self.cur.execute(f"""INSERT INTO books (name, author, year, genre, pin, image)
            VALUES ('{bn}', '{ba}', {by}, '{bg}', '{bpn}', '{img}')""")
            self.con.commit()
        self.bn.clear()
        self.ba.clear()
        self.by.clear()
        self.bg.clear()
        self.bpn.clear()
        self.bpp = 1
        self.get_list()

    def filter(self):
        self.filt.clear()
        tables = self.cur.execute("""SELECT * FROM sqlite_master WHERE type='table'""").fetchall()
        filted_tables = []
        filted_tables.append('books')
        for i in range(len(tables) - 1):
            if tables[i + 1][1] not in filted_tables:
                filted_tables.append(tables[i + 1][1])
        self.filted_tables = filted_tables
        self.filt.addItems(filted_tables)

    def delcatfilt(self):
        self.delc.clear()
        tables = self.cur.execute("""SELECT * FROM sqlite_master WHERE type='table'""").fetchall()
        filted_tables = []
        for i in range(len(tables) - 1):
            filted_tables.append(tables[i + 1][1])
        for i in range(5):
            filted_tables.pop(0)
        self.delc.addItems(filted_tables)

    def delcat(self):
        a = ['facorite', 'readed', 'to_read', 'books']
        cat = self.delc.currentText()
        if cat in self.filted_tables and cat not in a:
            self.cur.execute(f"""DROP TABLE {cat}""")
        self.delcatfilt()
        self.filter()

    def addcat(self):
        name = self.addc.text()
        if name not in self.filted_tables and name != '':
            self.cur.execute(f"""CREATE TABLE {name} (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id         REFERENCES books (id) 
                )""")
        self.delcatfilt()
        self.filter()

    def get_list(self):
        self.flagger()
        self.list.clear()
        t = self.search.text()
        cat = self.filt.currentText()
        if cat == 'books':
            book_list = self.cur.execute(f"""SELECT * FROM books WHERE id""").fetchall()
        else:
            books_id = self.cur.execute(f"""SELECT * FROM {cat}""").fetchall()
            book_list = []
            for i in books_id:
                book_list.append(self.cur.execute(f"""SELECT * FROM books WHERE id = '{i[1]}'""").fetchall()[0])
        for i in book_list:
            if t.lower() in i[1].lower() or t.lower() in i[2].lower():
                self.list.addItem(i[1])
        self.list.itemClicked.connect(self.get_info)

    def get_info(self, item):
        z = item.text()
        book_info = self.cur.execute(f"""SELECT * FROM books WHERE name = '{z}'""").fetchall()[0]
        bname = book_info[1]
        bauth = str(book_info[2]) + '\n' + str(book_info[4]) + ' ' + str(book_info[3]) + ' года'
        bpin = str(book_info[5])
        bimg = 'data/images/' + book_info[6]
        if bpin == 'None' or bpin == '':
            bpin = '*к этой книге нет заметки*'
        if self.fl:
            self.iw = Window2(bname, bauth, bimg, bpin)
            self.iw.show()
            self.fl = False


class Window2(QWidget):
    def __init__(self, b1, b2, b3, b4):
        super(Window2, self).__init__()
        self.setGeometry(650, 100, 600, 930)
        self.setWindowTitle(b1)

        self.n = QLabel(self)
        self.n.setText(b1)
        self.f = self.n.font()
        self.f.setPointSize(34)
        self.n.setFont(self.f)
        self.n.setGeometry(20, 0, 600, 80)

        self.a = QLabel(self)
        self.a.setText(b2)
        self.f1 = self.a.font()
        self.f1.setPointSize(16)
        self.a.setFont(self.f1)
        self.a.setGeometry(20, 70, 600, 65)

        self.p = QLabel(self)
        self.p.setText(b4)
        self.f2 = self.p.font()
        self.f2.setPointSize(12)
        self.p.setFont(self.f2)
        self.p.setGeometry(20, 115, 600, 65)

        self.px = QPixmap(b3)
        self.p = self.px.scaled(700, 700, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.image = QLabel(self)
        self.image.move(20, 175)
        self.image.setPixmap(self.p)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
