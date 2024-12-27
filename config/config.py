from aiogram import Bot
from models import SAU, Schemotech

DATABASE_URI = 'postgresql+psycopg2://postgres:admin@localhost:5432/'
BOT_TOKEN = "7767003722:AAFVqiPeojKo9C-miKu1WnI8WD_UGtg6L4k"
TELEGRAM_CHANNEL_ID = -1002422970488
ANSWERS_FOR_MODERATION = []
USERS_MESSAGES_FREQ = {}
IS_ADMIN_BUSY = {}
SUBJECT_NAME_TO_CLASS = {"Средства автоматизации и управления": SAU, "Схемотехника": Schemotech}
bot = None
dp = None