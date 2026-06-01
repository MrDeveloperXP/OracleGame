"""
OracleHost — Ultra-Light Telegram Test Bot
Zero framework deps. Uses raw HTTP API + requests.
"""

import os
import random
import time
import logging
from typing import Optional

import requests

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_UPDATE = 0
GUESS_NUM: dict[int, int] = {}  # chat_id -> number


def send(chat_id: int, text: str) -> Optional[dict]:
    r = requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    return r.json() if r.ok else None


def handle(msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    name = msg["from"]["first_name"]

    if text == "/start":
        send(chat_id,
            f"👋 Hey {name}!\n"
            "This bot proves OracleHost Telegram hosting works.\n\n"
            "Commands:\n"
            "/guess — guess a number 1–10\n"
            "/dice — roll a die\n"
            "/ping — health check"
        )

    elif text == "/ping":
        send(chat_id, "🏓 *Pong!* Bot is alive. ✅")

    elif text == "/dice":
        faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        roll = random.randint(1, 6)
        send(chat_id, f"🎲 *{roll}* {faces[roll]}")

    elif text == "/guess":
        GUESS_NUM[chat_id] = random.randint(1, 10)
        send(chat_id, "🔢 I picked a number *1–10*. Type your guess!")

    elif text.isdigit() and chat_id in GUESS_NUM:
        guess = int(text)
        target = GUESS_NUM[chat_id]
        if guess == target:
            del GUESS_NUM[chat_id]
            send(chat_id, f"🎉 *Correct!* It was {target}.")
        else:
            hint = "⬆️ Higher!" if guess < target else "⬇️ Lower!"
            send(chat_id, f"{hint} Try again.")

    elif text:
        send(chat_id, f"Unknown command. Try /start")


def poll() -> None:
    global LAST_UPDATE
    params = {"timeout": 30, "offset": LAST_UPDATE + 1}
    try:
        r = requests.get(f"{API}/getUpdates", params=params, timeout=35)
        if not r.ok:
            return
        for update in r.json().get("result", []):
            LAST_UPDATE = update["update_id"]
            if "message" in update:
                handle(update["message"])
    except requests.exceptions.ReadTimeout:
        pass  # normal — long poll timeout
    except Exception as e:
        logger.error(f"Poll error: {e}")


def main() -> None:
    logger.info("🌀 OracleHost Test Bot starting (polling)...")
    # Verify token
    me = requests.get(f"{API}/getMe", timeout=10).json()
    if me.get("ok"):
        bot_user = me["result"]["username"]
        logger.info(f"✅ Authenticated as @{bot_user}")
    else:
        logger.error(f"❌ Token invalid: {me}")
        return

    while True:
        poll()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
