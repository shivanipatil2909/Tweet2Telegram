import os
import json
import openai
import telegram
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

last_tweet = None

# Read latest tweet from JSON file
def read_latest_tweet():
    try:
        with open("latest_tweet.json", "r") as file:
            data = json.load(file)
            return data.get("tweet")
    except FileNotFoundError:
        print("❌ No tweet file found.")
        return None
    except json.JSONDecodeError:
        print("❌ Error decoding tweet JSON.")
        return None

# **Intent Detection Keywords**
IMPORTANT_KEYWORDS = ["partnership", "announcement", "important", "launch", "giveaway", "contest"]
IGNORE_KEYWORDS = ["random", "fun", "meme", "joke"]

def check_intent(tweet):
    tweet_lower = tweet.lower()
    
    if any(keyword in tweet_lower for keyword in IMPORTANT_KEYWORDS):
        return "important"
    if any(keyword in tweet_lower for keyword in IGNORE_KEYWORDS):
        return "ignore"
    return "normal"

# **Templates for Messages**
TEMPLATES = [
    "🚨 Quest Alert 🚨\n\n{tweet}\n\n🔗 Check it out: https://x.com/joinzo",
    "📢 Weekly Community Call Announcement!\n\n{tweet}\n\n🔗 Join us: https://x.com/joinzo",
    "⭐ Special Announcement ⭐\n\n{tweet}\n\n🎁 Don't miss it: https://x.com/joinzo"
]

# **Generate Telegram Message**
def generate_telegram_message(tweet):
    intent = check_intent(tweet)
    
    if intent == "ignore":
        print("⏳ Tweet is not important, skipping.")
        return None
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a social media assistant. Format tweets into engaging Telegram posts."},
                {"role": "user", "content": f'Tweet: "{tweet}". Format this tweet in an engaging way using one of these templates:\n\n{TEMPLATES}'}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return random.choice(TEMPLATES).format(tweet=tweet)  # Use random template if API fails

# **Send Telegram Message**
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# **Main Loop**
def main():
    global last_tweet
    while True:
        tweet = read_latest_tweet()
        if tweet and tweet != last_tweet:
            last_tweet = tweet
            message = generate_telegram_message(tweet)
            if message:
                send_telegram_message(message)
        else:
            print("⏳ No new tweet found.")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
