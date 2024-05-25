import logging
import shutil
import time
from slicer import slice_audio
import os
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


def main(audio: str) -> str:
    logging.info('main started')
    dir_name = audio.split(".")[0].lower()

    slice_audio(audio)
    logging.info('slice completed')
    lsdir = os.listdir(dir_name)
    lsdir_reversed = lsdir[::-1]

    threads = [transcribe_audio_thread(
        f'{dir_name}/{file}') for file in lsdir_reversed]
    logging.info('threads created')

    res = ''.join(thread for thread in threads)

    res_text = add_prompt(res)
    shutil.rmtree(dir_name)
    logging.info('speech completed')
    return res_text


if __name__ == "__main__":
    print(main())

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Время Исполнения: ', elapsed_time)
