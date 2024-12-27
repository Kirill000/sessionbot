# import structlog
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import messages
from config.config import bot
from mainSQL import database
from models import Users
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters import is_channel_member, is_admin, freq_check
from aiogram.fsm.storage.base import StorageKey
from ast import literal_eval
from aiogram import types
import asyncio
from config import config
# from fluent.runtime import FluentLocalization
# 
# from filters.is_owner import IsOwnerFilter

# Declare router

router = Router()
router.message.filter(F.chat.type == "private", is_channel_member, is_admin, freq_check) # allow bot admin actions only for bot owner

# Declare handlers
# logger = structlog.get_logger()

# # Handlers:

class Form(StatesGroup):
    sendall_text = State()
    user_id_ban = State()
    add_user = State()
    mod = State()
    mod_msg = State()
    mod_sub = State()
    author_to_edit = State()
    
async def moderation_cycle():
    print("LAUNCHED")

    try:
        while True:
            print('dd')
            users = database.select_all_params_from_table_by_column_in_dict('users', Users, 'is_admin', True)
            if len(config.ANSWERS_FOR_MODERATION) != 0:
                print("MODERING", users, config.IS_ADMIN_BUSY)
                for user in users:
                    send_mod = False
                    if not user["id"] in config.IS_ADMIN_BUSY:
                        send_mod = True
                    else:
                        if config.IS_ADMIN_BUSY[user["id"]] == False:
                            send_mod = True
                    print(send_mod)   
                    if send_mod:
                        print('doing')
                        config.IS_ADMIN_BUSY[user["id"]] = True
                        kb = [[KeyboardButton(text="Cancel")], [KeyboardButton(text="Approve")]]
                        kb.append([types.KeyboardButton(text="Главное меню")])
                        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
                        print('q')
                        print(config.ANSWERS_FOR_MODERATION)
                        print(config.ANSWERS_FOR_MODERATION[0][1], int(config.ANSWERS_FOR_MODERATION[0][0]))
                        q = database.databaseSearchByID(config.SUBJECT_NAME_TO_CLASS[config.ANSWERS_FOR_MODERATION[0][1]], int(config.ANSWERS_FOR_MODERATION[0][0]))
                        print('aftq')
                        photos = []
                        print('photos')
                        if literal_eval(q['answer_imgs']) != None:
                            is_caption = 1
                            for photo in literal_eval(q['answer_imgs']):
                                photos.append(types.InputMediaPhoto(media=photo, caption=(str(q['id'])+". "+str(q["title"])+"\n"+"Ответ: "+str(q['answer_text']))*is_caption))
                                is_caption = 0
                        print('state')
                        new_storage_key = StorageKey(config.bot.id, user['id'], user['id'])
                        print('fsm')
                        state = FSMContext(storage=config.dp.storage, key=new_storage_key)
                        # Устанавливаем состояние
                        print('state is set')
                        await state.update_data(mod_msg=q)
                        await state.update_data(mod_sub=config.ANSWERS_FOR_MODERATION[0][1])
                        if photos != []:
                            await config.bot.send_media_group(int(user['id']), media=photos)
                        else:
                            await config.bot.send_message(int(user['id']), text=q["title"]+"\n"+"Ответ: "+q['answer_text'])
                        await config.bot.send_message(int(user['id']), text="По кнопкам ниже примите решение", reply_markup=keyboard)       
                        print('sent')
                        config.ANSWERS_FOR_MODERATION.pop(0)
                        await state.set_state(Form.mod)
            await asyncio.sleep(10)
    except Exception as error:
        print(error)
    
