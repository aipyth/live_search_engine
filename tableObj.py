import numpy
import csv
import re

class Table():
    def __init__(self, file=None):

        self.Table = None
        self.Header = None
        self.EntryFlag = False

        if file != None:
            self.loadFile(file)
        else:
            pass

    def __call__(self):
        return self.Table

    def __setitem__(self, offset, value):
        self.Table[offset] = value

    def __getitem__(self, offset, *key):
        if key:
            return self.Table[offset][key]
        return self.Table[offset]


    def loadFile(self, file):
        with open(file, 'r') as f:
            csv_table = list(csv.reader(f))
            self.Table = numpy.array(csv_table)
        self.Header = self.Table[0]
        self.Table = self.Table[1:]
        self.fixingTypes()

    def fixingTypes(self):
        for index, row in enumerate(self.Table):
            for segment, item in enumerate(row):
                try:
                    # int_item = int(item)
                    # float_item = float(item)
                    # print(int_item)
                    # if eval(item) == int_item:
                    #     self.Table[index, segment] = int_item
                    # elif eval(item) == float_item:
                    #     self.Table[index, segment] = float_item
                    self.Table[index, segment] = float(item)
                except ValueError:
                    pass

    def search(self, value, column):
        if type(column) != int:
            try:
                column = list(self.Header).index(column)
            except ValueError:
                return False

        search_operator, search_number = self.parseValue(value)

        if search_operator:
            pickup_column = self.Table[:, column]
            # search_bool_result = "pickup_column {} search_number".format(search_operator)
            search_bool = pickup_column == search_number
            search_bool = self._search(pickup_column, search_bool,
                                    search_number, search_operator)
            result = self.Table[search_bool]

            return result
        return False

    def searchIn(self, value, column, table):
        if type(column) != int:
            try:
                column = list(self.Header).index(column)
            except ValueError:
                return False

        search_operator, search_number = self.parseValue(value)

        if search_operator:
            pickup_column = table[:, column]
            search_bool = pickup_column == search_number
            search_bool = self._search(pickup_column, search_bool,
                                    search_number, search_operator)
            result = table[search_bool]

            return result
        return False

    def _search(self, pickup_column, search_bool, expression, operator):
        for counter, value in enumerate(pickup_column):
            expression_is_string = False
            try:
                value = float(value)
                try:
                    expression = float(expression)
                except ValueError:
                    expression_is_string = True
            except ValueError:
                pass


            if operator == None:
                exp_to_eval0 = "lower(value) in lower({})".format(expression)
                exp_to_eval1 = "lower({}) in lower(value)".format(expression)
                if eval(exp_to_eval0) or eval(exp_to_eval1):
                    search_bool[counter] = True
                else:
                    search_bool[counter] = False
            else:
                if expression_is_string:
                    exp_to_eval = "value {} \"{}\"".format(operator, expression)
                else:
                    exp_to_eval = "value {} {}".format(operator, expression)
                if eval(exp_to_eval):
                    search_bool[counter] = True
                else:
                    search_bool[counter] = False

        return search_bool

    def parseValue(self, value):
        f_symbols = ['<', '>', '!', '=']
        try:
            int(value[0])
            return (None, value)
        except ValueError:
            try:
                int(value[1])
                if value[0] == '=':
                    return ('==', value[1:])
                return (value[0], value[1:])
            except ValueError:
                if value[1] != '=':
                    if value[0] == '=':
                        return ('==', value[1:])
                    return (value[0], value[1:])
                return (value[:2], value[2:])


if __name__ == "__main__":
    table = Table('Mammals.csv')

    # print(table.parseValue('>38.412342'))
    # print(table.Header)
    # table.search('3.0', 3)
    # print(table.search('!=3.0', -1))
    print(table.searchIn('=1', -1))

    # size = table[:, 3:]
    # print(size)
