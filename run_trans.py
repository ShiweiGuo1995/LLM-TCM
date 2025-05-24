from flask import Flask, render_template, request, jsonify
import random
from TermsMapper import TermsMapper
from openai import OpenAI
from zhipuai import ZhipuAI

app = Flask(__name__, template_folder='templates', static_folder='static')


class RandomExample:
    def __init__(self, dataset_path):
        self.dataset = []

        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line != '>>>///>>>' and line != '///>>>///':
                    self.dataset.append(line)

    def get_random_example(self):
        return random.choice(self.dataset)


datasets = RandomExample('data/examples_deepseek.txt')


class Mapper:
    def __init__(self, terms_file, only_terms_file):
        self.mapper = TermsMapper(terms_file, only_terms_file)
        self.mapper = self.mapper.mapper

        self.term_items = self.mapper.items()

    def match_item(self, ch_sent):
        terms_contained = [term[0] for term in self.term_items if term[0] in ch_sent]

        if '' in terms_contained:
            terms_contained.remove('')
        english_terms = []

        for term in terms_contained:
            term = term.strip()
            english_terms.append(self.mapper[term])

        return terms_contained, english_terms


terms_mapper = Mapper('terms/terms.csv', 'terms/only_terms.csv')


class Translation:
    def __init__(self):
        deep_seek_api_key = 'sk-4ab718a8e2524a579bed2bacc11cf001'
        zhipu_api_key = '29f0b108d8a84a1595b7ec48acbd7402.fvX0lHmuvfjnu1oR'
        qwen_api_key = 'sk-0e41552340714d2fb37eef3bc9dbfc13'

        self.deep_seek = OpenAI(api_key=deep_seek_api_key, base_url="https://api.deepseek.com")
        self.qwen = OpenAI(api_key=qwen_api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.zhipu = ZhipuAI(api_key=zhipu_api_key)

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

        self.llm_dict = {'Qwen': 'qwen', 'Zhipu': 'zhipu', 'Deepseek': 'deep_seek'}

    def get_prompt(self, to_trans, chinese_terms, english_terms):
        ug_str = ""
        for i in range(len(chinese_terms)):
            ug_str += chinese_terms[i] + ': ' + str(english_terms[i]) + ', '

        prompt_str = self.user_prompt.format(to_trans, ug_str)

        return prompt_str

    def do_translate(self, to_trans, llm='deep_seek'):
        chinese_terms, english_terms = terms_mapper.match_item(to_trans)
        llm = self.llm_dict[llm]

        print(to_trans)
        print(chinese_terms)
        print(english_terms)
        print(llm)

        sentence = self.get_prompt(to_trans, chinese_terms, english_terms)
        if llm == 'deep_seek':
            try:
                completion = self.deep_seek.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {'role': 'system', 'content': self.sys_prompt},
                        {'role': 'user', 'content': sentence}
                    ],
                    stream=False
                )

                r = completion.choices[0].message.content

                return r.strip(), sentence, chinese_terms, english_terms
            except Exception as e:
                print(f"Error message: {e}")
                return 'None Response!'
        elif llm == 'qwen':
            try:
                completion = self.qwen.chat.completions.create(
                    model="qwen-turbo",
                    messages=[
                        {'role': 'system', 'content': self.sys_prompt},
                        {'role': 'user', 'content': sentence}
                    ]
                )

                r = completion.choices[0].message.content

                return r.strip(), sentence, chinese_terms, english_terms
            except Exception as e:
                print(f"Error message: {e}")
                return 'None Response!'
        elif llm == 'zhipu':
            try:
                completion = self.zhipu.chat.completions.create(
                    model="glm-4-plus",
                    messages=[
                        {'role': 'system', 'content': self.sys_prompt},
                        {'role': 'user', 'content': sentence}
                    ]
                )

                r = completion.choices[0].message.content

                return r.strip(), sentence, chinese_terms, english_terms
            except Exception as e:
                print(f"Error message: {e}")
                return 'None Response!'


translator = Translation()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/translate_random_example', methods=['POST'])
def random_example_button_click():
    example = datasets.get_random_example()
    return jsonify({'input_text': example})


@app.route('/do_translate', methods=['POST'])
def do_translate_button_click():
    data = request.json
    to_trans_text = data.get('to_trans_text')
    ll_name = data.get('llm_name')
    print(ll_name)

    results = translator.do_translate(to_trans_text, llm=ll_name)
    en_r = results[0]
    ch_terms, eng_terms = results[2], results[3]

    terms_str = ''
    for ch_t, en_ts in zip(ch_terms, eng_terms):
        terms_str += ch_t + ': ' + str(en_ts) + '<br>'

    prompt_text = results[1]

    print(to_trans_text)
    print(en_r)

    return jsonify({'output_text': en_r,  'terms': terms_str, 'prompt_text': prompt_text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
