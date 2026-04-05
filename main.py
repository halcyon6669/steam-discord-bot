"""Main entry point - checks prices and sends Telegram notifications."""

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Bot

from src.config import Config
from src.steam_crawler import SteamCrawler
from src.scheduler import PriceChecker


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = Config.from_env()
    config.ensure_data_dir()

    watch_list = os.getenv("WATCH_LIST", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not watch_list:
        logger.info("No games to watch")
        return

    if not chat_id:
        logger.error("TELEGRAM_CHAT_ID is required")
        return

    crawler = SteamCrawler(rate_limit_delay=config.rate_limit_delay)
    bot = Bot(token=config.telegram_token)

    app_ids = [int(x.strip()) for x in watch_list.split(",") if x.strip()]

    price_checker = PriceChecker(bot, crawler, int(chat_id))
    await price_checker.check_games(app_ids)

    logger.info("Done")


if __name__ == "__main__":
    asyncio.run(main())
