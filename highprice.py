import requests
import json
from config import APIError
from datetime import datetime


def highprice(data):
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
        for i, hotel in enumerate(data_response['searchResults']['results'], start=0):
            i += 1
            yield hotel['id'], hotel['name'], hotel['address']['streetAddress'], hotel['landmarks'][0]['distance'], \
                  hotel['ratePlan']['price']['current'], str(round(hotel['ratePlan']['price']['exactCurrent'] * period.days, 2)) + ' RUB'
            if i == int(data['hotelsQty']):
                break
    else:
        raise APIError
