import os
import requests
import feedparser
import sys

# --- CONFIG ---
# Using a 2026-tested Nitter instance
RSS_URL = "https://nitter.net/mementomori_boi/rss" 
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Check if the secret is missing before doing anything else
if not WEBHOOK_URL:
    print("!! ERROR: DISCORD_WEBHOOK_URL not found in Secrets. Check your repo settings.")
    sys.exit(1)

WANT = ["maintenance", "メンテナンス", "メンテ", "character", "新登場", "ラメント", "復刻", "event", "イベント", "開催", "anniversary", "周年", "記念", "キャンペーン"]
IGNORE = ["live", "生放送", "YouTube", "grand battle", "グランドバトル", "グラバト", "guild battle", "ギルドバトル", "ギルバト", "version update", "アップデート", "Ver."]

# --- THE LOGIC ---
try:
    print(f"Connecting to: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("RSS feed is empty. Sending status to Discord.")
        requests.post(WEBHOOK_URL, json={"content": "⚠️ Filter active, but the RSS feed is currently empty (Twitter blocking)."})
    else:
        print(f"Checking {len(feed.entries)} tweets...")
        for entry in feed.entries[:5]:
            text = entry.title.lower()
            if any(x.lower() in text for x in IGNORE):
                continue
            if any(x.lower() in text for x in WANT):
                requests.post(WEBHOOK_URL, json={"content": f"**MementoMori Update:**\n{entry.link}"})

except Exception as e:
    print(f"Script Error: {e}")
    sys.exit(1)
