import json

from flask import Flask, request

from flight_db import FlightDB
import utility

app = Flask(__name__)
flight_database = FlightDB('postgres', 'admin', '192.168.178.54', 5432, 'postgres')


@app.route('/')
def main():
    return 'some text'


@app.route('/actual_flight_data', methods=['GET'])
def view_do_something():
    if request.method == 'POST':
        return json.dumps(flight_database.check_flight_dicts(utility.get_flight_information_dict()))
    else:
        return "NO OK"


@app.route('/max_range_of_flights', methods=['POST'])
def view_do_something():
    """
    get max Range of received flights since specific date from database
    example for interval string: '2020-07-24 11:20:41'
    """
    if request.method == 'POST':
        interval = request.get_data().decode("utf-8")
        utility.get_max_range(flight_database.get_flight_data(interval))
    else:
        return "NO OK"


@app.route('/count_of_flights', methods=['POST'])
def view_do_something():
    """
    get count of flights since specific date from database
    example for interval string: '2020-07-24 11:20:41'
    """
    if request.method == 'POST':
        interval = request.get_data().decode("utf-8")
        utility.get_count_of_flights(flight_database.get_flight_data(interval))
    else:
        return "NO OK"


@app.route('/actual_ship_data', methods=['POST'])
def ship_data_endpoint():
    if request.method == 'POST':
        # returns a hardcoded string, because AIS Receiver receives no data from my location
        return json.dumps([{'ship_name': 'MSI TEST', 'lat': 52.502158, 'lon': 13.444523, 'speed': 8, 'ship_size': 15}])
    else:
        return "NO OK"


@app.route('/history_of_flight', methods=['POST'])
def view_do():
    if request.method == 'POST':
        flight_number = request.get_data().decode("utf-8")
        all_coordinates = flight_database.get_all_coordinates_of_flight_number(flight_number)
        return json.dumps(all_coordinates)
    else:
        return "NO OK"


@app.route('/history_of_ship', methods=['POST'])
def get_all_positions_of_ship_name():
    if request.method == 'POST':
        ship_name = request.get_data().decode("utf-8")
        all_coordinates = flight_database.get_all_coordinates_of_ship_name(ship_name)
        return json.dumps(all_coordinates)
    else:
        return "NO OK"


if __name__ == '__main__':
    app.run(host='192.168.178.40')
