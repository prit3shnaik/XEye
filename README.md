# 👁️ XEye: X (Twitter) Monitor

XEye is a lightweight, serverless bot that tracks X accounts and sends notifications to Discord and Telegram. It runs entirely on **GitHub Actions**, meaning zero cost and zero hardware usage for you.

## 🚀 Features
- **No X API Required**: Uses guest-token scraping.
- **Dual Notifications**: Alerts sent to Discord Webhooks and Telegram Bots.
- **Remote Control**: Add new accounts to track directly via Telegram commands.
- **Serverless**: Runs every 15 minutes via GitHub Actions.

## 🛠️ Setup
1. **GitHub Secrets**: Add these in `Settings > Secrets > Actions`:
   - `GH_PAT`: Your GitHub Personal Access Token.
   - `TELEGRAM_TOKEN`: From @BotFather.
   - `TELEGRAM_CHAT_ID`: Your Chat ID.
   - `DISCORD_WEBHOOK`: Your Discord Webhook URL.

2. **Permissions**: 
   - Go to `Settings > Actions > General`.
   - Set **Workflow permissions** to `Read and write permissions`.

## 📱 Usage
Message your Telegram bot:
- `/track <username>` - Adds a new X user to the watch list.
- The bot checks for new posts every 15 minutes automatically.
