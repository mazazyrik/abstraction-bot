import asyncio
import aiohttp
import logging


async def start_async_operation(text):
    prompt = {
        "modelUri": "gpt://b1g9b4dhssf7u0rot67t/yandexgpt/latest",
        "completionOptions": {
            "stream": True,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVN2CNjLpFAwtwCIGbnhuOOegcF9Ac557YZBSmR"
    }

    async with aiohttp.ClientSession() as session:
        for attempt in range(5):  # Максимум 5 попыток
            async with session.post(url, headers=headers, json=prompt) as response:
                if response.status == 429:
                    # Экспоненциальная задержка
                    await asyncio.sleep(2 ** attempt)
                    continue  # Повторить попытку
                response.raise_for_status()
                result_json = await response.json()
                return result_json.get('id')
    raise Exception("Exceeded maximum retries for start_async_operation")


async def summarize_text(text):
    # Ваша логика для обработки текста
    return await start_async_operation(text)


async def get_text(chunks):
    sem = asyncio.Semaphore(5)  # Ограничение на 5 параллельных запросов

    async def sem_task(chunk):
        async with sem:
            return await summarize_text(chunk)

    tasks = [asyncio.create_task(sem_task(chunk)) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    return results


async def add_prompt(text):
    logging.info('add_prompt started')

    if isinstance(text, str):
        text = text.encode('utf-8').decode('utf-8')

    text_len = len(text)
    num_chunks = -(-text_len // 10_000)
    summaries = []
    logging.info(f'number of chunks is {num_chunks}')

    for i in range(num_chunks):
        chunk = text[i * 10_000:(i + 1) * 10_000]
        summaries.append(chunk)

    threads = await get_text(summaries)
    final_summary = ' '.join(threads)

    return final_summary
