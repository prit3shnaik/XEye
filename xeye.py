import os
import json
import requests
import base64
import asyncio
from discord_webhook import DiscordWebhook

# --- CONFIGURATION (Loaded from GitHub Secrets) ---
TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK")
GH_TOKEN = os.getenv("GH_PAT")
REPO = os.getenv("GITHUB_REPOSITORY")  # Format: "username/repo"

# --- HELPER FUNCTIONS ---

def send_notifications(user, text, url):
    """Sends alerts to Discord and Telegram."""
    msg = f"👁️ **XEye Alert: {user}**\n\n{text}\n\n{url}"
    
    # Discord
    if DISCORD_URL:
        try:
            DiscordWebhook(url=DISCORD_URL, content=msg).execute()
        except Exception as e:
            print(f"Discord Error: {e}")

    # Telegram
    if TELE_TOKEN and TELE_CHAT_ID:
        tele_api = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        try:
            requests.post(tele_api, json={"chat_id": TELE_CHAT_ID, "text": msg})
        except Exception as e:
            print(f"Telegram Error: {e}")

def update_github_json(new_users):
    """Updates usernames.json in your repo via GitHub API."""
    url = f"https://api.github.com/repos/{REPO}/contents/usernames.json"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Get current file info to get the 'sha' (required for updates)
    curr_file = requests.get(url, headers=headers).json()
    sha = curr_file.get("sha")
    
    content_b64 = base64.b64encode(json.dumps(new_users).encode()).decode()
    payload = {
        "message": "XEye: Update monitored users",
        "content": content_b64,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)

async def handle_commands():
    """Checks Telegram for new /track or /untrack commands."""
    if not TELE_TOKEN: return
    
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/getUpdates"
    updates = requests.get(url).json().get("result", [])
    
    if not updates: return

    with open("usernames.json", "r") as f:
        users = json.load(f)
    
    changed = False
    for up in updates:
        text = up.get("message", {}).get("text", "")
        # Command: /track username
        if text.startswith("/track "):
            new_user = text.split(" ")[1].strip().replace("@", "")
            if new_user not in users:
                users.append(new_user)
                changed = True
        # Command: /untrack username
        elif text.startswith("/untrack "):
            target = text.split(" ")[1].strip().replace("@", "")
            if target in users:
                users.remove(target)
                changed = True

    if changed:
        update_github_json(users)

# --- MAIN MONITORING LOGIC ---

def run_monitor():
    """Checks X for new posts."""
    if not os.path.exists("usernames.json"):
        with open("usernames.json", "w") as f: json.dump([], f)
        return

    with open("usernames.json", "r") as f:
        target_users = json.load(f)

    history = {}
    if os.path.exists("last_seen.json"):
        with open("last_seen.json", "r") as f:
            try: history = json.load(f)
            except: history = {}

    for user in target_users:
        try:
            # Using vxtwitter API for no-login scraping
            resp = requests.get(f"https://api.vxtwitter.com/{user}", timeout=10).json()
            tweet_id = resp.get("id_str")
            
            if tweet_id and history.get(user) != tweet_id:
                tweet_text = resp.get("text", "No text content")
                tweet_url = f"https://x.com/{user}/status/{tweet_id}"
                
                send_notifications(user, tweet_text, tweet_url)
                history[user] = tweet_id
                print(f"Success: New post from {user}")
        except Exception as e:
            print(f"Error checking {user}: {e}")

    # Save progress
    with open("last_seen.json", "w") as f:
        json.dump(history, f)

if __name__ == "__main__":
    # 1. Look for new commands from you on Telegram
    asyncio.run(handle_commands())
    # 2. Check X for new posts
    run_monitor()
