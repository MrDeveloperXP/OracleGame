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
ADMIN_IDS_RAW = os.environ.get("ADMIN_ID", "")  # comma-separated Telegram user IDs
ADMIN_IDS = {int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()}
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_UPDATE = 0
GUESS_NUM: dict[int, int] = {}  # chat_id -> number
TOTAL_UPDATES = 0
START_TIME = time.time()


def send(chat_id: int, text: str) -> Optional[dict]:
    r = requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
    return r.json() if r.ok else None


def send_action(chat_id: int, action: str) -> None:
    """Send chat action (typing, etc.) so the user sees a visual indicator."""
    requests.post(f"{API}/sendChatAction", json={"chat_id": chat_id, "action": action}, timeout=5)


# ── Trivia data ──────────────────────────────────────────────────────────────

CAT_FACTS = [
    "A cat's brain is 90% similar to a human's.",
    "Cats sleep 70% of their lives.",
    "A group of cats is called a clowder.",
    "Cats can't taste sweetness.",
    "The oldest known pet cat existed 9,500 years ago.",
    "A cat's nose print is as unique as a human's fingerprint.",
    "Cats have 32 muscles in each ear.",
    "Cats can rotate their ears 180 degrees.",
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
    "What's a programmer's favourite hangout place? The Foo Bar.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: \"Can I join you?\"",
    "There are only 10 kinds of people: those who understand binary and those who don't.",
    "Why do Java developers wear glasses? Because they can't C#.",
]

QUOTES = [
    "\"The best way to predict the future is to invent it.\" — Alan Kay",
    "\"Any sufficiently advanced technology is indistinguishable from magic.\" — Arthur C. Clarke",
    "\"Simplicity is prerequisite for reliability.\" — Edsger W. Dijkstra",
    "\"The function of good software is to make the complex appear to be simple.\" — Grady Booch",
    "\"First, solve the problem. Then, write the code.\" — John Johnson",
    "\"Talk is cheap. Show me the code.\" — Linus Torvalds",
    "\"Programming isn't about what you know; it's about what you can figure out.\" — Chris Pine",
]

WEATHER_CONDITIONS = ["☀️ Sunny", "⛅ Partly Cloudy", "☁️ Overcast", "🌧️ Rainy", "⛈️ Thunderstorm", "🌤️ Clear Sky", "🌫️ Foggy"]
WEATHER_CITIES = ["New York", "Tokyo", "London", "Berlin", "Moscow", "Dubai", "Singapore", "Sydney"]

# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_start(chat_id: int, name: str) -> None:
    send(
        chat_id,
        "👋 Hey {}!\n"
        "OracleHost Bot v2.0 — now with more features!\n\n"
        "Commands:\n"
        "/guess — guess a number 1-10\n"
        "/dice — roll a die\n"
        "/ping — health check\n"
        "/cat — random cat fact 🐱\n"
        "/joke — programmer joke 😄\n"
        "/quote — inspirational quote 💡\n"
        "/weather — fake weather report 🌤️\n"
        "/echo <text> — echo your message\n"
        "/stats — bot stats *(admin only)* 📊\n"
        "/broadcast <msg> — test broadcast *(admin only)* 📢".format(name),
    )


def cmd_ping(chat_id: int) -> None:
    send(chat_id, "🏓 *Pong!* Bot is healthy. ✅")


def cmd_dice(chat_id: int) -> None:
    faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    roll = random.randint(1, 6)
    send(chat_id, f"🎲 *{roll}* {faces[roll]}")


def cmd_guess_start(chat_id: int) -> None:
    GUESS_NUM[chat_id] = random.randint(1, 10)
    send(chat_id, "🔢 I picked a number *1–10*. Type your guess!")


def cmd_guess_play(chat_id: int, text: str) -> None:
    guess = int(text)
    target = GUESS_NUM[chat_id]
    if guess == target:
        del GUESS_NUM[chat_id]
        send(chat_id, f"🎉 *Correct!* It was {target}.")
    else:
        hint = "⬆️ Higher!" if guess < target else "⬇️ Lower!"
        send(chat_id, f"{hint} Try again.")


def cmd_cat(chat_id: int) -> None:
    send_action(chat_id, "typing")
    fact = random.choice(CAT_FACTS)
    send(chat_id, f"🐱 *Cat Fact:* {fact}")


