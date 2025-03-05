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

# Initialize OpenAI and Telegram Bot
openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Store last processed tweet to avoid duplicates
last_tweet = None

# Keywords for intent detection
KEYWORDS = {
    "partnership": ["collaboration", "partnered", "teamed up", "joining forces"],
    "important_announcement": ["announcement", "launch", "breaking", "important update", "big news"],
}

# Templates
TEMPLATES = {
    "partnership": [
        "🚀 New Partnership Alert!\n\n{tweet}\n\n🔗 {link}",
        "🎉 We’re excited to announce our latest collaboration!\n\n{tweet}\n\nCheck it out: {link}"
    ],
    "important_announcement": [
        "📢 Important Announcement!\n\n{tweet}\n\n🔗 More details: {link}",
        "🔥 Breaking News!\n\n{tweet}\n\nGet the full story: {link}"
    ],
    "default": [
        "✨ Latest Update from Zo!\n\n{tweet}\n\n🔗 Read more: {link}",
        "💡 Stay in the loop!\n\n{tweet}\n\nCheck it out: {link}"
    ]
}

# Read latest tweet from JSON file (Node.js saves it here)
def read_latest_tweet():
    try:
        with open("latest_tweet.json", "r") as file:
            data = json.load(file)
            return data.get("tweet")
    except Exception as e:
        print(f"❌ Error reading tweet: {e}")
        return None

# Extract link from tweet text (assuming URL is at the end)
def extract_link(tweet):
    words = tweet.split()
    return words[-1] if words[-1].startswith("http") else None

# Detect intent using AI
def detect_intent(tweet):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media assistant. Classify the tweet as 'partnership', 'important_announcement', or 'default'."},
                {"role": "user", "content": f'Classify this tweet: "{tweet}"'}
            ]
        )
        intent = response["choices"][0]["message"]["content"].strip().lower()
        if intent in TEMPLATES:
            return intent
        return "default"
    except Exception as e:
        print(f"❌ Error detecting intent: {e}")
        return "default"

# Generate AI-based formatted message
def generate_telegram_message(tweet):
    link = extract_link(tweet) or "https://x.com/joinzo"
    intent = detect_intent(tweet)
    template = random.choice(TEMPLATES[intent])
    return template.format(tweet=tweet, link=link)

# Send message to Telegram
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

# Main loop to check for new tweets
def main():
    global last_tweet
    while True:
        tweet = read_latest_tweet()
        if tweet and tweet != last_tweet:
            last_tweet = tweet
            message = generate_telegram_message(tweet)
            send_telegram_message(message)
        else:
            print("⏳ No new tweet found.")

        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()
