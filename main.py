import logging
import threading
import asyncio
import pyrogram
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *
from aiogram import Router, Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from router import user_router
from callback import callback


async def main():
    bot = Bot("")
    dp = Dispatcher()
    dp.include_routers(user_router.router, callback.callback_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())