def cmd_joke(chat_id: int) -> None:
    send_action(chat_id, "typing")
    joke = random.choice(JOKES)
    send(chat_id, f"😄 {joke}")


def cmd_quote(chat_id: int) -> None:
    send_action(chat_id, "typing")
    quote = random.choice(QUOTES)
    send(chat_id, f"💡 {quote}")


def cmd_weather(chat_id: int) -> None:
    send_action(chat_id, "find_location")
    city = random.choice(WEATHER_CITIES)
    temp = random.randint(-5, 42)
    condition = random.choice(WEATHER_CONDITIONS)
    humidity = random.randint(20, 95)
    wind = random.randint(0, 40)
    send(
        chat_id,
        f"🌤️ *Weather Report*\n"
        f"📍 {city}\n"
        f"🌡️ {temp}°C — {condition}\n"
        f"💧 Humidity: {humidity}%\n"
        f"💨 Wind: {wind} km/h",
    )


def cmd_echo(chat_id: int, args: str) -> None:
    if not args:
        send(chat_id, "Usage: /echo <message>")
        return
    send(chat_id, f"🗣️ *Echo:* {args}")


def cmd_stats(chat_id: int, user_id: int) -> None:
    """Admin-only: show bot stats."""
    if user_id not in ADMIN_IDS:
        send(chat_id, "⛔ *Access denied.* This command is for admins only.")
        return
    uptime_secs = time.time() - START_TIME
    hours = int(uptime_secs // 3600)
    mins = int((uptime_secs % 3600) // 60)
    secs = int(uptime_secs % 60)
    send(
        chat_id,
        f"📊 *Bot Statistics*\n"
        f"⏱️ Uptime: {hours}h {mins}m {secs}s\n"
        f"📨 Updates handled: `{TOTAL_UPDATES}`\n"
        f"👥 Active guess games: `{len(GUESS_NUM)}`\n"
        f"🆔 Your ID: `{user_id}`",
    )


def cmd_broadcast(chat_id: int, user_id: int, args: str) -> None:
    """Admin-only: broadcast a message. (placeholder — just echoes intent)"""
    if user_id not in ADMIN_IDS:
        send(chat_id, "⛔ *Access denied.* This command is for admins only.")
        return
    if not args:
        send(chat_id, "Usage: /broadcast <message>")
        return
    send(chat_id, f"📢 *Broadcast ready:* `{args}`\n*(Feature not fully implemented — this is a test)*")


# ── Message handler ──────────────────────────────────────────────────────────


def handle(msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    name = msg["from"]["first_name"]

    if text == "/start":
        cmd_start(chat_id, name)

    elif text == "/ping":
        cmd_ping(chat_id)

    elif text == "/dice":
        cmd_dice(chat_id)

    elif text == "/guess":
        cmd_guess_start(chat_id)

    elif text == "/cat":
        cmd_cat(chat_id)

    elif text == "/joke":
        cmd_joke(chat_id)

    elif text == "/quote":
        cmd_quote(chat_id)

    elif text == "/weather":
        cmd_weather(chat_id)

    elif text == "/stats":
        cmd_stats(chat_id, msg["from"]["id"])

    elif text.startswith("/broadcast"):
        cmd_broadcast(chat_id, msg["from"]["id"], text[11:].strip())

    elif text.startswith("/echo"):
        cmd_echo(chat_id, text[5:].strip())

    elif text.isdigit() and chat_id in GUESS_NUM:
        cmd_guess_play(chat_id, text)

    elif text:
        send(chat_id, "Unknown command. Try /start")


def poll() -> None:
    global LAST_UPDATE, TOTAL_UPDATES
    params = {"timeout": 30, "offset": LAST_UPDATE + 1}
    try:
        r = requests.get(f"{API}/getUpdates", params=params, timeout=35)
        if not r.ok:
            return
        for update in r.json().get("result", []):
            LAST_UPDATE = update["update_id"]
            if "message" in update:
                TOTAL_UPDATES += 1
                handle(update["message"])
    except requests.exceptions.ReadTimeout:
        pass  # normal — long poll timeout
    except Exception as e:
        logger.error(f"Poll error: {e}")


def main() -> None:
    logger.info("🌀 OracleHost Test Bot v2.0 starting (polling)...")
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
