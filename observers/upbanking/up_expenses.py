from __future__ import annotations
from urllib.parse import quote
import requests
import datetime


from observers import Observer
from collector import Collector

from repositories.influxdb import post_to_influx
from repositories.redis import get_value


class UpBankingExpensesObserver(Observer):
    endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='

    def update(self, event: Collector) -> None:
        headers = {"Authorization": "Bearer " + get_value('up_token')}
        url = self.endpoint + self.__from_timestamp(1)
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Handling Connection Error for Expenses will try again in another 5")
            return

        payload = self.__format_payload(response)
        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

    def __from_timestamp(self, since):
        date = datetime.datetime.now() - datetime.timedelta(days=since)
        return quote(str(date.isoformat('T') + '+11:00'))

    def __format_transaction(self, transaction):
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

    def __format_payload(self, response):
        return [self.__format_transaction(transaction)
                for transaction in response.json()['data'] if float(transaction['attributes']['amount']['value']) < 0]

