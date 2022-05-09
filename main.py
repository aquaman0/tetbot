import telebot
from telebot import types
from hotels_api import get_cities_dict
from bestdeal import bestdeal
from history import history
from lowprice import lowprice, get_photos
import sqlite3
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
from botdb import dbAccess
import highprice
import config

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(
        message.from_user.id,
        f'{message.from_user.first_name}, добро пожаловать в телеграм-бот Too Easy Travel\n' +
        'Что может этот бот?\n' +
        '/help — помощь по командам бота\n' +
        '/lowprice — вывод самых дешёвых отелей в городе\n' +
        '/highprice — вывод самых дорогих отелей в городе\n' +
        '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n' +
        '/history — вывод истории поиска отелей')


user_info = {}


@bot.message_handler(commands=['lowprice'])
def main_func(message):
    user_command = message.text

    def first_step(message):
        bot.send_message(message.from_user.id, 'Введите название города:')
        bot.register_next_step_handler(message, get_city)

    def get_city(message):
        try:
            if message.text.isalpha():
                cities_dict = get_cities_dict(message.text)
                cities = cities_dict.values()
                cities_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                for city in cities:
                    cities_markup.add(city)

                bot.send_message(message.from_user.id, 'Выберите нужный город:', reply_markup=cities_markup)
                bot.register_next_step_handler(message, choose_city, cities_dict)
            else:
                raise ValueError('Название города должно содержать только буквы.')
        except ValueError as err:
            bot.send_message(message.from_user.id, str(err))
            bot.send_message(message.from_user.id, 'Введите название города:')
            bot.register_next_step_handler(message, get_city)

    def choose_city(message, cities):
        user_info[message.from_user.id] = {}
        for city_id, i_city in cities.items():
            if i_city == message.text:
                user_info[message.from_user.id]['city'] = i_city
                user_info[message.from_user.id]['city_id'] = city_id

        date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).build()
        bot.send_message(message.from_user.id, 'Выберите дату прибытия в отель:', reply_markup=date_markup)

    def checkin(message, checkin_date):
        user_info[message.id]['checkin'] = str(checkin_date)
        date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=2).build()
        bot.send_message(message.id, 'Выберите дату отъезда из отеля:', reply_markup=date_markup)

    def checkout(message, checkout_date):
        user_info[message.id]['checkout'] = str(checkout_date)
        hotels_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        hotels_Qty_markup.row('1', '2', '3')
        hotels_Qty_markup.row('4', '5', '6')
        msg = bot.send_message(message.id, text='Введите кол-во отелей (максимум - 6)', reply_markup=hotels_Qty_markup)
        bot.register_next_step_handler(msg, hotels_Qty)

    def hotels_Qty(message):
        user_info[message.from_user.id]['hotelsQty'] = message.text
        photo_req_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        photo_req_markup.row('Да', 'Нет')
        bot.send_message(message.from_user.id, 'Загрузить фото отелей?', reply_markup=photo_req_markup)
        bot.register_next_step_handler(message, photo_req)

    def photo_req(message):
        if message.text.lower() == 'да':
            photo_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            photo_Qty_markup.row('1', '2', '3')
            photo_Qty_markup.row('4', '5', '6')
            photo_Qty_markup.row('7', '8', '9')
            bot.send_message(message.from_user.id, 'Введите кол-во фото (максимум - 9)', reply_markup=photo_Qty_markup)
        bot.register_next_step_handler(message, command_redirection)

    def command_redirection(message):
        photoQty = message.text
        data = user_info[message.from_user.id]
        if message.text.isdigit():
            user_info[message.from_user.id]['photoQty'] = message.text
        if user_command == '/lowprice':
            for i_hotel in lowprice(data):
                bot.send_message(message.from_user.id,
                                 f'Название отеля: {str(i_hotel[1])}\n'
                                 f'Адрес отеля: {str(i_hotel[2])}\n'
                                 f'От центра: {str(i_hotel[3])}\n'
                                 f'Цена за ночь: {str(i_hotel[4])}\n')
                if photoQty.isdigit():
                    photos = get_photos(i_hotel[0], photoQty)
                    bot.send_media_group(message.from_user.id, photos)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
    def call_checkin(call):
        result, key, step = DetailedTelegramCalendar(min_date=datetime.date.today(),
                                                     locale='ru',
                                                     calendar_id=1).process(call.data)
        if not result and key:
            bot.edit_message_text('Выберите дату прибытия в отель:',
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f'Дата прибытия: {result}',
                                  call.message.chat.id,
                                  call.message.message_id)
            checkin(call.message.chat, result)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
    def call_checkout(call):
        result, key, step = DetailedTelegramCalendar(min_date=datetime.date.today(),
                                                     locale='ru',
                                                     calendar_id=2).process(call.data)
        if not result and key:
            bot.edit_message_text('Выберите дату отъезда:',
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f'Дата отъезда: {result}',
                                  call.message.chat.id,
                                  call.message.message_id)
            checkout(call.message.chat, result)

    first_step(message)


@bot.message_handler(content_types=['text'])
def get_messages(message):
    bot.send_message(message.from_user.id, f'You said {message.text}')


if __name__ == "__main__":
    bot.polling(none_stop=True)
