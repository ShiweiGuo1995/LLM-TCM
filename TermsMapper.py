import pandas as pd
import re
from pathlib import Path
from collections import defaultdict


def is_title(s):
    return bool(re.search(r'\d', str(s)))


def is_number_regex(s):
    pattern = r'^-?\d+(\.\d+)?$'
    return bool(re.match(pattern, s))


def merge_null_revise(data):
    to_delete_rows = []
    all_rows = []

    for i, row in data.iterrows():
        if type(row['WGM2#']) is str and not is_number_regex(row['WGM2#']):
            print(row['WGM2#'])
            to_delete_rows.append(i)

    data = data.drop(index=data.index[to_delete_rows])
    columns = data.columns.tolist()
    first_row = data.iloc[0]
    all_rows.append(first_row)
    for i, row in data.iterrows():
        if i == 0:
            all_rows.append(row)
        elif pd.isnull(row['WGM2#']):
            for column in columns[1:]:
                if not pd.isnull(row[column]):
                    if pd.isnull(all_rows[-1][column]):
                        all_rows[-1][column] = row[column]
                    else:
                        all_rows[-1][column] += ' ' + row[column]
        else:
            all_rows.append(row)

    for i, row in enumerate(all_rows):
        if row['Chinese term'] == '太阳经证':
            all_rows[i]['Synonyms'] = None
        if (not pd.isnull(row['Synonyms'])) and '\n' in row['Synonyms']:
            all_rows[i]['Synonyms'] = row['Synonyms'].replace('\n', '; ')

    data = pd.DataFrame(all_rows)
    data = data.iloc[:, 1:]
    data = data.dropna(how='all')

    return data


class TermsMapper:
    def __init__(self, csv_path, output_path):
        terms_path = Path(output_path)
        self.key_header = ['Chinese term', 'English term']
        self.used_header = self.key_header + ['Synonyms', 'Chinese synonyms']

        if not terms_path.exists():
            csv_data = pd.read_csv(csv_path)
            csv_data = merge_null_revise(csv_data)
            self.headers = csv_data.columns.tolist()
            self.csv_data_used = csv_data[self.used_header]
            self.csv_key_data = csv_data[self.key_header]
            self.csv_data_used = self.csv_data_used[~self.csv_key_data.apply(lambda row: row.map(is_title)).any(axis=1)]
            # self.csv_data_used = self.csv_data_used[~self.csv_key_data.apply(lambda row: row.astype(str).str.contains('null').any(), axis=1)]
            # self.csv_data_used = self.csv_data_used.dropna()

            self.csv_data_used.to_csv(output_path, index=False)
        else:
            self.csv_data_used = pd.read_csv(output_path)

        # self.mapper = self.csv_data_used.set_index(self.used_header[0])[self.used_header[1]].to_dict()
        self.mapper = defaultdict(list)
        self.trans_csv2dict()

    def trans_csv2dict(self):
        for i, row in self.csv_data_used.iterrows():
            chinese_term = row['Chinese term']
            english_term = row['English term']
            self.mapper[chinese_term].append(english_term)

            synonyms = row['Synonyms']
            chinese_synonyms = row['Chinese synonyms']

            if not pd.isnull(synonyms):
                if ';' in synonyms:
                    synonyms = synonyms.split(';')
                    self.mapper[chinese_term].extend(synonyms)
                else:
                    self.mapper[chinese_term].append(synonyms)
            if not pd.isnull(chinese_synonyms):
                if '；' in chinese_synonyms:
                    chinese_synonyms = chinese_synonyms.split('；')
                    for cs in chinese_synonyms:
                        self.mapper[cs].extend(self.mapper[chinese_term])
                else:
                    self.mapper[chinese_synonyms].extend(self.mapper[chinese_term])

    def get_terms_mapper(self):
        print(self.used_header)
        print(self.csv_data_used)
        print(self.mapper)

        mapper = {k: str(v) for k, v in self.mapper.items()}
        mapper_df = pd.DataFrame(list(mapper.items()), columns=['Chinese', 'English'])
        mapper_df.to_csv('terms/final_terms.csv', index=False)


if __name__ == '__main__':
    terms_mapper = TermsMapper('terms/terms.csv', 'terms/only_terms.csv')
    terms_mapper.get_terms_mapper()
