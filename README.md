# AI Chatbot with AIML (Python)

A production-ready chatbot using **AIML** for rule-based dialog, with Python integrations for utilities (weather, wiki, time) and a simple **Flask web UI** + **CLI**.

## Features
- AIML knowledge base (greetings, small talk, FAQs, tools/predicates)
- Fast boot using saved **brain** file
- Utility intents handled in Python:
  - `weather in <city>` via OpenWeather (requires API key)
  - `wiki <topic>` summary via Wikipedia
  - `time` / `date`
- Web UI (Flask) + CLI runner
- Session-based user variables (predicates) per user
- Easy to extend with your own `.aiml` files

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config.sample.json config.json  # then edit API keys
python app.py  # web UI at http://127.0.0.1:5000
# or
python cli_bot.py
```

## Project Structure
```
aiml_chatbot_project/
├─ app.py               # Flask web app
├─ cli_bot.py           # Terminal chatbot
├─ requirements.txt
├─ config.sample.json   # Copy to config.json with your secrets
├─ templates/
│  └─ index.html        # Web chat interface
├─ static/
│  └─ style.css         # Minimal styles
└─ aiml/
   ├─ startup.xml       # Loads all AIML sets
   ├─ std-greetings.aiml
   ├─ smalltalk.aiml
   ├─ faqs.aiml
   └─ tools.aiml
```

## Notes
- For OpenWeather, create a free account and add your key to `config.json`.
- Wikipedia summaries use the official API (no key needed).
- Keep adding AIML files in `/aiml` and include them from `startup.xml`.
- To persist learning/predicates across runs, the kernel saves `bot_brain.brn` automatically.
