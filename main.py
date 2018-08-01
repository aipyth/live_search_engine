from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from threading import Thread
from time import time

import numpy as np
import csv

from tableObj import Table

class LabelLikeButton(QLabel):
    clicked = pyqtSignal()
    def __init__(self, parent = None):
        QLabel.__init__(self, parent)
        # QPushButton.__init__(self)

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

        self.ParamInput.deleteLater()
        self.ParamComboBox.deleteLater()
        self.DeleteButton.deleteLater()
        self.index = self.parentWindow.SearchFields.index(self)
        del self.parentWindow.SearchFields[self.index]

    def add_headers_into_cb(self, content):
        self.index = self.parentWindow.SearchFields.index(self)
        self.ParamComboBox.clear()
        for item in content:
            self.ParamComboBox.addItem(item)
        self.ParamComboBox.setCurrentIndex(self.index)

class ColumnsWindow(QWidget):
    def __init__(self, mainwindow):
        QWidget.__init__(self, parent=mainwindow)
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle('Pick up columns')
        self.setWindowModality(Qt.WindowModal)

        self.mainWindow = mainwindow
        self.allColModel = self.returnAllColumnsModel()
        self.currColModel = self.returnCurrentColumnsModel()

        self.AllColumnsTable = QListView()
        self.AllColumnsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.AllColumnsTable.setModel(self.allColModel)
        self.SelectedColumnsTable = QListView()
        self.SelectedColumnsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.SelectedColumnsTable.setModel(self.currColModel)

        self.AllColumnsLable = QLabel('Available items:')
        self.SelectedColumnsLable = QLabel('Current set:')

        self.setStyleSheet(""" QLabel {
            padding: 6px;
            background-color: #cfcfcf;
            font-family: sans-serif;
            font-weight: 600;
        }
        """)

        self.AddButton = QPushButton('>>')
        self.AddButton.clicked.connect(self.add_single)
        self.AddButton.setFixedSize(30, 30)
        self.AddButton.setFlat(True)
        self.AddButton.setStyleSheet("""QPushButton {
            background-color: #0c9951;
            color: #2b2b2b;
        }""")
        self.RemoveButton = QPushButton('<<')
        self.RemoveButton.clicked.connect(self.delete_single)
        self.RemoveButton.setFixedSize(30, 30)
        self.RemoveButton.setFlat(True)
        self.RemoveButton.setStyleSheet("""QPushButton {
            background-color: #99260c;
            color: #2b2b2b;
        }""")
        self.AddAllButton = QPushButton('Add All')
        self.AddAllButton.clicked.connect(self.add_all)
        self.DeleteAllButton = QPushButton('Remove All')
        self.DeleteAllButton.clicked.connect(self.delete_all)
        self.OkButton = QPushButton('OK')
        self.OkButton.clicked.connect(self.save_changes)
        self.OkButton.setStyleSheet("""QPushButton{
            background-color: #319149;
            color: #eee;
        }""")
        self.CancelButton = QPushButton('Cancel')
        self.CancelButton.clicked.connect(self.close)
        self.CancelButton.setStyleSheet("""QPushButton{
            background-color: #882d2d;
            color: #eee;
        }""")

        self.AllColumnsLayout = QVBoxLayout()
        self.AllColumnsLayout.addWidget(self.AllColumnsLable)
        self.AllColumnsLayout.addWidget(self.AllColumnsTable)

        self.SelectedColumnsLayout = QVBoxLayout()
        self.SelectedColumnsLayout.addWidget(self.SelectedColumnsLable)
        self.SelectedColumnsLayout.addWidget(self.SelectedColumnsTable)

        self.ARButtonsLayout = QVBoxLayout()
        self.ARButtonsLayout.addWidget(self.AddButton)
        self.ARButtonsLayout.addWidget(self.RemoveButton)
        self.ARButtonsLayout.setAlignment(Qt.AlignHCenter)

        self.ButtonsLayout = QVBoxLayout()
        self.ButtonsLayout.addWidget(self.AddAllButton)
        self.ButtonsLayout.addWidget(self.DeleteAllButton)
        self.ButtonsLayout.addWidget(self.OkButton)
        self.ButtonsLayout.addWidget(self.CancelButton)
        self.ButtonsLayout.setAlignment(Qt.AlignBottom)

        self.MainLayout = QHBoxLayout()
        self.MainLayout.addLayout(self.AllColumnsLayout)
        self.MainLayout.addLayout(self.ARButtonsLayout)
        self.MainLayout.addLayout(self.SelectedColumnsLayout)
        self.MainLayout.addLayout(self.ButtonsLayout)

        self.setLayout(self.MainLayout)

    def add_all(self):
        lst = self.returnAllColumnsModel().stringList()
        self.currColModel.setStringList(lst)

    def add_single(self):
        selected_list = self.AllColumnsTable.selectedIndexes()
        old_list = self.currColModel.stringList()
        new_list = [selected.data() for selected in selected_list]
        self.currColModel.setStringList(old_list + new_list)

    def delete_all(self):
        self.currColModel.removeRows(0, self.currColModel.rowCount())

    def delete_single(self):
        selected_list = self.SelectedColumnsTable.selectedIndexes()
        counter = 0
        for index in selected_list:
            self.currColModel.removeRows(index.row()-counter, 1)
            counter += 1

    def save_changes(self):
        columns = self.currColModel.stringList()
        table = self.mainWindow.CSVTable
        indexes = [np.where(table.table == col_name)[1][0] for col_name in columns]
        pick_up_col = [table.table[:,index] for index in indexes]
        table.Table = np.column_stack(pick_up_col)[1:]
        table.Header = np.array(columns)
        self.mainWindow.setItemModel(table.Table)
        for item in self.mainWindow.SearchFields:
            try:
                item.add_headers_into_cb(table.Header)
            except AttributeError:
                pass
        self.close()

    def returnCurrentColumnsModel(self):
        columns = [item for item in self.mainWindow.CSVTable.Header]
        sli = QStringListModel(columns)
        return sli

    def returnAllColumnsModel(self):
        columns = [item for item in self.mainWindow.CSVTable.table[0]]
        sli_all = QStringListModel(columns)
        return sli_all

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle('Search Engine')

        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Search Engine')
        self.resize(1200, 800)

        self.CSVTable = None
        self.Delimiter = ','
        self.Encoding = 'utf-8'
        self.TableFontSize = '15'
        self.SearchFields = []   # this array will contain SearchFileds objects
        self.RunningThreads = {'Search': None} # contains list of threads running,
                                # there always must be only 1 thread in searching!!!

        self.OpenCSVButton = QPushButton('Open CSV')
        self.OpenCSVButton.clicked.connect(self.openCSV)

        self.SetColumnsButton = QPushButton('Select columns')
        self.SetColumnsButton.clicked.connect(self.show_CW)

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

        self.ProgressBar = QProgressBar()
        self.ProgressBar.setRange(0, 100)
        self.ProgressBar.setValue(0)
        self.ProgressBar.setStyleSheet(""" QProgressBar {
        border: 1px solid #000;
        border-radius: 2px;
        text-align: middle;
        color: #222;
        font-weight: 400;
        }
        QProgressBar::chunk {
        background-color: #66c3ff;
        }""")
        self.StatusLabel = QLabel()

        ### LAYOUTS ###

        self.MainSearchField = SearchField(self)
        self.SearchFields.append(self.MainSearchField)

        self.ButtonBox = QHBoxLayout()
        self.ButtonBox.setAlignment(Qt.AlignLeft)
        self.ButtonBox.addWidget(self.OpenCSVButton)
        self.ButtonBox.addWidget(self.SetColumnsButton)
        self.ButtonBox.addWidget(self.AddSearchFieldButton)
        self.ButtonBox.addWidget(self.SearchButton)
        self.ButtonBox.addWidget(self.SetDelimiterButton)
        self.ButtonBox.addWidget(self.SetEncodingButton)
        self.ButtonBox.addWidget(self.SetTableFontSizeButton)

        self.SearchBox = QHBoxLayout()
        self.SearchBox.addLayout(self.MainSearchField)

        self.StatusLayout = QHBoxLayout()
        self.StatusLayout.addWidget(self.ProgressBar, alignment =
                              Qt.AlignLeft | Qt.AlignHCenter)
        self.StatusLayout.addWidget(self.StatusLabel, alignment =
                              Qt.AlignRight | Qt.AlignHCenter)
        self.StatusLayout.setSpacing(10)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.addLayout(self.ButtonBox)
        self.MainLayout.addSpacing(10)
        self.MainLayout.addLayout(self.SearchBox)
        self.MainLayout.addSpacing(10)
        self.MainLayout.addWidget(self.ResultArea)
        self.MainLayout.addLayout(self.StatusLayout)

        self.setLayout(self.MainLayout)

        self.openRecent()

    def resizeEvent(self, qresizeEvent):
        self.ProgressBar_width = qresizeEvent.size().width() // 2 - 30
        self.ProgressBar.setFixedSize(self.ProgressBar_width, 16)
        QWidget.resizeEvent(self, qresizeEvent)

    def updateProgressBar(self, value):
        self.ProgressBar.setValue(value)

    def updateStatusLabel(self, value):
        self.StatusLabel.setText(value)

    def show_CW(self):
        pick_col = ColumnsWindow(self)
        pick_col.show()

    def search_in(self):
        if self.CSVTable != None:
            if self.RunningThreads['Search'] == None:
                self.start_searching_thread()
            else:
                self.RunningThreads['Search'].end()
                self.start_searching_thread()

    def start_searching_thread(self):
        self.thread = SearchThread(self, self.CSVTable)
        self.RunningThreads['Search'] = self.thread
        self.thread.searchdone.connect(self.endingSearch)#, Qt.AutoConnection )
        self.thread.collect()
        self.thread.start()

    def endingSearch(self, data):
        print("heaaaaaaaaaare")
        # self.RunningThreads['Search'].deleteLater()
        self.RunningThreads['Search'] = None

        self.setItemModel(data)

    def paintSearchBox(self):
        for item in self.SearchFields:
            self.SearchBox.addLayout(item)

    def addSearchField(self):
        sf = SearchField(self)
        self.SearchFields.append(sf)
        try:
            sf.add_headers_into_cb(self.CSVTable.Header)
        except AttributeError:
            pass

        self.paintSearchBox()

    def setItemModel(self, content):
        self.resultsThread = SetModelThread(content, self)
        self.resultsThread.statussignal.connect(self.updateProgressBar)
        self.resultsThread.start()

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
        from time import time
        st = time()

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

        print("Open file time - ", time() - st)

    def openRecent(self):
        try:
            with open('recent.info', 'r') as r:
                file = r.read()
            self.openCSV(file)
        except FileNotFoundError:
            return

    def closeEvent(self, event):
        # here write func to save settings on quit
        self.close()

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

