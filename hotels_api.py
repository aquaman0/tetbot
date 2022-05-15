import requests
import json
import re
from telebot.types import InputMediaPhoto
from config import APIError, CityFindingError


def get_cities_dict(user_city: str):
    url = "https://hotels-com-provider.p.rapidapi.com/v1/destinations/search"

    querystring = {"query": user_city, "currency": "RUB", "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
        'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        data_response = json.loads(response.text)
        cities_list = data_response['suggestions'][0]['entities']
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

    else:
        raise APIError


def get_photos(hotel_id, qty):
    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/photos"

    querystring = {"hotel_id": hotel_id}

    headers = {
        "X-RapidAPI-Host": "hotels-com-provider.p.rapidapi.com",
        "X-RapidAPI-Key": "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data_response = json.loads(response.text)
    all_photos = []
    for i, photo in enumerate(data_response, start=0):
        i += 1
        all_photos.append(InputMediaPhoto(photo['mainUrl']))
        if i == int(qty):
            break
    return all_photos
