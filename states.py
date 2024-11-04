from aiogram.fsm.state import State, StatesGroup

class UploadSession(StatesGroup):
    get_zipfile = State()

class UploadProxy(StatesGroup):
    get_proxy = State()

class GetLinkForReport(StatesGroup):
    get_link = State()