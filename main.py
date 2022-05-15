import telebot
from telebot import types
from hotels_api import get_cities_dict
from bestdeal import bestdeal
from hotels_api import get_photos
from lowprice import lowprice
from telegram_bot_calendar import DetailedTelegramCalendar
import datetime
from highprice import highprice
from config import token, CityInputError, APIError, ElemQtyError, PriceRangeInputError, CityFindingError, MinMaxError, DistanceError, HotelsQtyError, YesOrNoError, NoHotelsError, NoHistoryError
from botdb import insert, fetch_by_id

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
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


@bot.message_handler(commands=['help'])
def help_func(message):
    bot.send_message(
        message.from_user.id,
        'Что ещё может этот бот?\n' +
        '/help — помощь по командам бота\n' +
        '/lowprice — вывод самых дешёвых отелей в городе\n' +
        '/highprice — вывод самых дорогих отелей в городе\n' +
        '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n' +
        '/history — вывод истории поиска отелей')


user_info = {}


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def main_func(message):
    user_command = message.text
    command_time = datetime.datetime.now()

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
                raise CityInputError
        except (CityInputError, CityFindingError) as city_error:
            bot.send_message(message.from_user.id, str(city_error))
            bot.send_message(message.from_user.id, 'Введите название города:')
            bot.register_next_step_handler(message, get_city)

    def choose_city(message, cities):
        user_info[message.from_user.id] = {}
        user_info[message.from_user.id]['user_id'] = message.from_user.id
        for city_id, i_city in cities.items():
            if i_city == message.text:
                user_info[message.from_user.id]['city'] = i_city
                user_info[message.from_user.id]['city_id'] = city_id
        bestdeal_filter(message)

    def bestdeal_filter(message):
        if user_command == '/bestdeal':
            bot.send_message(message.from_user.id, 'Введите диапазон цен через пробел (например: 5000 10000):')
            bot.register_next_step_handler(message, distance)
        else:
            date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).build()
            bot.send_message(message.from_user.id, 'Выберите дату прибытия в отель:', reply_markup=date_markup)

    def distance(message):
        try:
            prices_range = message.text.split()
            if len(prices_range) != 2:
                raise ElemQtyError
            else:
                if prices_range[0].isdigit() and prices_range[1].isdigit():
                    if int(prices_range[1]) <= int(prices_range[0]):
                        raise MinMaxError
                    else:
                        user_info[message.from_user.id]['min_price'] = prices_range[0]
                        user_info[message.from_user.id]['max_price'] = prices_range[1]
                        dist_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                        dist_markup.row('1', '3', '5')
                        msg = bot.send_message(message.from_user.id,
                                               text='Выберите необходимое расстояние до центра (в км)',
                                               reply_markup=dist_markup)
                        bot.register_next_step_handler(msg, save_distance)
                else:
                    raise PriceRangeInputError
        except (ElemQtyError, MinMaxError, PriceRangeInputError) as error:
            bot.send_message(message.from_user.id, str(error))
            bot.send_message(message.from_user.id, 'Введите диапазон цен через пробел (например: 5000 10000):')
            bot.register_next_step_handler(message, distance)

    def save_distance(message):
        try:
            if message.text.isdigit():
                user_info[message.from_user.id]['distance'] = message.text
                date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).build()
                bot.send_message(message.from_user.id, 'Выберите дату прибытия в отель:', reply_markup=date_markup)
            else:
                raise DistanceError
        except DistanceError as distance_error:
            bot.send_message(message.from_user.id, str(distance_error))
            dist_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            dist_markup.row('1', '3', '5')
            msg = bot.send_message(message.from_user.id,
                                   text='Выберите необходимое расстояние до центра (в км)',
                                   reply_markup=dist_markup)
            bot.register_next_step_handler(msg, save_distance)

    def checkin(message, checkin_date):
        user_info[message.id]['checkin'] = str(checkin_date)
        date_markup, step = DetailedTelegramCalendar(min_date=checkin_date,
                                                     calendar_id=2).build()
        bot.send_message(message.id, 'Выберите дату отъезда из отеля:', reply_markup=date_markup)

    def checkout(message, checkout_date):
        user_info[message.id]['checkout'] = str(checkout_date)
        user_info[message.id]['command'] = user_command
        user_info[message.id]['command_time'] = command_time
        hotels_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        hotels_Qty_markup.row('1', '2', '3')
        hotels_Qty_markup.row('4', '5', '6')
        msg = bot.send_message(message.id, text='Введите кол-во отелей (максимум - 6)',
                               reply_markup=hotels_Qty_markup)
        bot.register_next_step_handler(msg, hotels_Qty)

    def hotels_Qty(message):
        try:
            if message.text.isdigit():
                user_info[message.from_user.id]['hotelsQty'] = message.text
                photo_req_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                photo_req_markup.row('Да', 'Нет')
                bot.send_message(message.from_user.id, 'Загрузить фото отелей?', reply_markup=photo_req_markup)
                bot.register_next_step_handler(message, photo_req)
            else:
                raise HotelsQtyError
        except HotelsQtyError as hotels_qty_error:
            bot.send_message(message.from_user.id, str(hotels_qty_error))
            hotels_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            hotels_Qty_markup.row('1', '2', '3')
            hotels_Qty_markup.row('4', '5', '6')
            msg = bot.send_message(message.from_user.id,
                                   text='Введите кол-во отелей (максимум - 6)',
                                   reply_markup=hotels_Qty_markup)
            bot.register_next_step_handler(msg, hotels_Qty)

    def photo_req(message):
        try:
            if message.text.lower() == 'да':
                photo_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                photo_Qty_markup.row('1', '2', '3')
                photo_Qty_markup.row('4', '5', '6')
                photo_Qty_markup.row('7', '8', '9')
                bot.send_message(message.from_user.id, 'Введите кол-во фото (максимум - 9)',
                                 reply_markup=photo_Qty_markup)
                bot.register_next_step_handler(message, command_redirection)
            elif message.text.lower() != 'да' or message.text.lower() != 'нет':
                raise YesOrNoError
        except YesOrNoError as yes_or_no_error:
            bot.send_message(message.from_user.id, str(yes_or_no_error))
            photo_req_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            photo_req_markup.row('Да', 'Нет')
            bot.send_message(message.from_user.id, 'Загрузить фото отелей?', reply_markup=photo_req_markup)
            bot.register_next_step_handler(message, photo_req)

    def command_redirection(message):
        photoQty = message.text
        user_query = user_info[message.from_user.id]
        user_info[message.from_user.id]['results'] = []
        if message.text.isdigit():
            user_info[message.from_user.id]['photoQty'] = message.text
        try:
            if user_command == '/lowprice':
                for i_hotel in lowprice(user_query):
                    msg = f'Название отеля: {str(i_hotel[1])}\n'\
                          f'Адрес отеля: {str(i_hotel[2])}\n'\
                          f'От центра: {str(i_hotel[3])}\n'\
                          f'Цена за ночь: {str(i_hotel[4])}\n'\
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if photoQty.isdigit():
                        photos = get_photos(i_hotel[0], photoQty)
                        bot.send_media_group(message.from_user.id, photos)
            elif user_command == '/highprice':
                for i_hotel in highprice(user_query):
                    msg = f'Название отеля: {str(i_hotel[1])}\n' \
                          f'Адрес отеля: {str(i_hotel[2])}\n' \
                          f'От центра: {str(i_hotel[3])}\n' \
                          f'Цена за ночь: {str(i_hotel[4])}\n' \
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if photoQty.isdigit():
                        photos = get_photos(i_hotel[0], photoQty)
                        bot.send_media_group(message.from_user.id, photos)
            elif user_command == '/bestdeal':
                for i_hotel in bestdeal(user_query):
                    msg = f'Название отеля: {str(i_hotel[1])}\n' \
                          f'Адрес отеля: {str(i_hotel[2])}\n' \
                          f'От центра: {str(i_hotel[3])}\n' \
                          f'Цена за ночь: {str(i_hotel[4])}\n' \
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if photoQty.isdigit():
                        photos = get_photos(i_hotel[0], photoQty)
                        bot.send_media_group(message.from_user.id, photos)
        except NoHotelsError as hotels_error:
            bot.send_message(message.from_user.id, str(hotels_error))
        except APIError as api_error:
            bot.send_message(message.from_user.id, str(api_error))
        else:
            insert(user_id=user_info[message.from_user.id]['user_id'], city=user_info[message.from_user.id]['city'],
                   city_id=user_info[message.from_user.id]['city_id'], checkin=user_info[message.from_user.id]['checkin'],
                   checkout=user_info[message.from_user.id]['checkout'], command=user_info[message.from_user.id]['command'],
                   command_time=user_info[message.from_user.id]['command_time'], results=user_info[message.from_user.id]['results'])
        help_func(message)

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
        checkin_date = user_info[call.message.chat.id]['checkin'].split('-')
        result, key, step = DetailedTelegramCalendar(min_date=datetime.date(year=int(checkin_date[0]),
                                                                            month=int(checkin_date[1]),
                                                                            day=int(checkin_date[2])),
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


@bot.message_handler(commands=['history'])
def history(message):
    try:
        for entry in fetch_by_id(message.from_user.id):
            query = ''
            for i_entry in entry:
                if isinstance(i_entry, list):
                    for hotel_string in i_entry:
                        query += '\n'
                        query += hotel_string
                else:
                    query += str(i_entry)
                    query += '\n'
            bot.send_message(message.from_user.id, query)
    except NoHistoryError as history_error:
        bot.send_message(message.from_user.id, history_error)
        help_func(message)


if __name__ == "__main__":
    bot.polling(none_stop=True)
