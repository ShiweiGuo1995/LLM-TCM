import pandas as pd
from read_data import ParallelData, SingleData
from TermsMapper import TermsMapper


class TermsMatcher:
    def __init__(self, terms_file, only_terms_file, chinese_file, english_file, parallel_file):
        self.terms_mapper = TermsMapper(terms_file, only_terms_file)
        self.terms_mapper = self.terms_mapper.mapper
        self.parallel_file = parallel_file

        if english_file:
            self.parallel_data = ParallelData(chinese_file, english_file, parallel_file)
            self.chinese = self.parallel_data.chinese_data
            self.english = self.parallel_data.english_data
        else:
            data = SingleData(chinese_file)
            self.chinese = data.chinese_data

    def match_terms(self):
        results = []
        terms_list = self.terms_mapper.items()

        for ch in self.chinese:
            terms_contained = [term[0] for term in terms_list if term[0] in ch]

            # if self.parallel_file:
            #     terms_contained = [term for term in terms_contained if len(term) > 2]

            if terms_contained:
                results.append([ch, terms_contained])

        for i, item in enumerate(results):
            if '' in item[1]:
                results[i][1].remove('')
            english_terms = []
            for term in results[i][1]:
                term = term.strip()
                english_terms.append(self.terms_mapper[term])

            results[i].append(english_terms)

        print(results)

        return results


if __name__ == '__main__':
    terms_matcher = TermsMatcher('terms/terms.csv', 'terms/only_terms.csv',
                                 'data/examples.txt', None, None)
    terms_matcher.match_terms()
