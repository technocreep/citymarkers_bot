from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text


from config import TOKEN, MY_ID, CITE_URL
from states import Form
from api.hosting_api import send_to_host
from api.server_api import send_to_server
from keyboards.start_help_kb import start_help_keyboard

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


async def start_bot(*args):
    await bot.send_message(chat_id=MY_ID,
                           text='bot is working')


@dp.message_handler(commands=['start'])
async def get_started(msg: types.Message):
    user = msg.from_user.full_name
    await msg.answer(text=f'Привет, {user}! С помощью этого бота можно добавить метку в проект CITYMARKERS',
                     reply_markup=start_help_keyboard())


@dp.message_handler(Text(equals='help'))
async def get_help(msg: types.Message):
    await msg.reply(text=f'{msg.from_user.full_name}, нажми "старт", чтобы добавить метку',
                    reply_markup=start_help_keyboard())


@dp.message_handler(Text(equals=['start']))
async def process_start(message: types.Message):
    user = message.from_user.username
    await bot.send_message(chat_id=MY_ID,
                           text=f'Bot Now used by @{user}')

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='unnamed')]
        ],
        resize_keyboard=True
    )
    await message.answer(text='Поiхали \U0001F31A \nКак называется сие творение?',
                         reply_markup=reply_markup)
    await Form.Name.set()


@dp.message_handler(state=Form.Name)
async def add_name(msg: types.Message, state: FSMContext):
    name = msg.text
    await state.update_data(name=name)
    # custom_keyboard = [['anonimous']]
    # reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='anonymous')]
        ],
        resize_keyboard=True
    )
    await bot.send_message(chat_id=msg.from_user.id,
                           text='А кто, собственно, автор?',
                           reply_markup=reply_markup)
    await Form.Author.set()


@dp.message_handler(state=Form.Author)
async def add_author(msg: types.Message, state: FSMContext):
    author = msg.text
    await state.update_data(author=author)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Я прям возле творения!',
                            request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await bot.send_message(chat_id=msg.from_user.id,
                           text='Теперь пришли мне локацию этой работы',
                           reply_markup=reply_markup)
    await Form.Location.set()


@dp.message_handler(state=Form.Location, content_types=['location'])
async def add_location(msg: types.Message, state: FSMContext):
    loc = [msg.location.latitude, msg.location.longitude]
    await state.update_data(location=loc)
    await msg.answer('Круто, теперь шли фотку!',
                     reply_markup=ReplyKeyboardRemove())
    await Form.Photo.set()


@dp.message_handler(state=Form.Photo, content_types=['photo'])
async def add_photo(msg: types.Message, state: FSMContext):
    file_id = msg.photo[1]['file_id']
    await state.update_data(photo=file_id)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Не хочу')]
        ],
        one_time_keyboard=True,
        resize_keyboard=True)
    await bot.send_message(chat_id=msg.from_user.id,
                           text='На всякий случай черкани адресок',
                           reply_markup=reply_markup)
    await Form.Addrdate.set()


@dp.message_handler(state=Form.Addrdate)
async def add_addrdate(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'Не хочу':
        addrdate = '---'
    else:
        addrdate = msg.text
    await state.update_data(addrdate=addrdate)

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='граффити')],
            [KeyboardButton(text='стрит-арт')]
        ],
        one_time_keyboard=True,
        resize_keyboard=True)

    await bot.send_message(chat_id=msg.from_user.id,
                           text='Это граффити или стрит-арт?',
                           reply_markup=reply_markup)
    await Form.Typeof.set()


@dp.message_handler(state=Form.Typeof)
async def add_typeof(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'граффити':
        await state.update_data(typeof='graffity')
    elif msg.text.lower() == 'стрит-арт':
        await state.update_data(typeof='streetart')
    custom_keyboard = [
        [KeyboardButton(text='на месте')],
        [KeyboardButton(text='закрашена')]
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    await bot.send_message(chat_id=msg.from_user.id,
                           text='Работа на месте (on spot) или закрашена (buff) ?',
                           reply_markup=reply_markup)
    await Form.Status.set()


@dp.message_handler(state=Form.Status)
async def add_status(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'закрашена':
        await state.update_data(status='buff')
    elif msg.text.lower() == 'на месте':
        await state.update_data(status='onspot')
    data = await state.get_data()
    text = f'''
Название: {data.get('name')}
Автор: {data.get('author')}
Местечко: {data.get('location')}
Адресок: {data.get('addrdate')}
Статусец: {data.get('status')}
Тип: {data.get('typeof')}
'''
    await bot.send_photo(chat_id=msg.from_user.id,
                         photo=data.get('photo'),
                         caption=text)

    custom_keyboard = [
        [KeyboardButton(text='Ништяк')],
        [KeyboardButton(text='Всё по новой давай!')]
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
    await bot.send_message(chat_id=msg.from_user.id,
                           text='Считай, что метка уже на карте :). Осталось подтвердить',
                           reply_markup=reply_markup)
    await state.reset_state(with_data=False)


@dp.message_handler()
async def make_decision(msg: types.Message, state: FSMContext):
    if msg.text == 'Ништяк':
        data = await state.get_data()
        file_id = data.get('photo')

        photo_url = send_to_host(file_id=file_id)

        response_from_server = await send_to_server(photo_url=photo_url, data=data)
        print(response_from_server)
        if response_from_server == 201:
            await state.finish()

            await msg.answer(text=F'Удача, брат! Ищи метку на карте: {CITE_URL}',
                             reply_markup=start_help_keyboard())
        else:
            await state.finish()
            await msg.answer(text='Беда на сервере, брат! Давай в другой раз?',
                             reply_markup=start_help_keyboard())

    elif msg.text == 'Всё по новой давай!':
        await state.finish()

        reply_markup = start_help_keyboard()
        await msg.answer(text='Ну, давай снова. Жми Старт',
                         reply_markup=reply_markup)


if __name__ == '__main__':
    executor.start_polling(dp,
                           # on_startup=start_bot
                           )
