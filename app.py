import os
import json
import re
from datetime import datetime, date
from flask import Flask, request, render_template, jsonify
import aiml
import requests

APP_DIR = os.path.dirname(os.path.abspath(__file__))
AIML_DIR = os.path.join(APP_DIR, "aiml")
BRAIN_PATH = os.path.join(APP_DIR, "bot_brain.brn")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

# Load config
CONFIG = {}
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)

OPENWEATHER_KEY = CONFIG.get("openweather_api_key")

# Init Flask
app = Flask(__name__)

# One Kernel per process
kernel = aiml.Kernel()

def bootstrap_kernel():
    if os.path.exists(BRAIN_PATH):
        kernel.bootstrap(brainFile=BRAIN_PATH)
    else:
        # Load from startup, then save brain for faster startup next time
        kernel.bootstrap(learnFiles=os.path.join(AIML_DIR, "startup.xml"), commands="LOAD AIML B")
        kernel.saveBrain(BRAIN_PATH)

bootstrap_kernel()

def handle_util_intents(text: str):
    """
    Lightweight Python-side handlers for utility intents.
    Supported:
      - weather in <city>
      - wiki <topic>
      - time / date
    """
    t = text.lower().strip()

    # time/date
    if re.search(r'\b(time|current time|what time)\b', t):
        return datetime.now().strftime("The time is %H:%M:%S.")
    if re.search(r'\b(date|today\'?s date)\b', t):
        return date.today().strftime("Today's date is %B %d, %Y.")

    # weather
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
        except Exception as e:
            return "I couldn't fetch the weather right now."

    # wiki summary
    m = re.search(r'^(wiki|wikipedia)\s+(.+)$', t)
    if m:
        topic = m.group(2).strip()
        try:
            # Wikipedia API summary
            s_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(topic)
            r = requests.get(s_url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                extract = data.get("extract")
                if extract:
                    # Keep it concise
                    return extract[:600] + ("..." if len(extract) > 600 else "")
            return f"I couldn't find a summary for \"{topic}\"."
        except Exception:
            return "I couldn't reach Wikipedia right now."

    return None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    payload = request.get_json(force=True)
    user_id = payload.get("user_id", "anon")
    text = payload.get("message", "").strip()

    # Attach predicates per user
    kernel.setPredicate("userid", user_id, user_id)

    # First try utility intents
    util = handle_util_intents(text)
    if util:
        return jsonify({"reply": util})

    # Then AIML response
    reply = kernel.respond(text, user_id)
    if not reply:
        reply = "Sorry, I don't know that yet."
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
