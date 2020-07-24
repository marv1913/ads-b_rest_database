import json
import time
from math import sin, cos, sqrt, atan2, radians

import requests

from flight_db import FlightDB

flight_database = FlightDB('postgres', 'admin', '192.168.178.54', 5432, 'postgres')
my_position = {'latitude': 52.667118, 'longitude': 13.379452}

import socket

UDP_IP = "127.0.0.1"

UDP_PORT = 10110

sock = socket.socket(socket.AF_INET,  # Internet

                     socket.SOCK_DGRAM)  # UDP

sock.bind((UDP_IP, UDP_PORT))



def get_flight_information_dict():
    response = requests.get('http://192.168.178.79:8080/data/aircraft.json')
    dict = json.loads(response.text)
    return dict['aircraft']


def get_current_flights():
    current_flights_as_dict_list = flight_database.check_flight_dicts(get_flight_information_dict())
    return flight_database.add_history_coordinates_to_flight_dict_list(current_flights_as_dict_list)


def get_current_ship_data():
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    return json.loads(data)


def print_flight_statistic():
    while True:
        flight_json = get_flight_information_dict()
        if len(flight_json) != 0:
            print(flight_json)
            print('current max range: ' + str(get_current_max_range()))
        time.sleep(2)


def get_count_of_flights(flight_dict_list):
    counted_flights = []
    count = 0
    for flight_dict in flight_dict_list:
        if flight_dict['flight'] not in counted_flights:
            counted_flights.append(flight_dict['flight'])
            count += 1
    return count


def get_current_max_range():
    flight_dict_list = get_flight_information_dict()
    max_distance = -1
    for airplane_info_dict in flight_dict_list:
        temp_distance = get_distance(my_position['latitude'], my_position['longitude'], airplane_info_dict['lat'],
                                     airplane_info_dict['lon'])
        if temp_distance > max_distance:
            max_distance = temp_distance
    return max_distance


def get_max_range(flight_dict_list):
    max_range = -1
    max_range_dict = {}
    for flight_dict in flight_dict_list:
        temp_distance = get_distance(flight_dict['lat'], flight_dict['lon'], my_position['latitude'],
                                     my_position['longitude'])
        if temp_distance > max_range:
            max_range = temp_distance
            max_range_dict = flight_dict
    return max_range, max_range_dict


def get_flights_inside_certain_range(flight_dict_list, range):
    flights_inside_range = []
    for flight_dict in flight_dict_list:
        temp_distance = get_distance(flight_dict['lat'], flight_dict['lon'], my_position['latitude'],
                                     my_position['longitude'])
        if temp_distance <= range:
            already_in_list = False
            for temp_flight_dict in flights_inside_range:
                if temp_flight_dict['flight'] == flight_dict['flight']:
                    already_in_list = True
            if not already_in_list:
                flights_inside_range.append(flight_dict)
    return flights_inside_range


def get_distance(latitude1, longitude1, latitude2, longitude2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(latitude1)
    lon1 = radians(longitude1)
    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


if __name__ == '__main__':
    # get current flight_data from dump1090 REST Server and add them to database
    while True:
        dict_list = get_flight_information_dict()
        dict_list = flight_database.check_flight_dicts(dict_list)
        for temp_dict in dict_list:
            flight_database.insert_flight_data(temp_dict)
            print('inserted')
        time.sleep(4)


