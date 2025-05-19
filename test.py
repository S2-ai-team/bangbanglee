import sounddevice as sd
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer
import wave
import json

samplerate = 16000
duration = 5
device_index = 1  # 마이크 장치 번호

print("녹음 시작...")
recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16', device=device_index)
sd.wait()
write("output.wav", samplerate, recording)
print("녹음 완료 → output.wav 저장")


