import json

class Settings():
    def __init__(self):
        self.Delimiter = ','
        self.Encoding = 'utf-8'
        self.FontSize = '16'
        self.LiveSearchFlag = True

        self.read()

    def save(self):
        self.parametersDict =  {'Delimiter': self.Delimiter,
                                'Encoding': self.Encoding,
                                'FontSize': self.FontSize,
                                'LiveSearch': self.LiveSearchFlag}

        with open('settings.json', 'w') as fp:
            json.dump(self.parametersDict, fp)

    def read(self):
        try:
            with open('settings.json', 'r') as fp:
                self.parametersDict = json.load(fp)

                self.Delimiter = self.parametersDict['Delimiter']
                self.Encoding = self.parametersDict['Encoding']
                self.FontSize = self.parametersDict['FontSize']
                self.LiveSearchFlag = self.parametersDict['LiveSearch']
        except FileNotFoundError:
            self.save()

    def __getitem__(self, item):
        return self.parametersDict[item]


if __name__ == '__main__':
    set = Settings()
    # print(set['Delimiter'])
    # set.save()
    # set.read()
