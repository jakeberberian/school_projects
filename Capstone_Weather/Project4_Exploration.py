# https://projects.raspberrypi.org/en/projects/fetching-the-weather/

from requests import get
import json
from pprint import pprint
from math import *
import geocoder

# Raspberry Pi weather data retrieval

# Data retrieval


def fetch_stations():
    """
    This function takes no arguments. When run, it will return all Raspberry Pi weather
    stations from around the world.
    """
    url = 'https://apex.oracle.com/pls/apex/raspberrypi/weatherstation/getallstations'
    return get(url).json()['items']


def fetch_weather(station_id):
    """
    This function takes a station id (found from above) and returns a list of the latest
    measurements from the specified station.
    """
    url = 'https://apex.oracle.com/pls/apex/raspberrypi/weatherstation/getlatestmeasurements/' + str(station_id)
    return get(url).json()['items']

def haversine(lon1, lon2, lat1, lat2):
    """
    This function takes a pair of coordinates and calculates the distance between the two,
    using the Haversine formula. This is calculated in kilometers.
    """
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = pow(sin(dlat/2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon/2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return c * 6371

def find_me():
    """
    This is a function that takes no arguments and returns your machine's current lat/lon coordinates.
    This will help find the closet Raspberry Pi weather station to you.
    """
    return geocoder.ip('me').latlng


def find_closest():
    """
    This function takes no arguments and returns the closest weather station to your machine's current
    location. This is pulled from `find_me()` function.
    """
    my_lon = find_me()[1]
    my_lat = find_me()[0]
    all_stations = fetch_stations()

    smallest = 20036 # Longest possible distance between two points on Earth
    for station in all_stations:
        station_lon = station['weather_stn_long']
        station_lat = station['weather_stn_lat']
        distance = haversine(my_lon, station_lon, my_lat, station_lat)
        if distance < smallest:
            smallest = distances
            closest_station = station['weather_stn_id']
    return closest_station



def fetch_closest():
    """
    This function takes no arguments and return the data for the closest weather station to your machine.
    """
    return fetch_weather(find_closest())
