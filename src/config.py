"""Configuration loader for Steam Telegram Bot."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    telegram_token: str
    database_path: Path
    check_interval_hours: int
    rate_limit_delay: float

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            msg = "TELEGRAM_TOKEN environment variable is required"
            raise ValueError(msg)

        db_path = os.getenv("DATABASE_PATH", "./data/bot.db")
        check_interval = int(os.getenv("CHECK_INTERVAL_HOURS", "6"))
        rate_limit = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))

        return cls(
            telegram_token=token,
            database_path=Path(db_path),
            check_interval_hours=check_interval,
            rate_limit_delay=rate_limit,
        )

    def ensure_data_dir(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
