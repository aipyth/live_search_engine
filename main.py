from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy
import csv

from tableObj import Table

class LabelLikeButton(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent = None):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()

class SearchField(QHBoxLayout):
    def __init__(self, mainwindow, parent=None):
        QHBoxLayout.__init__(self, parent)

        self.parentWindow = mainwindow

        self.DeleteButton = LabelLikeButton("×")
        self.ParamComboBox = QComboBox()
        self.ParamInput = QLineEdit()

        self.ParamInput.textChanged.connect(self.parentWindow.search_in)
        self.DeleteButton.clicked.connect(self.delete)
        self.DeleteButton.setStyleSheet("""LabelLikeButton {
            font-family: sans-serif;
            font-weight: 1000;
            font-size: 26px;
            color: #000;
        }
        LabelLikeButton:hover, LabelLikeButton:focus {
            color: #d22525;
        }""")

        self.SFLayout = QVBoxLayout()
        self.SFLayout.addWidget(self.ParamComboBox)
        self.SFLayout.addWidget(self.ParamInput)
        self.setAlignment(Qt.AlignJustify)

        self.addWidget(self.DeleteButton,
                        alignment=Qt.AlignCenter)
        self.addLayout(self.SFLayout)

    def delete(self):
        self_index = self.parentWindow.SearchFields.index(self)
        self.ParamInput.deleteLater()
        self.ParamComboBox.deleteLater()
        self.DeleteButton.deleteLater()
        del self.parentWindow.SearchFields[self_index]

    def add_headers_into_cb(self, content):
        self.ParamComboBox.clear()
        for item in content:
            self.ParamComboBox.addItem(item)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Search Engine')
        self.resize(1200, 800)

        self.CSVTable = None
        self.Delimiter = ','
        self.Encoding = 'utf-8'
        self.TableFontSize = '15'
        self.SearchFields = []   # this array will contain SearchFileds objects

        self.OpenCSVButton = QPushButton('Open CSV')
        self.OpenCSVButton.clicked.connect(self.openCSV)

        self.AddSearchFieldButton = QPushButton('Add Search Field')
        self.AddSearchFieldButton.clicked.connect(self.addSearchField)

        self.SearchButton = QPushButton('Search')
        self.SearchButton.clicked.connect(self.search_in)

        self.SetDelimiterButton = QPushButton('Set Delimiter')
        self.SetDelimiterButton.clicked.connect(self.setDelimiter)

        self.SetEncodingButton = QPushButton('Set Encoding')
        self.SetEncodingButton.clicked.connect(self.setEncoding)

        self.SetTableFontSizeButton = QPushButton('Set Font Size for Table')
        self.SetTableFontSizeButton.clicked.connect(self.setTableFontSize)

        self.ResultArea = QTableView()
        self.ResultArea.setStyleSheet("""QTableView{
            font-size: %spx;
        }""" %(self.TableFontSize))

        self.MainSearchField = SearchField(self)
        self.SearchFields.append(self.MainSearchField)

        ### LAYOUTS ###

        self.ButtonBox = QHBoxLayout()
        self.ButtonBox.setAlignment(Qt.AlignLeft)
        self.ButtonBox.addWidget(self.OpenCSVButton)
        self.ButtonBox.addWidget(self.AddSearchFieldButton)
        self.ButtonBox.addWidget(self.SearchButton)
        self.ButtonBox.addWidget(self.SetDelimiterButton)
        self.ButtonBox.addWidget(self.SetEncodingButton)
        self.ButtonBox.addWidget(self.SetTableFontSizeButton)

        self.SearchBox = QHBoxLayout()
        self.SearchBox.addLayout(self.MainSearchField)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.addLayout(self.ButtonBox)
        self.MainLayout.addSpacing(10)
        self.MainLayout.addLayout(self.SearchBox)
        self.MainLayout.addSpacing(10)
        self.MainLayout.addWidget(self.ResultArea)

        self.setLayout(self.MainLayout)

        self.openRecent()

    def search_in(self):
        if self.CSVTable != None:
            self.thread = SearchThread(self, self.CSVTable)
            self.thread.searchdone.connect(self.setItemModel, Qt.QueuedConnection )
            self.thread.start()

    def paintSearchBox(self):
        for item in self.SearchFields:
            self.SearchBox.addLayout(item)

    def addSearchField(self):
        sf = SearchField(self)
        try:
            sf.add_headers_into_cb(self.CSVTable.Header)
        except AttributeError:
            pass
        self.SearchFields.append(sf)
        self.paintSearchBox()

    def setItemModel(self, content):
        item_model = QStandardItemModel(parent=self)
        for row in content:
            row_items = []
            for item in row:
                it = QStandardItem(item)
                row_items.append(it)
            item_model.appendRow(row_items)
        item_model.setHorizontalHeaderLabels(self.CSVTable.Header)
        self.ResultArea.setModel(item_model)

        self.writeRecent()

    def writeRecent(self):
        with open('recent.info', 'w') as r:
            bytes = r.write(self.file)
        return bytes

    def getFileName(self):
        file_obj = QFileDialog.getOpenFileName(parent=self, caption="Open CSV",
                                        filter="CSV (*.csv)")
        return file_obj[0]

    def openCSV(self, file=None):
        self.file = file
        if not self.file:
            self.file = self.getFileName()
        try:
            self.CSVTable = Table(self.file, self.Delimiter, self.Encoding)
        except Exception as errors:
            self.showInfo('Error', str(errors))
            return
        for field in self.SearchFields:
            field.add_headers_into_cb(self.CSVTable.Header)
        self.setItemModel(self.CSVTable.Table)

    def openRecent(self):
        try:
            with open('recent.info', 'r') as r:
                file = r.read()
            self.openCSV(file)
        except FileNotFoundError:
            return

    def setDelimiter(self):
        dialog = QInputDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            print("QInputDialog(setDelimiter) Button OK")
            self.Delimiter = dialog.textValue()
        else:
            print("QInputDialog(setDelimiter) Button Cancel")

    def setEncoding(self):
        dialog = QInputDialog(self)
        result = dialog.exec_()
        if result:
            print("QInputDialog(setEncoding) Button OK")
            self.Encoding = dialog.textValue()
        else:
            print("QInputDialog(setEncoding) Button Cancel")

    def setTableFontSize(self):
        dialog = QInputDialog(self)
        result = dialog.exec_()
        if result:
            print("QInputDialog(setTableFontSize) Button OK")
            self.TableFontSize = dialog.textValue()
            self.ResultArea.setStyleSheet("""QTableView{
                font-size: %spx;
            }""" %(self.TableFontSize))
        else:
            print("QInputDialog(setTableFontSize) Button Cancel")

    def showInfo(self, header, info):
        infoWindow = QMessageBox.information(self, header, info,
                                            buttons=QMessageBox.Close,
                                            defaultButton=QMessageBox.Close)

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
            if table == False:
                return
        self.searchdone.emit(table)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    LoadScreen = QSplashScreen(QPixmap("se-loadscreen.jpg"))
    LoadScreen.show()
    QThread.sleep(0.3)
    qApp.processEvents()

    window = MainWindow()
    window.show()
    LoadScreen.finish(window)
    sys.exit(app.exec_())
