import os
import requests
import feedparser

# --- SETTINGS ---
# Use a Nitter RSS link for mementomori_boi
RSS_URL = "https://nitter.poast.org/mementomori_boi/rss" 
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# THE "WANT" LIST (Triggers a notification)
WANT = [
    "maintenance", "メンテナンス", "メンテ", 
    "character", "新登場", "ラメント", "復刻", # New, Lament, Rerun
    "event", "イベント", "開催", 
    "anniversary", "周年", "記念", "キャンペーン"
]

# THE "IGNORE" LIST (Blocks notification even if WANT is present)
IGNORE = [
    "live", "生放送", "YouTube", 
    "grand battle", "グランドバトル", "グラバト",
    "guild battle", "ギルドバトル", "ギルバト",
    "version update", "アップデート", "Ver."
]

# --- THE LOGIC ---
feed = feedparser.parse(RSS_URL)

# Check the latest 3 tweets to catch everything since the last run
for entry in feed.entries[:3]:
    text = entry.title.lower()
    link = entry.link
    
    # Check IGNORE list first
    if any(x.lower() in text for x in IGNORE):
        print(f"Skipping (Ignored term found): {link}")
        continue
    
    # Check WANT list
    if any(x.lower() in text for x in WANT):
        payload = {"content": f"**MementoMori Update Found:**\n{link}"}
        requests.post(WEBHOOK_URL, json=payload)
        print(f"Sent to Discord: {link}")
