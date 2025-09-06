import asyncio
import uvicorn
from aiogram import Dispatcher
from bot.loader import bot, dp
from bot.handlers import start, subscription, profile  # позже подключишь profile, referral и т.д.
from bot.api import app as fastapi_app


async def run_bot():
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(profile.router)

    # dp.include_router(profile.router)
    # dp.include_router(referral.router)
    # dp.include_router(faq.router)
    # dp.include_router(access_file.router)

    await dp.start_polling(bot)


async def run_api():
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(run_bot(), run_api())


if __name__ == "__main__":
    asyncio.run(main())
