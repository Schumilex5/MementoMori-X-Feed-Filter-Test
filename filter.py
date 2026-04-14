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

def run_filter():
    rss_url = "https://rss.app/feeds/gNSWbxS89cf9JqaP.xml"
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    gist_id = os.getenv("GIST_ID")
    gist_token = os.getenv("GIST_TOKEN")
    
    WANT_KEYWORDS = [
        "新キャラ", "登場", "実装", "ラメント", "lament", "cv", "song by", 
        "予告", "メンテ", "アップデート", "開催", "復刻", "運命ガチャ", "ピックアップ"
    ] 
    IGNORE_KEYWORDS = [
        "キャンペーン", "プレゼント", "抽選", "リツイート", "フォロー", "amazonギフト", "記念"
    ]

    if not all([webhook_url, gist_id, gist_token]):
        print("Error: Missing environment variables.")
        return

    try:
        last_sent_id = get_last_id(gist_id, gist_token)
        print(f"Checking for tweets newer than ID: {last_sent_id}")

        response = requests.get(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # FIXED: Explicitly using the 'xml' parser to handle RSS data properly
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')

        if not items:
            print("No items found.")
            return

        newest_processed_id = last_sent_id
        
        for item in reversed(items[:15]):
            title = item.find('title').text if item.find('title') else ""
            description = item.find('description').text if item.find('description') else ""
            link = item.find('link').text if item.find('link') else ""
            
            # Use status ID for numerical comparison
            match = re.search(r'status/(\d+)', link)
            current_id = match.group(1) if match else link

            if current_id <= last_sent_id:
                continue

            # Check both title and body for keywords
            full_content = (title + " " + description).lower()

            if any(word.lower() in full_content for word in IGNORE_KEYWORDS):
                continue

            if any(word.lower() in full_content for word in WANT_KEYWORDS):
                # Using vxtwitter for the high-quality embed card
                clean_link = link.replace("x.com", "vxtwitter.com").replace("twitter.com", "vxtwitter.com")
                
                payload = {
                    "username": "MementoMori Official",
                    "avatar_url": "https://mementomori.jp/favicon.ico",
                    "content": f"**{title}**\n{clean_link}"
                }
                
                res = requests.post(webhook_url, json=payload)
                if res.status_code in [200, 204]:
                    newest_processed_id = current_id
                    print(f"Posted: {current_id}")

        if newest_processed_id != last_sent_id:
            update_last_id(gist_id, gist_token, newest_processed_id)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_filter()
