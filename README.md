# OracleHost Deployment Test — Telegram Bot

Quick test to verify your Telegram hosting is working on OracleHost.

## Files

- `bot.py` — Number guessing game bot (python-telegram-bot v20+)
- `requirements.txt` — Dependencies

## Deploy

1. Set your bot token from [@BotFather](https://t.me/BotFather):
   - Set env var `BOT_TOKEN=your_token_here`

2. Either:
   - **Webhook mode**: Set `WEBHOOK_URL=https://your-app.oraclehost.site` → bot uses webhook
   - **Polling mode**: Leave `WEBHOOK_URL` empty → bot uses polling

3. Install:
   ```bash
   pip install -r requirements.txt
   ```

4. Run:
   ```bash
   python bot.py
   ```

## Commands

| Command   | Action                        |
|-----------|-------------------------------|
| `/start`  | Welcome menu with buttons     |
| `/guess`  | Play Guess the Number (1–50)  |
| `/dice`   | Roll a virtual die            |
| `/ping`   | Health check — pong!          |
| `/info`   | Bot status info               |
| `/cancel` | Cancel current game           |
