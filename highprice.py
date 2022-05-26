import requests
import json
from config import APIError, NoHotelsError
from datetime import datetime
from collections.abc import Iterable


def highprice(data: dict) -> Iterable[tuple]:
    """
    Функция, которая осуществляет поиск отелей, фильтруя их по убыванию цены, получая
    данные от пользователя.

    Проверяется успешен ли был запрос к API, если код ответа "200", далее проверяется заполнен
    ли полученный от API список, если исключений не было, то при помощи json-обработки
    формируется ответ от API.

    Проверяется есть ли ключ "streetAddress" в словаре hotel["address"], так как при поиске в некоторых
    городах, такой ключ отсутствует и вместо полного адреса будет выводится значение ключа hotel["address"].

    Далее, в цикле ведётся поиск подходящих отелей, генерируются кортежи с необходимыми значениями,
    до тех пор пока количество отелей не будет равно количеству отелей, полученных от пользователя.

    Если получен пустой список при обращении к API, то вызывается исключение "NoHotelsError", которое обрабатывается
    в основной функции.

    Если возникла ошибка при обращении к API, то вызывается исключение "APIError", которое обрабатывается
    в основной функции.
    """

    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"

    querystring = {"checkin_date": data['checkin'], "checkout_date": data['checkout'],
                   "sort_order": 'PRICE_HIGHEST_FIRST', "destination_id": data['city_id'], "adults_number": "1",
                   "locale": "ru_RU", "currency": "RUB", "page_number": "1"}

    headers = {
        'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
        'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        checkin = data['checkin'].split('-')
        checkout = data['checkout'].split('-')
        period = datetime(int(checkout[0]), int(checkout[1]), int(checkout[2])) - datetime(int(checkin[0]), int(checkin[1]), int(checkin[2]))
        data_response = json.loads(response.text)
        if data_response['searchResults']['results']:
            for i, hotel in enumerate(data_response['searchResults']['results'], start=0):
                i += 1
                total_price = str(round(hotel["ratePlan"]["price"]["exactCurrent"] * period.days, 2)) + ' RUB'
                if 'streetAddress' in hotel['address']:
                    yield hotel['id'], hotel['name'], hotel['address']['streetAddress'], \
                          hotel['landmarks'][0]['distance'], hotel['ratePlan']['price']['current'], \
                          total_price, 'www.hotels.com/ho' + str(hotel['id'])
                    if i == int(data['hotelsQty']):
                        break
                else:
                    yield hotel['id'], hotel['name'], hotel['address']['locality'], \
                          hotel['landmarks'][0]['distance'], hotel['ratePlan']['price']['current'], \
                          total_price, 'www.hotels.com/ho' + str(hotel['id'])
                    if i == int(data['hotelsQty']):
                        break
        else:
            raise NoHotelsError
    else:
        raise APIError
