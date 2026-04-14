import os
import requests
import feedparser

# --- CONFIG ---
# If this RSS link is empty, use RSS.app to get a fresh one for mementomori_boi
RSS_URL = "https://nitter.net/mementomori_boi/rss" 
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

WANT = ["maintenance", "メンテナンス", "メンテ", "character", "新登場", "ラメント", "復刻", "event", "イベント", "開催", "anniversary", "周年", "記念", "キャンペーン"]
IGNORE = ["live", "生放送", "YouTube", "grand battle", "グランドバトル", "グラバト", "guild battle", "ギルドバトル", "ギルバト", "version update", "アップデート", "Ver."]

# --- THE LOGIC ---
# First, send a status update to Discord to prove the connection is ALIVE
requests.post(WEBHOOK_URL, json={"content": "✅ **System Check:** Script is running on Node 24. Checking feed now..."})

feed = feedparser.parse(RSS_URL)

if not feed.entries:
    # If the feed is blocked/empty, tell Discord so you know why there are no tweets
    requests.post(WEBHOOK_URL, json={"content": "❌ **RSS Error:** The Twitter feed is empty. Twitter is blocking the current RSS link."})
else:
    found_any = False
    for entry in feed.entries[:5]:
        text = entry.title.lower()
        if any(x.lower() in text for x in IGNORE):
            continue
        if any(x.lower() in text for x in WANT):
            requests.post(WEBHOOK_URL, json={"content": f"**MementoMori Update Found:**\n{entry.link}"})
            found_any = True
    
    if not found_any:
        print("Feed was read successfully, but no matching tweets were found today.")
