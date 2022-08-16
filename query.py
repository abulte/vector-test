from datetime import datetime

from influxdb_client import InfluxDBClient

client = InfluxDBClient(
    url="http://localhost:8086",
    token="A2jqhzcRPZeT3bAF",
    org="etalab"
)

query_api = client.query_api()

query = '''
    from(bucket:"vector-bucket")
    |> range(start: _start, stop: _stop)
    |> filter(fn:(r) => r._measurement == "dataset.dataset_id")
    |> filter(fn: (r) => r.dataset_id == "5b7ffc618b4c4169d30727e0")
'''

params = {
    "_start": datetime(2022, 6, 3),
    "_stop": datetime(2022, 6, 4)
}

tables = query_api.query(query, params=params)

for table in tables:
    print(table)
    for record in table.records:
        print(record["_time"], record["dataset_id"], record["status_code"], record["request_mode"], record["request_type"], record["_value"])
