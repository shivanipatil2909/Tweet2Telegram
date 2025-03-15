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

# Zop Labs link
ZOP_LABS_LINK = "https://x.com/joinzo"

# Predefined Message Templates
MESSAGE_TEMPLATES = [
    "🚀 *Breaking News\!* 🚀\n\n{tweet}\n\n🔗 [Tweet Link]({tweet_link})\n🌟 Stay updated with [Zop Labs]({zop_labs_link})",
    "🎯 *Quest Alert\!* 🎯\n\n📢 {tweet}\n\n🔗 [Tweet Link]({tweet_link})\n🔍 Learn more at [Zop Labs]({zop_labs_link})",
    "🔥 *Web3 Game Changer\!* 🔥\n\n{tweet}\n\n🚀 Read now: [Tweet Link]({tweet_link})\n🔗 More at [Zop Labs]({zop_labs_link})",
    "🎉 *Big Announcement\!* 🎉\n\n{tweet}\n\n🔗 Read more: [Tweet Link]({tweet_link})\n👀 Check out [Zop Labs]({zop_labs_link})",
    "💡 *Innovator Spotlight\!* 💡\n\n🚀 {tweet}\n\n🔗 [Tweet Link]({tweet_link})\n🌍 Stay tuned with [Zop Labs]({zop_labs_link})",
    "📢 *Community Call\!* 📢\n\n{tweet}\n\n🔗 [Tweet Link]({tweet_link})\n📅 Join us at [Zop Labs]({zop_labs_link})",
    "🛠 *Dev Update\!* 🛠\n\n{tweet}\n\n🔗 [Tweet Link]({tweet_link})\n👨‍💻 Explore at [Zop Labs]({zop_labs_link})",
    "🚨 *Security Alert\!* 🚨\n\n{tweet}\n\n🔗 [Tweet Link]({tweet_link})\n🔍 Stay secure with [Zop Labs]({zop_labs_link})"
]

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

# OpenAI-based Intent Detection
async def get_tweet_intent(tweet):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a tweet analyzer. Categorize the tweet as 'important', 'normal', or 'ignore' based on its content."},
                {"role": "user", "content": f"Analyze the following tweet:\n\n{tweet}\n\nReturn only one of these categories: important, normal, ignore."}
            ]
        )
        intent = response.choices[0].message.content.strip().lower()
        return intent if intent in ["important", "normal", "ignore"] else "normal"
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return "normal"

# OpenAI-based Tweet Enhancement
async def enhance_tweet(tweet):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a social media expert. Rewrite the tweet to make it more engaging, using emojis and excitement while keeping the main message the same."},
                {"role": "user", "content": f"Original Tweet:\n{tweet}\n\nMake it more exciting with emojis and engaging language."}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return tweet  # Fallback to original tweet if there's an error

# Format Message (Escape Markdown + Random Template)
def format_message(tweet, tweet_link):
    tweet = escape_markdown(tweet, version=2)
    tweet_link = escape_markdown(tweet_link, version=2)
    zop_labs_link = escape_markdown(ZOP_LABS_LINK, version=2)

    message_template = random.choice(MESSAGE_TEMPLATES)

    return message_template.format(tweet=tweet, tweet_link=tweet_link, zop_labs_link=zop_labs_link)

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

            # Skip if tweet is ignored or duplicate
            if current_tweet_hash in ignored_hashes:
                print("⏳ Ignored tweet detected, skipping.")
            elif current_tweet_hash == last_tweet_hash:
                print("⏳ Duplicate tweet detected, skipping.")
            else:
                intent = await get_tweet_intent(tweet)
                
                if intent == "ignore":
                    print("⏳ Tweet marked as 'ignore', skipping.")
                    ignored_hashes.add(current_tweet_hash)
                else:
                    tweet = await enhance_tweet(tweet)
                    message = format_message(tweet, tweet_link)
                    await send_telegram_message(message)
                    last_tweet_hash = current_tweet_hash  # Update last processed tweet
            
            # Save processed tweets
            save_processed_tweets(last_tweet_hash, ignored_hashes)
        else:
            print("⏳ No new tweet found.")

        await asyncio.sleep(60)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
