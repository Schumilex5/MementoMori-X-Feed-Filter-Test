import os
import requests
from bs4 import BeautifulSoup

def run_filter():
    # --- CONFIGURATION ---
    username = "mementomori_boi"
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    
    # ADD YOUR KEYWORDS HERE (Case-insensitive)
    WANT_KEYWORDS = ["memento", "update", "new"] 
    IGNORE_KEYWORDS = ["giveaway", "ad", "promo"]

    # Target URL (X Syndication is more stable for scraping)
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    
    print(f"Scraping @{username}...")

    if not webhook_url:
        print("CRITICAL ERROR: DISCORD_WEBHOOK is not set in GitHub Secrets.")
        return

    # Browser-like headers to avoid being blocked by X
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tweets = soup.find_all(class_='timeline-Tweet')
        print(f"Found {len(tweets)} tweets in the feed.")

        if not tweets:
            print("No tweets found. X might be rate-limiting the runner.")
            return

        for tweet in tweets:
            # 1. Extract tweet text and link
            text_element = tweet.find(class_='timeline-Tweet-text')
            if not text_element:
                continue
                
            content = text_element.get_text().lower()
            link_element = tweet.find('a', class_='timeline-Tweet-timestamp')
            link = link_element['href'] if link_element else "No link found"

            # 2. Apply IGNORE Filter
            if any(word.lower() in content for word in IGNORE_KEYWORDS):
                print(f"Skipping tweet (Contains Ignored Word): {content[:50]}...")
                continue

            # 3. Apply WANT Filter
            if any(word.lower() in content for word in WANT_KEYWORDS):
                print(f"Match Found: {content[:50]}... Sending to Discord.")
                
                payload = {
                    "username": "X Filter Bot",
                    "content": f"**Match Found for @{username}!**\n{text_element.get_text()}\n\n🔗 [View on X]({link})"
                }
                
                res = requests.post(webhook_url, json=payload)
                if res.status_code in [200, 204]:
                    print("Successfully sent to Discord.")
                else:
                    print(f"Discord error: {res.status_code}")
            else:
                print(f"No match found in tweet: {content[:50]}...")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_filter()
