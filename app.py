from flask import Flask, request, jsonify
import os
import json
import time
import threading
import requests

app = Flask(__name__)
QUEUE_DIR = "/tmp/gpt_autopush"
RELAY_URL = os.environ.get("RELAY_URL", "https://cristal-gpt-relay.onrender.com/relay")

@app.route("/")
def home():
    return "AutoPusher Web Service v2 is active", 200

@app.route("/pushfile", methods=["POST"])
def receive_file():
    task = request.json
    fname = task.get("filename")
    data = task.get("data")
    if not fname or not data:
        return jsonify({"error": "Missing filename or data"}), 400
    os.makedirs(QUEUE_DIR, exist_ok=True)
    full_path = os.path.join(QUEUE_DIR, fname)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump({"filename": fname, "data": data}, f, indent=2, ensure_ascii=False)
    return jsonify({"status": "saved", "file": fname})

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
                        task = json.load(f)
                    res = requests.post(RELAY_URL, json=task)
                    if res.status_code == 200:
                        print(f"Pushed: {fname}")
                        os.remove(fpath)
                    else:
                        print(f"Failed push {fname}: {res.text}")
        except Exception as e:
            print("Error:", e)
        time.sleep(15)

# Démarrer le thread de fond
threading.Thread(target=autopush_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
