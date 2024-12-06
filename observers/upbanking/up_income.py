import requests
import datetime


from observers import Observer
from collector import Collector

from repositories.influxdb import post_to_influx
from repositories.redis import get_value


class UpBankingIncomeObserver(Observer):
    endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='

    def update(self, event: Collector) -> None:
        headers = {"Authorization": "Bearer " + get_value('up_token')}
        url = self.endpoint + self.__from_timestamp(1)
        try:
            response = requests.get(url, headers=headers)
        except ConnectionError:
            print("Handling Connection Error for Income will try again in another 5")
            return

        payload = self.__format_payload(response)
        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

    def __from_timestamp(self, since):
        date = datetime.datetime.now() - datetime.timedelta(days=since)
        return str(date.isoformat('T') + '+11:00')

    def __format_transaction(self, transaction):
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

    def __filter_transaction(self, transaction):
        amount = float(transaction['attributes']['amount']['value'])
        description = transaction['attributes']['description']
        if amount < 0 or description.startswith("Cover from") or description.startswith("Transfer from"):
            return False
        return True

    def __format_payload(self, response):
        return [self.__format_transaction(transaction)
                for transaction in response.json()['data']
                if self.__filter_transaction(transaction)]