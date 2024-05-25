import logging
import shutil
import time
from slicer import slice_audio
import os
import asyncio
from speech import Speech
from threads import ThreadWithReturnValue
from chat import add_prompt
start_time = time.time()


sp = Speech()


def transcribe_audio_thread(audio_file: str):
    thread = ThreadWithReturnValue(
        target=sp.transcribe_audio, args=(audio_file,))
    thread.start()
    return thread.join()


async def transcribe_task(dir_name, lsdir_reversed):
    loop = asyncio.get_event_loop()
    threads = (
        [
            await loop.run_in_executor(
                None, transcribe_audio_thread, f'{dir_name}/{file}',
            ) for file in lsdir_reversed
        ]
    )
    return threads


async def main(audio: str) -> str:
    logging.info('main started')
    dir_name = audio.split(".")[0].lower()

    slice_audio(audio)

    logging.info('slice completed')
    lsdir = os.listdir(dir_name)
    lsdir_reversed = lsdir[::-1]
    stop_flag = False
    threads = await transcribe_task(dir_name, lsdir_reversed)
    stop_flag = True
    while not stop_flag:
        await asyncio.sleep(0.2)
    res_text = await add_prompt(''.join(thread for thread in threads))
    shutil.rmtree(dir_name)
    logging.info('speech completed')
    return res_text


if __name__ == "__main__":
    main()
    end_time = time.time()
    elapsed_time = end_time - start_time
