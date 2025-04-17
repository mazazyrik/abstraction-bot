"""
Constants module for SpeechAI bot.
Contains configuration values loaded from environment variables.
"""
import os
from aiogram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MY_CHAT_ID = int(os.getenv('TELEGRAM_MY_CHAT_ID', 0))
bot = Bot(token=TOKEN)

# YooKassa Payments
PAYMENTS_TOKEN = os.getenv('YOOKASSA_PAYMENTS_TOKEN')
PAYMENT_ID = os.getenv('YOOKASSA_PAYMENT_ID')
