import requests
import random
import time

BOT_TOKEN = "7590753386:AAFzciQ6_CqU5XMdDwqVOS4DCVGg8c4B95k"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

a = ["❤️", "🔥", "👍", "😂", "🎉"]
last_update_id = None

while True:
    res = requests.get(API_URL + "getUpdates", params={"offset": last_update_id, "timeout": 10})
    data = res.json()

    if data.get("ok"):
        for update in data["result"]:
            last_update_id = update["update_id"] + 1

            # Check agar message ya channel_post aaye
            for key in ["message", "channel_post"]:
                if key in update:
                    msg = update[key]
                    chat_id = msg["chat"]["id"]
                    message_id = msg["message_id"]
                    emoji = random.choice(a)

                    payload = {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "reaction": [{"type": "emoji", "emoji": emoji, "is_big": True}]
                    }

                    r = requests.post(API_URL + "setMessageReaction", json=payload)
                    print(r.json())

    time.sleep(1)
