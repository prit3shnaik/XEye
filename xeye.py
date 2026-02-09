import os, json, requests
from discord_webhook import DiscordWebhook

def notify(user, text, url):
    msg = f"👁️ XEye Alert: {user}\n{text}\n{url}"
    # Send to Telegram
    requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('TELEGRAM_CHAT_ID'), "text": msg})
    # Send to Discord
    DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'), content=msg).execute()

def check():
    # Load users and history
    with open("usernames.json", "r") as f: users = json.load(f)
    history = {}
    if os.path.exists("last_seen.json"):
        with open("last_seen.json", "r") as f: history = json.load(f)

    for user in users:
        try:
            r = requests.get(f"https://api.vxtwitter.com/{user}").json()
            tid = r.get("id_str")
            if tid and history.get(user) != tid:
                notify(user, r.get("text", ""), f"https://x.com/{user}/status/{tid}")
                history[user] = tid
        except: continue

    with open("last_seen.json", "w") as f: json.dump(history, f)

if __name__ == "__main__": check()
