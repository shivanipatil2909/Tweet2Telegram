# Nitter Tweet Scraper

A simple Python script to fetch tweets from Nitter (an alternative Twitter front-end) and save them to a file.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python tweet_scraper.py
```

## Configuration

You can modify these variables in the script:
- `NITTER_INSTANCE`: The Nitter instance to use
- `USERNAME`: Twitter username to scrape
- `TWEET_COUNT`: Number of tweets to fetch
- `OUTPUT_FILE`: Where to save the tweets

## Note
This script uses Nitter as it doesn't require authentication. If an instance becomes unavailable, you can switch to another one from: https://github.com/zedeus/nitter/wiki/Instances
