# measuring-stations-api
API to manage measuring stations and the data they collect

## Overview
This project provides a REST API to store and retrieve sensor data from multiple
measuring stations. The REST API is implemented using FastAPI and the data is
stored as timeseries data in an InfluxDB database.

Each measuring station has an ID, an address and a list of sensors. Each sensor
takes a measurement once per minute which has a timestamp and a value within the
range [0, 100].

## Running the project
After cloning the repo, go to the project directory and create a virtual
environment for python and activate it. The commands vary depending on the
operating system and the shell, so check the documentation if you are unsure
(https://docs.python.org/3/library/venv.html). For example, for Linux with bash:
```
python -m venv .venv
source .venv/bin/activate
```
Then install the required dependencies:
```
python -m pip install -r requirements.txt
```

### Creating the database
Create and start InfluxDB in a docker container:
```
docker run \
    --name measuring-stations-influxdb2 \
    --publish 8086:8086 \
    --mount type=volume,source=measuring-stations-influxdb2-data,target=/var/lib/influxdb2 \
    --mount type=volume,source=measuring-stations-influxdb2-config,target=/etc/influxdb2 \
    --env DOCKER_INFLUXDB_INIT_MODE=setup \
    --env DOCKER_INFLUXDB_INIT_USERNAME=ADMIN_USERNAME \
    --env DOCKER_INFLUXDB_INIT_PASSWORD=ADMIN_PASSWORD \
    --env DOCKER_INFLUXDB_INIT_ORG=ORG_NAME \
    --env DOCKER_INFLUXDB_INIT_BUCKET=BUCKET_NAME \
    --env DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=AUTH_TOKEN \
    --detach \
    influxdb:2
```
This will create a docker container named `measuring-stations-influxdb2` and
create 2 volumes `measuring-stations-influxdb2-data` and
`measuring-stations-influxdb2-config`. It uses the port 8086 (a browser-based
GUI can be accessed at http://localhost:8086, but it's not needed for our
project).

To see the live logs, run `docker logs -f measuring-stations-influxdb2`.

Once created, you can stop the container with
`docker stop measuring-stations-influxdb2` and start it again with
`docker start measuring-stations-influxdb2`.

To remove it, run `docker rm measuring-stations-influxdb2`. To remove the
volumes, run
`docker volume rm measuring-stations-influxdb2-config measuring-stations-influxdb2-data`.

### Running the API server
Finally start the API server:
- Development mode: `fastapi dev main.py`
- Production mode: `fastapi run main.py`

## Usage
With the server running, you should be able to access the API at
http://localhost:8000 and the API documentation at http://localhost:8000/docs or
alternatively at http://localhost:8000/redoc. The endpoints are documented
there.

Here are a few examples using `curl`.

### Create Measuring Station
Measuring Stations can be created using the endpoint
`/measuring-stations/{station_id}` with the `PUT` method. For example:
```
curl -X 'PUT' 'http://127.0.0.1:8000/measuring-stations/station-1?address=Paris%2C%20France' -H 'accept: application/json'
```

### Retrieve Measuring Station
Use `/measuring-stations/{station_id}` with `GET`, e.g.:
```
curl -X 'GET' 'http://127.0.0.1:8000/measuring-stations/station-1' -H 'accept: application/json'
```

### Upload Sensors Data
Use `/measuring-stations/{station_id}/sensor-data` with `PUT`, e.g.:
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sensor-1": [
    {
      "ts": 1718628540,
      "value": 32.0
    }
  ]
}'
```

### Retrieve Measurements
Use `/measuring-stations/{station_id}/sensor-data/{sensor_id}` with `GET`, e.g.:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-1?start=0&stop=1722866400' \
  -H 'accept: application/json'
```

## Next steps and ideas for improvement
- [ ] Write data batchwise to DB instead of point by point
- [ ] Write tests and run them in the CI
- [ ] Replace hardcoded values and make them configurable
- [ ] Benchmarks, check how many requests and data points the system can handle
  per second
- [ ] Authentication for the REST API endpoints
- [ ] Pre-commit hooks
- [ ] Create a docker image for the API and a compose file for the 2 services
  (InfluxDB, API) so that the entire application can be started and stopped with
  a single command
