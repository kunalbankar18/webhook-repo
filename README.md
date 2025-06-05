# 📘 webhook-repo – GitHub Webhook Receiver with Flask + MongoDB

This repository implements a **Flask-based webhook receiver** for GitHub events like `push`, `pull_request`, and `merge`. It stores events in MongoDB and displays them in a simple UI that updates every 15 seconds.

---

## 📦 Features

- Receives GitHub Webhook events from `action-repo`
- Stores events in MongoDB with a structured schema
- Serves a clean UI that polls MongoDB every 15 seconds
- Displays formatted messages for:
  - `Push`
  - `Pull Request`
  - `Merge`

---

## 🧑‍💻 Tech Stack

- Python 3.x
- Flask
- MongoDB (local or Atlas)
- HTML + JavaScript (for polling UI)

---

## 🚀 Getting Started

### 1️⃣ Clone this repo
```bash
git clone https://github.com/yourusername/webhook-repo.git
cd webhook-repo
```

### 2️⃣ Install dependencies
```bash
pip install flask pymongo
```

### 3️⃣ Set up MongoDB

Make sure MongoDB is running locally at:
```
mongodb://localhost:27017
```

Or use a cloud URI by exporting it:
```bash
export MONGO_URI="your_mongo_connection_string"
```

### 4️⃣ Run Flask App
```bash
python app.py
# or
flask run
```

By default, it runs on: [http://localhost:5000](http://localhost:5000)

---

## ✨ Endpoints

### `/webhook` (POST)
Receives GitHub events and stores them in MongoDB.

Example Payload:
```json
{
  "request_id": "abc123",
  "author": "kunalbankar",
  "action": "PUSH",
  "from_branch": "",
  "to_branch": "main",
  "timestamp": "5th June 2025 - 2:00 PM UTC"
}
```

### `/events` (GET)
Returns the list of events in JSON format for frontend polling.

### `/` (GET)
Loads a simple HTML UI that fetches and displays events every 15 seconds.

---

## 🧪 Testing the Webhook Locally

### 🔸 With Postman or `curl`:
```bash
curl -X POST http://localhost:5000/webhook \
     -H "Content-Type: application/json" \
     -d '{
           "request_id": "test123",
           "author": "kunal",
           "action": "PULL_REQUEST",
           "from_branch": "dev",
           "to_branch": "main",
           "timestamp": "5th June 2025 - 4:00 PM UTC"
         }'
```

### 🔹 With GitHub

Use this as the **Webhook URL** in your `action-repo`:
```
http://<your-server>/webhook
```

To test it locally with public access:
```bash
ngrok http 5000
```

Use the generated ngrok URL as the webhook endpoint.

---

## 🗂 MongoDB Schema

Collection: `events`  
Example Document:
```json
{
  "request_id": "abc123",
  "author": "kunalbankar",
  "action": "PUSH",
  "from_branch": "",
  "to_branch": "main",
  "timestamp": "5th June 2025 - 2:00 PM UTC"
}
```

---

## 🧼 UI Sample

Displays entries like:

- `kunal pushed to main on 5th June 2025 - 2:00 PM UTC`
- `kunal submitted a pull request from dev to main on 5th June 2025 - 4:00 PM UTC`
- `kunal merged branch staging to master on 6th June 2025 - 12:00 PM UTC`

---
