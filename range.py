import json
import time
from math import sin, cos, sqrt, atan2, radians

import requests

from flight_db import FlightDB

flight_database = FlightDB('postgres', 'admin', '192.168.178.54', 5432, 'postgres')
my_position = {'latitude': 52.667118, 'longitude': 13.379452}

# import socket
#
# UDP_IP = "127.0.0.1"
#
# UDP_PORT = 10110
#
# sock = socket.socket(socket.AF_INET,  # Internet
#
#                      socket.SOCK_DGRAM)  # UDP
#
# sock.bind((UDP_IP, UDP_PORT))


# my_position = bvs_position

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
    # get_max_range(300)

    flight_dict_list = flight_database.get_flight_data('2020-07-24 11:20:41')

    # print(flight_database.check_flight_dicts(get_flight_information_dict()))
    # flight_database.insert_ship_data(
    #     {'ship_name': 'MSI TEST', 'lat':52.502158, 'lon': 13.444523, 'speed': 8, 'ship_size': 15})
    while True:
        dict_list = get_flight_information_dict()
        dict_list = flight_database.check_flight_dicts(dict_list)
        for dict in dict_list:
            flight_database.insert_flight_data(dict)
            print('inserted')
        time.sleep(4)

    test_dict_list = [
        {'hex': '440037', 'flight': 'EJU9042 ', 'alt_baro': 8000, 'alt_geom': 8275, 'gs': 290.7, 'ias': 250, 'tas': 282,
         'mach': 0.436, 'track': 243.0, 'track_rate': -0.03, 'roll': 0.2, 'mag_heading': 239.6, 'baro_rate': 0,
         'geom_rate': -32, 'squawk': '1000', 'category': 'A3', 'nav_qnh': 1013.6, 'nav_altitude_mcp': 8000,
         'nav_heading': 239.8, 'lat': 52.623115, 'lon': 13.276507, 'nic': 8, 'rc': 186, 'seen_pos': 13.4, 'version': 2,
         'nic_baro': 1, 'nac_p': 9, 'nac_v': 1, 'sil': 3, 'sil_type': 'perhour', 'gva': 2, 'sda': 2, 'mlat': [],
         'tisb': [], 'messages': 357, 'seen': 13.1, 'rssi': -23.8}]
    example_list = [
        {'hex': '40780d', 'flight': 'BAW983', 'alt_baro': 12550, 'alt_geom': 13025, 'gs': 308.4, 'ias': 250, 'tas': 304,
         'mach': 0.476, 'track': 272.8, 'track_rate': -1.59, 'roll': -23.2, 'mag_heading': 267.5, 'baro_rate': 1792,
         'geom_rate': 1792, 'squawk': '1343', 'emergency': 'none', 'category': 'A3', 'nav_qnh': 1013.6,
         'nav_altitude_mcp': 28000, 'nav_heading': 0.0, 'lat': 52.645111, 'lon': 13.490753, 'nic': 8, 'rc': 186,
         'seen_pos': 0.1, 'version': 2, 'nic_baro': 1, 'nac_p': 9, 'nac_v': 1, 'sil': 3, 'sil_type': 'perhour',
         'gva': 2, 'sda': 2, 'mlat': [], 'tisb': [], 'messages': 1662, 'seen': 0.0, 'rssi': -14.2,
         'recorded_positions': [[52.645065, 13.494263], [52.643971, 13.505964], [52.642388, 13.514361],
                                [52.639618, 13.523788], [52.636196, 13.531546], [52.632519, 13.537589],
                                [52.627165, 13.543945], [52.61967, 13.549282], [52.615713, 13.551008],
                                [52.612198, 13.551865], [52.607117, 13.552017], [52.600724, 13.550616],
                                [52.597, 13.548737], [52.592606, 13.545685], [52.586197, 13.538361],
                                [52.584366, 13.535538], [52.580846, 13.528721], [52.578278, 13.521729],
                                [52.57647, 13.514753], [52.575073, 13.506241], [52.574295, 13.498001],
                                [52.573654, 13.489609], [52.572922, 13.479843], [52.572556, 13.474579],
                                [52.571954, 13.465864], [52.571303, 13.456996], [52.570816, 13.450241],
                                [52.570221, 13.442535], [52.569627, 13.435181], [52.568975, 13.42647],
                                [52.568436, 13.419952], [52.567858, 13.412423], [52.567252, 13.404027],
                                [52.56674, 13.397435], [52.565856, 13.38637], [52.565506, 13.381577],
                                [52.564878, 13.373029], [52.564041, 13.362198], [52.594666, 12.824478],
                                [52.594986, 12.82753], [52.597511, 12.851807], [52.598419, 12.860641],
                                [52.599653, 12.872524], [52.602493, 12.899597], [52.606682, 12.939619],
                                [52.608172, 12.954215], [52.610267, 12.974304], [52.613618, 13.007028],
                                [52.613937, 13.010025], [52.615356, 13.023529], [52.616592, 13.035889],
                                [52.618011, 13.049622], [52.619763, 13.066825], [52.621207, 13.080793],
                                [52.622324, 13.091544], [52.624054, 13.108673], [52.62529, 13.120499],
                                [52.626839, 13.135725], [52.628329, 13.150164], [52.629501, 13.162155],
                                [52.630936, 13.176139], [52.632379, 13.190342], [52.633759, 13.203888],
                                [52.635223, 13.218079], [52.636662, 13.232091], [52.638012, 13.245353],
                                [52.639618, 13.260727], [52.640671, 13.271027], [52.642202, 13.285767],
                                [52.643691, 13.300127], [52.645134, 13.31386], [52.646531, 13.326651],
                                [52.647995, 13.339539], [52.649734, 13.354416], [52.651419, 13.368556],
                                [52.653048, 13.381034], [52.654953, 13.395004], [52.656586, 13.406459],
                                [52.658478, 13.419418], [52.660446, 13.433914], [52.662094, 13.447876],
                                [52.663147, 13.462753], [52.663476, 13.473868], [52.663101, 13.485413],
                                [52.661102, 13.501177], [52.658076, 13.513576], [52.654266, 13.524094],
                                [52.650907, 13.531311], [52.645134, 13.540336], [52.639083, 13.547241],
                                [52.632751, 13.552094], [52.625024, 13.555324], [52.620322, 13.556266],
                                [52.613805, 13.556266], [52.607008, 13.555246], [52.601212, 13.553467],
                                [52.59581, 13.550262], [52.591461, 13.546448], [52.587067, 13.541107],
                                [52.582855, 13.533936], [52.580658, 13.528976], [52.578006, 13.521266],
                                [52.575958, 13.51232], [52.57489, 13.50441], [52.574328, 13.497803],
                                [52.573677, 13.489877], [52.573151, 13.483047], [52.572464, 13.473892],
                                [52.571869, 13.46611], [52.571045, 13.455658], [52.570697, 13.45064],
                                [52.569992, 13.44101], [52.569394, 13.432826], [52.568756, 13.424377],
                                [52.568253, 13.417892], [52.567749, 13.411026], [52.566694, 13.397121],
                                [52.566467, 13.394012], [52.565826, 13.385391], [52.614689, 13.21977],
                                [52.61499, 13.222885], [52.616135, 13.23494], [52.61725, 13.246294],
                                [52.618744, 13.261108], [52.619293, 13.266678], [52.620758, 13.280945],
                                [52.62204, 13.293076], [52.622177, 13.294296], [52.624283, 13.312988],
                                [52.624931, 13.318569], [52.625815, 13.325553], [52.62735, 13.337936],
                                [52.628655, 13.347682], [52.630371, 13.359909], [52.6321, 13.371695],
                                [52.632889, 13.376999], [52.635086, 13.3918], [52.635405, 13.394139],
                                [52.636708, 13.40387], [52.638617, 13.434161], [52.638291, 13.441851],
                                [52.637639, 13.449306], [52.636276, 13.458099], [52.634707, 13.464844],
                                [52.632751, 13.471146], [52.629819, 13.478498], [52.627441, 13.4832],
                                [52.602722, 13.499527], [52.599094, 13.498901], [52.595535, 13.497543]]}]
