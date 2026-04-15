import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from deep_translator import GoogleTranslator  # New import for translation

def clean_text(text):
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    return text.strip()

def run_filter():
    rss_url = "https://rss.app/feeds/gNSWbxS89cf9JqaP.xml"
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    
    WANT_KEYWORDS = [
        "新キャラ", "New Character", "登場", "Appears", "実装", "Released",
        "ラメント", "Lament", "cv", "song by", "予告", "Preview",
        "開催", "Held", "復刻", "Rerun", "運命ガチャ", "Chance of Fate",
        "ピックアップ", "Pick-up", "キャンペーン", "Campaign", "記念", "Anniversary"
    ]

    IGNORE_KEYWORDS = [
        "ライブ", "Live", "アップデート", "Update", "メンテ", "Maintenance",
        "プレゼント", "Present", "抽選", "Lottery", "リツイート", "Retweet", "フォロー", "Follow",
    ]

    if not webhook_url:
        print("Error: Missing DISCORD_WEBHOOK.")
        return

    try:
        response = requests.get(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        if not items:
            print("No items found in feed.")
            return

        now = datetime.now(timezone.utc)
        time_threshold = now - timedelta(hours=204)

        for item in reversed(items):
            pub_date_str = item.find('pubDate').text if item.find('pubDate') else None
            if not pub_date_str: continue
            
            pub_date = parsedate_to_datetime(pub_date_str)
            if pub_date < time_threshold: continue

            title = clean_text(item.find('title').text if item.find('title') else "")
            description = clean_text(item.find('description').text if item.find('description') else "")
            link = item.find('link').text if item.find('link') else ""

            if title.startswith("RT ") or "RT by @" in title: continue

            full_content = (title + " " + description).lower()
            
            if any(word.lower() in full_content for word in IGNORE_KEYWORDS): continue

            if any(word.lower() in full_content for word in WANT_KEYWORDS):
                # Translate the description to English
                try:
                    translated_text = GoogleTranslator(source='auto', target='en').translate(description)
                except Exception as e:
                    print(f"Translation failed: {e}")
                    translated_text = "Translation unavailable."

                if "x.com" in link:
                    clean_link = link.replace("x.com", "vxtwitter.com")
                elif "twitter.com" in link:
                    clean_link = link.replace("twitter.com", "vxtwitter.com")
                else:
                    clean_link = link
                
                # Format the message: Translation followed by the link
                discord_message = f"**Translation:**\n{translated_text}\n\n{clean_link}"
                
                payload = {
                    "username": "MementoMori Official",
                    "content": discord_message
                }
                
                res = requests.post(webhook_url, json=payload)
                if res.status_code in [200, 204]:
                    print(f"Posted: {clean_link}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_filter()
