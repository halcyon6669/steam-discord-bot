"""Price checker - monitors games and sends Telegram notifications."""

from telegram import Bot

from src.steam_crawler import SteamCrawler, STEAM_STORE_URL


class PriceChecker:
    def __init__(self, bot: Bot, crawler: SteamCrawler, chat_id: int) -> None:
        self.bot = bot
        self.crawler = crawler
        self.chat_id = chat_id

    async def check_games(self, app_ids: list[int]) -> None:
        for app_id in app_ids:
            game = await self.crawler.get_game_details(app_id)
            if game and game.discount_percent > 0:
                await self._notify_sale(game)

    async def _notify_sale(self, game) -> None:
        url = f"{STEAM_STORE_URL}/app/{game.app_id}"

        text = f"🎮 **{game.name}** 正在打折！\n\n"
        text += f"折扣: -{game.discount_percent}%\n"
        text += f"现价: {game.discounted_price or 'N/A'}\n"
        text += f"原价: {game.original_price or 'N/A'}\n"
        text += f"\n{url}"

        await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
