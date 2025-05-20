import subprocess
from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime
import requests

app = Flask(__name__)

os.makedirs("json", exist_ok=True)
if not os.path.exists("json/flash.json"):
    with open("json/flash.json", "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

with open("json/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
API_KEY = config["API_KEY"]

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"
headers = {"Content-Type": "application/json"}

summary_prompt = "다음 내용을 한국어로 2~4문장 요약해 줘. 설명 없이 요약만 출력해."
situation_prompt = "다음 대화 내용을 바탕으로 어떤 상황이었는지 분석해 줘. '학교에서 친구와 다툼', '기분 좋은 하루 시작', '스트레스받은 하루' 등 간결하게 말해 줘."

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        subprocess.run(["python", "stt.py"])
        return redirect(url_for("index"))

    try:
        with open("json/flash.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    return render_template("index.html", logs=logs)

@app.route("/summarize")
def summarize():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open("json/flash.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        return "flash.json 없음"

    today_logs = [entry["text"] for entry in logs if entry["time"].startswith(today)]
    if not today_logs:
        return "오늘 기록 없음"

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

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
