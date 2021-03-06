import uuid

import psycopg2


class FlightDB:

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def execute_command(self, command):
        connection = psycopg2.connect(user=self.user, password=self.password, host=self.host, port=self.port,
                                      database=self.database)
        cursor = connection.cursor()
        cursor.execute(command)
        try:
            result = cursor.fetchall()
        except psycopg2.ProgrammingError:
            result = []
        connection.commit()
        connection.close()
        return result

    def get_all_coordinates_of_flight_number(self, flight_number):
        all_coordinates_tuple_list = []
        all_entries_of_flight = self.execute_command(
            "select * from flight_history where flight_number= '" + flight_number + "' order by time_added desc;")
        all_coordinates = self.get_coordinates_from_geography()

        for flight_tuple in all_entries_of_flight:
            coordinates = self.get_coordinates_tuple_of_certain_id(all_coordinates, flight_tuple[6])
            all_coordinates_tuple_list.append(coordinates)
        return all_coordinates_tuple_list

    def get_all_coordinates_of_ship_name(self, ship_name):
        all_coordinates_tuple_list = []
        all_entries_of_ship = self.execute_command(
            "select * from ships where ship_name= '" + ship_name + "' order by time_added desc;")
        all_coordinates = self.get_all_coordinates_from_ship_table()
        for ship_tuple in all_entries_of_ship:
            coordinates = self.get_coordinates_tuple_of_certain_id(all_coordinates, ship_tuple[5])
            all_coordinates_tuple_list.append(coordinates)
        return all_coordinates_tuple_list

    def insert_flight_data(self, flight_dict):
        if self.check_entry_existing(flight_dict['flight'].strip(), flight_dict['lat'], flight_dict['lon']):
            return
        try:
            self.execute_command("Insert into flight_history values ('" + flight_dict[
                'flight'].strip() + "'," + str(flight_dict['nav_altitude_mcp']) + "," + str(
                flight_dict['gs']) + ", ST_GeogFromText('POINT(" + str(flight_dict['lon']) + " " + str(
                flight_dict['lat']) + ")'), " + str(flight_dict['track']) + ",  '" + str(
                self.get_actual_timestamp()) + "','" + str(uuid.uuid1()) + "')");
        except KeyError:
            print('flight_dict has bad format: ' + str(flight_dict))

    def insert_ship_data(self, ship_dict):
        try:
            self.execute_command("Insert into ships values ('" + ship_dict[
                'ship_name'].strip() + "', ST_GeogFromText('POINT(" + str(ship_dict['lon']) + " " + str(
                ship_dict['lat']) + ")'), " + str(ship_dict['speed']) + ",  " + str(
                ship_dict['ship_size']) + ",'" + str(
                self.get_actual_timestamp()) + "','" + str(uuid.uuid1()) + "')");
        except KeyError:
            print('flight_dict has bad format: ' + str(ship_dict))

    def check_entry_existing(self, flight_number, lat, lon):
        """
        checks whether coordinate for flight_number is already existing
        :return: true or false
        """
        flight_number = flight_number.strip()
        result = self.execute_command(
            "SELECT * from flight_history where flight_number = '" + flight_number + "' and coordinates = ST_GeogFromText('POINT(" + str(
                lon) + " " + str(lat) + ")')")

        if len(result) > 0:
            return True
        return False

    def get_flight_data(self, flight_after_timestamp=None, flight_number=None, get_recorded_positions=False):
        if flight_after_timestamp is not None and flight_number is None:
            result = self.execute_command(
                "Select * from flight_history where time_added > '" + flight_after_timestamp + "'");
        if flight_after_timestamp is not None and flight_number is not None:
            result = self.execute_command(
                "Select * from flight_history where time_added > '" + flight_after_timestamp + "' and flight_number='" + flight_number + "'");
        if flight_after_timestamp is None and flight_number is None:
            result = self.execute_command('Select * from flight_history')
        if flight_after_timestamp is None and flight_number is not None:
            result = self.execute_command(
                "Select * from flight_history where flight_number= '" + flight_number + "'");
        flight_dict_list = []
        coordinates_tuple_list = self.get_coordinates_from_geography()
        for flight_tuple in result:
            temp_dict = {'flight': flight_tuple[0]}
            coordinate_tuple = self.get_coordinates_tuple_of_certain_id(coordinates_tuple_list, flight_tuple[6])
            temp_dict['lat'] = coordinate_tuple[0]
            temp_dict['lon'] = coordinate_tuple[1]
            temp_dict['altitude'] = flight_tuple[1]
            temp_dict['track'] = flight_tuple[4]
            temp_dict['speed'] = flight_tuple[2]
            temp_dict['time_added'] = str(flight_tuple[5])
            if get_recorded_positions:
                temp_dict['recorded_positions'] = self.get_all_coordinates_of_flight_number(flight_tuple[0])
            flight_dict_list.append(temp_dict)
        return flight_dict_list

    def get_coordinates_from_geography(self):
        result = self.execute_command(
            "SELECT id, ST_X(coordinates::geometry), ST_Y(coordinates::geometry) FROM flight_history");
        return result

    def get_all_coordinates_from_ship_table(self):
        result = self.execute_command(
            "SELECT id, ST_X(coordinates::geometry), ST_Y(coordinates::geometry) FROM ships");
        return result

    def get_coordinates_tuple_of_certain_id(self, coordinates_tuple_list, id):
        for coordinates_tuple in coordinates_tuple_list:
            if id == coordinates_tuple[0]:
                return coordinates_tuple[2], coordinates_tuple[1]

    def get_coordinates_of_flights(self, flight_number):
        my_list = []
        result = self.execute_command(
            "SELECT ST_X(coordinates::geometry), ST_Y(coordinates::geometry) FROM flight_history where flight_number='"
            + flight_number + "' order by time_added desc");
        for tuple in result:
            my_list.append([tuple[1], tuple[0]])
        return my_list

    def get_actual_timestamp(self):
        import datetime;
        ts = datetime.datetime.now()
        ts = str(ts)
        index = ts.rfind('.')
        ts = ts[:index]
        return ts

    def add_history_coordinates_to_flight_dict_list(self, flight_dict_list):
        for flight_dict in flight_dict_list:
            coordinates_list = self.get_coordinates_of_flights(flight_dict['flight'])
            flight_dict['recorded_positions'] = coordinates_list
        return flight_dict_list

    def get_flight_number_list(self, flight_dict_list):
        temp_list = []
        for flight_dict in flight_dict_list:
            temp_list.append(flight_dict['flight'])
        return temp_list

    def check_flight_dicts(self, dict_list):
        corrected_dict_list = []
        for dict in dict_list:
            keys = dict.keys()
            is_valid = True
            if 'flight' not in keys or 'lat' not in keys or 'lon' not in keys:
                is_valid = False
            if 'flight' in keys:
                dict['flight'] = dict['flight'].strip()
            if is_valid:
                corrected_dict_list.append(dict)
        return corrected_dict_list

    def check_ship_data_list(self, dict_list):
        temp_list = []
        for my_dict in dict_list:
            keys = my_dict.keys()
            if 'ship_name' in keys and 'lat' in keys and 'lon' in keys:
                temp_list.append(my_dict)
        return temp_list
