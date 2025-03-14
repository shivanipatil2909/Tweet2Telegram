import os
import json
import openai
import telegram
import asyncio
import random
from telegram.helpers import escape_markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)  # ✅ Corrected API Call
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Zop Labs link
ZOP_LABS_LINK = "https://x.com/joinzo"

# Predefined Message Templates 🔥
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
            return data.get("tweet"), data.get("tweet_link")
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ No valid tweet file found.")
        return None, None

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

# OpenAI-based Intent Detection
async def get_tweet_intent(tweet):
    try:
        response = await openai_client.chat.completions.create(  # ✅ Fixed OpenAI API Call
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

# Format Message (Escape Markdown + Random Template)
def format_message(tweet, tweet_link):
    tweet = escape_markdown(tweet, version=2)  # ✅ Escape Markdown for Telegram
    tweet_link = escape_markdown(tweet_link, version=2)
    zop_labs_link = escape_markdown(ZOP_LABS_LINK, version=2)

    # Select a random message template 🎲
    message_template = random.choice(MESSAGE_TEMPLATES)

    return message_template.format(tweet=tweet, tweet_link=tweet_link, zop_labs_link=zop_labs_link)

# Send Telegram Message
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="MarkdownV2")
        print("✅ Message sent to Telegram!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# Main Loop
async def main():
    last_tweet = load_last_tweet()
    
    while True:
        tweet, tweet_link = read_latest_tweet()
        if tweet and tweet != last_tweet:
            intent = await get_tweet_intent(tweet)  # ✅ Awaiting async function
            
            if intent == "ignore":
                print("⏳ Tweet is not important, skipping.")
            else:
                message = format_message(tweet, tweet_link)
                await send_telegram_message(message)
                save_last_tweet(tweet)
                last_tweet = tweet
        else:
            print("⏳ No new tweet found.")
        
        await asyncio.sleep(60)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())  # ✅ Corrected for async execution