@router.message(F.text, Form.mod)
async def mod_check(message: Message, state: FSMContext):
    
    data = await state.get_data()
    question = data.get("mod_msg")
    subject = data.get("mod_sub")
    
    if message.text == "Approve":
        question['is_approved'] = True
        print(subject)
        approved_questions = database.select_all_params_from_table_by_column_in_dict(config.SUBJECT_NAME_TO_CLASS[subject].__name__, config.SUBJECT_NAME_TO_CLASS[subject], 'is_approved', True)
        
        amount_of_approved_questions_for_user = 0
        for q in approved_questions:
            print(question['author'], q['author'])
            if question["author"] == q['author']:
                amount_of_approved_questions_for_user += 1
        
        print(amount_of_approved_questions_for_user)
        if amount_of_approved_questions_for_user == 2:
            user = database.databaseSearchByID(Users, int(question["author"]))
            sbs = user["subjects_allowed_to_read"]+subject+"|"
            user["subjects_allowed_to_read"] = sbs
            database.databaseUpdateEntity(Users, user['id'], user)
            await config.bot.send_message(int(user['id']), "Ваши вопросы прошли проверку и Вам открыт доступ для чтения вопросов по предмету "+subject)
        
        database.databaseUpdateEntity(config.SUBJECT_NAME_TO_CLASS[subject], question['id'], question)
        await state.clear()
        config.IS_ADMIN_BUSY[message.from_user.id] = False
    elif message.text == "Cancel":
        await state.update_data(author_to_edit=question['author'])
        question['answer_text'] = ""
        question['answer_imgs'] = "[]"
        question['author'] = None
        question['is_empty'] = True
        database.databaseUpdateEntity(config.SUBJECT_NAME_TO_CLASS[subject], question['id'], question)
        await state.set_state(Form.author_to_edit)
        kb = []
        kb.append([types.KeyboardButton(text="Главное меню")])
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Напишите какие правки нужно сделать", reply_markup=keyboard)
        
@router.message(F.text, Form.author_to_edit)
async def mod_check(message: Message, state: FSMContext):
    data = await state.get_data()
    author = data.get('author_to_edit')
    question = data.get("mod_msg")
    config.IS_ADMIN_BUSY[message.from_user.id] = False
    print(question)
    await config.bot.send_message(int(author), "Сделанный Вами вопрос "+str(question["id"])+" не прошел проверку. Комментарий модератора: "+message.text)
    await state.clear()
    
@router.message(F.text.lower() == "изменить статус блокировки пользователя")
async def cmd_owner_hello9(message: Message, state: FSMContext):#, l10n: FluentLocalization):

    kb = []

    kb.append([types.KeyboardButton(text="Главное меню")])
    
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        
    await message.answer(
                text="Введите ID пользователя", reply_markup=keyboard
                )
    await state.set_state(Form.user_id_ban)

@router.message(F.text.lower() == "добавить пользователя")
async def cmd_owner_hello9(message: Message, state: FSMContext):#, l10n: FluentLocalization):
        
    kb = []

    kb.append([types.KeyboardButton(text="Главное меню")])
    
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        
    await message.answer(
                text="Введите ID пользователя", reply_markup=keyboard
                )
    await state.set_state(Form.add_user)

@router.message(F.text, Form.user_id_ban)
async def cmd_owner_hello2(message: Message, state: FSMContext):#, l10n: FluentLocalization):
    
    user_id = int(message.text)
    user = database.databaseSearchByID(Users, user_id)
    
    if user == None:
        sbs = ""
        for s in config.SUBJECT_NAME_TO_CLASS.keys():
            sbs += s+"|"
        database.databaseAddCommitMultiply(Users, {"id": user_id, 'subjects_allowed_to_read': sbs})
        await message.answer("Пользователь был успешно добавлен")
    else:
        await message.answer("Данный пользователь уже существует")
    await state.clear()

@router.message(F.text, Form.user_id_ban)
async def cmd_owner_hello2(message: Message, state: FSMContext):#, l10n: FluentLocalization):
    
    user_id = int(message.text)
    user = database.databaseSearchByID(Users, user_id)
    
    if user != None:
        if config.USERS_MESSAGES_FREQ[str(user_id)][2]:
            await message.answer("Пользователь был разбанен")
            await bot.send_message(int(user_id), "Вы были разбанены.")
        else:
            await message.answer("Пользователь был забанен")
            await bot.send_message(int(user_id), "Вы были забанены по решению администратора. Если вы считаете, что это произошло по ошибке, пишите модератору в телеграм канале")
        user["is_banned"] = not user["is_banned"]
        database.databaseUpdateEntity(Users, user['id'], user)
        await state.clear()
    else:
        await message.answer("Данный пользователь не найден. Возможно, вы ошиблись, попробуйте заново.")
        await state.set_state(Form.user_id_ban)
        

# # Here is some example !ping command ...
# @router.message(
#     # IsOwnerFilter(is_owner=True),
#     Command(commands=["ping"]),
# )
# async def cmd_ping_bot(message: Message):#, l10n: FluentLocalization):
#     await message.reply(messages.ping_msg)

#delete and add subscriptions