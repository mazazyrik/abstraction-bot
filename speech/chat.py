import logging
import requests
import json
from prompt import prompt as text_prompt


def add_prompt(text):
    logging.info('add_prompt started')

    prompt = {
        "modelUri": "gpt://b1g9b4dhssf7u0rot67t/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": ("Ты ассистент который помогает "
                         "пользователям в написании конспектов."
                         )
            },
            {
                "role": "user",
                "text": text_prompt
            },
            {
                "role": "assistant",
                "text": 'Хорошо я поняла. Ожидаю вводный текст'
            },

        ]
    }
    text_len = len(text)
    num_chunks = -(-text_len // 4096)
    for i in range(num_chunks):
        chunk = text[i * 4096:(i + 1) * 4096]
        prompt['messages'].append(
            {
                "role": "user",
                "text": chunk
            }
        )

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2CNjLpFAwtwCIGbnhuOOegcF9Ac557YZBSmR"
    }
    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    result_json = json.loads(result)
    try:
        res = result_json.get(
            'result'
        ).get(
            'alternatives'
        )[0].get(
            'message'
        ).get(
            'text'
        )
    except AttributeError:
        res = (
            'Нейросеть не смогла расшифровать этот текст. '
            f'Попробуйте ещё раз.\n\n'
            'Если вы делали разбор файла, то проверьте не состоит ли '
            f'он из картинок.\n\n'
            'Если вы делали разбор аудио, то проверьте не '
            'состоит ли он из тишины.'
        )
    return res
