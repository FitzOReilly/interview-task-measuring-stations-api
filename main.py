import influxdb_client
from fastapi import FastAPI
from pydantic import BaseModel, Field

ORG = "ORG_NAME"
AUTH_TOKEN = "AUTH_TOKEN"
URL = "http://localhost:8086"


class MeasuringStation(BaseModel):
    id: str
    address: str


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
