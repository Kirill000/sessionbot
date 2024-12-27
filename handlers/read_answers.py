from os import getenv
import config.config as config

from aiogram import F, Router
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import messages
from mainSQL import SQLDataBase
from models import Users, SAU, Schemotech
from WBClass import WB
from datetime import datetime, timedelta
from ast import literal_eval
from config.config import bot
from mainSQL import database
from filters import is_channel_member, freq_check
import random

# BOT_TOKEN = "7601918498:AAF2tJiIHbxqseispXgGRX9FwFNMI86qFVo"
# TOKEN = getenv(BOT_TOKEN)

router = Router()

router.message.filter(F.chat.type == "private", is_channel_member, freq_check) # allow bot admin actions only for bot owner

class Form(StatesGroup): 
    subject_to_read = State()
    q_num_to_read = State()

@router.message(F.text.lower() == "смотреть ответы")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    
    kb = []
    for table in config.SUBJECT_NAME_TO_CLASS.keys():
        kb.append([types.KeyboardButton(text=table)])
    kb.append([types.KeyboardButton(text="Главное меню")])
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Выберите предмет", reply_markup=keyboard
        )
    await state.set_state(Form.subject_to_read)

@router.message(F.text, Form.subject_to_read)
async def echo_handler(message: Message, state: FSMContext):
    
    user = database.databaseSearchByID(Users, message.from_user.id)
    correct_table = False
    for table in config.SUBJECT_NAME_TO_CLASS.keys():
        if message.text == table:
            correct_table = True
            break
    await state.update_data(subject_to_read=message.text)
    if correct_table and ((message.text in user["subjects_allowed_to_read"]) or user['is_admin']):
    
        await message.answer(
            "Введите номер вопроса для чтения или ищите по ключевым словам", parse_mode=ParseMode.HTML
        )
        await state.set_state(Form.q_num_to_read)
        
    elif not message.text in user["subjects_allowed_to_read"]:
        await message.answer("Данная категория Вам недоступна", parse_mode=ParseMode.HTML)
        await state.clear()
    elif not correct_table:
        await message.answer("Данная категория не найдена", parse_mode=ParseMode.HTML)
        await state.set_state(Form.q_num_to_read)


@router.message(F.text, Form.q_num_to_read)
async def echo_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    subject_to_read = data.get("subject_to_read")
    queried_questions = []
    
    try:
        queried_questions.append(database.databaseSearchByID(config.SUBJECT_NAME_TO_CLASS[subject_to_read], int(message.text)))
    except ValueError:
        questions = database.select_all_params_from_table_in_dict(config.SUBJECT_NAME_TO_CLASS[subject_to_read])   
        for q in questions:
            if message.text.lower() in q['title'].lower():
                queried_questions.append(q)
                
    
    if len(queried_questions) > 1:
        await state.update_data(cur_q=message.text)
        msg_txt = ""
        for q in queried_questions:
            msg_txt += str(q["id"])+". "+q["title"]+"\n"
        await message.answer("по Вашему запросу подходят сразу несколько вопросов:\n"+msg_txt)
        await state.set_state(Form.q_num_to_read)
    elif len(queried_questions) == 0:
        await message.answer("По вашему запросу ничего не найдено", parse_mode=ParseMode.HTML)
        await state.set_state(Form.q_num_to_read)
    elif len(queried_questions) == 1:
        q = queried_questions[0]
        
        if not q['is_empty'] and q['is_approved']:    
            photos = []
            if literal_eval(q['answer_imgs']) != None:
                is_caption = 1
                for photo in literal_eval(q['answer_imgs']):
                    photos.append(types.InputMediaPhoto(media=photo, caption=(str(q['id'])+". "+q["title"]+"\n\n"+q['answer_text'])*is_caption))
                    is_caption = 0
                
            if photos != []:    
                await message.answer_media_group(media=photos) 
            else:
                await message.answer(text=str(q['id'])+". "+q["title"]+"\n\n"+q['answer_text'])
            await state.set_state(Form.q_num_to_read)
        else:
            await message.answer(text="Данный вопрос не отвечен или находится на проверке у модератора")
            await state.set_state(Form.q_num_to_read)
            