from models import Users
from datetime import datetime, timedelta
from mainSQL import database
from WBClass import WB
from config import config    
from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsChannelMemberFilter(BaseFilter):
    def __init__(self, is_subscribed) -> None:
        self.is_subscribed=is_subscribed

    async def __call__(self, message: Message) -> bool:
            
        user_channel_status = await config.bot.get_chat_member(chat_id=config.TELEGRAM_CHANNEL_ID, user_id=message.from_user.id)

        if user_channel_status.status != 'left':
            self.is_subscribed = True
            return True
        else:
            if self.is_subscribed:
                await message.answer(text='Для продолжения работы с ботом подпишитесь на наш телеграм канал - там все самые последние обновления https://t.me/+cGjCHpVNMx1lYzhi')
                self.is_subscribed = False
                return False
        
class IsAdminFilter(BaseFilter):
    def __init__(self, admin) -> None:
        self.admin=admin

    async def __call__(self, message: Message) -> bool:
        
        user = database.databaseSearchByID(Users, message.from_user.id)
        
        if user == None:
            if self.admin:
                await message.answer("Вы не являетесь администратором")
                self.admin = False
                return False
        else:
            if user["is_admin"] == False:
                if self.admin:
                    await message.answer("Вы не являетесь администратором")
                    self.admin = False
                    return False
            else:
                self.admin = True
                return True

class FreqCheck(BaseFilter):
    def __init__(self):
        self.trig = datetime.now()
        
    async def __call__(self, message: Message) -> bool:

        try:        
            freq_data = config.USERS_MESSAGES_FREQ[str(message.from_user.id)]
            prev_time = datetime.strptime(freq_data[0], "%Y-%m-%d %H:%M:%S.%f")
            amount = freq_data[1]
            is_banned = freq_data[2]
            
            if not is_banned:                
                    
                if prev_time+timedelta(seconds=2) >= datetime.now():
                    config.USERS_MESSAGES_FREQ[str(message.from_user.id)][1] = amount + 1
                    if amount == 4:
                        await message.answer("Вы слишком часто отправляете сообщения (лимит: 9 сообщений в 2 секунды). В случае продолжения мы будем вынуждены ограничить доступ к боту. Разблокировка пользователя осуществляется только через модератора.")
                else:
                    config.USERS_MESSAGES_FREQ[str(message.from_user.id)][1] = 0
                
                config.USERS_MESSAGES_FREQ[str(message.from_user.id)][0] = str(datetime.now())
                
                if config.USERS_MESSAGES_FREQ[str(message.from_user.id)][1] >= 9:
                    config.USERS_MESSAGES_FREQ[str(message.from_user.id)][2] = True
                    await message.answer("Вы были забанены из-за частой отправки сообщений. Если вы считаете, что это ошибка, напишите модератору в телеграм канале.")
                    with open("BANNED_USERS_LOG.txt", "w") as file:
                        file.write(str(config.USERS_MESSAGES_FREQ))
                        file.close()
                    return False
                else:
                    return True
            
            else:
                return False
            
        except KeyError:
            config.USERS_MESSAGES_FREQ[str(message.from_user.id)] = [str(datetime.now()), 0, 0]
            return True

is_admin = IsAdminFilter(admin=True)
is_channel_member = IsChannelMemberFilter(is_subscribed=True)
freq_check = FreqCheck()

