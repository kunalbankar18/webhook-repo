from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime,timezone
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client["github_hooks"]
collection = db["events"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_json()
    event = request.headers.get('X-GitHub-Event')

    print(f"Received event: {event}")
    print(payload)

    data = {
        "request_id": request.headers.get('X-GitHub-Delivery'),
        "author": None,
        "action": None,
        "from_branch": None,
        "to_branch": None,
        "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
    }

    if event == "push":
        data["author"] = payload.get("pusher", {}).get("name")
        data["action"] = "push"
        data["to_branch"] = payload.get("ref", "").split("/")[-1]

    elif event == "pull_request":
        pr = payload.get("pull_request", {})
        data["author"] = pr.get("user", {}).get("login")
        data["from_branch"] = pr.get("head", {}).get("ref")
        data["to_branch"] = pr.get("base", {}).get("ref")
        is_merged = pr.get("merged", False)

        if payload.get("action") == "closed" and is_merged:
            data["action"] = "MERGE"
        else:
            data["action"] = payload.get("action").upper()

    collection.insert_one(data)
    return jsonify({"status": "success"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort("timestamp", -1))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)