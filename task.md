Your task is to create an API to manage measuring stations and the data they
collect. It should be possible to create and retrieve measuring stations via the
API. Each measuring station has an address and an ID, and can have up to 10
sensors. Each sensor takes a measurement once per minute in the following
format:
```json
{
    "ts": 1718628540,
    "value": 32.0
}
```
The measured value should be in the range of `[0, 100]`. The stations send all
measurements from their sensors to the API, which stores them in the backend.
Additionally, the API should provide an endpoint to retrieve the measurements of
a specific sensor from a station for a given time interval `[x, y]`.
