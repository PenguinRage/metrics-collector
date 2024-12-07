import requests

from observers import Observer
from collector import Collector

from repositories.influxdb import post_to_influx
from repositories.redis import get_value

import datetime


class UpBankingAccountsObserver(Observer):
    endpoint = "https://api.up.com.au/api/v1/accounts"

    def update(self, event: Collector) -> None:
        headers = {"Authorization": "Bearer " + get_value('up_token')}
        try:
            response = requests.get(self.endpoint, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Handling Connection Error for Accounts will try again in another 5")
            return

        payload = self.__format_payload(response)
        if payload:
            print('Pushing new payload to Influx - {}'.format(payload))
            post_to_influx(payload)

    def __is_saver(self, account):
        return account['attributes']['accountType'] == 'SAVER'

    def __get_current_timestamp(self):
        date = datetime.datetime.now()
        return str(date.isoformat('T') + '+11:00')

    def __format_payload(self, response):
        accounts = response.json()['data']
        results = []
        for account in accounts:
            results.append(self.__format_account(account))
        return results

    def __format_account(self, account):
        name = account['attributes']['displayName'].split()
        return {
            "measurement": "accounts",
            "time": self.__get_current_timestamp(),
            "tags": {
                "source": "UP_BANKING",
                "name": " ".join(name[1:]) if self.__is_saver(account) else " ".join(name),
                "account-type": account['attributes']['accountType'],
                "currency": account['attributes']['balance']['currencyCode']
            },
            "fields": {
                "balance": float(account['attributes']['balance']['value'])
            }
        }