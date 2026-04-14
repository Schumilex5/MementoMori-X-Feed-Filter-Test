import os
import requests
import feedparser

# --- SETTINGS ---
# Using a different Nitter instance in case the old one was blocked
RSS_URL = "https://nitter.privacydev.net/mementomori_boi/rss" 
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

WANT = ["maintenance", "メンテナンス", "メンテ", "character", "新登場", "ラメント", "復刻", "event", "イベント", "開催", "anniversary", "周年", "記念", "キャンペーン", "test"] # I added "test" here
IGNORE = ["live", "生放送", "YouTube", "grand battle", "グランドバトル", "グラバト", "guild battle", "ギルドバトル", "ギルバト", "version update", "アップデート", "Ver."]

# --- THE LOGIC ---
print(f"Checking feed: {RSS_URL}")
feed = feedparser.parse(RSS_URL)

if not feed.entries:
    print("!! ERROR: The RSS feed is totally empty. We need a new RSS URL.")
else:
    print(f"Success: Found {len(feed.entries)} tweets. Checking for matches...")

for entry in feed.entries[:5]:
    text = entry.title.lower()
    link = entry.link
    print(f"Analyzing tweet: {text[:50]}...")

    if any(x.lower() in text for x in IGNORE):
        print(f"X Rejected (Ignore list): {link}")
        continue
    
    # If it matches WANT list OR contains "test"
    if any(x.lower() in text for x in WANT):
        payload = {"content": f"**MementoMori Update:**\n{link}"}
        res = requests.post(WEBHOOK_URL, json=payload)
        print(f">> SENT TO DISCORD! Status Code: {res.status_code}")
