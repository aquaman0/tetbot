import requests
import json
import re
import sqlite3

##### SQLite
# conn = sqlite3.connect('user_cities_temp.db')
#     cur = conn.cursor()
#     cur.execute("""CREATE TABLE IF NOT EXISTS cities_id(
#        city_id INT,
#        city_name TEXT);
#     """)
#     conn.commit()
#
# cur.execute(f"""INSERT INTO cities_id(city_id, city_name)
#                    VALUES('{int(i_city['destinationId'])}', '{city}');""")
#                 conn.commit()
#
#         cur.execute("SELECT * FROM cities_id;")
#         all_results = cur.fetchall()
########

def get_cities_dict(user_city: str):
    url = "https://hotels-com-provider.p.rapidapi.com/v1/destinations/search"

    querystring = {"query": user_city, "currency": "RUB", "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
        'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
    }



    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            data_response = json.loads(response.text)
            cities_list = data_response['suggestions'][0]['entities']
            cities_dict = {}
        else:
            print('Добавить ошибку')

        for i_city in cities_list:
            if i_city['type'] == 'CITY':
                city = re.sub(r"<span class='highlighted'>", '', i_city['caption'])
                city = re.sub(r"</span>", '', city)
                cities_dict[i_city['destinationId']] = city


        return cities_dict
    except ValueError:
        return False


# def find_destination_id(user_city):
#     url = "https://hotels-com-provider.p.rapidapi.com/v1/destinations/search"
#
#     querystring = {"query": user_city, "currency": "RUB", "locale": "ru_RU"}
#
#     headers = {
#         'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
#         'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
#         }
#
#     response = requests.request("GET", url, headers=headers, params=querystring)
#     data_response = json.loads(response.text)
#
#     for i_elem in data_response['suggestions']:
#         if i_elem['group'] == 'CITY_GROUP':
#             for i_entity in i_elem['entities']:
#                 if i_entity['type'] == 'CITY' and i_entity['name'] == user_city.title():
#                     dest_Id = i_entity['destinationId']
#                     return dest_Id
#
#
# def find_hotels(data):
#     url = "https://hotels-com-provider.p.rapidapi.com/v1/hotels/search"
#
#     querystring = {"checkin_date": data['checkin'], "checkout_date": data['checkout'],
#                    "sort_order": data['sort_order'], "destination_id": data['city_id'], "adults_number": "1",
#                    "locale": "ru_RU", "currency": "RUB", "page_number": "1"}
#
#     headers = {
#         'x-rapidapi-host': "hotels-com-provider.p.rapidapi.com",
#         'x-rapidapi-key': "b448616148mshc86ccd41d33c3dfp18ab05jsn28b912e1ca26"
#     }
#
#     response = requests.request("GET", url, headers=headers, params=querystring)
#     data_response = json.loads(response.text)
#     hotels_list = ''
#     for i, hotel in enumerate(data_response['searchResults']['results'], start=0):
#         hotels_list += hotel['name'] + '\n' + 'Стоимость за сутки: ' + hotel['ratePlan']['price']['current'] + '\n'
#         i += 1
#         if i == int(data['hotelsQty']):
#             break
#     return hotels_list