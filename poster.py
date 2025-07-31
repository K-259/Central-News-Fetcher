import logging
import telegram
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import config

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """Escapes text for Telegram's MarkdownV2 parse mode."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(telegram.error.NetworkError),
    reraise=True
)
async def post_article(bot: telegram.Bot, title: str, link: str):
    """Formats and sends an article to the configured Telegram channel with retry logic."""
    escaped_title = escape_markdown(title)
    escaped_link = escape_markdown(link)
    escaped_caption = escape_markdown(config.CAPTION)

    message = (
        f"*{escaped_title}*\n\n"
        f"Read more: {escaped_link}\n\n"
        f"_{escaped_caption}_"
    )
    
    await bot.send_message(
        chat_id=config.CHANNEL_ID,
        text=message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=False
    )
    logger.info(f"Successfully posted: {title}")

