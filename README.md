# Telegram Video Downloader Streamtape Bot

The Telegram Video Downloader Bot is designed to help users conveniently download videos from provided URLs through Telegram. It offers a freemium model, allowing users to download up to 3 videos every 12 hours for free. For users who need more frequent access, premium access can be granted by making a one-time payment of ₹199 or via manual addition by an admin.

This bot is intended for individuals who want a simple and fast way to download videos without needing separate tools or complicated processes. Admins can monitor users' activity and grant premium access using special bot commands, giving them flexibility in user management.

**Key users include:**

- General Users: Download limited videos for free or opt for premium access.

- Admins/Moderators: Manage premium access and oversee user behavior.


## Features

- Video Downloading from URLs
Users can share a video URL with the bot, and the bot will download the video and send it via Telegram.
- Freemium Access Model

-> Free Users: Can download up to 3 videos every 12 hours.

-> Premium Users: Get unlimited downloads after a one-time payment or manual admin approval
- Payment Integration through UPI ID
Users can make a ₹199 payment via UPI ID to upgrade to premium. After manual verification of the payment, admins can use /add_user <user_id> to enable premium access.
- Status Updates
The bot provides real-time status updates during video downloads and uploads to ensure transparency.
- Timeout and Retry Mechanism
Supports timeouts and automatic retries during video uploads to handle slow or interrupted networks.
- Cross-Platform Support
The bot works smoothly across all Telegram platforms, including mobile, desktop, and web.


## Tech Stack

**Programming Language:**

- Python

**Frameworks & Libraries:**

- **Python-Telegram-Bot:** For building Telegram bot functionalities.
- **Asyncio:** For handling asynchronous tasks like video downloads and uploads.
- **Selenium:** For web scraping to extract video links.
- **SQLite:** For managing user and premium membership data.

**Database:**

- **SQLite:** Lightweight database for tracking user activity and premium membership.

**Development Tools:**

- **Logging:** For tracking bot activity and errors.
- **WebDriver (Selenium):** For automated browser interaction during video scraping.


## Installation

1. Clone the repository:

```bash
  git clone <repository-url>
  cd <project-directory>

```
2.  Install Dependencies:
```bash
    pip install -r requirements.txt
```
3. Get the Bot Token and Username from BotFather

- Open Telegram and search for BotFather (a verified bot for creating and managing bots).

- Start a chat with BotFather by typing /start.
- Create a new bot by sending the /newbot command.
- Choose a name for your bot. (This will be the display name for your bot.)
- Select a username for your bot. Make sure it ends with the word bot (e.g., myawesomebot).
- BotFather will send you a token after the bot is created. This token is essential to connect your code with Telegram.
**Example token:** 1234567890:ABCDefGhijklMNOpqrStuvWxYZabcdeFghijK



4. Add the Bot Token:
Replace "YOUR_TELEGRAM_BOT_TOKEN" in the payment.py file with your actual bot token.
```bash
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
```
5. Ensure ChromeDriver is Set Up:
Make sure Chromedriver is installed and accessible in your system's PATH or placed in the project folder.

6.  Run the Bot:
```bash
python streamtape_bot.py
```
    
## Usage/Examples

To use the Telegram video bot, follow these steps:

**1. Start the Bot**

- Search for your bot on Telegram using its username and click Start to initialize the conversation.

**2. Commands:**

Use the following commands to interact with the bot:

- **/start**: Initiates the bot and provides a welcome message.
- **/pay**: Requests the UPI ID for payment processing.
- **/add_user <user_id>**: Manually adds a user to the premium users list.


## Acknowledgement

 - **Streamtape Scraper** is from [dr-pandit-69's Streamtape Video Downloader](https://github.com/dr-pandit-69/streamtape-video-downloader)



