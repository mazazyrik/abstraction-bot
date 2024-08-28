import logging
import aiohttp
import asyncio
import json


async def send_request(session, prompt):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2CNjLpFAwtwCIGbnhuOOegcF9Ac557YZBSmR"
    }

    while True:
        async with session.post(url, headers=headers, json=prompt) as response:
            if response.status == 429:
                logging.warning(
                    'Received 429 Too Many Requests. Retrying after delay...')
                await asyncio.sleep(5)  # Задержка перед повторной попыткой
                continue

            result = await response.text()
            result_json = json.loads(result)

            try:
                res = result_json.get('result').get('alternatives')[
                    0].get('message').get('text')
                return res  # Возвращаем результат
            except (AttributeError, IndexError):
                return (
                    'Нейросеть не смогла расшифровать этот текст. '
                    'Попробуйте ещё раз.\n\n'
                    'Если вы делали разбор файла, то проверьте не состоит ли '
                    'он из картинок.\n\n'
                    'Если вы делали разбор аудио, то проверьте не '
                    'состоит ли он из тишины.'
                )


async def add_prompt(text):
    logging.info('add_prompt started')

    prompt = {
        "modelUri": "gpt://b1g9b4dhssf7u0rot67t/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
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
            },
            {
                "role": "assistant",
                "text": 'Хорошо я поняла. Ожидаю вводный текст'
            },
        ]
    }

    text_len = len(text)
    num_chunks = -(-text_len // 4096)
    prompts = []

    for i in range(num_chunks):
        chunk = text[i * 4096:(i + 1) * 4096]
        prompt_copy = prompt.copy() 
        prompt_copy['messages'].append(
            {
                "role": "user",
                "text": chunk
            }
        )
        prompts.append(prompt_copy)

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, p) for p in prompts]
        results = await asyncio.gather(*tasks)

    return results
