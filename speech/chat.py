import logging
import aiohttp
import asyncio
import json


async def send_request(session, prompt):
    url = 'https://300.ya.ru/api/sharing-url'
    headers = {
        # "Content-Type": "application/json",
        'Authorization': 'OAuth y0_AgAAAABYuub4AAoX4wAAAAEPLLlYAAC2U7V0IuRI-51UzcHKb09sWTD3Qg'
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
        'article_url': ''
    }

    text_len = len(text)
    num_chunks = -(-text_len // 10_000)
    prompts = []

    for i in range(num_chunks):
        chunk = text[i * 10_000:(i + 1) * 10_000]
        prompt['text'] = chunk
        prompts.append(prompt)

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, p) for p in prompts]
        results = await asyncio.gather(*tasks)

    return '/n'.join(results)
