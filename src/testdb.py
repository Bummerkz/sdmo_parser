from datetime import datetime
import random

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


# You can generate a Token from the "Tokens Tab" in the UI
token = "diSq8xKXop8sH7C5cvKJSWPQIIE0yVa_-1VMTzCik9btfZ6qdCFOU8NGkhRepH1ylF_j0uUWWriwIhcvWcXUhg=="
org = "hismatullin.v@gmail.com"
bucket = "test"

client = influxdb_client.InfluxDBClient(url="https://europe-west1-1.gcp.cloud2.influxdata.com", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)



# for i in range(0, 100000):
#     p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", random.randint(-200, 5000))
#     write_api.write(bucket=bucket, org=org, record=p)


query_api = client.query_api()
query = 'from(bucket:"test")\
|> range(start: -10m)\
|> filter(fn:(r) => r._measurement == "my_measurement")\
|> filter(fn: (r) => r.location == "Prague")\
|> filter(fn:(r) => r._field == "temperature" )'

result = query_api.query(org=org, query=query)

print(result)


# results = []
# for table in result:
#   for record in table.records:
#     results.append((record.get_field(), record.get_value()))

# print(results)