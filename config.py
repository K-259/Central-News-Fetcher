import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Telegram Settings ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CAPTION = os.getenv("CAPTION")

# --- Scheduling ---
# Default to 60 minutes if not set
SCHEDULE_MINUTES = int(os.getenv("SCHEDULE_MINUTES", 60))

# --- News Sources ---
RSS_URL = os.getenv("RSS_URL")
SCRAPE_URL = os.getenv("SCRAPE_URL")

# --- Scraper Configuration ---
SCRAPE_CONFIG = {
    "element": os.getenv("SCRAPE_TARGET_ELEMENT", "a"),
    "attrs": {
        os.getenv("SCRAPE_TARGET_ATTR_KEY"): os.getenv("SCRAPE_TARGET_ATTR_VALUE")
    }
}

# --- Database ---
DB_FILE = "news_database.sqlite"

# --- Validation ---
if not all([BOT_TOKEN, CHANNEL_ID, RSS_URL, SCRAPE_URL]):
    raise ValueError("One or more critical environment variables are not set.")
