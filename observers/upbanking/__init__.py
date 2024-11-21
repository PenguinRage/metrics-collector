from __future__ import annotations

import os
from urllib.parse import quote
from redis import Redis
import requests
import datetime
import logging


from observers import Observer
from collector import Collector

from repositories.influxdb import post_to_influx


redis = Redis(host="server.local", password=os.environ['REDIS_PWD'], charset="utf-8", decode_responses=True)

redis.ping()

print('Connected to Redis "{}"'.format('172.17.0.2'))


class UpBankingExpensesObserver(Observer):
    endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='

    def update(self, event: Collector) -> None:
        headers = {
            "Authorization": "Bearer " + redis.get('up_token')}
        url = self.endpoint + self.from_timestamp(1)
        response = requests.get(url, headers=headers)
        payload = self.format_payload(response)
        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

    def from_timestamp(self, since):
        date = datetime.datetime.now() - datetime.timedelta(days=since)
        return quote(str(date.isoformat('T') + '+11:00'))

    def format_transaction(self, transaction):
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

    def format_payload(self, response):
        return [self.format_transaction(transaction) for transaction in response.json()['data'] if float(transaction['attributes']['amount']['value']) < 0]

