from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError
import requests
import logging


def post_to_influx(payload):
    try:
        client = InfluxDBClient(host='server.local', port=8086, username='penguinrage', password='C4Nur34D')
        client.switch_database('home_assistant')
        client.write_points(payload)
    except InfluxDBServerError:
        logging.error('Failed to send metrics to influxdb')
    except requests.exceptions.ConnectionError:
        logging.error('Failed to connect to InfluxDB')
    finally:
        client.close()