import telebot
from telebot import types
from hotels_api import get_cities_dict
from bestdeal import bestdeal
from hotels_api import get_photos
from lowprice import lowprice
from telegram_bot_calendar import DetailedTelegramCalendar
import datetime
from highprice import highprice
from config import token, CityInputError, APIError, ElemQtyError, PriceRangeInputError, CityFindingError
from config import MinMaxError, DistanceError, HotelsQtyError, YesOrNoError, NoHotelsError, NoHistoryError
from botdb import insert, fetch_by_id, create_db, is_db_exists
from collections.abc import Callable

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
    """
    Функция, которая вызывается при получении от пользователя команды "/start",
    при вызове отправляет пользователю, в соответствии с его id, приветственное сообщение, и
    предлагает выбрать следующую команду.
    """

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
def help_func(message: types.Message) -> None:
    """
    Функция, которая вызывается при получении от пользователя команды "/help",
    либо при окончании работы функций "/lowprice", "/highprice", "/bestdeal",
    при вызове отправляет пользователю, в соответствии с его id, сообщение, и
    предлагает выбрать следующую команду.
    """

    bot.send_message(
        message.from_user.id,
        'Что ещё может этот бот?\n' +
        '/help — помощь по командам бота\n' +
        '/lowprice — вывод самых дешёвых отелей в городе\n' +
        '/highprice — вывод самых дорогих отелей в городе\n' +
        '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n' +
        '/history — вывод истории поиска отелей')


