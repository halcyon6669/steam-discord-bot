"""Main entry point - checks prices and sends Telegram notifications."""

import asyncio
import logging

from dotenv import load_dotenv
from telegram import Bot

from src.config import Config
from src.steam_crawler import SteamCrawler
from src.scheduler import PriceChecker
import config


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config_obj = Config.from_env()
    config_obj.ensure_data_dir()

    chat_id = config_obj.telegram_chat_id
    if not chat_id:
        logger.error("TELEGRAM_CHAT_ID is required")
        return

    if not config.games:
        logger.info("No games to watch")
        return

    crawler = SteamCrawler(rate_limit_delay=config_obj.rate_limit_delay)
    bot = Bot(token=config_obj.telegram_token)

    app_ids = [g["app_id"] for g in config.games]

    price_checker = PriceChecker(bot, crawler, chat_id)
    await price_checker.check_games(app_ids)

    logger.info("Done")


if __name__ == "__main__":
    asyncio.run(main())
