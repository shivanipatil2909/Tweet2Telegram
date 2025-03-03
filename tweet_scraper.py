import ssl
import certifi

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
import snscrape.modules.twitter as sntwitter
import json

def fetch_elon_tweets():
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterUserScraper("elonmusk").get_items()):
        if i >= 5:  # Get the latest 5 tweets
            break
        tweets.append(tweet.content)
    
    return tweets

# Fetch tweets
elon_tweets = fetch_elon_tweets()

# Save tweets to a text file
with open("elon_tweets.txt", "w", encoding="utf-8") as file:
    for tweet in elon_tweets:
        file.write(tweet + "\n\n")

print("Tweets saved successfully!")
