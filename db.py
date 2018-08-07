import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtSql
from shlex import split

class MySqlModel(QtSql.QSqlQueryModel):

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QtSql.QSqlQueryModel.data(self, index, role)

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(1500, 900)
        self.id = 0
        self.table = ''
        self.Columns = '*'

        self.View = QTableView()
        self.TableFont = self.View.property('font')

        self.openDB()

        self.OpenButton = QPushButton('Open DB')
        self.OpenButton.clicked.connect(self.openDB)

        self.SetColumnsButton = QPushButton('Columns')
        self.SetColumnsButton.clicked.connect(self.ColumnsWindow.show)

        self.FontButton = QPushButton('Font')
        self.FontButton.clicked.connect(self.fontDialog)

        # LAYOUTS
        self.SearchFieldsGrid = QGridLayout()
        self.makeSearchFieldsGrid()

        self.ButtonBox = QHBoxLayout()
        self.ButtonBox.setAlignment(Qt.AlignLeft)
        self.ButtonBox.addWidget(self.OpenButton)
        self.ButtonBox.addWidget(self.SetColumnsButton)
        self.ButtonBox.addWidget(self.FontButton)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.ButtonBox)
        self.mainLayout.addLayout(self.SearchFieldsGrid)
        self.mainLayout.addWidget(self.View)

        self.setLayout(self.mainLayout)

    def openDB(self):
        self.FilePath = self.getFileName()
        if self.FilePath:
            self.createDB()
            self.getHeaders()
            self.setTable()
            # self.makeSearchFieldsGrid()

            try:
                self.ColumnsWindow.hide()
                self.ColumnsWindow.close()
                self.ColumnsWindow.deleteLater()

                self.ColumnsWindow = ColumnsWindow(self)
                self.SetColumnsButton.clicked.connect(self.ColumnsWindow.show)
            except AttributeError:
                self.ColumnsWindow = ColumnsWindow(self)

    def setTable(self):
        self.Columns = '*' if self.Columns == '' else self.Columns
        # self.QModel = QtSql.QSqlQueryModel()
        self.QModel = MySqlModel()
        self.SearchQuery = "select {} from {}".format(self.Columns, self.table)
        print(self.SearchQuery)
        # self.SearchQuery = "select {} from usda".format(self.Columns)#, self.table)
        self.QModel.setQuery(self.SearchQuery, self.DB)
        self.View.setModel(self.QModel)

        header = self.View.horizontalHeader()
        for i in range(len(header)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        # self.View.resizeColumnsToContents()
        self.View.resizeRowsToContents()
        self.View.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.View.clicked.connect(self.copyText)

    def makeSearchFieldsGrid(self):
        self.SearchFieldsGrid.setSpacing(5)

        self.clearLayout(self.SearchFieldsGrid)

        # self.cb = QCheckBox(self)
        # self.cb.stateChanged.connect(self.changeQuery)
        # self.SearchFieldsGrid.addWidget(self.cb, 0, 0)
        # self.SearchFieldsGrid.setColumnMinimumWidth(0, 30)

        n = len(self.Headers)
        qwidth = [self.View.columnWidth(i) for i in range(n)]
        # print(qwidth)
        self.qles = [None for i in range(n)]
        for i in range(n):
            self.qles[i] = QLineEdit(self)
            self.qles[i].setObjectName(self.Headers[i])
            self.qles[i].textChanged[str].connect(self.setSearchQuery)

            label = QLabel(self.Headers[i])

            self.SearchFieldsGrid.addWidget(label, 0, i + 1, alignment=Qt.AlignCenter)
            self.SearchFieldsGrid.addWidget(self.qles[i], 1, i + 1)
            # self.SearchFieldsGrid.setColumnMinimumWidth(i + 1, qwidth[i] - 5)


    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

    def createDB(self):
        # binding to an existing database

        self.DB = QtSql.QSqlDatabase.addDatabase('QSQLITE')

        # self.DB.setDatabaseName('usda.db')
        self.DB.setDatabaseName(self.FilePath)
        self.DB.open()

    def getHeaders(self):
        # getting a list of Headers
        self.query = QtSql.QSqlQuery(db = self.DB)
        self.query.exec_("PRAGMA table_info({})".format(self.table))

        # filling the list of headings
        self.HeaderList = []
        while self.query.next():
            self.HeaderList.append(self.query.value(1))

        # create a query parameter dictionary
        self.paramsDict = {x: ['', '', ''] for x in self.HeaderList}
        self.paramsDict[''] = ["{} {} '%{}%'", '', '']

    def changeQuery(self, state):
        self.state = state
        self.setSearchQuery('')

    def setSearchQuery(self, text):
        # switch handling
        try:
            if self.state == Qt.Checked:
                self.paramsDict[''] = ["{0} {1} '% {2}%' or {0} {1} '{2}%'", '', '']
            else:
                self.paramsDict[''] = ["{} {} '%{}%'", '', '']
        except:
            self.paramsDict[''] = ["{} {} '%{}%'", '', '']
        # processing of more and less characters
        if text != '':
            if text[0] == '<':
                matching = '<'
                queryString = "{} {} {}"
                text = text[1:]
            elif text[0] == '>':
                matching = '>'
                queryString = "{} {} {}"
                text = text[1:]
            else:
                queryString = self.paramsDict[''][0]
                matching = 'like'
        else:
            queryString, matching, text = self.paramsDict['']
        # filling in the query parameters dictionary
        self.paramsDict[self.sender().objectName()] = [queryString, matching, text]
        paramList = []
        # assembling query parameters into a list
        for name, value in self.paramsDict.items():
            if len(value) == 3:
                queryString, matching, text = value
                if queryString.find('%') != -1:
                    queryString = self.paramsDict[''][0]
                if text != '':
                    paramList.append(queryString.format(name, matching, text))
        # assembling query parameters into a string
        if len(paramList) == 0:
            params = ''
        elif len(paramList) == 1:
            params = 'where {}'.format(paramList[0])
        else:
            params = 'where {}'.format(" and ".join(paramList))
        # assembling the query and updating the table according to it

        self.Columns = '*' if self.Columns == '' else self.Columns
        self.searchQuery = "select {} from {} {}".format(self.Columns, self.table, params)
        #qmodel = QtSql.QSqlQueryModel()
        self.QModel.setQuery(self.searchQuery, self.DB)
        # self.dispatchColumns()

        # set model
        self.View.setModel(self.QModel)
        header = self.View.horizontalHeader()
        for i in range(len(header)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.View.resizeRowsToContents()

    def getFileName(self):
        file_obj = QFileDialog.getOpenFileName(parent=self, caption="Open",
                                        filter="SQLites Database (*.db)")
        return file_obj[0]

    def dispatchColumns(self):
        col_number = len(self.HeaderList)
        for index in range(col_number):
            if self.HeaderList[index] not in self.Headers:
                print("Col {} dispatched".format(index))
                self.QModel.removeColumn(index)

    def copyText(self, index):
        QApplication.clipboard().setText(index.data())

    def fontDialog(self):

        self.TableFont, valid = QFontDialog.getFont(self.TableFont)
        print(self.TableFont)
        if valid:
            self.View.setFont(self.TableFont)
            self.View.resizeRowsToContents()
            for i in self.qles:
                i.setFont(self.TableFont)

    def closeEvent(self, event):
        # TODO: write save functions
        QWidget.close(self)

class ColumnsWindow(QWidget):
    def __init__(self, mainwindow):
        QWidget.__init__(self, parent=mainwindow)
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle('Pick up columns')

        self.mainWindow = mainwindow
        self.mainWindow.Headers = self.mainWindow.HeaderList
        self.allTablesModel = self.returnAllTables()
        self.allColModel = self.returnAllColumnsModel()
        self.currColModel = self.returnCurrentColumnsModel()
        self.mainWindow.Columns = "{}".format(", ".join(self.currColModel.stringList()))

        self.PickTableTable = QListView()
        self.PickTableTable.pressed.connect(self.setTable)
        self.PickTableTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.PickTableTable.setModel(self.allTablesModel)
        self.AllColumnsTable = QListView()
        self.AllColumnsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.AllColumnsTable.setModel(self.allColModel)
        self.SelectedColumnsTable = QListView()
        self.SelectedColumnsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.SelectedColumnsTable.setModel(self.currColModel)

        self.PickTableLable = QLabel('Pick a table:')
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

        self.PickTableLayout = QVBoxLayout()
        self.PickTableLayout.addWidget(self.PickTableLable)
        self.PickTableLayout.addWidget(self.PickTableTable)

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
        self.MainLayout.addLayout(self.PickTableLayout)
        self.MainLayout.addLayout(self.AllColumnsLayout)
        self.MainLayout.addLayout(self.ARButtonsLayout)
        self.MainLayout.addLayout(self.SelectedColumnsLayout)
        self.MainLayout.addLayout(self.ButtonsLayout)

        self.setLayout(self.MainLayout)

        self.show()

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

        self.mainWindow.Headers = self.currColModel.stringList()
        self.mainWindow.Columns = "{}".format(", ".join(self.currColModel.stringList()))
        self.loadChanges()
        self.hide()

    def loadChanges(self):

        self.mainWindow.setTable()
        self.mainWindow.makeSearchFieldsGrid()

    def setTable(self, table):
        self.mainWindow.table = table.data()
        print("self.mainWindow.table = '{}'".format(self.mainWindow.table))
        self.mainWindow.getHeaders()
        self.mainWindow.setTable()
        self.update_info()
        self.mainWindow.makeSearchFieldsGrid()
        self.mainWindow.Headers = self.currColModel.stringList()
        self.loadChanges()

    def returnAllTables(self):
        columns = self.mainWindow.DB.tables()
        sli = QStringListModel(columns)
        return sli

    def returnCurrentColumnsModel(self):
        columns = [item for item in self.mainWindow.Headers]
        sli = QStringListModel(columns)
        return sli

    def returnAllColumnsModel(self):
        columns = [item for item in self.mainWindow.HeaderList]
        sli_all = QStringListModel(columns)
        return sli_all

    def update_info(self):
        self.allTablesModel = self.returnAllTables()
        self.allColModel = self.returnAllColumnsModel()
        self.currColModel = self.returnAllColumnsModel()

        self.PickTableTable.setModel(self.allTablesModel)
        self.AllColumnsTable.setModel(self.allColModel)
        self.SelectedColumnsTable.setModel(self.currColModel)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    MainWindow = MainWindow()
    MainWindow.show()
    MainWindow.ColumnsWindow.show()

    sys.exit(app.exec_())
