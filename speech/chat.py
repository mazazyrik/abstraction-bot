import asyncio
import requests
import logging
from prompt import prompt as text_prompt
from threads import ThreadWithReturnValue


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
                "text": text_prompt
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


def get_text_thread(text):
    logging.info('get_text_thread started')
    thread = ThreadWithReturnValue(target=summarize_text, args=(text,))
    thread.start()
    return thread


async def get_text(chunks):
    loop = asyncio.get_event_loop()

    threads = (
        [
            await loop.run_in_executor(
                None, get_text_thread, chunk,
            ) for chunk in chunks
        ]
    )

    return threads


async def add_prompt(text):
    logging.info('add_prompt started')

    text_len = len(text)
    num_chunks = -(-text_len // 4096)
    summaries = []
    logging.info(f'number of chunks is {num_chunks}')

    for i in range(num_chunks):
        chunk = text[i * 4096:(i + 1) * 4096]
        summaries.append(chunk)
    stop_flag = False
    threads = await get_text(summaries)
    stop_flag = True
    while not stop_flag:
        await asyncio.sleep(0.2)

    final_summary = ' '.join(thread for thread in threads)

    return final_summary
