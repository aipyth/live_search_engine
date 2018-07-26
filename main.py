from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy
import csv

from tableObj import Table

class SearchField(QVBoxLayout):
    def __init__(self, parent=None):
        QVBoxLayout.__init__(self, parent)

        self.ParamComboBox = QComboBox()
        self.ParamInput = QLineEdit()

        self.addWidget(self.ParamComboBox)
        self.addWidget(self.ParamInput)

    def add_headers_into_cb(self, content):
        for item in content:
            self.ParamComboBox.addItem(item)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowFlags(Qt.Window)
        self.resize(800, 450)

        self.SearchFields = []

        self.SearchButton = QPushButton('Search')
        self.SearchButton.clicked.connect(self.search_in)

        self.OpenCSVButton = QPushButton('Open CSV')
        self.OpenCSVButton.clicked.connect(self.openCSV)

        self.ResultArea = QTableView()

        self.MainSearchField = SearchField()
        self.SubSearchField = SearchField()
        self.SearchFields.append(self.MainSearchField)
        self.SearchFields.append(self.SubSearchField)

        self.ButtonBox = QVBoxLayout()
        self.ButtonBox.addWidget(self.OpenCSVButton)
        self.ButtonBox.addWidget(self.SearchButton)

        self.SearchBox = QHBoxLayout()
        self.SearchBox.addLayout(self.MainSearchField)
        self.SearchBox.addLayout(self.ButtonBox)
        self.SearchBox.addLayout(self.SubSearchField)
        self.SearchBox.addSpacing(8)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.addLayout(self.SearchBox)
        self.MainLayout.addSpacing(10)
        self.MainLayout.addWidget(self.ResultArea)
        self.setLayout(self.MainLayout)

        # self.openRecent()

    def add_headers_into_cbs(self, SearchBox_items, ParamBox_items):
        for item in SearchBox_items:
            self.SearchComboBox.addItem(item)
        for item in ParamBox_items:
            self.ParamComboBox.addItem(item)
        return True

    def search_in(self):
        self.thread = SearchThread(self, self.CSV)
        self.thread.searchdone.connect(self.setItemModel, Qt.QueuedConnection )
        self.thread.start()

    def setItemModel(self, content):
        item_model = QStandardItemModel(parent=self)
        for row in content:
            row_items = []
            for item in row:
                it = QStandardItem(item)
                row_items.append(it)
            item_model.appendRow(row_items)
        item_model.setHorizontalHeaderLabels(self.CSV.Header)
        self.ResultArea.setModel(item_model)
        with open('recent.info', 'w') as r:
            r.write(self.file)

    def getFileName(self):
        file_obj = QFileDialog.getOpenFileName(parent=self, caption="Open CSV",
                                        filter="CSV (*.csv)")
        return file_obj[0]

    def openCSV(self, file=None):
        self.file = file
        if not self.file:
            self.file = self.getFileName()
        self.CSV = Table(self.file)
        for field in self.SearchFields:
            field.add_headers_into_cb(self.CSV.Header)
        self.setItemModel(self.CSV.Table)

    def openRecent(self):
        try:
            with open('recent.info', 'r') as r:
                file = r.read()
            self.openCSV(file)
        except FileNotFoundError:
            return


class SearchThread(QThread):
    searchdone = pyqtSignal(numpy.ndarray)
    def __init__(self, window, table_obj, parent=None):
        QThread.__init__(self, parent)

        self.table_obj = table_obj
        self.table = self.table_obj.Table
        self.window = window

        self.fields = self.window.SearchFields
        self.requests = []

        for field in self.fields:
            temp_list = []
            if field.ParamInput.displayText() == '':
                continue
            temp_list.append(field.ParamComboBox.currentIndex())
            temp_list.append(field.ParamInput.displayText())
            self.requests.append(temp_list)

    def run(self):
        table = self.table
        for request in self.requests:
            column = request[0]
            value = request[1]
            table = self.table_obj.searchIn(value, column, table)
        self.searchdone.emit(table)


# TODO:   done  QStandartItemModel class with opening file and other stuff
#               figure  out how to make that model change dynamically
#               add feature to create and delete SearchInputFields
#               MAKE EVERYTHING PRETTY!!!

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    LoadScreen = QSplashScreen(QPixmap("se-loadscreen.jpg"))
    LoadScreen.show()
    QThread.sleep(1)
    qApp.processEvents()

    window = MainWindow()
    window.show()
    LoadScreen.finish(window)
    #window.openCSV('Mammals.csv')
    sys.exit(app.exec_())
