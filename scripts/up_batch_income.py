import datetime
import os
import string
from urllib.parse import quote
import requests
from redis import Redis

from repositories.influxdb import post_to_influx

endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='


def from_timestamp(since):
    date = datetime.datetime.now() - datetime.timedelta(days=since)
    return quote(str(date.isoformat('T') + '+11:00'))


def format_transaction(transaction):
    #print(transaction)
    return {
        "measurement": "income",
        "time": transaction['attributes']['createdAt'],
        "tags": {
            "source": "UP_BANKING",
            "description": transaction['attributes']['description'],
            "transaction_type": transaction['attributes']['transactionType']
        },
        "fields": {"amount": float(transaction['attributes']['amount']['value'])}
    }


def __filter_transaction(transaction):
    amount = float(transaction['attributes']['amount']['value'])
    description = transaction['attributes']['description']
    if amount < 0 or description.startswith("Cover from") or description.startswith("Transfer from"):
        return False
    return True


def format_payload(response):
    return [format_transaction(transaction)
            for transaction in response.json()['data']
            if __filter_transaction(transaction)]


def test():
    redis = Redis(host="server.local", password=os.environ['REDIS_PWD'], charset="utf-8", decode_responses=True)
    headers = {
        "Authorization": "Bearer " + redis.get('up_token')}
    url = endpoint + from_timestamp(705)
    print(url)
    response = requests.get(url, headers=headers)
    payload = format_payload(response)
    if payload:
        print('Pushing new payload to Influx - {}'.format(payload))
        post_to_influx(payload)
    next = response.json()['links']['next']

    while next is not None:
        response = requests.get(response.json()['links']['next'], headers=headers)
        payload = format_payload(response)
        #print(response.json()['links']['next'])
        next = response.json()['links']['next']

        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

test()
