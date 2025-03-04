// import { Rettiwt } from "rettiwt-api";
// import dotenv from "dotenv";

// dotenv.config();

// const apiKey = process.env.API_KEY;
// const username = "joinzo"; // Change to any Twitter handle
// let lastTweetText = null;

// async function getLatestTweet() {
//     try {
//         if (!apiKey) {
//             console.error("API key is missing. Ensure you have set API_KEY in the .env file.");
//             return;
//         }

//         const rettiwt = new Rettiwt({ apiKey });
//         const tweets = await rettiwt.tweet.search({ fromUsers: [username] }, 1);

//         if (!tweets?.list || tweets.list.length === 0) {
//             console.log("No new tweets.");
//             return;
//         }

//         const latestTweet = tweets.list[0].fullText;

//         if (latestTweet !== lastTweetText) {
//             lastTweetText = latestTweet;
//             console.log(latestTweet);
//         } else {
//             console.log("No new tweet.");
//         }
//     } catch (error) {
//         console.error("Error fetching latest tweet:", error);
//     }
// }

// setInterval(getLatestTweet, 1000); 


import { Rettiwt } from "rettiwt-api";
import dotenv from "dotenv";
import OpenAI from "openai";
import TelegramBot from "node-telegram-bot-api";

dotenv.config();

const apiKey = process.env.API_KEY;
const openAiApiKey = process.env.OPENAI_API_KEY;
const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID; // Your Telegram group ID
const username = "joinzo"; // Change to any Twitter handle
let lastTweetText = null;

// Initialize OpenAI API
const openai = new OpenAI({ apiKey: openAiApiKey });

// Initialize Telegram Bot
const bot = new TelegramBot(telegramBotToken, { polling: false });

async function getLatestTweet() {
    try {
        if (!apiKey) {
            console.error("API key is missing. Ensure you have set API_KEY in the .env file.");
            return;
        }

        const rettiwt = new Rettiwt({ apiKey });
        const tweets = await rettiwt.tweet.search({ fromUsers: [username] }, 1);

        if (!tweets?.list || tweets.list.length === 0) {
            console.log("No new tweets.");
            return;
        }

        const latestTweet = tweets.list[0].fullText;

        if (latestTweet !== lastTweetText) {
            lastTweetText = latestTweet;
            console.log("Latest Tweet:", latestTweet);

            // Generate AI-enhanced Telegram message
            const message = await generateTelegramMessage(latestTweet);

            // Send the message to the Telegram group
            bot.sendMessage(chatId, message);
        } else {
            console.log("No new tweet.");
        }
    } catch (error) {
        console.error("Error fetching latest tweet:", error);
    }
}

async function generateTelegramMessage(tweet) {
    try {
        const completion = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
                { role: "system", content: "You are a social media assistant. Create engaging Telegram announcements for new tweets." },
                {
                    role: "user",
                    content: `Tweet: "${tweet}"\n\nGenerate an engaging Telegram message announcing this to our community.`,
                },
            ],
        });

        return completion.choices[0].message.content;
    } catch (error) {
        console.error("Error generating AI message:", error);
        return `🚀 New tweet alert! \n"${tweet}" \n\nJoin the discussion! 💬`;
    }
}

// Run every 60 seconds
setInterval(getLatestTweet, 60000);
