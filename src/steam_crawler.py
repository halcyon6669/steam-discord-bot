"""Steam API client for fetching game prices and discounts."""

import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup


STEAM_STORE_URL = "https://store.steampowered.com"
SEARCH_URL = f"{STEAM_STORE_URL}/search/results"


@dataclass
class GameInfo:
    """Game price and discount information."""

    app_id: int
    name: str
    original_price: Optional[str]
    discounted_price: Optional[str]
    discount_percent: int
    is_free: bool
    is_historical_low: bool


class SteamCrawler:
    """Async crawler for Steam store pages."""

    def __init__(self, rate_limit_delay: float = 1.0) -> None:
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0

    async def _rate_limit(self) -> None:
        elapsed = asyncio.get_event_loop().time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def search_games(self, query: str) -> list[GameInfo]:
        """Search for games by name."""
        await self._rate_limit()

        params = {"term": query, "force_incomplete": "1", "filter": "top_sellers"}
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCH_URL, params=params) as response:
                response.raise_for_status()
                html = await response.text()

        return self._parse_search_results(html)

    def _parse_search_results(self, html: str) -> list[GameInfo]:
        soup = BeautifulSoup(html, "html.parser")
        games: list[GameInfo] = []

        for result in soup.select(".search_result_row"):
            app_id = self._extract_app_id(result)
            name = result.select_one(".title")
            price_div = result.select_one(".search_price")

            if not app_id or not name:
                continue

            game_info = self._parse_price_info(result, app_id, name.text, price_div)
            games.append(game_info)

        return games

    def _extract_app_id(self, element) -> Optional[int]:
        href = element.get("href", "")
        if "app/" in href:
            try:
                return int(href.split("app/")[1].split("/")[0])
            except (IndexError, ValueError):
                pass
        return None

    def _parse_price_info(self, element, app_id: int, name: str, price_div) -> GameInfo:
        discount_span = element.select_one(".search_discount span")
        discount_percent = 0
        if discount_span:
            text = discount_span.text.strip().replace("%", "").replace("-", "")
            try:
                discount_percent = int(text)
            except ValueError:
                pass

        original_price: Optional[str] = None
        discounted_price: Optional[str] = None
        is_free = False

        if price_div:
            original = price_div.select_one(".strike")
            if original:
                original_price = original.text.strip()
                for sibling in price_div.find_all(string=True):
                    if sibling == original:
                        continue
                    text = str(sibling).strip()
                    if text and text not in [original.text]:
                        discounted_price = text
                        break
            else:
                price_text = price_div.text.strip()
                if price_text:
                    discounted_price = price_text
                is_free = "free" in price_div.text.lower()

        return GameInfo(
            app_id=app_id,
            name=name,
            original_price=original_price,
            discounted_price=discounted_price,
            discount_percent=discount_percent,
            is_free=is_free,
            is_historical_low=False,
        )

    async def get_game_details(self, app_id: int) -> Optional[GameInfo]:
        """Get detailed price info for a specific game."""
        await self._rate_limit()

        url = f"{STEAM_STORE_URL}/app/{app_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                html = await response.text()

        return self._parse_game_page(html, app_id)

    def _parse_game_page(self, html: str, app_id: int) -> Optional[GameInfo]:
        soup = BeautifulSoup(html, "html.parser")

        name_elem = soup.select_one(".apphub_AppName")
        if not name_elem:
            return None
        name = name_elem.text.strip()

        game_area = soup.select_one("#game_area_purchase")
        if not game_area:
            return None

        price_info = game_area.select_one(".game_purchase_price") or game_area.select_one(
            ".discount_original_price"
        )

        original_price: Optional[str] = None
        discounted_price: Optional[str] = None
        discount_percent = 0
        is_free = False

        discount_elem = game_area.select_one(".discount_pct")
        if discount_elem:
            text = discount_elem.text.strip().replace("%", "").replace("-", "")
            try:
                discount_percent = int(text)
            except ValueError:
                pass

        original_elem = game_area.select_one(".discount_original_price")
        if original_elem:
            original_price = original_elem.text.strip()

        discounted_elem = game_area.select_one(".discount_final_price")
        if discounted_elem:
            discounted_price = discounted_elem.text.strip()

        price_text = price_info.text.strip() if price_info else ""
        if "free" in price_text.lower():
            is_free = True
        elif not discounted_price:
            discounted_price = price_text

        return GameInfo(
            app_id=app_id,
            name=name,
            original_price=original_price,
            discounted_price=discounted_price,
            discount_percent=discount_percent,
            is_free=is_free,
            is_historical_low=False,
        )
