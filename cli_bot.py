import os
import json
import aiml
import re
from datetime import datetime, date
import requests

APP_DIR = os.path.dirname(os.path.abspath(__file__))
AIML_DIR = os.path.join(APP_DIR, "aiml")
BRAIN_PATH = os.path.join(APP_DIR, "bot_brain.brn")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

CONFIG = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)

OPENWEATHER_KEY = CONFIG.get("openweather_api_key")

kernel = aiml.Kernel()

def bootstrap_kernel():
    if os.path.exists(BRAIN_PATH):
        kernel.bootstrap(brainFile=BRAIN_PATH)
    else:
        kernel.bootstrap(learnFiles=os.path.join(AIML_DIR, "startup.xml"), commands="LOAD AIML B")
        kernel.saveBrain(BRAIN_PATH)

def handle_util_intents(text: str):
    t = text.lower().strip()
    if re.search(r'\b(time|current time|what time)\b', t):
        return datetime.now().strftime("The time is %H:%M:%S.")
    if re.search(r'\b(date|today\'?s date)\b', t):
        return date.today().strftime("Today's date is %B %d, %Y.")
    m = re.search(r'weather\s+in\s+([a-zA-Z\s\-\.]+)$', t)
    if m and OPENWEATHER_KEY:
        city = m.group(1).strip().title()
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric"}
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if data.get("cod") != 200:
                return f"Sorry, I couldn't find weather for {city}."
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            feels = data["main"].get("feels_like")
            return f"Weather in {city}: {desc}, {temp}°C (feels like {feels}°C)."
        except Exception:
            return "I couldn't fetch the weather right now."
    m = re.search(r'^(wiki|wikipedia)\s+(.+)$', t)
    if m:
        topic = m.group(2).strip()
        try:
            s_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(topic)
            r = requests.get(s_url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                if extract:
                    return extract[:600] + ("..." if len(extract) > 600 else "")
            return f"I couldn't find a summary for \"{topic}\"."
        except Exception:
            return "I couldn't reach Wikipedia right now."
    return None

if __name__ == "__main__":
    bootstrap_kernel()
    print("🤖 AIML Chatbot (type 'quit' to exit)")
    user_id = "cli-user"
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if text.lower() == "quit":
            print("Bye!")
            break

        util = handle_util_intents(text)
        if util:
            print("Bot:", util)
            continue

        reply = kernel.respond(text, user_id)
        if not reply:
            reply = "Sorry, I don't know that yet."
        print("Bot:", reply)
