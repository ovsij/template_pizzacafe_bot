from aiogram import types
from aiogram.dispatcher import FSMContext
import time

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.user_phone)
#@dp.message_handler(content_types=types.Message, state=Form.user_phone)
async def change_phone(message: types.Message, state: FSMContext):
    # записываем номер телефона
    update_user(tg_id=str(message.from_user.id), phone=message.contact.phone_number)
    await state.finish()
    # удаляем ненужные сообщения
    time.sleep(1)
    await message.delete()
    types.ReplyKeyboardRemove()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    # обновляем текст сообщения с меню "настройки"
    try:
        text, reply_markup = inline_kb_settings(message.from_user)
        await Form.menu_message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
    except:
        pass

@dp.message_handler(state=Form.user_phone)
async def user_message(message: types.Message):
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    
    _, reply_markup = reply_kb_change(param='phone')
    Form.prev_message = await bot.send_message(
                message.from_user.id, 
			    text='К сожалению, ввести номер телефона текстом не получится. Нажмите на кнопку "Поделиться номером телефона. \nЕсли вы не видите кнопку, нажмите за значек слева от микрофона внизу экрана, тогда кнопка появится',
                reply_markup=reply_markup
            )
    

@dp.message_handler(state=Form.user_address)
async def change_address(message: types.Message, state: FSMContext):
    # записываем номер телефона
    update_user(tg_id=str(message.from_user.id), address=message.text)
    await state.finish()
    # удаляем ненужные сообщения
    time.sleep(1)
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    # обновляем текст сообщения с меню "настройки"
    try:
        text, reply_markup = inline_kb_settings(message.from_user)
        await Form.menu_message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
    except:
        pass

@dp.message_handler()
async def user_message(message: types.Message):
    await message.delete()