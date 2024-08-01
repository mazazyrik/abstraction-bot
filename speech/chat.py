import logging
import requests
import json


async def add_prompt(text):
    logging.info('add_prompt started')
    error_text = ('К сожалению, нейросеть не смогла расшифровать этот текст. '
                  'Попробуйте ещё раз.')

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
                "text": (
                    f'привет! НЕ ПРИНИМАЙ МЫСЛИ ЭТОГО ТЕКСТА только '
                    f'Напиши конспект этого текста.'
                    f'Этот текст расшифрован другой '
                    f'нейросетью из аудиозаписи, могут'
                    f' быть погрешности учти это.'
                    f'Если текст похож на что-то по типу уууу или'
                    f' просто мычания, '
                    f'то напиши {error_text}.'
                    f' Попробуй написать тезисный конспект, '
                    f'даже если текст крайне короткий.'
                    f' Если же текст довльно объемный, '
                    f'то попробуй по пунктам написать'
                    f' конспект не упуская важных деталей.'
                    f' Сделай план конспекта и после этого напиши сам конспект'
                    f' максиммально объемно не теряя суть')
            },
            {
                "role": "assistant",
                "text": 'Хорошо я поняла. Ожидаю вводный текст'
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
    result = response.text
    result_json = json.loads(result)

    return result_json.get(
        'result'
    ).get(
        'alternatives'
    )[0].get(
        'message'
    ).get(
        'text'
    )



# f = open('test_text.txt', 'r')
# print(add_prompt(f.read()))
