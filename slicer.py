import pydub

audio = pydub.AudioSegment.from_file("input.mp3", format="mp3")

num_slices = len(audio) // 30000 + 1

for i in range(num_slices):
    start = i * 30000
    end = min((i + 1) * 30000, len(audio))
    slice = audio[start:end]
    slice.export(f"output_{i}.mp3", format="mp3")