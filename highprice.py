import telebot
from telebot import types
from hotels_api import get_cities_dict
from bestdeal import bestdeal
from history import history
import sqlite3
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
from botdb import dbAccess
import config

bot = telebot.TeleBot(config.token)