import pickle
import os
from TermsMapper import TermsMapper
from terms_matcher import TermsMatcher


class GenSingleFile:
    def __init__(self, raw_file_path, terms_pick, outputs_dir):
        self.parallel_sentence = []
        self.terms_chinese = []
        self.terms_english = []
        terms_mapper = TermsMapper('terms/terms.csv', 'terms/only_terms.csv')
        self.terms_mapper = terms_mapper.mapper

        terms_matcher = TermsMatcher('terms/terms.csv', 'terms/only_terms.csv',
                                     'data/Chinese.txt', 'data/English.txt', 'data/parallel_data.csv')
        self.terms_matcher = terms_matcher.match_terms()

        with open(raw_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != '>>>///>>>':
                    chinese_english = line.split('||')
                    self.parallel_sentence.append((chinese_english[0], chinese_english[1]))

        if terms_pick is not None:
            with open(terms_pick, 'rb') as f:
                tmp_terms = pickle.load(f)
                print(len(tmp_terms))
        else:
            tmp_terms = self.terms_matcher

        if not os.path.isdir(outputs_dir):
            os.mkdir(outputs_dir)

        print(len(self.parallel_sentence))
        for i in range(len(self.parallel_sentence)):
            curr_chinese_sen = self.parallel_sentence[i][0]
            curr_english_sen = self.parallel_sentence[i][1]
            curr_chinese_terms = tmp_terms[i][1]

            count = 0
            for terms in curr_chinese_terms:
                if terms in curr_chinese_sen:
                    count += 1

            if count / len(curr_chinese_terms) > 0.3:
                print(curr_chinese_sen)
                print(curr_english_sen)
                print(curr_chinese_terms)

                if terms_pick is not None:
                    curr_english_terms = [self.terms_mapper[term] for term in curr_chinese_terms]
                else:
                    curr_english_terms = tmp_terms[i][2]
                print(curr_english_terms)

                save_path = os.path.join(outputs_dir, str(i) + '.txt')
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write('Original Text' + '\n')
                    f.write(curr_chinese_sen + '\n')
                    f.write('Matched Terms' + '\n')
                    f.write(str(curr_chinese_terms) + '\n')
                    f.write('Matched Terms Translation' + '\n')
                    f.write(str(curr_english_terms) + '\n')
                    f.write('Translation' + '\n')
                    f.write(curr_english_sen)


if __name__ == '__main__':
    gen_single_file = GenSingleFile('data/outputs.txt', None, 'outputs_four_test_dir')
