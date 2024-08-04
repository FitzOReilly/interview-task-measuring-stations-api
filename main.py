import influxdb_client
from fastapi import FastAPI
from influxdb_client.client.write_api import SYNCHRONOUS
from pydantic import BaseModel, Field

ORG = "ORG_NAME"
AUTH_TOKEN = "AUTH_TOKEN"
URL = "http://localhost:8086"


class MeasuringStation(BaseModel):
    id: str
    address: str


class Measurement(BaseModel):
    ts: int
    value: float = Field(gt=0.0, lt=100.0)


app = FastAPI()


@app.put("/measuring-stations/{station_id}", status_code=201)
async def create_measuring_station(station_id: str, address: str):
    client = influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG)
    buckets_api = client.buckets_api()
    buckets_api.create_bucket(bucket_name=f"{station_id}", description=address)


@app.get("/measuring-stations/{station_id}")
async def retrieve_measuring_station(station_id: str):
    client = influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG)
    buckets_api = client.buckets_api()
    bucket = buckets_api.find_bucket_by_name(station_id)
    station = {"id": bucket.name, "address": bucket.description}
    return station


@app.put("/measuring-stations/{station_id}/sensor-data", status_code=201)
async def upload_sensors_data(
    station_id: str,
    sensor_measurements: list[tuple[str, list[Measurement]]],
):
    client = influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for sensor_id, measurements in sensor_measurements:
        for measurement in measurements:
            point = (
                influxdb_client.Point(sensor_id)
                .field("value", measurement.value)
                .time(time=measurement.ts, write_precision="s")
            )
            write_api.write(bucket=station_id, org=ORG, record=point)


@app.get("/measuring-stations/{station_id}/sensor-data/{sensor_id}")
async def retrieve_measurements(station_id: str, sensor_id: str, start: int, stop: int):
    if start > stop:
        return []
    client = influxdb_client.InfluxDBClient(url=URL, token=AUTH_TOKEN, org=ORG)
    query_api = client.query_api()
    # InfluxDB Query
    # - range is exclusive, so we have to add 1 to include the stop timestamp
    # - In map, the timestamp is converted:
    #   RFC3339 -> unix nanosecond timestamp -> unix second timestamp
    query = f"""from(bucket: "{station_id}")
        |> range(start: {start}, stop: {stop + 1})
        |> filter(fn: (r) => r._measurement == "{sensor_id}")
        |> map(fn: (r) => ({{ts: int(v: r._time) / 1000000000, value: r._value}}))"""
    tables = query_api.query(query, org=ORG)
    records = []
    for table in tables:
        records.extend(
            [{"ts": record["ts"], "value": record["value"]} for record in table.records]
        )
    return records
