"""
Chat handling module for SpeechAI bot.
Manages conversation flow, message processing, and AI responses.
Integrates with OpenAI API for natural language processing.
"""

import logging
import asyncio
from prompt import prompt as base_prompt
from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey

config = YandexGPTConfigManagerForAPIKey(
    model_type="yandexgpt-lite",
    catalog_id="b1g9b4dhssf7u0rot67t",
    api_key="AQVN2CNjLpFAwtwCIGbnhuOOegcF9Ac557YZBSmR"
)

yandex_gpt = YandexGPT(config_manager=config)


async def get_completion(text):
    msg = [{"role": "user", "text": base_prompt + text}]

    while True:
        try:
            completion = await yandex_gpt.get_async_completion(
                messages=msg, timeout=300, max_tokens=2000
            )
            logging.info('Chunk completed successfully.')
            return completion
        except Exception as e:
            if "429" in str(e):
                logging.warning(
                    "Received 429 error. Retrying in 15 seconds...")
                await asyncio.sleep(15)
            else:
                logging.error(f"Error in get_completion: {e}")
                return None


def slice_to_chunks(text):
    return [text[i:i + 5000] for i in range(0, len(text), 5000)]


async def get_text(chunks):
    results = []

    for i in range(0, len(chunks), 5):
        batch = chunks[i:i + 5]
        batch_results = await asyncio.gather(
            *(get_completion(chunk) for chunk in batch)
        )

        results.extend(filter(None, batch_results))

    return results


async def add_prompt(text):
    chunks = slice_to_chunks(text)
    full_text = await get_text(chunks)

    if not full_text:
        return "ошибка"

    return ' '.join(full_text)
