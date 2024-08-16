import requests
import logging


def summarize_text(text):
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
                         "пользователям в написании конспектов.")
            },
            {
                "role": "user",
                "text": text
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2CNjLpFAwtwCIGbnhuOOegcF9Ac557YZBSmR"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result_json = response.json()

    try:
        res = result_json.get('result').get('alternatives')[
            0].get('message').get('text')
    except (AttributeError, IndexError):
        res = (
            'Нейросеть не смогла расшифровать этот текст. '
            'Попробуйте ещё раз.\n\n'
            'Если вы делали разбор файла, то проверьте не состоит ли '
            'он из картинок.\n\n'
            'Если вы делали разбор аудио, то проверьте не '
            'состоит ли он из тишины.'
        )
    return res


def add_prompt(text):
    logging.info('add_prompt started')

    text_len = len(text)
    num_chunks = -(-text_len // 4096)
    summaries = []

    for i in range(num_chunks):
        chunk = text[i * 4096:(i + 1) * 4096]
        summary = summarize_text(chunk)
        summaries.append(summary)

    final_summary = summarize_text(' '.join(summaries))

    return final_summary
