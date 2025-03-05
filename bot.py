import os
import json
import openai
import telegram
import time
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

# Read latest tweet from JSON file (Node.js saves it here)
def read_latest_tweet():
    try:
        with open("latest_tweet.json", "r") as file:
            data = json.load(file)
            return data.get("tweet")
    except Exception as e:
        print(f"❌ Error reading tweet: {e}")
        return None

# Generate AI-based message for Telegram
def generate_telegram_message(tweet):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media assistant. Make announcements engaging."},
                {"role": "user", "content": f'Tweet: "{tweet}". Generate an engaging Telegram message.'}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Error generating AI message: {e}")
        return f"🚀 New tweet alert!\n\"{tweet}\""

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
