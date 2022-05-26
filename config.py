import re
from telebot import types

token = '5373986484:AAE_Q_jmOFX6TT5LnDUr7prCHrg9XkIrH-Q'


def city_choose_markup(cities):
    cities_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for city in cities:
        cities_markup.add(city)
    return cities_markup


def dist_markup():
    distance = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    distance.row('1', '3', '5')
    return distance


def hotels_Qty_markup():
    qty_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    qty_markup.row('1', '2', '3')
    qty_markup.row('4', '5', '6')
    return qty_markup


def price_range_check(prices_range):
    prices_range_list: list = prices_range.split()
    if len(prices_range_list) != 2:
        raise ElemQtyError
    else:
        if not (prices_range_list[0].isdigit() and prices_range_list[1].isdigit()):
            raise PriceRangeInputError
        else:
            if int(prices_range_list[1]) < int(prices_range_list[0]):
                raise MinMaxError
    return True


def photo_req_markup():
    photo_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    photo_markup.row('Да', 'Нет')
    return photo_markup


def photo_Qty_markup():
    photo_Qmarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    photo_Qmarkup.row('1', '2', '3')
    photo_Qmarkup.row('4', '5', '6')
    photo_Qmarkup.row('7', '8', '9')
    return photo_Qmarkup


def number_transform(num_text: str) -> float:
    """
    Функция для преобразования строки в число с плавающей точкой.

    :param num_text: Строка.
    :return: Число с плавающей точкой.
    """
    new_num = re.sub(r',', ".", num_text)
    new_num = re.sub(r'[a-zA-Zа-яёА-ЯЁ]', "", new_num)
    return float(new_num)


class CityInputError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Название города должно состоять только из букв.'):
        self.message = message
        super().__init__(self.message)


class CityFindingError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='К сожалению, такой город не найден. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class APIError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Внутренняя ошибка сервера. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class ElemQtyError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Ошибка ввода. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class MinMaxError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Максимальная цена должна быть больше минимальной. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class PriceRangeInputError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Цены должны состоять только из цифр. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class DistanceError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Расстояние должно содержать только цифры. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class HotelsQtyError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Количество отелей должно содержать только цифры. Пожалуйста повторите запрос.'):
        self.message = message
        super().__init__(self.message)


class YesOrNoError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='Пожалуйста, выберите "Да" или "Нет".'):
        self.message = message
        super().__init__(self.message)


class NoHotelsError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='К сожалению, по запросу ничего не найдено. Пожалуйста, измените параметры.'):
        self.message = message
        super().__init__(self.message)


class NoHistoryError(Exception):
    """
    Класс, производный от класса Exception, содержащий информацию об ошибке.
    """

    def __init__(self, message='История поиска отсутствует.'):
        self.message = message
        super().__init__(self.message)