# Steam Telegram Bot

Telegram bot for monitoring Steam game prices and notifying when games go on sale.

## Commands

- `/start` - 欢迎信息
- `/search <游戏名>` - 搜索游戏
- `/add <app_id>` - 添加到监控列表
- `/remove <app_id>` - 移除监控
- `/list` - 查看监控列表
- `/check <app_id>` - 检查是否打折
- `/togglesale` - 开启/关闭通知
- `/topdeals` - 查看折扣榜

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Copy `.env.example` to `.env` and add your bot token:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the bot:
   ```bash
   python main.py
   ```

## GitHub Actions

This bot runs on a schedule (every 6 hours) via GitHub Actions.

1. Push this repo to GitHub
2. Add `TELEGRAM_TOKEN` to repository Secrets
3. The workflow runs automatically or can be triggered manually

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_TOKEN` | Yes | - | Telegram bot token |
| `DATABASE_PATH` | No | `./data/bot.db` | SQLite database path |
| `CHECK_INTERVAL_HOURS` | No | `6` | Price check interval |
| `RATE_LIMIT_DELAY` | No | `1.0` | Seconds between Steam requests |
