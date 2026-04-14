import os
import requests
from bs4 import BeautifulSoup

def run_filter():
    # --- CONFIGURATION ---
    rss_url = "https://rss.app/feeds/gNSWbxS89cf9JqaP.xml"
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    
    # --- REFINED KEYWORDS ---
    WANT_KEYWORDS = [
        "新キャラ", "登場", "実装", "ラメント", "lament", "cv", "song by",
        "予告", "メンテ", "アップデート", "開催", "復刻", "update", "maintenance",
        "運命ガチャ", "ピックアップ", "布告", "告知"
    ] 

    IGNORE_KEYWORDS = [
        "キャンペーン", "プレゼント", "抽選", "リツイート", "フォロー", 
        "giveaway", "retweet", "campaign", "thank you", "記念", "amazonギフト"
    ]

    if not webhook_url:
        print("CRITICAL ERROR: DISCORD_WEBHOOK is not set.")
        return

    try:
        response = requests.get(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('item')

        if not items:
            return

        # We only process the LATEST tweet to avoid spamming the channel
        # RSS feeds are sorted newest to oldest.
        for item in items[:3]: # Check only the 3 most recent to stay current
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            
            # 1. Clean the link to use fxtwitter for the "Ideal" big image look
            clean_link = link.replace("x.com", "fxtwitter.com").replace("twitter.com", "fxtwitter.com")
            
            full_text = title.lower()

            # 2. Filter Logic
            if any(word.lower() in full_text for word in IGNORE_KEYWORDS):
                continue

            if any(word.lower() in full_text for word in WANT_KEYWORDS):
                # 3. Construct the clean message
                # No embeds, just plain text + fxtwitter link = Clean "Kepler" look
                message = f"{title}\n\n{clean_link}"
                
                payload = {
                    "username": "MementoMori Official",
                    "avatar_url": "https://mementomori.jp/favicon.ico",
                    "content": message
                }
                
                requests.post(webhook_url, json=payload)
                print(f"Sent: {title[:30]}")
                # Break after sending the most recent match to prevent spam
                break 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_filter()
