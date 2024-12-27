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
    subject = State()
    questions = State()
    cur_q = State()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    
    kb = []
    kb.append([types.KeyboardButton(text="Отвечать на вопросы")])
    kb.append([types.KeyboardButton(text="Смотреть ответы")])

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Привет! Выберите чем Вы хотите заняться)", reply_markup=keyboard
        )

@router.message(F.text.lower() == "главное меню")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    
    kb = []
    kb.append([types.KeyboardButton(text="Отвечать на вопросы")])
    kb.append([types.KeyboardButton(text="Смотреть ответы")])

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await state.clear()
    await message.answer(
        "Привет! Выберите чем Вы хотите заняться)", reply_markup=keyboard
        )

@router.message(F.text.lower() == "отвечать на вопросы")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    
    kb = []
    for table in config.SUBJECT_NAME_TO_CLASS.keys():
        kb.append([types.KeyboardButton(text=table)])

    kb.append([types.KeyboardButton(text="Главное меню")])
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Выберите предмет", reply_markup=keyboard
        )
    await state.set_state(Form.subject)

@router.message(F.text, Form.subject)
async def echo_handler(message: Message, state: FSMContext):
    
    await state.update_data(subject=message.text)
    correct_table = False
    for table in config.SUBJECT_NAME_TO_CLASS.keys():
        if message.text == table:
            correct_table = True
            break
        
    if correct_table:
        user = database.databaseSearchByID(Users, message.from_user.id)
        
        try:
            sbjcts = user["subjects_allowed_to_read"]
        except:
            sbjcts = ""
        
        if user == None or not message.text in sbjcts:
            
            if user == None:
                questions_answered_amount = 0
            else:
                questions_answered_amount = len(database.select_all_params_from_table_by_column_in_dict(str(config.SUBJECT_NAME_TO_CLASS[message.text].__name__), "", "author", user['id'])) 
            
            msg_text = ""
            
            empty_questions = database.select_all_params_from_table_by_column_in_dict(str(config.SUBJECT_NAME_TO_CLASS[message.text].__name__), "", "is_empty", True)
            kb = []
            questions_lst = []
            
            if len(empty_questions) != 0 and questions_answered_amount < 3:
                if len(empty_questions) > 3-questions_answered_amount:
                    numbers = random.sample(range(0, len(empty_questions)), 3-questions_answered_amount)
                    for num in numbers:
                        q = empty_questions[num]
                        msg_text += str(q["id"])+". "+q["title"]+"\n\n"
                        kb.append([types.KeyboardButton(text=str(q["id"]))])
                        questions_lst.append(q["id"])
                else:
                    for q in empty_questions:
                        msg_text += str(q["id"])+". "+q["title"]+"\n\n"
                        kb.append([types.KeyboardButton(text=str(q["id"]))])
                        questions_lst.append(q["id"])
                
                kb.append([types.KeyboardButton(text="Главное меню")])      
                await state.update_data(questions=questions_lst)
                
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                await message.answer(
                    "Для доступа ко всем вопросам нужно ответить минимум на 3 вопроса (если вам досталось меньше, значит это последние вопросы и вам повезло))\nВаши вопросы: \n\n"+msg_text, reply_markup=keyboard, parse_mode=ParseMode.HTML
                )
                await message.answer(
                    "По кнопке клавиатуры сначала пришлите номер вопроса, на который вы собрались отвечать, а затем уже сам ответ", parse_mode=ParseMode.HTML
                )
                await state.set_state(Form.questions)
            elif questions_answered_amount >= 3:
                keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Еще вопрос")], [types.KeyboardButton(text="Главное меню")]], resize_keyboard=True)
                await message.answer("Вы ответили на все необходимые вопросы, спасибо!\nЕсли хотите, можете выбрать еще вопрос или выберите другой предмет", reply_markup=keyboard)
                await state.clear()
                await state.update_data(subject=message.text)
            else:
                await message.answer(
                    "На данный момент ответ на вопросы данной категории недоступен (либо они все отвечены, либо их в прицнипе нет)", parse_mode=ParseMode.HTML
                )
                await state.clear()
        else:
            keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Еще вопрос")], [types.KeyboardButton(text="Главное меню")]], resize_keyboard=True)
            await message.answer("Вы ответили на все необходимые вопросы, спасибо!\nЕсли хотите, можете выбрать еще", reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await state.clear()
            await state.update_data(subject=message.text)
    else:
        await message.answer("Вы выбрали неверную категорию", parse_mode=ParseMode.HTML)


@router.message(F.text, Form.questions)
async def echo_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    questions_lst = data.get("questions")
    question_in_lst = False
    
    for q in questions_lst:
        if str(q) == message.text:
            question_in_lst = True
            
    kb = []
    kb.append([types.KeyboardButton(text="Главное меню")])
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    if question_in_lst:
        await state.update_data(cur_q=int(message.text))
        await message.answer("Введите ответ на вопрос", reply_markup=keyboard)
        await state.set_state(Form.cur_q)
    else:
        await message.answer("Вы выбрали неверный номер вопроса. Попробуйте заново", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        await state.set_state(Form.questions)

@router.message(Form.cur_q)
async def echo_handler(message: Message, state: FSMContext):
    
    if message.text != "Еще вопрос":
        data = await state.get_data()
        question = data.get("cur_q")
        subject = data.get("subject")

        user = database.databaseSearchByID(Users, message.from_user.id)
        if user == None:
            database.databaseAddCommitMultiply(Users, {"id": message.from_user.id, "is_admin": message.from_user.id==2099975508})
            
        # question = database.databaseSearchByID(config.SUBJECT_NAME_TO_CLASS[subject])
        photos = []
        async for msg in config.bot.iter_media_group(chat_id=message.chat.id, message_id=message.message_id):
            if msg.photo:
                photos.append(msg.photo[-1].file_id)
                
        if photos != []:
            database.databaseUpdateEntity(config.SUBJECT_NAME_TO_CLASS[subject], question, {"id": question, "answer_text": message.caption, "answer_imgs": str(photos), "author": message.from_user.id, "is_empty": False})    
        else:
            database.databaseUpdateEntity(config.SUBJECT_NAME_TO_CLASS[subject], question, {"id": question, "answer_text": message.text, "author": message.from_user.id, "is_empty": False})    
        
        questions_lst = data.get("questions")
        try:
            questions_lst.remove(question)
            await state.update_data(questions=questions_lst)
        except:
            questions_lst = []
        print('appended')
        config.ANSWERS_FOR_MODERATION.append([question, subject])
        if len(questions_lst) == 0:
            keyboard = types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Еще вопрос")], [types.KeyboardButton(text="Главное меню")]], resize_keyboard=True)
            await message.answer("Вы ответили на все необходимые вопросы, спасибо!\nЕсли хотите, можете выбрать еще вопрос или выберите другой предмет", reply_markup=keyboard)
            await state.clear()
            await state.update_data(subject=subject)
        else:
            kb = []
            for q in questions_lst:
                kb.append([types.KeyboardButton(text=str(q))])
            kb.append([types.KeyboardButton(text="Главное меню")])
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer("Ваш ответ записан. Мы отправим Вам сообщение о решении модератора, а пока можете поотвечать на оставшиеся вопросы", reply_markup=keyboard, parse_mode=ParseMode.HTML)
            await state.set_state(Form.questions)
    else:
        await message.answer("Попробуйте заново")

@router.message(F.text.lower() == "еще вопрос")
async def echo_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    subject = data.get("subject")
    print(subject)
    empty_questions = database.select_all_params_from_table_by_column_in_dict(str(config.SUBJECT_NAME_TO_CLASS[subject].__name__), "", "is_empty", True)
    
    if len(empty_questions) > 0:
        q = empty_questions[0]
        await state.update_data(questions=[q["id"]])
        await state.update_data(cur_q=q["id"])
        await message.answer("Введите ответ на данный вопрос: \n"+str(q["id"])+". "+q["title"])
        await state.set_state(Form.cur_q)
    else:
        await message.answer("Неотвеченных вопросов не осталось!", parse_mode=ParseMode.HTML)
        await state.clear()