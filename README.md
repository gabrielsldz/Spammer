# Twitter Automated Posting Tool

## Overview

This project provides a Python-based tool for automating the posting of tweets on Twitter using multiple accounts, image uploads, and customizable delays. It supports multi-threading, account validation, and image upload in chunks, allowing the user to post to Twitter efficiently using multiple accounts simultaneously. This is an educational tool designed to demonstrate concepts like multithreading, HTTP requests, and automation.

## Features

- **Multi-threaded Tweet Posting**: Allows you to post from multiple Twitter accounts simultaneously.
- **Image Upload**: Supports uploading images to Twitter in chunks using the multi-step upload process.
- **Account Management**: Validates and checks the status of Twitter accounts before posting.
- **Customizable Delays**: You can set delays between posts for each account and between threads to prevent rate-limiting and ensure smooth operation.
- **Proxy Support**: Optionally, you can use proxies for each thread to mask the IP addresses of the posting accounts.

## Requirements

Before using this tool, you need the following libraries:

- `requests`
- `pyfiglet`
- `colorama`

Install them using `pip`:

```bash
pip install requests pyfiglet colorama
```

Additionally, you will need:

- **Twitter account cookies and tokens** for each account to be used in the tool. These will be stored in a file (e.g., `contas.txt`).
- **Tweet text** to be posted, stored in a file (e.g., `tweet.txt`).
- Optionally, an **image** to be included in your tweet (e.g., `image.png`).

## Files

- **contas.txt**: Contains the login information (cookies, auth tokens) for each Twitter account to be used. The file should have the following structure:
  
  ```
  login: <account_login>
  CT0: <CT0_token>
  AUTH_TOKEN: <auth_token>
  ```

- **tweet.txt**: Contains the text of the tweet to be posted. For example:
  
  ```
  This is an automated tweet!
  ```

- **image.png**(needs to be literally image.png) : The image file you want to attach to the tweet.

## Usage

1. Prepare the following files:
   - `contas.txt`: List of Twitter account credentials (cookies and tokens).
   - `tweet.txt`: The content of your tweet.
   - `image.png`: (Optional) Image to upload with the tweet.

2. Customize the configuration by editing the code or providing inputs during execution:
   - The number of accounts to use.
   - Delays between posts for each account and delay between threads.

3. Run the script:

```bash
python twitter_automation.py
```

4. The script will prompt you for:
   - The number of accounts to use for posting.
   - The delays between each tweet for each account (in seconds).
   - The delay between the threads (in seconds).

## How It Works

1. **Account Parsing and Validation**:
   - The script reads the account data from `contas.txt`.
   - It checks the validity of each account by attempting an upload to Twitter. Invalid accounts will be excluded from posting.

2. **Tweet Creation**:
   - The content from `tweet.txt` will be used as the base text for your tweet.
   - Each tweet will have a counter appended to it to differentiate each tweet made by the same account.

3. **Image Upload (optional)**:
   - If an image is specified, it will be uploaded in chunks using Twitter’s media upload API.
   
4. **Multi-threading**:
   - Multiple threads will be spawned to handle different accounts. Each thread will post tweets to Twitter simultaneously.
   - Each thread will respect the delay specified for that account, ensuring the tool doesn't hit Twitter’s rate limits.

5. **Proxy Support**:
   - Optionally, proxies can be used for each thread to avoid IP bans or rate-limiting.

6. **Posting**:
   - After image upload (if any), the tweet is posted to Twitter using the `CreateTweet` API endpoint.

7. **Post-Validation**:
   - After every 5 tweets, the tool will perform a quick check to validate the status of the account by re-uploading the image.

## Example

1. Prepare the `contas.txt` with your account data:

```
login: user1
CT0: your_ct0_token
AUTH_TOKEN: your_auth_token
```

2. Prepare the `tweet.txt` with your tweet:

```
This is an automated tweet!
```

3. Optionally, provide an `image.png` to attach to the tweet.

4. Run the script:

```bash
python twitter_automation.py
```

5. Enter the required details when prompted:
   - Number of accounts to use.
   - Delays between posts and between threads.

6. The script will post tweets using the provided accounts and display the status of each post.

## Notes

- **Rate Limiting**: The tool respects delays to avoid hitting Twitter’s rate limits, but be cautious when using many accounts or posting frequently.
- **Account Limits**: Ensure you have enough Twitter accounts in the `contas.txt` file for the number of threads you want to use.
- **Error Handling**: If an error occurs (e.g., account validation fails, upload fails), the script will handle it and attempt to move on to the next account or retry.

## Disclaimer

This tool is for educational purposes only. Ensure you have permission to use the Twitter accounts and that you are in compliance with Twitter's terms of service and usage policies. Abuse of this tool can result in account suspension or banning.

---

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
