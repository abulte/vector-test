from influxdb_client import InfluxDBClient

bucket = "vector-bucket"
url = "http://localhost:8086/"
org = "etalab"
token = "A2jqhzcRPZeT3bAF"

measurements_dict = {
    "reuse": "reuse.reuse_id",
    "resource": "resource.resource_id",
    "dataset": "dataset.dataset_id",
    "organization": "organization.organization_id",
    "resource_hit": "resource_hit.resource_id",
}

durations = ["1y", "1m", "1w", "1d"]

with InfluxDBClient(url=url, token=token, org=org) as client:
    print("Connecting to InfluxDB")
    query_api = client.query_api()

    for duration in durations:
        for name, measurement in measurements_dict.items():
            id_key = f"{measurement}".split(".")[1]
            query = f"""
                from(bucket: "{bucket}")
                    |> range(start: -{duration})
                    |> filter(fn: (r) => r._measurement == "{measurement}")
                    |> group(columns: ["{id_key}"])
                    |> count()
                """
                    # |> aggregateWindow(every: 1m, fn: sum, createEmpty: true)
                    # |> yield(name: "sum")            print(duration, measurement)
            print(duration, name)
            tables = query_api.query(query)

            for table in tables:
                for record in table.records:
                    print(record[id_key], record.get_value())
                    # print(str(record["_time"]) + " - " + record.get_measurement()
                    #       + " " + record.get_field() + "=" + str(record.get_value()))
