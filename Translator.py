import pandas as pd
from openai import OpenAI
from terms_matcher import TermsMatcher
import time
from zhipuai import ZhipuAI


class Translator:
    def __init__(self, terms_file, only_terms_file, chinese_file, english_file, parallel_file):
        matcher = TermsMatcher(terms_file, only_terms_file, chinese_file, english_file, parallel_file)
        self.to_trans = matcher.match_terms()

        self.sys_prompt = "你是一个中医领域的专家，并且精通中文和英文。"
        self.user_prompt = (f"请将以下文本翻译成英文，要求译文尽可能的符合中医领域的翻译规范，并且参考所给出的部分中英文术语对照。\n"
                            "输出只要翻译的文本，不要包含其他信息或者格式，输出结果不要分行。\n"
                            "待翻译文本：{}\n"
                            "中英文术语对照：[{}]\n"
                            "一个中文术语可能对应多个英文术语，根据语境自行选择。需要注意，术语对照中可能存在一定的噪声或者错误，可以适当的放弃部分对照，自行翻译术语，"
                            "但原则上，术语需要尽可能的按照提供的对照进行翻译。对于不在提供的术语对照中的术语，尽可能的按照中医翻译规范进行翻译。\n"
                            "再次强调，在翻译顺畅的前提下，一定要尽可能的利用上给定的术语对照。")
        self.sys_prompt_without_terms = "You are a helpful assistant."
        self.user_prompt_without_terms = (f"请将以下文本翻译成英文，要求输出只要翻译的文本，不要包含其他信息或者格式，输出结果不要分行。\n"
                                          "待翻译文本：{}")

        # self.api_key = "sk-0e41552340714d2fb37eef3bc9dbfc13"
        # self.api_key = "29f0b108d8a84a1595b7ec48acbd7402.fvX0lHmuvfjnu1oR"
        self.api_key = "sk-4ab718a8e2524a579bed2bacc11cf001"

        # self.path_outputs = "data/outputs_examples.txt"
        # self.path_outputs_without_terms = "data/outputs_examples_without_terms.txt"

        self.path_outputs = "data/run_outputs_deepseek.txt"
        self.path_outputs_without_terms = "data/run_outputs_without_terms_deepseek.txt"

    def gen_trans_prompt(self, mode):
        results = []
        if mode == 'terms':
            user_prompt = self.user_prompt
        else:
            user_prompt = self.user_prompt_without_terms

        for item in self.to_trans:
            sentence = item[0]
            chinese_terms = item[1]
            english_terms = item[2]

            ug_str = ""
            for i in range(len(chinese_terms)):
                ug_str += chinese_terms[i] + ': ' + str(english_terms[i]) + ', '

            if mode == 'terms':
                prompt_str = user_prompt.format(sentence, ug_str)
            else:
                prompt_str = user_prompt.format(sentence)
            results.append(prompt_str)

        return results

    # def do_translate(self, sentence, mode):
    #     if mode == 'terms':
    #         sys_prompt = self.sys_prompt
    #     else:
    #         sys_prompt = self.sys_prompt_without_terms
    #
    #     try:
    #         client = OpenAI(
    #             api_key=self.api_key,
    #             base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    #         )
    #
    #         completion = client.chat.completions.create(
    #             model="qwen-turbo",
    #             messages=[
    #                 {'role': 'system', 'content': sys_prompt},
    #                 {'role': 'user', 'content': sentence}
    #             ]
    #         )
    #
    #         r = completion.choices[0].message.content
    #
    #         return r.strip()
    #     except Exception as e:
    #         print(f"Error message: {e}")

    def do_translate(self, sentence, mode):
        if mode == 'terms':
            sys_prompt = self.sys_prompt
        else:
            sys_prompt = self.sys_prompt_without_terms

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
            )

            completion = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {'role': 'system', 'content': sys_prompt},
                    {'role': 'user', 'content': sentence}
                ],
                stream=False
            )

            r = completion.choices[0].message.content

            return r.strip()
        except Exception as e:
            print(f"Error message: {e}")
            return 'None Response!'

    # def do_translate(self, sentence, mode):
    #     if mode == 'terms':
    #         sys_prompt = self.sys_prompt
    #     else:
    #         sys_prompt = self.sys_prompt_without_terms
    #
    #     try:
    #         client = ZhipuAI(api_key=self.api_key)
    #
    #         completion = client.chat.completions.create(
    #             model="glm-4-plus",
    #             messages=[
    #                 {'role': 'system', 'content': sys_prompt},
    #                 {'role': 'user', 'content': sentence}
    #             ]
    #         )
    #
    #         r = completion.choices[0].message.content
    #
    #         return r.strip()
    #     except Exception as e:
    #         print(f"Error message: {e}")

    def translate_all(self, out_path, mode='terms'):
        all_outputs = []

        to_trans_sentences = self.gen_trans_prompt(mode)
        for i, sentence in enumerate(to_trans_sentences):
            all_outputs.append(self.do_translate(sentence, mode))
            print(all_outputs[-1])
            print('done...{}/{}'.format(i + 1, len(to_trans_sentences)))

            time.sleep(1.5)

        with open(out_path, 'w', encoding='utf-8') as f:
            for sentence, output in zip(self.to_trans, all_outputs):
                f.write(sentence[0] + '||' + output + '\n')
                f.write('>>>///>>>' + '\n')


if __name__ == '__main__':
    translator = Translator('terms/terms.csv', 'terms/only_terms.csv',
                            'data/run_examples.txt', None, None)
    translator.translate_all(translator.path_outputs)
