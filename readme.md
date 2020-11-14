
## ADS-B REST database manager
This application inserts received ADS-B data from [dump1090-fa](https://github.com/flightaware/dump1090) into a postgresql database and provides a REST-Server with different endpoints to get these data.

## Deployment

There are two ways to launch the application:

**Using docker-compose:**

 1. install [dump1090-fa](https://github.com/flightaware/dump1090) and make sure that the dump1090-fa service is running
 2. clone repository 
 3. cd into root directory of the cloned repository and run "docker-compose up"
 4. by default the REST-Server is running at Port 3000 and is listening for all IP adresses

**build manually**
 1. install [dump1090-fa](https://github.com/flightaware/dump1090) and make sure that the dump1090-fa service is running
 2. you need to create a Postgresql database with a table named "flight_history"
 3. how the table has to look like is mentioned in the file "create_databases.sql"
 4. edit the database configuration in the `variables.py` file
 5. to start the insertion of received ADS-B data run `python3 utility.py`
 6. to start the REST server run `python3 rest_server.py`

By default the program gets the flight data from dump1090 all 4 seconds an inserts them into the database. If you need more data you can decrease this interval in the  main method of the `utility.py` module.


