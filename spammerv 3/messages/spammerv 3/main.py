import requests
import time
import json
import random
from datetime import datetime, timedelta

DISCORD_API = "https://discord.com/api/v9/channels/{}/messages"


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_message(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def send_message(token, channel_id, message):
    url = DISCORD_API.format(channel_id)
    headers = {"Authorization": token}
    payload = {"content": message}

    r = requests.post(url, json=payload, headers=headers)

    if r.status_code == 200:
        print(f"✅ Gönderildi → {channel_id}")
        return True

    if r.status_code == 429:
        retry = r.json().get("retry_after", 1)
        print(f"⚠️ Rate limit! {retry}s bekleniyor")
        time.sleep(retry)
        return send_message(token, channel_id, message)

    print(f"❌ Hata {r.status_code} → {channel_id}")
    return False


def main():
    config = load_config()
    token = config["token"]
    channels = config["channels"]

    global_delay = config["global_delay_seconds"]
    channel_cooldown = timedelta(seconds=config["channel_cooldown_seconds"])

    # kanal son gönderim zamanları
    last_sent = {c["channel_id"]: None for c in channels}

    print("🚀 Cooldown-aware scheduler başladı")

    while True:
        random.shuffle(channels)  # 🔀 KANAL SIRASI HER TUR RASTGELE

        now = datetime.utcnow()
        sent_any = False

        for item in channels:
            cid = item["channel_id"]
            last_time = last_sent[cid]

            if last_time and now - last_time < channel_cooldown:
                continue  # cooldown dolmamış

            message = load_message(item["message_file"])

            if send_message(token, cid, message):
                last_sent[cid] = now
                sent_any = True
                break  # BU TURDA SADECE 1 MESAJ

        if not sent_any:
            print("⏳ Uygun kanal yok, cooldown bekleniyor...")

        delay = random.randint(
            global_delay - 120,
            global_delay + 120
        )

        print(f"🕒 {delay//60} dk bekleniyor...\n")
        time.sleep(delay)


if __name__ == "__main__":
    main()
