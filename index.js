import express from "express";
import { Rettiwt } from "rettiwt-api";
import dotenv from "dotenv";
import fs from "fs";
import { spawn } from "child_process";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

const apiKey = process.env.API_KEY;
const username = "joinzo"; // Updated Twitter/X username
let lastTweetId = null;

// ✅ Function to run Python script
function runPythonScript() {
    const pythonProcess = spawn("python", ["bot.py"]); // Use "python3" if needed

    pythonProcess.stdout.on("data", (data) => {
        console.log(`🐍 Python Output: ${data.toString()}`);
    });

    pythonProcess.stderr.on("data", (data) => {
        console.error(`❌ Python Error: ${data.toString()}`);
    });

    pythonProcess.on("close", (code) => {
        console.log(`🔄 Python script exited with code ${code}`);
    });
}

// ✅ Function to save latest tweet and run Python script
function saveLatestTweet(tweet, tweetId) {
    if (!tweetId) {
        console.error("❌ Error: Tweet ID is missing. Cannot generate tweet link.");
        return;
    }

    // Ensure the correct format for the tweet link
    const tweetLink = `https://x.com/${username}/status/${tweetId}`;
    const tweetData = { tweet, tweet_link: tweetLink };

    fs.writeFileSync("latest_tweet.json", JSON.stringify(tweetData, null, 2));
    console.log("✅ Tweet saved to latest_tweet.json:", tweetLink);

    // ✅ Run Python script after saving the tweet
    runPythonScript();
}

// ✅ Function to fetch the latest tweet
async function getLatestTweet() {
    try {
        if (!apiKey) {
            console.error("❌ API key is missing. Ensure you have set API_KEY in the .env file.");
            process.exit(1);
        }

        const rettiwt = new Rettiwt({ apiKey });
        const tweets = await rettiwt.tweet.search({ fromUsers: [username], limit: 1 });

        if (!tweets?.list || tweets.list.length === 0) {
            console.log("📭 No new tweets.");
            return;
        }

        const latestTweet = tweets.list[0]?.fullText;
        const latestTweetId = tweets.list[0]?.id; // Ensure correct ID field

        if (latestTweetId !== lastTweetId) {
            lastTweetId = latestTweetId;
            console.log("🐦 New Tweet:", latestTweet);
            saveLatestTweet(latestTweet, latestTweetId);
        } else {
            console.log("✅ No new tweet.");
        }
    } catch (error) {
        console.error("❌ Error fetching latest tweet:", error);
    }
}

// ✅ Run tweet check every 60 seconds
setInterval(getLatestTweet, 60000);

// ✅ Add a basic web server for Render
app.get("/", (req, res) => {
    res.send("🚀 Twitter bot is running...");
});

app.listen(PORT, () => {
    console.log(`✅ Server running on port ${PORT}`);
});
