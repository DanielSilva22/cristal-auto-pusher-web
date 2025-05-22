from flask import Flask
import os
import json
import time
import threading
import requests

app = Flask(__name__)
QUEUE_DIR = "/tmp/gpt_autopush"
RELAY_URL = os.environ.get("RELAY_URL", "https://cristal-gpt-relay.onrender.com/relay")

def autopush_loop():
    print("AutoPusher Web Loop Running...")
    while True:
        try:
            if not os.path.exists(QUEUE_DIR):
                os.makedirs(QUEUE_DIR)
            for fname in sorted(os.listdir(QUEUE_DIR)):
                if fname.endswith(".json"):
                    fpath = os.path.join(QUEUE_DIR, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    res = requests.post(RELAY_URL, json=data)
                    if res.status_code == 200:
                        print(f"Pushed: {fname}")
                        os.remove(fpath)
                    else:
                        print(f"Failed push {fname}: {res.text}")
        except Exception as e:
            print("Error:", e)
        time.sleep(15)

@app.route("/")
def home():
    return "AutoPusher Web Service is active", 200

# Lancer la boucle auto en background
threading.Thread(target=autopush_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
