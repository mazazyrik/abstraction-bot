import whisper
import ssl
import torch
ssl._create_default_https_context = ssl._create_unverified_context


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class Speech():

    def __init__(self, model='medium', device=DEVICE, download_root='models'):
        self.model = whisper.load_model(model, download_root=download_root)
        self.device = device

    def transcribe_audio(self, audio_file: str) -> str:
        audio = whisper.load_audio(audio_file)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.device)
        options = whisper.DecodingOptions(language="ru")
        result = whisper.decode(self.model, mel, options)
        return result.text

    def __call__(self, audio_file):
        return self.transcribe_audio(audio_file)
