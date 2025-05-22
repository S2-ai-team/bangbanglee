import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import io
import speech_recognition as sr
import json
from datetime import datetime
import requests
import threading

with open("json/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
API_KEY = config["API_KEY"]

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"
headers = {"Content-Type": "application/json"}

summary_prompt = "다음 내용을 한국어로 2~4문장 요약해 줘. 설명 없이 요약만 출력해."
situation_prompt = "다음 대화 내용을 바탕으로 어떤 상황이었는지 분석해 줘. '학교에서 친구와 다툼', '기분 좋은 하루 시작', '스트레스받은 하루' 등 간결하게 말해 줘."

samplerate = 16000
duration = 5
r = sr.Recognizer()

repeat = 10

def recognize_and_save(audio_data, index):
    buffer = io.BytesIO()
    wavfile.write(buffer, samplerate, audio_data)
    buffer.seek(0)

    with sr.AudioFile(buffer) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio, language='ko-KR')
        if not text.strip():
            text = "인식 안됨"
    except:
        text = "인식 안됨"

    print(f"[{index+1}] {text}")

    try:
        with open("json/flash.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text
    })

    with open("json/flash.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

threads = []

for i in range(repeat):
    print(f"[{i+1}] Recording...")
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    t = threading.Thread(target=recognize_and_save, args=(recording.copy(), i))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

def get_response(prompt, user_text):
    chat_history = [
        {"role": "user", "parts": [{"text": prompt}]},
        {"role": "user", "parts": [{"text": user_text}]}
    ]
    data = {"contents": chat_history}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return "error: " + response.text

def summarize_today():
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        with open("json/flash.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        print("no flash.json")
        return

    today_logs = [entry["text"] for entry in logs if entry["time"].startswith(today)]
    if not today_logs:
        print("no data")
        return

    combined_text = "\n".join(today_logs)
    summary = get_response(summary_prompt, combined_text)
    situation = get_response(situation_prompt, combined_text)

    try:
        with open("json/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    data[today] = {
        "summary": summary.strip(),
        "situation": situation.strip()
    }

    with open("json/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Saved in data.json.")

summarize_today()
