from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time

url = "http://localhost:8086"
token = "yjT8eyhxhxvx1hNHMrjI_XydvDVSr_SgtT88slxHxDN8_PlrDVT-7CeepsvrG5upwAGwo8a96iszTNYI8Oez4w=="
org = "UQ"
bucket = "InputData"

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    score = random.uniform(20, 30)

    point = (
        Point("Highscores")
        .tag("User", "test")
        .field("Score", score)
    )
    write_api.write(bucket=bucket, org=org, record=point)

    print("Wrote:", score)

    time.sleep(5)
