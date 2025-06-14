from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient, errors
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

# ============================
# Configure Logging
# ============================
logging.basicConfig(
    filename='webhook_app.log',          # Log file name
    level=logging.INFO,                  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# ============================
# Connect to MongoDB
# ============================
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["github_hooks"]
    collection = db["events"]
    logging.info("Connected to MongoDB successfully.")
except errors.ConnectionFailure as e:
    logging.error(f"MongoDB connection failed: {e}")
    raise

# ============================
# Routes
# ============================

@app.route('/')
def index():
    """
    Render the home page.
    """
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle GitHub webhook events.

    Expects JSON payload with 'X-GitHub-Event' header.
    Stores formatted data in MongoDB.
    """
    try:
        payload = request.get_json()
        event = request.headers.get('X-GitHub-Event')

        logging.info(f"Received event: {event}")
        logging.info(f"Payload: {payload}")

        data = {
            "request_id": request.headers.get('X-GitHub-Delivery'),
            "author": None,
            "action": None,
            "from_branch": None,
            "to_branch": None,
            "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC"),
            "created_at": datetime.now(timezone.utc)
        }

        if event == "push":
            data["author"] = payload.get("pusher", {}).get("name")
            data["action"] = "PUSH"
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
                data["action"] = payload.get("action", "").upper()

        collection.insert_one(data)
        logging.info("Event data inserted into MongoDB.")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """
    Retrieve webhook events from the last 15 seconds.
    """
    try:
        fifteen_sec_ago = datetime.now(timezone.utc) - timedelta(seconds=15)
        events = list(collection.find({"created_at": {"$gte": fifteen_sec_ago}}).sort("created_at", -1))

        for e in events:
            e["_id"] = str(e["_id"])
            e["created_at"] = e["created_at"].strftime("%d %B %Y - %I:%M:%S %p UTC")

        logging.info(f"Fetched {len(events)} events from the last 15 seconds.")
        return jsonify(events), 200
    except Exception as e:
        logging.error(f"Error fetching recent events: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================
# Run Flask App
# ============================
if __name__ == '__main__':
    logging.info("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
