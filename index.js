import { Rettiwt } from "rettiwt-api";
import dotenv from "dotenv";
import fs from "fs";

dotenv.config();

const apiKey = process.env.API_KEY;
const username = "joinzo"; // Change to the Twitter handle you want to track
let lastTweetText = null;

// Function to save the latest tweet to a JSON file
function saveLatestTweet(tweet) {
    const tweetData = { tweet };
    fs.writeFileSync("latest_tweet.json", JSON.stringify(tweetData, null, 2));  // Save JSON
    console.log("✅ Tweet saved to latest_tweet.json");
}

async function getLatestTweet() {
    try {
        if (!apiKey) {
            console.error("❌ API key is missing. Ensure you have set API_KEY in the .env file.");
            return;
        }

        const rettiwt = new Rettiwt({ apiKey });
        const tweets = await rettiwt.tweet.search({ fromUsers: [username] }, 1);

        if (!tweets?.list || tweets.list.length === 0) {
            console.log("📭 No new tweets.");
            return;
        }

        const latestTweet = tweets.list[0].fullText;

        if (latestTweet !== lastTweetText) {
            lastTweetText = latestTweet;
            console.log("🐦 New Tweet:", latestTweet);

            // ✅ Save to JSON file
            saveLatestTweet(latestTweet);
        } else {
            console.log("✅ No new tweet.");
        }
    } catch (error) {
        console.error("❌ Error fetching latest tweet:", error);
    }
}

// Run every 60 seconds
setInterval(getLatestTweet, 60000);


// import { spawn } from "child_process";
// import { Rettiwt } from "rettiwt-api";
// import dotenv from "dotenv";
// import fs from "fs";

// dotenv.config();

// const apiKey = process.env.API_KEY;
// const username = "joinzo"; // Twitter handle to track
// let lastTweetText = null;

// // Function to save the latest tweet to a JSON file
// function saveLatestTweet(tweet) {
//     const tweetData = { tweet };
//     fs.writeFileSync("latest_tweet.json", JSON.stringify(tweetData, null, 2));
//     console.log("✅ Tweet saved to latest_tweet.json");

//     // ✅ Run Python script after saving the latest tweet
//     runPythonScript();
// }

// // Function to run the Python script
// function runPythonScript() {
//     const pythonProcess = spawn("python", ["bot.py"]); // Change to "python3" if needed

//     pythonProcess.stdout.on("data", (data) => {
//         console.log(`🐍 Python Output: ${data.toString()}`);
//     });

//     pythonProcess.stderr.on("data", (data) => {
//         console.error(`❌ Python Error: ${data.toString()}`);
//     });

//     pythonProcess.on("close", (code) => {
//         console.log(`🔄 Python script exited with code ${code}`);
//     });
// }

// async function getLatestTweet() {
//     try {
//         if (!apiKey) {
//             console.error("❌ API key is missing. Ensure you have set API_KEY in the .env file.");
//             return;
//         }

//         const rettiwt = new Rettiwt({ apiKey });
//         const tweets = await rettiwt.tweet.search({ fromUsers: [username] }, 1);

//         if (!tweets?.list || tweets.list.length === 0) {
//             console.log("📭 No new tweets.");
//             return;
//         }

//         const latestTweet = tweets.list[0].fullText;

//         if (latestTweet !== lastTweetText) {
//             lastTweetText = latestTweet;
//             console.log("🐦 New Tweet:", latestTweet);
//             saveLatestTweet(latestTweet); // Save and trigger Python script
//         } else {
//             console.log("✅ No new tweet.");
//         }
//     } catch (error) {
//         console.error("❌ Error fetching latest tweet:", error);
//     }
// }

// // Run every 60 seconds
// setInterval(getLatestTweet, 60000);

