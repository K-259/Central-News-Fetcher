import logging
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import config

logger = logging.getLogger(__name__)

# Define what exceptions to retry on
RETRYABLE_EXCEPTIONS = (aiohttp.ClientError, asyncio.TimeoutError)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    reraise=True # Reraise the exception if all retries fail
)
async def fetch_rss_news(session: aiohttp.ClientSession):
    """Fetches and parses news from an RSS feed with retry logic."""
    logger.info(f"Fetching RSS feed from {config.RSS_URL}")
    async with session.get(config.RSS_URL, timeout=10) as response:
        response.raise_for_status()
        text = await response.text()
        feed = feedparser.parse(text)
        logger.info(f"Found {len(feed.entries)} entries in RSS feed.")
        return [{'title': entry.title, 'link': entry.link} for entry in feed.entries]

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    reraise=True
)
async def scrape_website_news(session: aiohttp.ClientSession):
    """Scrapes news headlines from a website with retry logic."""
    logger.info(f"Scraping website {config.SCRAPE_URL}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    async with session.get(config.SCRAPE_URL, headers=headers, timeout=15) as response:
        response.raise_for_status()
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        
        headlines = []
        selector = config.SCRAPE_CONFIG['element']
        attrs = config.SCRAPE_CONFIG['attrs']
        
        for item in soup.find_all(selector, attrs, limit=10):
            title = item.get_text(strip=True)
            link = item.get('href')
            if title and link:
                if not link.startswith('http'):
                    base_url = '/'.join(config.SCRAPE_URL.split('/')[:3])
                    link = base_url + link
                headlines.append({'title': title, 'link': link})
        
        logger.info(f"Found {len(headlines)} headlines from scraping.")
        return headlines

