import sqlite3
import logging
from . import config

logger = logging.getLogger(__name__)

def init_db():
    """Initializes the database and creates the 'articles' table if it doesn't exist."""
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.critical(f"Database initialization failed: {e}")
        raise

def url_is_posted(url: str) -> bool:
    """Checks if a URL has already been posted."""
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Failed to check URL {url}: {e}")
        return True # Assume posted to be safe

def add_posted_url(url: str):
    """Adds a new URL to the database of posted articles."""
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO articles (url) VALUES (?)", (url,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to add URL {url}: {e}")

