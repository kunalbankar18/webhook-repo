from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
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
    data = request.json
    event = {
        "request_id": data.get("request_id"),
        "author": data.get("author"),
        "action": data.get("action"),
        "from_branch": data.get("from_branch"),
        "to_branch": data.get("to_branch"),
        "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
    }
    collection.insert_one(event)
    return jsonify({"message": "Event stored"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort("timestamp", -1))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)