from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.webview import WebView
import shutil
import os
import json
from datetime import datetime
import requests
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import io
import speech_recognition as sr
import threading

class MainApp(App):
    def build(self):
        self.copy_assets_once()
        layout = BoxLayout(orientation='vertical')
        webview = WebView()
        html_path = os.path.join(self.user_data_dir, "index.html")
        webview.source = f"file://{html_path}"
        layout.add_widget(webview)
        return layout

    def copy_assets_once(self):
        if not os.path.exists(os.path.join(self.user_data_dir, "init.flag")):
            shutil.copy("html/index.html", os.path.join(self.user_data_dir, "index.html"))
            shutil.copy("json/config.json", os.path.join(self.user_data_dir, "config.json"))
            with open(os.path.join(self.user_data_dir, "flash.json"), "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)
            with open(os.path.join(self.user_data_dir, "init.flag"), "w") as f:
                f.write("ok")

    def get_response(self, prompt, user_text):
        with open(os.path.join(self.user_data_dir, "config.json"), "r", encoding="utf-8") as f:
            config = json.load(f)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={config['API_KEY']}"
        headers = {"Content-Type": "application/json"}
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

    def recognize_and_save(self, audio_data):
        buffer = io.BytesIO()
        wavfile.write(buffer, 16000, audio_data)
        buffer.seek(0)
        r = sr.Recognizer()
        with sr.AudioFile(buffer) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio, language='ko-KR')
            if not text.strip():
                text = "인식 안됨"
        except:
            text = "인식 안됨"
        flash_path = os.path.join(self.user_data_dir, "flash.json")
        try:
            with open(flash_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
        data.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": text
        })
        with open(flash_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_and_summarize(self):
        recording = sd.rec(int(16000 * 5), samplerate=16000, channels=1, dtype='int16')
        sd.wait()
        self.recognize_and_save(recording.copy())

