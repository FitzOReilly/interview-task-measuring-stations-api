### Request Examples
#### Let's create a station with id `station-1` and address `Paris, France`
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-1?address=Paris%2C%20France' \
  -H 'accept: application/json'
```
Response
```
"Created measuring station with id station-1"
```
#### Retrieve the station
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1' \
  -H 'accept: application/json'
```
Response
```
{"id":"station-1","address":"Paris, France"}
```
#### Trying to create another station with the same id causes an error
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-1?address=Berlin%2C%20Germany' \
  -H 'accept: application/json'
```
Response
```
"Measuring station with id station-1 already exists"
```
#### Retrieve the station, it is unchanged
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1' \
  -H 'accept: application/json'
```
Response
```
{"id":"station-1","address":"Paris, France"}
```
#### Choose a different id for the second station
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-2?address=Berlin%2C%20Germany' \
  -H 'accept: application/json'
```
Response
```
"Created measuring station with id station-2"
```
#### Upload 2 measurements for a sensor of station 1
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
    },
    {
      "ts": 1718628600,
      "value": 67.9
    }
  ]
}'
```
Response
```
"Uploaded sensor data for measuring station with id station-1"
```
#### Retrieve data for this sensor
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-1?start=0&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628540,"value":32.0},{"ts":1718628600,"value":67.9}]
```
#### Upload a measurement with the same timestamp as one of the earlier points
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sensor-1": [
    {
      "ts": 1718628540,
      "value": 99.0
    }
  ]
}'
```
Response
```
"Uploaded sensor data for measuring station with id station-1"
```
#### Retrieve sensor data, the point has been overwritten
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-1?start=0&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628540,"value":99.0},{"ts":1718628600,"value":67.9}]
```
#### Trying to upload a measurement which is out of range leads to an error
```
curl -X 'PUT' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sensor-1": [
    {
      "ts": 1718628540,
      "value": 101.0
    }
  ]
}'
```
Response
```
{"detail":[{"type":"less_than_equal","loc":["body","sensor-1",0,"value"],"msg":"Input should be less than or equal to 100","input":101.0,"ctx":{"le":100.0}}]}
```
#### Retrieve sensor data, the values are unchanged
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-1?start=0&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628540,"value":99.0},{"ts":1718628600,"value":67.9}]
```
#### Upload multiple measurements for multiple sensors
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
    },
    {
      "ts": 1718628600,
      "value": 67.9
    }
  ],
  "sensor-2": [
    {
      "ts": 1718628600,
      "value": 12.3
    },
    {
      "ts": 1718628660,
      "value": 80.5
    },
    {
      "ts": 1718628720,
      "value": 22.8
    }
  ]
}'
```
Response
```
"Uploaded sensor data for measuring station with id station-1"
```
#### Retrieve both sensors
##### Sensor 1
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-1?start=0&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628540,"value":32.0},{"ts":1718628600,"value":67.9}]
```
##### Sensor 2
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-2?start=0&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628600,"value":12.3},{"ts":1718628660,"value":80.5},{"ts":1718628720,"value":22.8}]
```
#### Use a smaller time range
```
curl -X 'GET' \
  'http://127.0.0.1:8000/measuring-stations/station-1/sensor-data/sensor-2?start=1718628660&stop=1722866400' \
  -H 'accept: application/json'
```
Response
```
[{"ts":1718628660,"value":80.5},{"ts":1718628720,"value":22.8}]
```
