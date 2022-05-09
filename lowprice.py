import requests
import json
from telebot.types import InputMediaPhoto


def lowprice(data):
    url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"

    querystring = {"checkin_date": data['checkin'], "checkout_date": data['checkout'],
                   "sort_order": 'PRICE', "destination_id": data['city_id'], "adults_number": "1",
                   "locale": "ru_RU", "currency": "RUB", "page_number": "1"}

    headers = {
        'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
        'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data_response = json.loads(response.text)
    for i, hotel in enumerate(data_response['searchResults']['results'], start=0):
        i += 1
        yield hotel['id'], hotel['name'], hotel['address']['streetAddress'], hotel['landmarks'][0]['distance'], hotel['ratePlan']['price']['current']
        if i == int(data['hotelsQty']):
            break


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
