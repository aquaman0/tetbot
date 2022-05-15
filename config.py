import re

token = '5373986484:AAE_Q_jmOFX6TT5LnDUr7prCHrg9XkIrH-Q'


def number_transform(num_text):
    new_num = re.sub(r',', ".", num_text)
    new_num = re.sub(r'[a-zA-Zа-яёА-ЯЁ]', "", new_num)
    return float(new_num)


class CityInputError(Exception):

    def __init__(self, message='Название города должно состоять только из букв.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class CityFindingError(Exception):

    def __init__(self, message='К сожалению, такой город не найден. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class APIError(Exception):

    def __init__(self, message='Внутренняя ошибка сервера. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class ElemQtyError(Exception):

    def __init__(self, message='Ошибка ввода. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class MinMaxError(Exception):

    def __init__(self, message='Максимальная цена должна быть больше минимальной. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class PriceRangeInputError(Exception):

    def __init__(self, message='Цены должны состоять только из цифр. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class DistanceError(Exception):

    def __init__(self, message='Расстояние должно содержать только цифры. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class HotelsQtyError(Exception):

    def __init__(self, message='Количество отелей должно содержать только цифры. Пожалуйста повторите запрос.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class YesOrNoError(Exception):

    def __init__(self, message='Пожалуйста, выберите "Да" или "Нет".'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class NoHotelsError(Exception):

    def __init__(self, message='К сожалению, по запросу ничего не найдено. Пожалуйста, измените параметры.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)


class NoHistoryError(Exception):

    def __init__(self, message='История поиска отсутствует.'):
        self.message = message
        # переопределяется конструктор встроенного класса `Exception()`
        super().__init__(self.message)