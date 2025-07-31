import logging
import asyncio
import aiohttp
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import our modules
from . import config, database, fetchers, poster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_news_cycle():
    """The main task that fetches, filters, and posts news."""
    logger.info("--- Starting new news cycle ---")
    bot = telegram.Bot(token=config.BOT_TOKEN)
    
    all_articles = []
    async with aiohttp.ClientSession() as session:
        # Gather all news sources concurrently
        fetch_tasks = [
            fetchers.fetch_rss_news(session),
            fetchers.scrape_website_news(session)
        ]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"A fetcher failed: {result}")
            else:
                all_articles.extend(result)

    if not all_articles:
        logger.info("No articles found in this cycle.")
        return

    logger.info(f"Fetched a total of {len(all_articles)} articles. Filtering for new ones.")
    
    new_articles_posted = 0
    for article in all_articles:
        if not database.url_is_posted(article['link']):
            try:
                await poster.post_article(bot, article['title'], article['link'])
                database.add_posted_url(article['link'])
                new_articles_posted += 1
                # Respectful delay to avoid flooding
                await asyncio.sleep(5) 
            except Exception as e:
                logger.error(f"Failed to post article {article['link']} after all retries: {e}")
    
    logger.info(f"--- News cycle complete. Posted {new_articles_posted} new articles. ---")


async def main():
    """Initializes the bot and starts the scheduler."""
    logger.info("Initializing database...")
    database.init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_news_cycle, 
        'interval', 
        minutes=config.SCHEDULE_MINUTES,
        id='news_cycle_job'
    )
    
    # Run once immediately at startup
    await run_news_cycle()

    scheduler.start()
    logger.info(f"Scheduler started. Will run every {config.SCHEDULE_MINUTES} minutes. Press Ctrl+C to exit.")

    # Keep the script running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down. Exiting.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"A critical error occurred in the main event loop: {e}")

