import requests
import json
import re
from config import APIError, CityFindingError, NoHotelsError
from collections.abc import Iterable


LOCALE = 'en_EN'
CURRENCY = 'USD'
URL = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"
HEADERS = {
        'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
        'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }


def api_request(querystring: dict, url: str) -> json:
    """
    Общая функция для запроса к API.
    :param querystring: Словарь с параметрами для API.
    :param url: Ссылка на API.
    :return: Ответ от API.
    """
    api_response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if api_response.status_code == 200:
        api_response = json.loads(api_response.text)
    else:
        raise APIError
    return api_response


def get_cities_dict(user_city: str) -> dict:
    """
    Функция, которая находит похожие города на город, введенный пользователем.

    Если похожих городов не было найдено, вызывается исключение "CityFindingError",
    которое обрабатывается в основной функции.

    Если при обращении к API возникла ошибка, то есть код ответа "200", то вызывается
    исключение "APIError", которое обрабатывается в основной функции.

    :param user_city: Название города.
    :return: Словарь, где ключи id городов, а значения - названия городов.
    """

    url = "https://hotels-com-provider.p.rapidapi.com/v1/destinations/search"

    querystring = {"query": user_city, "currency": "RUB", "locale": "ru_RU"}

    response = api_request(querystring, url)
    cities_list = response['suggestions'][0]['entities']
    cities_dict = {}
    for i_city in cities_list:
        if i_city['type'] == 'CITY':
            city = re.sub(r"<span class='highlighted'>", '', i_city['caption'])
            city = re.sub(r"</span>", '', city)
            cities_dict[i_city['destinationId']] = city
    if cities_dict:
        return cities_dict
    else:
        raise CityFindingError


def get_hotels_info(data: dict) -> json:
    """
    Функция, возвращающая пользователю словарь с информацией об отелях.
    :param data: Словарь с информацией о пользователе.
    :return: Информация об отелях в json.
    """
    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"

    if data['user_command'] == '/bestdeal':
        querystring = {"checkin_date": data['checkin'], "checkout_date": data['checkout'],
                       "sort_order": data['sort_order'], "destination_id": data['city_id'],
                       "adults_number": "1", "locale": "ru_RU", "currency": "RUB",
                       "price_min": data['min_price'], "price_max": data['max_price']}
    else:
        querystring = {"checkin_date": data['checkin'], "checkout_date": data['checkout'],
                   "sort_order": data['sort_order'], "destination_id": data['city_id'], "adults_number": "1",
                   "locale": "ru_RU", "currency": "RUB", "page_number": "1"}
    response = api_request(querystring, url)
    if response['searchResults']['results']:
        response = response['searchResults']['results']
    else:
        raise NoHotelsError
    return response


def get_photos(hotel_id: int) -> json:
    """
    Функция, которая создаёт список из InputMediaPhoto-объектов по id отеля, полученного
    от пользователя в соответствии с заданным количеством.

    :param hotel_id: id отеля.
    :return: Словарь в формате json.
    """
    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/photos"

    querystring = {"hotel_id": hotel_id}

    response = api_request(querystring, url)
    return response


def get_hotels(data: dict) -> Iterable[dict]:
    """
    Функция, которая получает из функции get_hotels_info словарь с отелями в формате json,
    записывает информацию в словарь и гененрирует ответ для пользователя.

    :param data: Словарь с информацией о пользователе.
    """
    hotels_qty = 0
    hotels = get_hotels_info(data)
    period = data['checkout'] - data['checkin']
    for hotel in hotels:
        hotels_qty += 1
        total_price = str(round(hotel["ratePlan"]["price"]["exactCurrent"] * period.days, 2)) + ' RUB'
        response = {'hotel_name': hotel["name"],
                    'hotel_address': hotel["address"]["streetAddress"],
                    'center_distance': hotel["landmarks"][0]["distance"],
                    'price_current': hotel["ratePlan"]["price"]["current"],
                    'price_total': total_price,
                    'web': f'www.hotels.com/ho{str(hotel["id"])}'}
        images = get_photos(hotel['id'])
        hotel_images = []
        for image in images:
            hotel_images.append(image['baseUrl'].replace('{size}', 'z'))
        response['hotel_images'] = hotel_images[:9]
        yield response
        if hotels_qty == int(data['hotelsQty']):
            break
