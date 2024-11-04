import zipfile
import os
import random
import aiohttp
import sqlite3

from aiogram import types, Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import UploadSession, UploadProxy
from database import database
from buttons import user_buttons

callback_router = Router()

bot = Bot("")

# Session

@callback_router.callback_query(F.data == "sessions")
async def session_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("To load sessions, prove .ZIP archive with .session files", reply_markup=user_buttons.cancel())
    await callback.answer()
    await state.set_state(UploadSession.get_zipfile)

@callback_router.message(UploadSession.get_zipfile, F.document)
async def upload_sessions(message: Message, state: FSMContext):
    document = message.document
    file_id = document.file_id
    file_format = message.document.file_name.split(".")[-1]
    if file_format == "zip":
        await bot.download(document, f"{message.from_user.username}_{file_id[0:6]}.zip")
        session_names = []
        with zipfile.ZipFile(f"{message.from_user.username}_{file_id[0:6]}.zip", "r") as file:
            if file.infolist():
                for info in file.infolist():
                    # print(info.filename.split(".session")[0])
                    new_name = f"{message.from_user.username}_{info.filename.split('.session')[0]}_{random.randint(1000, 10000)}"
                    session_names.append(new_name)
                    file.extract(info, path="session_files")
                    os.rename(os.path.join("session_files", info.filename), os.path.join("session_files", f"{new_name}.session"))
                # file.extractall("session_files")
        database.add_sessions(user_id=message.from_user.id, sessions=", ".join(session_names))
        os.remove(f"{message.from_user.username}_{file_id[0:6]}.zip")
        await message.answer("Sessions upload", reply_markup=user_buttons.meny_keyboard())
        await state.clear()
    else:
        await message.answer("You didn't send a zip file")


@callback_router.callback_query(F.data == "proxy")
async def proxy_callback(callback: CallbackQuery, state: FSMContext):
    text_proxy = f"To upload a proxy, send it in the format proxy_ip:port:username:password in a txt file"
    await callback.message.answer(text_proxy, reply_markup=user_buttons.cancel())
    await callback.answer()
    await state.set_state(UploadProxy.get_proxy)

@callback_router.message(UploadProxy.get_proxy, F.document)
async def upload_proxy(message: Message, state: FSMContext):
    document = message.document
    file_format = message.document.file_name.split(".")[-1]
    if file_format == "txt":
        await bot.download(document, f"{message.from_user.username}_proxy.txt")
        with open(f"{message.from_user.username}_proxy.txt", "r") as file:
            data = file.read()
            filtred_proxy = [result for result in data.split() if result.count(":") == 3]
            # checked_proxy = _check_proxy(proxy_list=filtred_proxy)
            # database.add_proxy(message.from_user.id, ", ".join(filtred_proxy))
        await state.clear()
        os.remove(f"{message.from_user.username}_proxy.txt")
        await message.answer("The proxies have been uploaded")
    else:
        await message.answer("You didn't send a txt file")

# Sessions view

@callback_router.callback_query(F.data == "loaded_session")
async def session_callback(callback: CallbackQuery, state: FSMContext):
    data = database.get_sessions(callback.from_user.id)
    if not data:
        string_data = "nothing"
    else:
        string_data = data
    await callback.message.answer(f"Your sessions: {string_data}")
    await callback.answer()
    