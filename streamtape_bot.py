import logging
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from scraper import get_download_link, download_video, setup_driver

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # Replace with your bot token
 

# SQLite database connection
def init_db():
    """Initialize the database and create the tables if they don't exist."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Table to track user activity
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            request_time TEXT
        )
    """)

    # Table to track premium users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS premium_Users (
            user_id TEXT PRIMARY KEY,
            premium_since TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def log_user_request(user_id):
    """Log the user's request in the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_activity (user_id, request_time) VALUES (?, ?)",
        (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()

def get_user_request_count(user_id):
    """Get the number of videos requested by the user in the last hour."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    twelve_hour_ago = datetime.now() - timedelta(hours=12)
    cursor.execute(
        "SELECT COUNT(*) FROM user_activity WHERE user_id = ? AND request_time >= ?",
        (user_id, twelve_hour_ago.strftime('%Y-%m-%d %H:%M:%S'))
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count

def is_premium_user(user_id):
    """Check if the user is a premium user."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM premium_Users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_premium_user(user_id):
    """Add the user to the premium_users table."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO premium_Users (user_id, premium_since) VALUES (?, ?)",
        (user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()

async def start(update: Update, context):
    """Handle the /start command."""
    await update.message.reply_text(
        "Hi! Send me a video URL, and I will download and send it to you.\n\n"
        "You can download up to 3 videos per 12 hour for free.\n"
        "To remove this limit, make a UPI payment of Rs.199 and get premium access."
    )

async def payment_verification(update: Update, context):
    """Handle payment verification."""
    user_id = str(update.message.from_user.id)
    
    if is_premium_user(user_id):
        await update.message.reply_text("You already have premium access. Enjoy unlimited downloads!")
        return

    await update.message.reply_text(
        "Please make a UPI payment of Rs.199 to continue.\n"
        "UPI ID: 9170576832@ptyes\n"
        "After payment, share the screenshot for verification."
    )

async def handle_payment_screenshot(update: Update, context):
    """Handle the payment screenshot shared by the user."""
    user_id = str(update.message.from_user.id)
    await update.message.reply_text(
        "Thank you for sharing the payment screenshot! Please wait for admin approval."
    )

ADMIN_USERS = [6214220920, 987654321]  # Replace these with actual admin Telegram IDs

def is_admin(user_id: int) -> bool:
    """Check if the given user_id belongs to an admin."""
    return user_id in ADMIN_USERS

async def add_user(update: Update, context):
    """Add a user to the premium list. Usage: /add_user <user_id>"""
    user_id = update.message.from_user.id

    if not is_admin(user_id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Please provide a user ID. Usage: /add_user <user_id>")
        return

    premium_user_id = context.args[0]
    add_premium_user(premium_user_id)  # Add the user to the premium table
    await update.message.reply_text(f"User {premium_user_id} has been added to the premium list.")




async def download_video_handler(update: Update, context):
    """Handle the video URL provided by the user."""
    user_id = str(update.message.from_user.id)

    # Check if the user is a premium user
    if not is_premium_user(user_id):
        request_count = get_user_request_count(user_id)
        
        # Enforce the download limit of 3 videos per hour
        if request_count >= 3:
            await update.message.reply_text(
                "You have reached your free limit of 3 videos in the past hour.\n"
                "Make a UPI payment to get unlimited premium access."
            )
            return  # Stop further execution if limit is reached

    url = update.message.text
    logger.info(f"Received URL from user {user_id}: {url}")
    await update.message.reply_text("Downloading the video... Please wait.")

    driver = None
    try:
        # Set up the WebDriver and download the video
        driver = setup_driver()
        file_name, video_url = get_download_link(driver, url)

        if not video_url:
            await update.message.reply_text("Couldn't find a valid video at the URL.")
            return

        download_video(video_url, file_name)
        file_path = os.path.join('videos', file_name)

        if os.path.exists(file_path):
            # Log the user's request only after a successful download
            log_user_request(user_id)

            await update.message.reply_text("Preparing to upload the video... This may take a few minutes.")
            await send_video_with_status(update, file_path)
        else:
            await update.message.reply_text("Error: Video file not found.")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while processing your request.")
    finally:
        if driver:
            driver.quit()


async def send_video_with_status(update: Update, file_path: str, retries: int = 3, timeout: int = 300):
    """Send the video with status updates, retry logic, and timeout for each attempt."""
    for attempt in range(retries):
        try:
            await update.message.reply_text(f"Uploading attempt {attempt + 1}... Please wait.")
            await asyncio.wait_for(send_video(update, file_path), timeout)
            await update.message.reply_text("Video sent successfully! 🎉")
            return

        except asyncio.TimeoutError:
            logger.error(f"Attempt {attempt + 1} timed out.")
            await update.message.reply_text("Uploading timed out. Retrying...")

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            await update.message.reply_text(f"Failed to send video: {e}. Retrying...")

        if attempt == retries - 1:
            await update.message.reply_text("Failed to send the video after multiple attempts.")
            return

        await asyncio.sleep(10)

async def send_video(update: Update, file_path: str):
    """Send the video."""
    with open(file_path, 'rb') as video_file:
        await update.message.reply_document(document=InputFile(video_file))

def main():
    """Run the bot."""
    init_db()

    application = (
        Application.builder()
        .token(TOKEN)
        .read_timeout(300)
        .write_timeout(300)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", payment_verification))
    application.add_handler(CommandHandler("addpremium", add_user))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video_handler))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()


