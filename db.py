# importing libs
import sys
from PyQt5.QtWidgets import (QWidget, QLineEdit,
                             QApplication, QTableView,
                             QVBoxLayout, QHBoxLayout,
                             QPushButton, QHeaderView,
                             QGridLayout, QCheckBox,
                             QFontDialog, QToolTip)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5 import QtSql
from shlex import split

# main application class
class Elephant_Finder(QWidget):

    # class initialization
    def __init__(self):
        super().__init__()

        self.initUI()

    # initializing widgets
    def initUI(self):
        self.id = 0
        # description of the geometry of the window and title
        self.setGeometry(100, 150, 1200, 600)
        self.setWindowTitle('Elephant Finder')
        # call database creation function
        self.createParamsDB()
        self.createDB()
        # displaying window elements
        self.setLayout(self.myLayout())
        self.show()

    # customize the display of window elements
    def myLayout(self):
        # creating a grid
        grid = QGridLayout()
        spacing = 5
        grid.setSpacing(spacing)
        # Adding a table mapping to a database
        grid.addLayout(self.sqlLayout(), 2, 0, 1, 0)
        # creating a switch
        self.cb = QCheckBox(self)
        self.cb.stateChanged.connect(self.changeQuery)
        grid.addWidget(self.cb, 1, 0)
        grid.setColumnMinimumWidth(0, 30)
        # create input fields
        n = len(self.headerList)
        qwidth = [self.view.columnWidth(i) for i in range(n)]
        #print(qwidth)
        self.qles = [None for i in range(n)]
        for i in range(0, n):
            self.qles[i] = QLineEdit(self)
            self.qles[i].setObjectName(self.headerList[i])
            self.qles[i].textChanged[str].connect(self.setSearchQuery)
            grid.addWidget(self.qles[i], 1, i + 1)
            grid.setColumnMinimumWidth(i + 1, qwidth[i] - spacing)
        # create buttons
        comboButton = QPushButton('font')
        comboButton.clicked.connect(self.fontDialog)
        saveButton = QPushButton('save')
        saveButton.clicked.connect(self.saveParams)
        loadButton = QPushButton('load')
        loadButton.clicked.connect(self.loadParams)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(comboButton)
        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(loadButton)
        grid.addLayout(buttonLayout, 0, 0, 1, n+1)
        self.loadParams()
        loadButton.setToolTip('{}'.format(', '.join([i[0] + ' = ' + i[1] for i in self.loadHint])))
        # return of the finished grid
        return grid

    # remembering the status of the switch after pressing and updating the table
    def changeQuery(self, state):

        self.state = state
        self.setSearchQuery('')

    # formulating a query to the database
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

        #maxLenCol1 = "select max(length(species)) from usda".format(params)
        """maxLenCol1 = "select species, length(species) from usda order by length(species) "
        maxCol1 = QtSql.QSqlQuery()
        maxCol1.exec(maxLenCol1)
        while maxCol1.next():
            print(maxCol1.value(0), maxCol1.value(1))
        """

        self.searchQuery = "select * from usda {}".format(params)
        #qmodel = QtSql.QSqlQueryModel()
        self.qmodel.setQuery(self.searchQuery, self.db)
        self.view.setModel(self.qmodel)
        self.view.resizeRowsToContents()

    # database creation
    def createDB(self):
        # binding to an existing database
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE', "usda")
        self.db.setDatabaseName('usda.db')
        self.db.open()
        # getting a list of headers
        self.query = QtSql.QSqlQuery(db = self.db)
        self.query.exec_("PRAGMA table_info(usda)")
        # filling the list of headings
        self.headerList = []
        while self.query.next():
            self.headerList.append(self.query.value(1))
        # create a query parameter dictionary
        self.paramsDict = {x: ['', '', ''] for x in self.headerList}
        self.paramsDict[''] = ["{} {} '%{}%'", '', '']

    # customize table display
    def sqlLayout(self):
        # retrieving data from the database
        self.qmodel = MySqlModel()
        self.searchQuery = "select * from usda"
        self.qmodel.setQuery(self.searchQuery, self.db)
        # view customization
        self.view = QTableView(self)
        self.view.setModel(self.qmodel)
        header = self.view.horizontalHeader()
        for i in range(len(header)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        #self.view.resizeColumnsToContents()
        self.view.resizeRowsToContents()
        #self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setSelectionMode(QTableView.SingleSelection)
        self.view.clicked.connect(self.copyText)
        self.view.setToolTip('Click on the cell to copy the text')
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.font = self.view.property('font')
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)
        # return table display
        return layout


    def copyText(self, index):

        sys_clip = QApplication.clipboard()
        sys_clip.setText(index.data())


    def createParamsDB(self):

        self.paramsdb = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.paramsdb.setDatabaseName('params.db')
        self.paramsdb.open()
        self.paramsQuery = QtSql.QSqlQuery(db = self.paramsdb)
        self.paramsQuery.exec_("create table params(id int primary key, text text, font text)")


    def saveParams(self):

        insert = "insert or replace into params values({0}, \"{1}\", \"{2}\")".format(
            self.id, self.searchQuery, self.font.toString())
        self.paramsQuery.exec_(insert)


    def loadParams(self):

        query = "select * from params where id = {}".format(self.id)
        self.paramsQuery.exec_(query)
        self.paramsQuery.next()
        params = self.paramsQuery.value(1)
        self.font.fromString(self.paramsQuery.value(2))
        self.view.setFont(self.font)
        for i in self.qles:
            i.setFont(self.font)
        self.view.resizeRowsToContents()
        self.paramsParse(params)


    def paramsParse(self, params):

        paramList = split(params)
        self.loadHint = []
        for name in self.headerList:
            if name in paramList:
                param = paramList[paramList.index(name) + 2]
                if param[0] == '%':
                    param = param.strip('%')
                    if param[0] == ' ':
                        param = param[1:]
                        self.cb.setChecked(True)
                    else:
                        self.cb.setChecked(False)
                self.qles[self.headerList.index(name)].setText(param)
                self.loadHint.append([name, param])


    def fontDialog(self):

        self.font, valid = QFontDialog.getFont(self.font)
        if valid:
            self.view.setFont(self.font)
            self.view.resizeRowsToContents()
            for i in self.qles:
                i.setFont(self.font)


# class used to align the data in the table to the center
class MySqlModel(QtSql.QSqlQueryModel):

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QtSql.QSqlQueryModel.data(self, index, role)

# launch application
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Elephant_Finder()
    sys.exit(app.exec_())
