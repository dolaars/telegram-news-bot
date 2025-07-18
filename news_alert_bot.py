import requests
from datetime import datetime
import time
import os

# === Configuration ===
TE_API_KEY = os.getenv("TE_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === Helper Functions ===

def get_today_events():
    url = f"https://api.tradingeconomics.com/calendar/country/all?c={TE_API_KEY}"
    print("Fetching events from TradingEconomics API...")
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error fetching calendar:", response.text)
        return []

    events = response.json()
    print(f"✅ Total events fetched: {len(events)}")
    today = datetime.utcnow().date()
    high_impact_events = []

    for event in events:
        try:
            event_date = datetime.fromisoformat(event["Date"]).date()
            if event_date == today and event.get("Importance") == 3:
                high_impact_events.append(event)
        except Exception as e:
            print("⚠️ Error parsing event:", e)
            continue

    print(f"📌 High-impact events today: {len(high_impact_events)}")
    return high_impact_events


def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    print(f"📨 Sent message to Telegram. Status: {response.status_code}")
    if response.status_code != 200:
        print("❌ Telegram error:", response.text)

# === Main Bot Loop ===

print("🚀 News Alert Bot is starting...")
send_telegram_alert("✅ Bot test: Telegram alert is working!")  # Optional test message

sent_events = set()

while True:
    events = get_today_events()
    for event in events:
        uid = event.get("Event") + event.get("Date")
        if uid not in sent_events:
            msg = (
                f"⚠️ <b>{event.get('Country')}</b>: <b>{event.get('Event')}</b>\n"
                f"🕒 {event.get('Date')}\n👥 Impact: HIGH"
            )
            send_telegram_alert(msg)
            sent_events.add(uid)

    print("🔁 Sleeping for 5 minutes...")
    time.sleep(300)  # Wait 5 minutes

