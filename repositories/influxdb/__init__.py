from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError
import requests
import logging
import os


def post_to_influx(payload):
    try:
        client = InfluxDBClient(
            host=os.environ['INFLUXDB_HOST'],
            port=8086,
            username=os.environ['INFLUXDB_USER'],
            password=os.environ['INFLUXDB_PWD'])
        client.switch_database('home_assistant')
        client.write_points(payload)
    except InfluxDBServerError:
        logging.error('Failed to send metrics to influxdb')
    except requests.exceptions.ConnectionError:
        logging.error('Failed to connect to InfluxDB')
    finally:
        client.close()
