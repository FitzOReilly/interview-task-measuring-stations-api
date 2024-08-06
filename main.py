import influxdb_client
from fastapi import FastAPI, Response, status
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel, Field

# Parameters to connect to InfluxDB
ORG = "ORG_NAME"
AUTH_TOKEN = "AUTH_TOKEN"
URL = "http://localhost:8086"


# Type alias for sensor id, for readability and also to make changing it easier
type SensorId = str


# Model for a measuring station
class MeasuringStation(BaseModel):
    id: str
    address: str
    sensor_ids: list[SensorId]


# Model for a measurement that validates the value range
class Measurement(BaseModel):
    ts: int
    value: float = Field(ge=0.0, le=100.0)


app = FastAPI()


@app.put("/measuring-stations/{station_id}", status_code=201)
async def create_measuring_station(
    station_id: str, address: str, response: Response
) -> str:
    """Creates a new measuring station with the given station id and address

    Returned status code:
    - 201 (Created) on successful creation
    - 400 (Bad Request) if there is already a station with the given id"""
    with influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG) as client:
        buckets_api = client.buckets_api()
        bucket = buckets_api.find_bucket_by_name(station_id)
        if bucket is not None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return f"Measuring station with id {station_id} already exists"
        # Store each measuring station in a separate bucket with
        # the station_id as bucket_name and its address as description
        buckets_api.create_bucket(bucket_name=station_id, description=address)
        return f"Created measuring station with id {station_id}"


@app.get("/measuring-stations/{station_id}")
async def retrieve_measuring_station(
    station_id: str, response: Response
) -> MeasuringStation | str:
    """Retrieves a measuring station and returns its id and address

    Returned status code:
    - 200 (Ok) on success
    - 404 (Not Found) if no station with the given station_id could be found
    """
    with influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG) as client:
        buckets_api = client.buckets_api()
        bucket = buckets_api.find_bucket_by_name(station_id)
        if bucket is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return f"Measuring station with id {station_id} not found"
        # Query to get the sensor ids
        query_api = client.query_api()
        query = """import "influxdata/influxdb/schema"

            schema.measurementTagValues(
                bucket: _station_id,
                measurement: "Measurement",
                tag: "sensorId",
                start: 0,
            )"""
        params = {"_station_id": station_id}
        tables = query_api.query(query, org=ORG, params=params)
        sensor_ids = [record["_value"] for table in tables for record in table.records]
        # The id and address are the bucket's name and description
        station = {
            "id": bucket.name,
            "address": bucket.description,
            "sensor_ids": sensor_ids,
        }
        return station


@app.put("/measuring-stations/{station_id}/sensor-data")
async def upload_sensor_data(
    station_id: str,
    sensor_measurements: dict[SensorId, list[Measurement]],
    response: Response,
) -> str:
    """Uploads sensor data for multiple sensors of a measuring station

    Returned status code:
    - 200 (Ok) on success
    - 400 (Not Found) if no station with the given station_id could be found
    """
    with influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG) as client:
        buckets_api = client.buckets_api()
        bucket = buckets_api.find_bucket_by_name(station_id)
        if bucket is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return f"Measuring station with id {station_id} not found"
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for sensor_id, measurements in sensor_measurements.items():
            for measurement in measurements:
                point = (
                    influxdb_client.Point("Measurement")
                    .tag("sensorId", sensor_id)
                    .field("value", measurement.value)
                    .time(time=measurement.ts, write_precision="s")
                )
                write_api.write(bucket=station_id, org=ORG, record=point)
        return f"Uploaded sensor data for measuring station with id {station_id}"


@app.get("/measuring-stations/{station_id}/sensor-data/{sensor_id}")
async def retrieve_measurements(
    station_id: str,
    sensor_id: str,
    start: int,
    stop: int,
    response: Response,
) -> list[Measurement] | str:
    """Retrieves sensor data for a specific sensor from a station within a given
    time interval and returns it as an array of measurements

    Returned status code:
    - 200 (Ok) on success
    - 400 (Not Found) if no station with the given station_id could be found
    """
    with influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG) as client:
        buckets_api = client.buckets_api()
        bucket = buckets_api.find_bucket_by_name(station_id)
        if bucket is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return f"Measuring station with id {station_id} not found"
        if start > stop:
            return []
        query_api = client.query_api()
        # InfluxDB Query
        # - `range` is exclusive, so we have to add 1 to include the stop timestamp
        # - In `map`, the timestamp is converted:
        #   RFC3339 -> unix nanosecond timestamp -> unix second timestamp
        query = """from(bucket: _station_id)
            |> range(start: _start, stop: _stop + 1)
            |> filter(fn: (r) => r.sensorId == _sensor_id)
            |> map(fn: (r) => ({ts: int(v: r._time) / 1000000000, value: r._value}))"""
        params = {
            "_station_id": station_id,
            "_sensor_id": sensor_id,
            "_start": start,
            "_stop": stop,
        }
        tables = query_api.query(query, org=ORG, params=params)
        measurements = [
            {"ts": record["ts"], "value": record["value"]}
            for table in tables
            for record in table.records
        ]
        return measurements
