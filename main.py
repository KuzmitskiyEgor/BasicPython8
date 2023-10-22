import json
import requests
import os
import folium
from dotenv import load_dotenv

from geopy import distance
from flask import Flask


def read_json(json_file):
    with open(json_file, encoding='CP1251') as my_file:
        coffeeshops = my_file.read()
    coffeeshops = json.loads(coffeeshops)
    return coffeeshops


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_nearest_coffeeshops(coffeeshops, my_coords):
    coffee_info = []
    for coffeeshop in coffeeshops:
        coffeeshop_latitude = coffeeshop['Latitude_WGS84']
        coffeeshop_longitude = coffeeshop['Longitude_WGS84']
        coffeeshop_coordinates = (coffeeshop_latitude, coffeeshop_longitude)
        distance_to = distance.distance(my_coords, coffeeshop_coordinates).km
        coffee = {
            'title': coffeeshop['Name'],
            'distance': distance_to,
            'latitude': coffeeshop_latitude,
            'longitude': coffeeshop_longitude
        }
        coffee_info.append(coffee)
    coffeeshop_info = sorted(coffee_info, key=lambda x: x['distance'])[:5]
    return coffeeshop_info


def get_map():
    load_dotenv()
    yandex_apikey = os.environ['APIKEY']
    coffeeshops = read_json("coffee.json")
    my_place = input("Где вы находитесь? ")
    my_coords = fetch_coordinates(yandex_apikey, my_place)
    coffeeshop_info = get_nearest_coffeeshops(coffeeshops, my_coords)
    map = folium.Map(location=my_coords, zoom_start=12, tiles="Stamen Terrain")
    for coffeeshop in coffeeshop_info:
        folium.Marker(
            location=[coffeeshop['latitude'], coffeeshop['longitude']],
            tooltip="Click me!",
            popup=coffeeshop['title'],
                ).add_to(map)
    map.save("index.html")
    with open('index.html', 'rb') as map_file:
        return map_file.read()


if __name__ == '__main__':
    app = Flask(__name__)
    app.add_url_rule('/', 'map', get_map)
    app.run('0.0.0.0')
