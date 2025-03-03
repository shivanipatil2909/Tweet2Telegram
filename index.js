import { Request } from 'rettiwt-core';

async function getElonTweets() {
  try {
    // Create a request for guest access
    const request = new Request();
    
    // Get tweets using search
    const tweetsRequest = request.tweet.search('from:elonmusk', 10);
    const response = await tweetsRequest;

    console.log('Recent tweets from Elon Musk:');
    console.log('----------------------------');
    console.log('Response:', response);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

getElonTweets();
