import os
import json
import openai
import telegram
import asyncio
import hashlib
import random
from telegram.helpers import escape_markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

BLUNT_EYE_MEDIA_LINK = "https://twitter.com/joinzo"

# Message Templates for three categories
MESSAGE_TEMPLATES = {
    "partnership": "🤝 *New Partnership Alert\!* 🤝\n\nWe’re excited to announce a new partnership that strengthens the Zo ecosystem\! Stay tuned for exciting updates and new opportunities\.\n\nFollow us on X to stay tuned\! \n\n🔗 [Tweet Link]({tweet_link})",
    "announcement": "🚀 *Big Announcement\!* 🚀\n\n{tweet}\n\nStay updated with the latest news\! \n\n🔗 [Tweet Link]({tweet_link})",
    "ama": "🎧 *AMA Session Incoming\!* 🎧\n\n{tweet}\n\nDon’t miss out\! Join us for insights and discussions\.\n\n🔗 [Tweet Link]({tweet_link})"
}

# Read latest tweet from JSON file
def read_latest_tweet():
    try:
        with open("latest_tweet.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("tweet", "").strip(), data.get("tweet_link", "")
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ No valid tweet file found.")
        return None, None

# Generate a hash for a given tweet
def generate_tweet_hash(tweet):
    return hashlib.sha256(tweet.lower().strip().encode()).hexdigest()

# Save processed tweets (including ignored ones)
def save_processed_tweets(last_hash, ignored_hashes):
    with open("processed_tweets.json", "w", encoding="utf-8") as file:
        json.dump({"last_tweet_hash": last_hash, "ignored_hashes": list(ignored_hashes)}, file, ensure_ascii=False)

# Load processed tweets
def load_processed_tweets():
    try:
        with open("processed_tweets.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("last_tweet_hash"), set(data.get("ignored_hashes", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return None, set()

# OpenAI-based Tweet Categorization
async def categorize_tweet(tweet):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a tweet classifier. Categorize the tweet into one of three categories: 'partnership', 'announcement', or 'ama'. If it does not fit, return 'ignore'."},
                {"role": "user", "content": f"Categorize the following tweet:\n\n{tweet}\n\nReturn one of: 'partnership', 'announcement', 'ama', or 'ignore'."}
            ]
        )
        category = response.choices[0].message.content.strip().lower()
        return category if category in ["partnership", "announcement", "ama"] else "ignore"
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return "ignore"

# Format Message (Escape Markdown + Correct Category)
def format_message(category, tweet, tweet_link):
    tweet = escape_markdown(tweet, version=2)
    tweet_link = escape_markdown(tweet_link, version=2)

    return MESSAGE_TEMPLATES[category].format(tweet=tweet, tweet_link=tweet_link)

# Send Telegram Message
async def send_telegram_message(message):
    try:
        async with bot:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="MarkdownV2")
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# Main Loop
async def main():
    last_tweet_hash, ignored_hashes = load_processed_tweets()
    
    while True:
        tweet, tweet_link = read_latest_tweet()
        if tweet:
            current_tweet_hash = generate_tweet_hash(tweet)

            if current_tweet_hash in ignored_hashes or current_tweet_hash == last_tweet_hash:
                print("⏳ Skipping tweet (ignored or duplicate).")
            else:
                category = await categorize_tweet(tweet)
                if category == "ignore":
                    ignored_hashes.add(current_tweet_hash)
                else:
                    message = format_message(category, tweet, tweet_link)
                    await send_telegram_message(message)
                    last_tweet_hash = current_tweet_hash
            save_processed_tweets(last_tweet_hash, ignored_hashes)
        else:
            print("⏳ No new tweet found.")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
