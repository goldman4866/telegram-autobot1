from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_USER_ID = os.getenv("TARGET_USER_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ??????? ??? ???????? message_id ? user_id
replies = {}

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_photo(chat_id, file_id, caption=""):
    url = f"{API_URL}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": file_id, "caption": caption}
    requests.post(url, json=payload)

def send_video(chat_id, file_id, caption=""):
    url = f"{API_URL}/sendVideo"
    payload = {"chat_id": chat_id, "video": file_id, "caption": caption}
    requests.post(url, json=payload)

def send_voice(chat_id, file_id):
    url = f"{API_URL}/sendVoice"
    payload = {"chat_id": chat_id, "voice": file_id}
    requests.post(url, json=payload)

def send_document(chat_id, file_id, caption=""):
    url = f"{API_URL}/sendDocument"
    payload = {"chat_id": chat_id, "document": file_id, "caption": caption}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" not in data:
        return "ok", 200

    message = data["message"]
    sender = message["from"].get("username", "Unknown")
    chat_id = message["chat"]["id"]

    # --- INCOMING FROM USERS ---
    if str(chat_id) != str(TARGET_USER_ID):
        replies[message["message_id"]] = chat_id

        if "text" in message:
            text = message["text"]
            forward = f"From @{sender}:{text}"
            send_message(TARGET_USER_ID, forward)
            send_message(chat_id, "Message received.")

        elif "photo" in message:
            file_id = message["photo"][-1]["file_id"]
            caption = message.get("caption", f"Photo from @{sender}")
            send_photo(TARGET_USER_ID, file_id, caption)
            send_message(chat_id, "Photo received.")

        elif "video" in message:
            file_id = message["video"]["file_id"]
            caption = message.get("caption", f"Video from @{sender}")
            send_video(TARGET_USER_ID, file_id, caption)
            send_message(chat_id, "Video received.")

        elif "voice" in message:
            file_id = message["voice"]["file_id"]
            send_voice(TARGET_USER_ID, file_id)
            send_message(chat_id, "Voice message received.")

        elif "document" in message:
            file_id = message["document"]["file_id"]
            caption = message.get("caption", f"Document from @{sender}")
            send_document(TARGET_USER_ID, file_id, caption)
            send_message(chat_id, "Document received.")

    # --- REPLIES FROM YOU ---
    elif "reply_to_message" in message:
        replied_text = message["reply_to_message"].get("text", "")
        recipient_id = None
        for user_id in set(replies.values()):
            if replied_text.startswith("From @"):
                recipient_id = user_id
                break

        if recipient_id:
            if "text" in message:
                send_message(recipient_id, message["text"])
            elif "photo" in message:
                file_id = message["photo"][-1]["file_id"]
                caption = message.get("caption", "")
                send_photo(recipient_id, file_id, caption)
            elif "video" in message:
                file_id = message["video"]["file_id"]
                caption = message.get("caption", "")
                send_video(recipient_id, file_id, caption)
            elif "voice" in message:
                file_id = message["voice"]["file_id"]
                send_voice(recipient_id, file_id)
            elif "document" in message:
                file_id = message["document"]["file_id"]
                caption = message.get("caption", "")
                send_document(recipient_id, file_id, caption)

    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True)
