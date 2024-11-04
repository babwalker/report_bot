import asyncio
import logging

from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import pyrogram
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import *
from pyrogram.errors import FloodWait, Timeout

from buttons import user_buttons
from database import database
from states import GetLinkForReport
from report_text import text

router = Router()

bot = Bot("")

# Base function

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Hello, {message.from_user.username}", reply_markup=user_buttons.meny_keyboard())
    database.add_user(message.from_user.id)

@router.message(F.text == "Cancel")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(f"Hello, {message.from_user.username}", reply_markup=user_buttons.meny_keyboard())
    await state.clear()

# Materials

@router.message(F.text == "Materials")
async def materials_handler(message: types.Message):
    await message.answer("Choose what you want to do", reply_markup=user_buttons.materials_keyboard())

# Sessions start

# class CustomHandler(logging.Handler):
#     def emit(self, record):
#         log_entry = self.format(record)
#         print(log_entry)

# logger = logging.getLogger()
# custom_handler = CustomHandler()
# custom_handler.setLevel(logging.WARNING)
# logger.addHandler(custom_handler)

async def _start_proxy_sessions(channel_name:str, session_name:str, proxy_string:str, user_id):

    try:
        proxy_split = proxy_string.split(":")
        proxy = {
            "scheme": "http",  # "socks4", "socks5" and "http" are supported
            "hostname": proxy_split[0],
            "port": int(proxy_split[1]),
            "username": proxy_split[2],
            "password": proxy_split[3]
        }

        logging.warning("TEST")

        app = Client(f"session_files/{session_name}", proxy=proxy)
        await app.start()

        try: # Check if there is a channel
            peer = await app.resolve_peer(f"@{channel_name}")

            try:
                access_hash = peer.access_hash
                peer_user_id = peer.user_id 
                peer = InputPeerUser(user_id=peer_user_id, access_hash=access_hash)

            except:
                access_hash = peer.access_hash
                channel_id = peer.channel_id 
                peer = InputPeerChannel(channel_id=channel_id, access_hash=access_hash)

            report_peer = ReportPeer(
                peer = peer,
                reason = InputReportReasonIllegalDrugs(),
                message = text
            )

            result = await app.invoke(report_peer)
            await bot.send_message(chat_id=user_id, text=f"Report sent")
            print(result)
            await app.stop()
        except pyrogram.errors.exceptions.bad_request_400.UsernameNotOccupied:
            await bot.send_message(chat_id=user_id, text=f"Nothing was found at this link")
            await app.stop()
        except Exception as e:
            print(f"Error: {e}")
            await app.stop()
    except FloodWait as e:
        await asyncio.sleep(e.value)  # Wait "value" seconds before continuing
    except Timeout as e:
        await app.stop()
        await bot.send_message(chat_id=user_id, text=f"Error: proxy {proxy_string} doesn't work")


async def _start_sessions(channel_name:str, session_name:str, user_id):

    try:
        app = Client(f"session_files/{session_name}")
        await app.start()
    except:
        await app.stop()
        await bot.send_message("Error")
        return

    try: # Check if there is a channel
        peer = await app.resolve_peer(f"@{channel_name}")

        try:
            access_hash = peer.access_hash
            peer_user_id = peer.user_id 
            peer = InputPeerUser(user_id=peer_user_id, access_hash=access_hash)

        except:
            access_hash = peer.access_hash
            channel_id = peer.channel_id 
            peer = InputPeerChannel(channel_id=channel_id, access_hash=access_hash)

        report_peer = ReportPeer(
            peer = peer,
            reason = InputReportReasonIllegalDrugs(),
            message = text
        )

        result = await app.invoke(report_peer)
        await bot.send_message(chat_id=user_id, text=f"Report sent")
        print(result)
        await app.stop()
    except pyrogram.errors.exceptions.bad_request_400.UsernameNotOccupied:
        await bot.send_message(chat_id=user_id, text=f"Nothing was found at this link")
        await app.stop()
    except Exception as e:
        print(f"Error: {e}")
        await app.stop()

@router.message(Command("report"))
async def get_link(message: types.Message, state: FSMContext):
    await message.answer("Send a link to the group/channel/bot you wanted to file a complaint against", reply_markup=user_buttons.cancel())
    await state.set_state(GetLinkForReport.get_link)

@router.message(GetLinkForReport.get_link)
async def report(message: types.Message, state: FSMContext):
    if "https://t.me" in message.text:
        if database.get_sessions(message.from_user.id):
            channel_name = message.text.split("t.me/")[-1].strip("/")
            proxy_list = database.get_proxy(message.from_user.id).split(",")
            if proxy_list:
                session_names = database.get_sessions(message.from_user.id).split()
                # print(proxy_list)
                # print(session_names)
                tasks = []
                for i, session_name in enumerate(session_names):
                    proxy = proxy_list[i % len(proxy_list)]
                    task = asyncio.create_task(_start_proxy_sessions(channel_name, session_name, proxy_string=proxy, user_id=message.from_user.id))
                    tasks.append(task)
                await asyncio.gather(*tasks)
                await state.clear()
            else:
                session_names = database.get_sessions(message.from_user.id).split()
                tasks = []
                for session_name in session_names:
                    task = asyncio.create_task(_start_sessions(channel_name, session_name, user_id=message.from_user.id))
                    tasks.append(task)
                await asyncio.gather(*tasks)
                await state.clear()
        else:
            await message.answer("Your list of downloaded sessions is empty", reply_markup=user_buttons.meny_keyboard())
            await state.clear()
    else:
        await message.answer("Enter the link")
