import pydub
import os


def slice_audio(audio_file: str):
    dir_name = audio_file.split(".")[0].lower()
    os.mkdir(dir_name)
    audio = pydub.AudioSegment.from_file(audio_file, format="mp3")
    num_slices = len(audio) // 30000 + 1

    for i in range(num_slices):
        start = i * 30000
        end = min((i + 1) * 30000, len(audio))
        slice = audio[start:end]
        slice.export(f"{dir_name}/output_{i}.mp3", format="mp3")
