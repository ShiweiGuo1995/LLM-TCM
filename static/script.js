$(document).ready(function() {
    $('#random_example_btn').click(function() {
        $.ajax({
            type: 'POST',
            url: '/translate_random_example',
            success: function(response) {
                $('#input_text').text(response.input_text);
            },
            error: function() {
                $('#input_text').text('出错了，请重试！');
            }
        });
    });

    $('#translate_btn').click(function() {
        $('#output_text').text('正在翻译中，请稍后...');
        $('#terms_div').text('正在检索术语，请稍后...');
        $('#prompt_text_div').text('正在生成提示词，请稍后...');
        var to_trans_text = $('#input_text').val();
        var llm_name = $('#llm_select').val();
        $.ajax({
            type: 'POST',
            url: '/do_translate',
            contentType: 'application/json',
            data: JSON.stringify({ to_trans_text:  to_trans_text, llm_name: llm_name}),
            success: function(response) {
                $('#output_text').text(response.output_text);
                $('#terms_div').html(response.terms);
                $('#prompt_text_div').html(response.prompt_text);
            },
            error: function() {
                $('#output_text').text('出错了，请重试！');
            }
        });
    });
});

// document.getElementById('random_example_btn').addEventListener('click', async () => {
//     const inputText = "random a example"
//
//     // 发送请求到后端
//     const response = await fetch('/translate_random_example', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ text: inputText }),
//     });
//
//     const result = await response.json();
//
//     document.getElementById('input_text').value = result.input_text;
// });
//
//
// document.getElementById('translateBtn').addEventListener('click', async () => {
//     const inputText = document.getElementById('inputA').value;
//
//     // 发送请求到后端
//     const response = await fetch('/translate', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ text: inputText }),
//     });
//
//     const result = await response.json();
//
//     // 更新文本框B和C的内容
//     document.getElementById('outputB').value = result.translated_text; // 假设返回的JSON中有这个字段
//     document.getElementById('outputC').value = result.other_info; // 假设返回的JSON中有其他信息
// });
