from TermsMapper import TermsMapper
from openai import OpenAI
import random
import pickle
from zhipuai import ZhipuAI


class GenExamples:
    def __init__(self, csv_path, output_path, generated_examples_path):
        terms_mapper = TermsMapper(csv_path, output_path)
        self.terms_mapper = list(terms_mapper.mapper.keys())

        self.examples_num = 512

        self.sys_prompt = "你是一个中医领域的专家，擅长中医学术论文、中医科普文章以及中医网络博客的编写。"
        self.user_prompt = (f"请根据给定的中医术语集生成一段风格化的文本，要求生成的文本尽量包含指定的术语集，包含的术语越多越好。\n"
                            "注意：输出只要生成的文本，不要包含其他内容或者格式信息，不要换行。\n"
                            "文本风格：{}\n"
                            "文本风格要求：{}\n"
                            "文本字数：不超过256个，不少于128个。\n"
                            "术语集：{}\n"
                            "再次强调，生成的文本里要尽可能多的包含给定术语集里的术语，但是如果术语集里的术语信息差异过大影响文本的可读性，"
                            "可以选择部分相关度高的术语进行文本生成，原则上应尽可能多的包含术语集里的术语。")

        self.text_style = ['中医学术论文', '中医科普论文', '中医网络博客']
        self.text_require = ["生成的文本要尽可能的符合中医学术论文的编写规范，严谨、逻辑自洽、用词专业规范。",
                             "生成的文本要尽可能的符合中医科普文章的编写风格，用词专业但可读性较强，不需要过多的专业知识也能流畅阅读。",
                             "生成的文本要尽可能的符合中医网络博客的编写风格，除了给定术语集里的专业术语外，无需太多专业词汇，内容贴近大众日常生活。"]

        # self.api_key = "sk-0e41552340714d2fb37eef3bc9dbfc13"
        # self.api_key = "29f0b108d8a84a1595b7ec48acbd7402.fvX0lHmuvfjnu1oR"
        self.api_key = "sk-4ab718a8e2524a579bed2bacc11cf001"

        self.generated_examples_path = generated_examples_path

        self.terms_style_list = []

    def gen_random_terms(self):
        return random.sample(self.terms_mapper, 8)

    def gen_random_style(self):
        index = [0, 1, 2]
        random_index = random.sample(index, 1)[0]

        return self.text_style[random_index], self.text_require[random_index]

    def gen_prompts(self):
        results = []

        for i in range(self.examples_num):
            random_terms = self.gen_random_terms()
            random_style = self.gen_random_style()

            self.terms_style_list.append((random_style[0], random_terms))

            prompt = self.user_prompt.format(random_style[0], random_style[1], str(random_terms))
            results.append(prompt)

        return results

    # def do_generate(self, sentence):
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

    def do_generate(self, sentence):
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

    # def do_generate(self, sentence):
    #     try:
    #         client = ZhipuAI(api_key=self.api_key)
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

    def generate_all(self):
        results = []

        all_sentences = self.gen_prompts()
        for i, sentence in enumerate(all_sentences):
            r = self.do_generate(sentence)
            print(r)
            print('{}/{}'.format(i + 1, len(all_sentences)))
            results.append(r)

        with open(self.generated_examples_path, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(r + '\n')
                f.write('>>>///>>>' + '\n')

        with open('terms_style_deepseek.pkl', 'wb') as f:
            pickle.dump(self.terms_style_list, f)


if __name__ == '__main__':
    gen = GenExamples('terms/terms.csv', 'terms/only_terms.csv', 'data/examples_deepseek.txt')
    gen.generate_all()

    with open('terms_style_deepseek.pkl', 'rb') as f:
        terms_style_list = pickle.load(f)

    print(terms_style_list)
