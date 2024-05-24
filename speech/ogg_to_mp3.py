from pydub import AudioSegment


def to_mp3(file):
    sound = AudioSegment.from_file(file)
    sound.export(f"{file.split('.')[0]}.mp3", format="mp3", bitrate="128k")
