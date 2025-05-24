import pandas as pd
from pathlib import Path


def split_data(data_):
    total_str = ''

    for str_ in data_:
        total_str += str_

    tmp_str_list = total_str.split('///>>>///')
    return tmp_str_list[:-1]


class SingleData:
    def __init__(self, chinese_path):
        self.chinese_data = []

        self.chinese_path = chinese_path

        self.get_data()

    def get_data(self):
        with open(self.chinese_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line != '>>>///>>>' and line != '///>>>///':
                    self.chinese_data.append(line)


class ParallelData:
    def __init__(self, chinese_path, english_path, csv_path):

        self.chinese_data = []
        self.english_data = []
        csv_path = Path(csv_path)

        if not csv_path.exists():
            with open(english_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line != '>>>///>>>':
                        self.english_data.append(line)

            with open(chinese_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line != '>>>///>>>' and line != '///>>>///':
                        self.chinese_data.append(line)

            # self.chinese_data = split_data(self.chinese_data)
            # self.english_data = split_data(self.english_data)

            if len(self.english_data) != len(self.chinese_data):
                print("The nums of english: {}".format(len(self.english_data)))
                print("The nums of chinese: {}".format(len(self.chinese_data)))
                raise Exception('The nums of english and chinese is not equation!')

            df = pd.DataFrame({'Chinese': self.chinese_data, 'English': self.english_data})
            df.to_csv(csv_path, index=False)
        else:
            df = pd.read_csv(csv_path)
            self.chinese_data = df['Chinese'].to_list()
            self.english_data = df['English'].to_list()

    def get_parallel_data(self):
        print(self.chinese_data)
        print(self.english_data)
        print(len(self.chinese_data))
        print(len(self.english_data))


if __name__ == '__main__':
    data = ParallelData('data/Chinese.txt', 'data/English.txt', 'data/parallel_data.csv')
    data.get_parallel_data()

    # data = SingleData('data/examples.txt')
    # data = data.chinese_data
    # print(data)
