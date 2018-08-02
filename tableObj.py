import numpy
import csv
import re
import time

class Table():
    def __init__(self, file, delimiter=None, encoding=None):

        self.Table = None
        self.Header = None
        self.Interrupt = False

        self.file = file
        self.Delimiter = ',' if delimiter == None else delimiter
        self.Encoding = 'utf-8'if encoding == None else encoding
        self.DType = (str)

        self.loadFile()

    def __call__(self):
        return self.Table

    def __setitem__(self, offset, value):
        self.Table[offset] = value

    def __getitem__(self, offset, *key):
        if key:
            return self.Table[offset][key]
        return self.Table[offset]


    def loadFile(self):
        table = []
        with open(self.file, 'r', encoding=self.Encoding) as f:
            csv_table = list(csv.reader(f, delimiter=self.Delimiter))
            self.table = numpy.array(csv_table, dtype=str)
        self.Header = self.table[0]
        self.Table = self.table[1:]
        # self.updateDataTypes()

    def updateDataTypes(self):  # for faster search

        for index, row in enumerate(self.Table):
            for segment, item in enumerate(row):
                try:
                    self.Table[index, segment] = int(item)
                except ValueError:
                    try:
                        self.Table[index, segment] = float(item)
                    except ValueError:
                        pass

    def retRealVar(self, var):
        var = str(var)
        try:
            var = int(var)
        except ValueError:
            try:
                var = float(var)
            except ValueError:
                pass
        return var

    def returnRealValues(self, *args):
        l = [self.retRealVar(item) for item in args]
        return l

    def searchIn(self, value, column, table, window, requests):
        window.updatelabel.emit("Searching...")
        self.Interrupt = False
        self.table_ = table

        # if type(column) != int:
        #     try:
        #         column = list(self.Header).index(column)
        #     except ValueError:
        #         return False
        try:
            search_operator, search_value = self.parseValue(value)
        except IndexError:
            search_operator, search_value = None, value

        search_value = self.returnRealValues(search_value)[0]
        print(search_operator, search_value)

        pickup_column = self.table_[:, column]
        search_bool = numpy.full(pickup_column.shape, True)
        from time import time
        st = time()
        try:
            pickup_column = numpy.array(pickup_column, dtype=float)
            search_operator = '==' if search_operator == None else search_operator
            expression = "pickup_column {operator} search_value".format(operator=search_operator)
            search_bool = eval(expression)
        except ValueError:
            search_bool = self._search(pickup_column, search_bool,
                                        search_value, search_operator,
                                        window, requests)
        print("Search time ", time() - st)
        result = self.table_[search_bool]
        window.updatelabel.emit("Search done!")
        return result

    def _search(self, pickup_column, search_bool, expression, operator, window, requests):
        len_pickup_col = len(pickup_column)
        for counter, value in enumerate(pickup_column):
            # if self.Interrupt == True:
            #     return False

            percent = (counter * 100 / len_pickup_col) / requests
            window.percentdone.emit(percent)
            dots = int(time.time()) % 3
            mssg = "Searching{}".format('.' * dots)
            window.updatelabel.emit(mssg)

            value, expression = self.returnRealValues(value, expression)

            if operator == None:
                exp_to_eval = "\"{}\".lower() in value.lower()".format(expression)

                try:
                    if eval(exp_to_eval):
                        search_bool[counter] = True
                    else:
                        search_bool[counter] = False
                except AttributeError:
                    return search_bool
            else:
                if type(expression) == str:
                    exp_to_eval = "value {} \"{}\"".format(operator, expression)
                else:
                    exp_to_eval = "value {} {}".format(operator, expression)

                try:
                    if eval(exp_to_eval):
                        search_bool[counter] = True
                    else:
                        search_bool[counter] = False
                except TypeError:
                    return search_bool
        return search_bool


    def parseValue(self, value):
        operators_list = ["!", "<", ">", "=", "<=", ">="]
        if value[0] == "!":
            return ("!=", value[1:])
        elif value[0] == "<" or value[0] == ">":
            if value[1] != "=":
                return (value[0], value[1:])
            else:
                return (value[:2], value[2:])
        elif value[0] == "=":
            return ("==", value[1:])
        else:
            return (None, value)


if __name__ == "__main__":
    table = Table('Mammals.csv')
    # table.searchIn()
