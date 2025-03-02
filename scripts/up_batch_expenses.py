import datetime
import os
from urllib.parse import quote
import requests
from redis import Redis

from repositories.influxdb import post_to_influx

endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='




def from_timestamp(since):
    date = datetime.datetime.now() - datetime.timedelta(days=since)
    return quote(str(date.isoformat('T') + '+11:00'))

def format_transaction(transaction):
    return {
        "measurement": "expenses",
        "time": transaction['attributes']['createdAt'],
        "tags": {
            "source": "UP_BANKING",
            "description": transaction['attributes']['description'],
            "category": transaction['relationships']['category']['data']['id'] if transaction['relationships']['category']['data'] is not None else "",
            "parent_category": transaction['relationships']['parentCategory']['data']['id'] if transaction['relationships']['category']['data'] is not None else "",
            "tag": transaction['relationships']['tags']['data'][0]['id'] if transaction['relationships']['tags']['data'] else ""
        },
        "fields": {"amount": float(transaction['attributes']['amount']['value']) * -1}
    }

def format_payload(response):
    return [format_transaction(transaction) for transaction in response.json()['data'] if float(transaction['attributes']['amount']['value']) < 0]

def test():
    redis = Redis(host="server.local", password=os.environ['REDIS_PWD'], charset="utf-8", decode_responses=True)
    headers = {
        "Authorization": "Bearer " + redis.get('up_token')}
    url = endpoint + from_timestamp(8)
    print(url)
    response = requests.get(url, headers=headers)
    payload = format_payload(response)
    if payload:
        print('Pushing new payload to Influx - {}'.format(payload))
        post_to_influx(payload)
    print(response.json())
    next = response.json()['links']['next']
    while (next is not None):
        response = requests.get(response.json()['links']['next'], headers=headers)
        payload = format_payload(response)
        print(response.json()['links']['next'])
        next = response.json()['links']['next']

        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

test()
