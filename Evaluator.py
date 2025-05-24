import pandas as pd
import time
from openai import OpenAI
from terms_matcher import TermsMatcher
from collections import Counter
from zhipuai import ZhipuAI


class Evaluator:
    def __init__(self, terms_file, only_terms_file, chinese_file, english_file, parallel_file, output_path, output_without_terms_path):
        self.output_path = output_path
        self.output_without_terms_path = output_without_terms_path

        matcher = TermsMatcher(terms_file, only_terms_file, chinese_file, english_file, parallel_file)
        self.terms_match = matcher.match_terms()

        self.chinese = []
        self.english_terms = []
        self.english = []

        self.sys_prompt = "你是一个中医领域的专家，并且精通中文和英文。"
        self.user_prompt = (f"请根据原始中文，评判以下两个英文译文的质量，评判的标准：1、译文整体信息的完整性与语法正确性，1-5分，分值越高表示越好；"
                            "2、译文中中医术语的翻译是否与给定的中英术语对照一致或相似，1-5分，译文中中医术语翻译出现在中英术语对照的数目越多分值越高。\n"
                            "输出只返回译文质量更好（得分更高）的译文的编号，例如,如果译文1更好，则输出1，反之输出2，不要包含其他内容或者格式。\n"
                            "中文文本：{}\n"
                            "中英术语对照：{}\n"
                            "译文1：{}\n"
                            "译文2：{}")

        self.read_file(output_path)
        self.read_file(output_without_terms_path, mode='naive')

        self.terms_str = self.get_terms_str()

        # self.api_key = "sk-0e41552340714d2fb37eef3bc9dbfc13"
        # self.api_key = "29f0b108d8a84a1595b7ec48acbd7402.fvX0lHmuvfjnu1oR"
        self.api_key = "sk-4ab718a8e2524a579bed2bacc11cf001"

    def read_file(self, file_path, mode='terms'):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != '>>>///>>>':
                    chinese, english = line.split('||')
                    if mode == 'terms':
                        self.chinese.append(chinese)
                        self.english_terms.append(english)
                    else:
                        self.english.append(english)

    def get_terms_str(self):
        results = []

        for item in self.terms_match:
            chinese_terms = item[1]
            english_terms = item[2]

            ug_str = ""
            for i in range(len(chinese_terms)):
                ug_str += chinese_terms[i] + ': ' + str(english_terms[i]) + ', '
            results.append(ug_str)

        return results

    def gen_evaluation_prompt(self):
        results = []

        for i, item in enumerate(self.chinese):
            prompt = self.user_prompt.format(self.chinese[i], self.terms_str[i], self.english_terms[i], self.english[i])
            results.append(prompt)

        return results

    # def do_evaluation(self, sentence):
    #     try:
    #         client = OpenAI(
    #             api_key=self.api_key,
    #             base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    #         )
    #
    #         completion = client.chat.completions.create(
    #             model="qwen-turbo",
    #             messages=[
    #                 {'role': 'system', 'content': self.sys_prompt},
    #                 {'role': 'user', 'content': sentence}
    #             ]
    #         )
    #
    #         r = completion.choices[0].message.content
    #
    #         return r.strip()
    #     except Exception as e:
    #         print(f"Error message: {e}")

    def do_evaluation(self, sentence):
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )

            completion = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {'role': 'system', 'content': self.sys_prompt},
                    {'role': 'user', 'content': sentence}
                ],
                stream=False
            )

            r = completion.choices[0].message.content

            return r.strip()
        except Exception as e:
            print(f"Error message: {e}")
            return 'None Response!'

    # def do_evaluation(self, sentence):
    #     try:
    #         client = ZhipuAI(api_key=self.api_key)
    #
    #         completion = client.chat.completions.create(
    #             model="glm-4-plus",
    #             messages=[
    #                 {'role': 'system', 'content': self.sys_prompt},
    #                 {'role': 'user', 'content': sentence}
    #             ]
    #         )
    #
    #         r = completion.choices[0].message.content
    #
    #         return r.strip()
    #     except Exception as e:
    #         print(f"Error message: {e}")

    def eval_all(self):
        results = []

        all_sentences = self.gen_evaluation_prompt()
        for sentence in all_sentences:
            r = self.do_evaluation(sentence)
            print(r)
            results.append(r)

        count = Counter(results)
        print(count)

        return results


if __name__ == '__main__':
    evaluator = Evaluator('terms/terms.csv', 'terms/only_terms.csv',
                          'data/run_examples.txt', None, None,
                          "data/run_outputs_deepseek.txt", "data/run_outputs_without_terms_deepseek.txt")
    rs = evaluator.eval_all()
    # rs = evaluator.gen_evaluation_prompt()
    # print(rs[1])
