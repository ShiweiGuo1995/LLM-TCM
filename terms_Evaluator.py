import math

import pandas as pd
from terms_matcher import TermsMatcher
from TermsMapper import TermsMapper
import pickle


class TermsEvaluator2:
    def __init__(self, terms_path, terms_path2, outputs_path, outputs_without_terms):
        terms_mapper = TermsMapper(terms_path, terms_path2)
        self.terms_mapper = terms_mapper.mapper

        self.all_english_terms = []
        self.all_style = []
        self.all_english_sentences = []
        self.all_english_sentences_wo_terms = []
        self.terms_num_per_sentence = []

        self.get_all_english_terms()

        self.read_english_sentences(outputs_path, self.all_english_sentences)
        self.read_english_sentences(outputs_without_terms, self.all_english_sentences_wo_terms)

    def get_all_english_terms(self):
        with open('terms_style_deepseek.pkl', 'rb') as f:
            terms_style = pickle.load(f)
            print(terms_style)

        for ts in terms_style:
            self.all_style.append(ts[0])
            english_term = [self.terms_mapper[t] for t in ts[1]]

            tmp = []
            self.terms_num_per_sentence.append(len(english_term))
            for ws in english_term:
                ws = [w.lower() for w in ws]
                tmp.extend(ws)

            self.all_english_terms.append(tmp)

    def read_english_sentences(self, file_path, list_container):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()

                if line != '>>>///>>>':
                    line = line.split('||')[1]
                    list_container.append(line)

    def get_terms_cover_rate(self, english_sentence, terms_list, terms_num):
        english_sentence = english_sentence.lower()
        count = 0
        for term in terms_list:
            if term in english_sentence:
                count += 1

        return count / (terms_num + 1)

    def do_evaluate(self):
        print(self.all_style)

        result_cover_rate_paper = []
        result_cover_rate_pos = []
        result_cover_rate_blog = []

        result_cover_rate_wo_paper = []
        result_cover_rate_wo_pos = []
        result_cover_rate_wo_blog = []

        for sentence, sentence_wo, terms, term_num, style in zip(self.all_english_sentences, self.all_english_sentences_wo_terms,
                                                                 self.all_english_terms, self.terms_num_per_sentence, self.all_style):
            if style == '中医学术论文':
                result_cover_rate_paper.append(self.get_terms_cover_rate(sentence, terms, term_num))
                result_cover_rate_wo_paper.append(self.get_terms_cover_rate(sentence_wo, terms, term_num))
            elif style == '中医科普论文':
                result_cover_rate_pos.append(self.get_terms_cover_rate(sentence, terms, term_num))
                result_cover_rate_wo_pos.append(self.get_terms_cover_rate(sentence_wo, terms, term_num))
            else:
                result_cover_rate_blog.append(self.get_terms_cover_rate(sentence, terms, term_num))
                result_cover_rate_wo_blog.append(self.get_terms_cover_rate(sentence_wo, terms, term_num))

        print("学术类型文章，共计{}篇，加入术语库覆盖率：{}，无术语库覆盖率：{}".format(len(result_cover_rate_paper),
                                                                                   sum(result_cover_rate_paper) / len(result_cover_rate_paper),
                                                                                   sum(result_cover_rate_wo_paper) / len(result_cover_rate_wo_paper)))
        print("科普类型文章，共计{}篇，加入术语库覆盖率：{}，无术语库覆盖率：{}".format(len(result_cover_rate_pos),
                                                                                   sum(result_cover_rate_pos) / len(result_cover_rate_pos),
                                                                                   sum(result_cover_rate_wo_pos) / len(result_cover_rate_wo_pos)))
        print("博客类型文章，共计{}篇，加入术语库覆盖率：{}，无术语库覆盖率：{}".format(len(result_cover_rate_blog),
                                                                                   sum(result_cover_rate_blog) / len(result_cover_rate_blog),
                                                                                   sum(result_cover_rate_wo_blog) / len(result_cover_rate_wo_blog)))


class TermsEvaluator:
    def __init__(self, terms_file, only_terms_file, chinese_file, outputs_path, outputs_without_terms):
        matcher = TermsMatcher(terms_file, only_terms_file, chinese_file, None, None)
        self.terms_match = matcher.match_terms()

        self.all_english_terms = []
        self.all_english_sentences = []
        self.all_english_sentences_wo_terms = []
        self.terms_num_per_sentence = []

        self.get_all_english_terms()
        self.read_english_sentences(outputs_path, self.all_english_sentences)
        self.read_english_sentences(outputs_without_terms, self.all_english_sentences_wo_terms)

    def read_english_sentences(self, file_path, list_container):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()

                if line != '>>>///>>>':
                    line = line.split('||')[1]
                    list_container.append(line)

    def get_all_english_terms(self):
        for term in self.terms_match:
            tmp = []
            english_term = term[-1]
            self.terms_num_per_sentence.append(len(english_term))
            for ws in english_term:
                ws = [w.lower() for w in ws]
                tmp.extend(ws)

            self.all_english_terms.append(tmp)

    def get_terms_cover_rate(self, english_sentence, terms_list, terms_num):
        english_sentence = english_sentence.lower()
        count = 0
        for term in terms_list:
            if term in english_sentence:
                count += 1

        return count / (terms_num + 1)

    def do_evaluate(self):
        result_cover_rate = []
        result_cover_rate_wo = []

        for sentence, sentence_wo, terms, term_num in zip(self.all_english_sentences, self.all_english_sentences_wo_terms,
                                                          self.all_english_terms, self.terms_num_per_sentence):
            result_cover_rate.append(self.get_terms_cover_rate(sentence, terms, term_num))
            result_cover_rate_wo.append(self.get_terms_cover_rate(sentence_wo, terms, term_num))

        return sum(result_cover_rate) / len(result_cover_rate), sum(result_cover_rate_wo) / len(result_cover_rate_wo)


if __name__ == '__main__':
    terms_evaluate = TermsEvaluator('terms/terms.csv', 'terms/only_terms.csv',
                                    'data/run_examples.txt', 'data/run_outputs_deepseek.txt',
                                    'data/run_outputs_without_terms_deepseek.txt')
    r1, r2 = terms_evaluate.do_evaluate()
    print("添加术语库后的术语覆盖率：{:.3f}%，无术语库的术语覆盖率：{:.3f}%".format(r1 * 100, r2 * 100))

    # terms_evaluate2 = TermsEvaluator2('terms/terms.csv', 'terms/only_terms.csv',
    #                                   'data/examples_outputs_deepseek.txt',
    #                                   'data/examples_outputs_without_terms_deepseek.txt')
    # terms_evaluate2.do_evaluate()
