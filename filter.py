import os
import requests
from bs4 import BeautifulSoup
import re

def get_last_id(gist_id, token):
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {"Authorization": f"token {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()['files']['last_id.txt']['content'].strip()
    return "0"

def update_last_id(gist_id, token, new_id):
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {"Authorization": f"token {token}"}
    data = {"files": {"last_id.txt": {"content": str(new_id)}}}
    requests.patch(url, headers=headers, json=data)

def clean_text(text):
    # Strips XML/CDATA tags for internal keyword matching
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    return text.strip()

def run_filter():
    rss_url = "https://rss.app/feeds/gNSWbxS89cf9JqaP.xml"
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    gist_id = os.getenv("GIST_ID")
    gist_token = os.getenv("GIST_TOKEN")
    
    # Filter Keywords in Pairs (JP, EN)
    WANT_KEYWORDS = [
        "新キャラ", "New Character",
        "登場", "Appears",
        "実装", "Released",
        "ラメント", "Lament",
        "cv", "song by",
        "予告", "Preview",
        "開催", "Held",
        "復刻", "Rerun",
        "運命ガチャ", "Chance of Fate",
        "ピックアップ", "Pick-up",
        "キャンペーン", "Campaign",
        "記念", "Anniversary"
    ]

    IGNORE_KEYWORDS = [
        "アップデート", "Update",
        "メンテ", "Maintenance",
        "プレゼント", "Present",
        "抽選", "Lottery",
        "リツイート", "Retweet",
        "フォロー", "Follow",
        "amazonギフト", "Amazon Gift"
    ]

    if not all([webhook_url, gist_id, gist_token]):
        print("Error: Missing environment variables.")
        return

    try:
        last_sent_id = get_last_id(gist_id, gist_token)
        response = requests.get(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # Proper XML parser to handle the feed correctly
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        if not items:
            return

        newest_processed_id = last_sent_id
        
        # Checking more items to ensure we don't miss the 3.5 Anni tweet if it's buried
        for item in reversed(items[:20]):
            title = clean_text(item.find('title').text if item.find('title') else "")
            description = clean_text(item.find('description').text if item.find('description') else "")
            link = item.find('link').text if item.find('link') else ""
            
            match = re.search(r'status/(\d+)', link)
            current_id = match.group(1) if match else link

            if current_id <= last_sent_id:
                continue

            # Skip Retweets to avoid "RT by @..." text blocks
            if title.startswith("RT ") or "RT by @" in title:
                continue

            # Combine for keyword checking
            full_content = (title + " " + description).lower()
            
            if any(word.lower() in full_content for word in IGNORE_KEYWORDS):
                continue

            if any(word.lower() in full_content for word in WANT_KEYWORDS):
                # Robust link replacement for vxtwitter
                if "x.com" in link:
                    clean_link = link.replace("x.com", "vxtwitter.com")
                elif "twitter.com" in link:
                    clean_link = link.replace("twitter.com", "vxtwitter.com")
                else:
                    clean_link = link
                
                # Payload: Drop ONLY the link as requested
                payload = {
                    "username": "MementoMori Official",
                    "content": clean_link
                }
                
                res = requests.post(webhook_url, json=payload)
                if res.status_code in [200, 204]:
                    newest_processed_id = current_id

        if newest_processed_id != last_sent_id:
            update_last_id(gist_id, gist_token, newest_processed_id)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_filter()