class SetModelThread(QThread):
    statussignal = pyqtSignal(int)
    def __init__(self, content, window):
        QThread.__init__(self)
        self.window = window
        self.content = content

    def run(self):

        st = time()

        counter = 1
        item_model = QStandardItemModel()
        item_model.setHorizontalHeaderLabels(self.window.CSVTable.Header)
        for row in self.content:
            percent = 100 * counter / len(self.content)
            self.statussignal.emit(percent)
            dots = int(time()) % 3 + 1
            mssg = "Setting table{}".format('.' * dots)
            self.window.updateStatusLabel(mssg)
            # self.window.updateStatusLabel('Setting table...')

            row_items = []
            for item in row:
                it = QStandardItem(item)
                row_items.append(it)
            item_model.appendRow(row_items)

            counter += 1

        self.window.ResultArea.setModel(item_model)
        self.window.updateStatusLabel('Ready!')
        print("Table set ", time() - st)

class SearchThread(QThread):
    searchdone = pyqtSignal(np.ndarray)
    def __init__(self, window, table_obj):
        QThread.__init__(self)
        self.table_obj = table_obj
        self.window = window

    def collect(self):
        self.table = self.table_obj.Table
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
        print("Searching...")
        table = self.table
        for request in self.requests:
            column, value = request[0], request[1]
            requests = len(self.requests)
            self.table_obj.Interrupt = False
            table = self.table_obj.searchIn(value, column, table, self.window, requests)
            # if table == False:
            #     return
        print("Ended searching")
        if self.window.RunningThreads['Search'] == self:
            self.searchdone.emit(table)

    def end(self):
        self.table_obj.Interrupt = True
        self.window.RunningThreads['Search'] = None
        # self.exit()
        # self.deleteLater()

class NewSearchThread(QThread): # here write a support for or, and, ()
                                # and replace with SearchThread
    searchdone = pyqtSignal(np.ndarray)
    def __init__(self, window, table_obj):
        QThread.__init__(self)
        self.table_obj = table_obj
        self.window = window

    def collect(self):
        self.table = self.table_obj.Table
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
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    LoadScreen = QSplashScreen(QPixmap("se-loadscreen.jpg"))
    LoadScreen.show()
    QThread.sleep(0.1)
    qApp.processEvents()

    window = MainWindow()
    window.show()
    LoadScreen.finish(window)
    sys.exit(app.exec_())
