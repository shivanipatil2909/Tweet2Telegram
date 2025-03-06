import os
import json
import openai
import telegram
import time
import random
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Define Zop Labs link
ZOP_LABS_LINK = "https://x.com/joinzo"

# Read latest tweet from JSON file (Handles Unicode Errors)
def read_latest_tweet():
    try:
        with open("latest_tweet.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("tweet")
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ No valid tweet file found.")
        return None

# Save last processed tweet
def save_last_tweet(tweet):
    with open("last_tweet.json", "w", encoding="utf-8") as file:
        json.dump({"last_tweet": tweet}, file, ensure_ascii=False)

# Load last processed tweet
def load_last_tweet():
    try:
        with open("last_tweet.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("last_tweet")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Intent Detection Keywords
IMPORTANT_KEYWORDS = ["partnership", "announcement", "important", "launch", "giveaway", "contest"]
IGNORE_KEYWORDS = ["random", "fun", "meme", "joke"]

def check_intent(tweet):
    tweet_lower = tweet.lower()
    if any(keyword in tweet_lower for keyword in IMPORTANT_KEYWORDS):
        return "important"
    if any(keyword in tweet_lower for keyword in IGNORE_KEYWORDS):
        return "ignore"
    return "normal"

# Message Templates
TEMPLATES = [
    "🚨 Quest Alert 🚨\n\n{tweet}",
    "📢 Weekly Community Call Announcement!\n\n{tweet}",
    "⭐ Special Announcement ⭐\n\n{tweet}"
]

# Ensure the link is included only if it's missing
def add_zop_labs_link(message):
    if ZOP_LABS_LINK not in message:
        return f"{message}\n\n🔗 {ZOP_LABS_LINK}"
    return message

# Generate Telegram Message
def generate_telegram_message(tweet):
    intent = check_intent(tweet)
    
    if intent == "ignore":
        print("⏳ Tweet is not important, skipping.")
        return None
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media assistant. Format tweets into engaging Telegram posts."},
                {"role": "user", "content": f'Tweet: "{tweet}". Format this tweet in an engaging way using a friendly and attention-grabbing style.'}
            ]
        )
        message = response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        message = random.choice(TEMPLATES).format(tweet=tweet)  # Use random template if API fails
    
    return add_zop_labs_link(message)  # Ensure link is added only if missing

# Send Telegram Message (Async Fix)
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# Main Loop
async def main():
    last_tweet = load_last_tweet()
    while True:
        tweet = read_latest_tweet()
        if tweet and tweet != last_tweet:
            message = generate_telegram_message(tweet)
            if message:
                await send_telegram_message(message)
                save_last_tweet(tweet)  # Store last tweet to avoid duplicates
                last_tweet = tweet
        else:
            print("⏳ No new tweet found.")
        
        await asyncio.sleep(60)  # Use asyncio.sleep to prevent blocking

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
