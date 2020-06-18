from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    Name = State()
    Author = State()
    Location = State()
    Photo = State()
    Addrdate = State()
    Status = State()
    Typeof = State()
