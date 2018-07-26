import numpy
import csv
import re

class Table():
    def __init__(self, file, delimiter=None, encoding=None):

        self.Table = None
        self.Header = None
        self.EntryFlag = False

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
        self.Table = numpy.genfromtxt(self.file, delimiter=self.Delimiter,
                                encoding=self.Encoding, dtype=self.DType)
        # with open(self.file, 'r') as f:
            # csv_table = list(csv.reader(f))
            # self.Table = numpy.array(csv_table)
        self.Header = self.Table[0]
        self.Table = self.Table[1:]
        self.fixingTypes()

    def fixingTypes(self):
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

    def returnRealVariables(self, *args):
        l = [self.retRealVar(item) for item in args]
        return l

    def searchIn(self, value, column, table=None):
        self.table = table
        if type(column) != int:
            try:
                column = list(self.Header).index(column)
            except ValueError:
                return False
        try:
            search_operator, search_number = self.parseValue(value)
        except IndexError:
            search_operator, search_number = None, value


        pickup_column = self.table[:, column]
        search_bool = pickup_column == search_number
        search_bool = self._search(pickup_column, search_bool,
                                search_number, search_operator)
        result = self.table[search_bool]
        return result

    def _search(self, pickup_column, search_bool, expression, operator):
        for counter, value in enumerate(pickup_column):
            # try:
            #     value = float(value)
            #     try:
            #         expression = int(expression)
            #     except ValueError:
            #         try:
            #             expression = float(expression)
            #         except ValueError:
            #             expression_is_string = True
            # except ValueError:
            #     pass
            # print(pickup_column)

            value, expression = self.returnRealVariables(value, expression)
            print("'{}'".format(value), expression)

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

    # print(table.parseValue('>38.412342'))
    # print(table.Header)
    # table.search('3.0', 3)
    # print(table.search('!=3.0', -1))
    print(table.searchIn('', 0))
    # print(table.Table)
    # print(table.parseValue('<90'))
    # print(type(table.retRealVar('5')))
    # print(table.returnRealVariables('1', '1.0', 2, 4, 'string'))

    # size = table[:, 3:]
    # print(size)