user_info: dict = {}


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def main_func(message: types.Message) -> None:
    """
    Основная функция, которая вызывается при получении от пользователя
    любой из команд для поиска: "/lowprice", "/highprice", "/bestdeal".

    Далее вызывается вложенная функция "first_step".
    """


    def first_step(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func", которая при вызове
        создаёт вложенный словарь user_info[message.from_user.id] в словаре "user_info".
        Во вложенный словарь "user_info[message.from_user.id]" записывается 3 пары:
        "user_id": id пользователя,
        "user_command": введеная пользователем команда,
        "command_time": дата и время вызова команды в формате datetime.datetime.

        Далее, отправляет пользователю, в соответствии с его id, сообщение с запросом города, и,
        далее регистрирует вызов следующей функции "get_city".
        """

        user_info[message.from_user.id]: dict = {}
        user_info[message.from_user.id]['user_id']: int = message.from_user.id
        user_info[message.from_user.id]['user_command']: str = message.text
        user_info[message.from_user.id]['command_time']: datetime.datetime = datetime.datetime.now()
        bot.send_message(message.from_user.id, 'Введите название города:')
        bot.register_next_step_handler(message, get_city)

    def get_city(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая принимает на вход переменную message типа types.Message, и
        первым шагом проверяет состоит ли введенный пользователем город только из букв,
        если нет, то вызывается исключение "CityInputError", пользователю отправляется сообщение с текстом исключения,
        функция повторно просит ввести город и повторно вызывается эта же функция.

        Если исключение не вызвано, то создаётся переменная "cities_dict", которая получает словарь,
        где ключи это id городов, а значения это названия городов (во избежание одинаковых названий городов).

        Далее создаётся переменная "cities", содержащая список с названиями городов и пользователю отправляется
        клавиатура с вариантами похожих городов.

        Далее регистрируется следующая функция, "choose_city", куда передаётся аргумент, "cities_dict".
        """

        try:
            if message.text.isalpha():
                cities_dict: dict = get_cities_dict(message.text)
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

    def choose_city(message: types.Message, cities: dict) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая с помощью цикла по значениям, принятого в качестве аргумента словаря "cities",
        находится значение, соответствующее выбору пользователя, и во вложенный словарь
        "user_info[message.from_user.id]" записываются 2 пары:
        "city": название города,
        "city_id": id города.

        Следующим шагом вызывается функция "bestdeal_filter".

        :param cities: Словарь, где ключи это id городов, а значения это названия городов.
        """

        for city_id, i_city in cities.items():
            if i_city == message.text:
                user_info[message.from_user.id]['city'] = i_city
                user_info[message.from_user.id]['city_id'] = city_id
        bestdeal_filter(message)

    def bestdeal_filter(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая определяет дальнейшие шаги для пользователя в зависимости от введенной команды.

        Если пользователь вводил команду "/bestdeal", то бот отправляет пользователю сообщение,
        в соответствии с его id, где предлагает ввести диапазон цен для поиска
        и регистрирует вызов функции "distance".

        Если же пользователь вводил команду "/lowprice" или "/highprice",
        то бот отправляет ему клавиатуру с календарём для выбора даты прибытия в отель,
        тем самым вызывая функцию обратного вызова "call_checkin".
        """
        if user_info[message.from_user.id]['user_command'] == '/bestdeal':
            bot.send_message(message.from_user.id, 'Введите диапазон цен через пробел (например: 5000 10000):')
            bot.register_next_step_handler(message, distance)
        else:
            date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).build()
            bot.send_message(message.from_user.id, 'Выберите дату прибытия в отель:', reply_markup=date_markup)

    def distance(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая присваивает переменной "prices_range" список со значениями,
        введеными пользователем в функции "bestdeal_filter", и:
        1. проверяет состоит ли оно из ровно 2 элементов
        (если нет, то вызывается исключение "ElemQtyError"),
        2. проверяет состоят ли оба элемента списка только из цифр
        (если нет, то вызывается исключение "PriceRangeInputError"),
        3. проверяет действительно ли минимальная цена меньше или равна максимальной
        (если нет, то вызывается исключение "MinMaxError").

        Если вызвано какое-либо из исключений, то выводится текст исключения, у пользователя
        заново запрашивается диапазон цен, и, повторно вызывается текущая функция.

        Если исключений не было вызвано, то во вложенный словарь "user_info[message.from_user.id]"
        записываются ключи "min_price" и "max_price", пользователю отправляется клавиатура
        с запросом расстояния о центра выбранного города и регистрируется следующая функция "save_distance".
        """

        try:
            prices_range: list = message.text.split()
            if len(prices_range) != 2:
                raise ElemQtyError
            else:
                if prices_range[0].isdigit() and prices_range[1].isdigit():
                    if int(prices_range[1]) <= int(prices_range[0]):
                        raise MinMaxError
                    else:
                        user_info[message.from_user.id]['min_price']: str = prices_range[0]
                        user_info[message.from_user.id]['max_price']: str = prices_range[1]
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

    def save_distance(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая проверяет состоит ли введенная пользователем дистанция только из цифр
        (на случай если пользователь введет дистанцию самостоятельно со своей клавиатуры),
        если нет, то вызывается исключение "DistanceError", выводится текст исключения,
        пользователю отправляется клавиатура с запросом расстояния до центра города, и
        повторно вызывается текущая функция.

        Если исключения не было, то расстояние до центра сохраняется во вложенном словаре
        "user_info[message.from_user.id]".
        Пользователю отправляется клавиатура с календарём для выбора даты прибытия в отель.
        """

        try:
            if message.text.isdigit():
                user_info[message.from_user.id]['distance']: str = message.text
                date_markup, step = DetailedTelegramCalendar(min_date=datetime.date.today(), calendar_id=1).build()
                bot.send_message(message.from_user.id, 'Выберите дату прибытия в отель:', reply_markup=date_markup)
            else:
                raise DistanceError
        except DistanceError as distance_error:
            bot.send_message(message.from_user.id, str(distance_error))
            dist_markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                                               resize_keyboard=True)
            dist_markup.row('1', '3', '5')
            msg = bot.send_message(message.from_user.id,
                                   text='Выберите необходимое расстояние до центра (в км)',
                                   reply_markup=dist_markup)
            bot.register_next_step_handler(msg, save_distance)

    def checkin(message: types.Message, checkin_date: datetime.date) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая вызывается только при вызове функции обратного вызова "call_checkin"
        и успешной её отработке.

        Первым этапом сохраняет дату заезда, принятую в качестве аргумента в текущую функцию
        во вложенный словарь "user_info[message.id]" (message.id соответствует message.from_user.id
        при вызове обычной функции, а при вызове callback-функции тип message видоизменяется).

        Бот отправляет пользователю клавиатуру с календарём для выбора
        даты отъезда из отеля.

        :param checkin_date: Дата заезда в формате datetime.date,
        полученная в результате выполнения callback-функции.
        """
        user_info[message.id]['checkin']: str = str(checkin_date)
        date_markup, step = DetailedTelegramCalendar(min_date=checkin_date,
                                                     calendar_id=2).build()
        bot.send_message(message.id, 'Выберите дату отъезда из отеля:', reply_markup=date_markup)

    def checkout(message: types.Message, checkout_date: datetime.date) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая вызывается только при вызове функции обратного вызова "call_checkout"
        и успешной её отработке.

        Первым этапом сохраняет дату заезда, принятую в качестве аргумента в текущую функцию
        во вложенный словарь "user_info[message.id]" (message.id соответствует message.from_user.id
        при вызове обычной функции, а при вызове callback-функции тип message видоизменяется).

        Бот отправляет пользователю клавиатуру с запросом количества отелей.
        Регистрируется вызов функции "hotels_Qty".

        :param checkout_date: Дата отъезда в формате datetime.date,
        полученная в результате выполнения callback-функции.
        """
        user_info[message.id]['checkout']: str = str(checkout_date)
        hotels_Qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        hotels_Qty_markup.row('1', '2', '3')
        hotels_Qty_markup.row('4', '5', '6')
        msg = bot.send_message(message.id, text='Введите кол-во отелей (максимум - 6)',
                               reply_markup=hotels_Qty_markup)
        bot.register_next_step_handler(msg, hotels_Qty)

    def hotels_Qty(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая проверят, состоит ли количество отелей введеное пользователем только из цифр.
        Если нет, то вызывается исключение "HotelsQtyError", пользователю заново отправляется сообщение
        с запросом количества отелей и повторно вызывается текущая функция.

        Если исключение не было вызвано, то полученное сообщение в виде текста записывается
        во вложенный словарь "user_info[message.from_user.id]".

        Далее, бот отправляет пользователю клавиатуру с запросом необходимости загрузки фотографий отелей.

        Регистрируется вызов функции "photo_req".
        """
        try:
            if message.text.isdigit():
                user_info[message.from_user.id]['hotelsQty']: str = message.text
                photo_req_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                photo_req_markup.row('Да', 'Нет')
                bot.send_message(message.from_user.id, 'Загрузить фото отелей?', reply_markup=photo_req_markup)
                bot.register_next_step_handler(message, photo_req)
            else:
                raise HotelsQtyError
        except HotelsQtyError as hotels_qty_error:
            bot.send_message(message.from_user.id, str(hotels_qty_error))
            hotels_Qty_markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                                                                     resize_keyboard=True)
            hotels_Qty_markup.row('1', '2', '3')
            hotels_Qty_markup.row('4', '5', '6')
            msg = bot.send_message(message.from_user.id,
                                   text='Введите кол-во отелей (максимум - 6)',
                                   reply_markup=hotels_Qty_markup)
            bot.register_next_step_handler(msg, hotels_Qty)

    def photo_req(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая проверяет полученное от пользователя сообщение.

        Если ответ не "да" и не "нет", то вызывается исключение "YesOrNoError".
        После вызова исключения, бот заново отправляет сообщение с запросом необходимости загрузки фотографий отелей
        и повторно вызывается текущая функция.

        Если пользователь ответил "да", то бот отправляет пользователю клавиатуру
        с запросом выбора количества фотографий для загрузки.

        Регистрируется следующая функция "command_redirection".
        """

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

    def command_redirection(message: types.Message) -> None:
        """
        Вложенная функция основной функции "main_func",
        которая, во вложенный словарь "user_info[message.from_user.id]" записывает ключ "results"
        со значением пустого списка для дальнейшей записи полученных результатов на запрос в базу данных.

        Следующим шагом проверяется, какую команду вызвал пользователь.
        Если вызвана команда "/lowprice", при помощи цикла вызывается
        импортированная функция "lowprice", которая принимает в качестве аргумента
        словарь "user_info[message.from_user.id]", содержащий информацию о конкретном пользователе.
        Функция путем обращения к API генерирует кортеж, состоящий из значений, соответствующих запросу.
        Бот отправляет пользователю сформированное из кортежа сообщение с ответом на запрос,
        добавляется элемент в список "user_info[message.from_user.id]['results']" с информацией об отеле.

        Если пользователь запрашивал фотографии, сначала во вложенный словарь "user_info[message.from_user.id]"
        записывается 2 пары:
        "photoQty": количество фотографий, запрошенных пользователем,
        "photos": список, содержащий элементы "InputMediaPhoto" библиотеки "telebot.types",
        найденных по переданному в качестве аргумента id отеля.

        Бот отправляет пользователю сгруппированные в одно сообщение фотографии по каждому отелю.

        По тому же принципу, при вызове пользователем команды "/highprice", вызывается импортированная
        функция "highprice", а при вызове команды "/bestdeal", вызывается импортированная функция "bestdeal".

        Обработка исключений.
        "NoHotelsError" вызывается если всё заполнено верно, запрос к API отработал
        успешно, но отели не были найдены.
        "APIError" вызывается в случае если возникла ошибка при обращении к API.

        При успешном выполнении кода, проверяется существует ли база данных в заданном файле, если нет,
        то при помощи импортированной функции "create_db" создаётся база данных.

        Вызовом импортируемой функции "insert" из словаря "user_info[message.from_user.id]"
        записываются необходимые значения в базу данных.

        Вызывается функция "help_func" для выбора пользователем дальнейших действий.
        """

        user_info[message.from_user.id]['results'] = []
        try:
            if user_info[message.from_user.id]['user_command'] == '/lowprice':
                for i_hotel in lowprice(user_info[message.from_user.id]):
                    msg = f'Название отеля: {str(i_hotel[1])}\n'\
                          f'Адрес отеля: {str(i_hotel[2])}\n'\
                          f'От центра: {str(i_hotel[3])}\n'\
                          f'Цена за ночь: {str(i_hotel[4])}\n'\
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if message.text.isdigit():
                        user_info[message.from_user.id]['photoQty'] = message.text
                        user_info[message.from_user.id]['photos'] = get_photos(i_hotel[0], message.text)
                        bot.send_media_group(message.from_user.id, user_info[message.from_user.id]['photos'])
            elif user_info[message.from_user.id]['user_command'] == '/highprice':
                for i_hotel in highprice(user_info[message.from_user.id]):
                    msg = f'Название отеля: {str(i_hotel[1])}\n' \
                          f'Адрес отеля: {str(i_hotel[2])}\n' \
                          f'От центра: {str(i_hotel[3])}\n' \
                          f'Цена за ночь: {str(i_hotel[4])}\n' \
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if message.text.isdigit():
                        user_info[message.from_user.id]['photoQty'] = message.text
                        user_info[message.from_user.id]['photos'] = get_photos(i_hotel[0], message.text)
                        bot.send_media_group(message.from_user.id, user_info[message.from_user.id]['photos'])
            elif user_info[message.from_user.id]['user_command'] == '/bestdeal':
                for i_hotel in bestdeal(user_info[message.from_user.id]):
                    msg = f'Название отеля: {str(i_hotel[1])}\n' \
                          f'Адрес отеля: {str(i_hotel[2])}\n' \
                          f'От центра: {str(i_hotel[3])}\n' \
                          f'Цена за ночь: {str(i_hotel[4])}\n' \
                          f'Общая стоимость: {str(i_hotel[5])}\n'
                    bot.send_message(message.from_user.id, msg)
                    user_info[message.from_user.id]['results'].append(msg)
                    if message.text.isdigit():
                        user_info[message.from_user.id]['photoQty'] = message.text
                        user_info[message.from_user.id]['photos'] = get_photos(i_hotel[0], message.text)
                        bot.send_media_group(message.from_user.id, user_info[message.from_user.id]['photos'])
        except NoHotelsError as hotels_error:
            bot.send_message(message.from_user.id, str(hotels_error))
        except APIError as api_error:
            bot.send_message(message.from_user.id, str(api_error))
        else:
            if not is_db_exists('bot_database.db'):
                create_db('bot_database.db')
            insert(user_id=user_info[message.from_user.id]['user_id'], city=user_info[message.from_user.id]['city'],
                   city_id=user_info[message.from_user.id]['city_id'], checkin=user_info[message.from_user.id]['checkin'],
                   checkout=user_info[message.from_user.id]['checkout'], command=user_info[message.from_user.id]['user_command'],
                   command_time=user_info[message.from_user.id]['command_time'], results=user_info[message.from_user.id]['results'])

        help_func(message)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
    def call_checkin(call: Callable[types.Message]) -> None:
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
    def call_checkout(call: Callable[types.Message]) -> None:
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
def history(message: types.Message) -> None:
    """
    Функция для поиска истории пользователя, которая вызывается при получении от пользователя команды "/help".
    При помощи цикла обращается к импортируемой функции "fetch_by_id",
    в цикле создается переменная "query", содержащая пустую строку, получает сгенерированный кортеж.

    Далее, функция проверяет является ли элемент кортежа списком (информация о полученных отелях
    хранится в виде списка), если не является, то в строку поочередно записывается каждый строчный элемент
    кортежа. А если полученный элемент является списком, то в цикле добавляется каждая строка с информацией
    об отеле.

    Бот отправляет пользователю сформированное сообщение с историей поиска.

    В случае отсутствия истории поиска обрабатывается исключение "NoHistoryError", выводится
    соответствующее сообщение и вызывается функция "help_func".
    """

    try:
        if is_db_exists('bot_database.db'):
            for entry in fetch_by_id(message.from_user.id, 'bot_database.db'):
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
        else:
            raise NoHistoryError
    except NoHistoryError as history_error:
        bot.send_message(message.from_user.id, history_error)
        help_func(message)


if __name__ == "__main__":
    bot.polling(none_stop=True)
