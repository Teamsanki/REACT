import requests
import random
import threading
import time

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        self.last_update_id = None
        self.emojis = ["❤️", "🔥", "👍", "😂", "🎉"]
        self.running = True

    def send_reaction(self, chat_id, message_id):
        emoji = random.choice(self.emojis)
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji, "is_big": True}]
        }
        res = requests.post(self.api_url + "setMessageReaction", json=payload)
        print(f"Reaction sent by bot {self.token[:10]}: {res.json()}")

    def run(self):
        while self.running:
            try:
                params = {"timeout": 10}
                if self.last_update_id:
                    params["offset"] = self.last_update_id
                res = requests.get(self.api_url + "getUpdates", params=params)
                data = res.json()
                if data.get("ok"):
                    for update in data["result"]:
                        self.last_update_id = update["update_id"] + 1

                        # Handle /clone command only for this bot
                        if "message" in update and "text" in update["message"]:
                            text = update["message"]["text"]
                            chat_id = update["message"]["chat"]["id"]
                            message_id = update["message"]["message_id"]

                            if text.startswith("/clone "):
                                # This bot won't clone itself; cloning handled externally
                                token_to_clone = text.split(" ", 1)[1].strip()
                                # Just send confirmation message here (actual cloning outside)
                                requests.post(self.api_url + "sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": f"Received clone command with token:\n{token_to_clone}"
                                })
                            else:
                                # Normal message - react to it
                                self.send_reaction(chat_id, message_id)

                        # Also react to other messages like channel_post if needed
                        for key in ["channel_post", "edited_message", "edited_channel_post"]:
                            if key in update:
                                msg = update[key]
                                self.send_reaction(msg["chat"]["id"], msg["message_id"])
            except Exception as e:
                print("Error:", e)
            time.sleep(1)

    def stop(self):
        self.running = False


# Main bot token (your original bot)
main_bot_token = "7298664300:AAGRodfJgGnwdjq9QcHSbT-Hx0r4jQF7980"
main_bot = TelegramBot(main_bot_token)

# Dictionary to hold cloned bots
cloned_bots = {}

def start_bot(token):
    bot = TelegramBot(token)
    cloned_bots[token] = bot
    thread = threading.Thread(target=bot.run)
    thread.daemon = True
    thread.start()
    return bot

# Start main bot
main_thread = threading.Thread(target=main_bot.run)
main_thread.daemon = True
main_thread.start()

print("Main bot running...")

# Simple way to listen for clone commands from main bot and start new bot
# Here, polling used; for production use webhook or better approach
while True:
    # This polling is only to detect clone command from main bot updates
    try:
        params = {"timeout": 10}
        if main_bot.last_update_id:
            params["offset"] = main_bot.last_update_id
        res = requests.get(main_bot.api_url + "getUpdates", params=params)
        data = res.json()

        if data.get("ok"):
            for update in data["result"]:
                main_bot.last_update_id = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    text = update["message"]["text"]
                    if text.startswith("/clone "):
                        token_to_clone = text.split(" ", 1)[1].strip()
                        if token_to_clone not in cloned_bots:
                            print(f"Cloning new bot with token: {token_to_clone}")
                            start_bot(token_to_clone)
                        else:
                            print("This bot is already cloned and running.")
    except Exception as e:
        print("Error in main clone listener:", e)
    time.sleep(2)
