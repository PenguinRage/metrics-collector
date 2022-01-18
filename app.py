from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import quote
from redis import Redis


import requests
import datetime
import schedule
import time

from repositories import influxdb
import logging

redis = Redis(host="172.17.0.2", password='K$jyLjd59tT#bV', charset="utf-8", decode_responses=True)

redis.ping()

logging.info('Connected to Redis "{}"'.format('172.17.0.2'))

class Collector(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass


class MetricsCollector(Collector):
    _observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        """
        Trigger an events in each subscriber.
        """
        for observer in self._observers:
            observer.update(self)

    def get_metrics(self) -> None:
        self.notify()


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, event: Collector) -> None:
        """
        Collect metric and push to metric to influxdb.
        """
        pass


class UpBankingTransactionObserver(Observer):
    endpoint = 'https://api.up.com.au/api/v1/transactions?filter[since]='

    def update(self, event: Collector) -> None:
        headers = {
            "Authorization": "Bearer " + redis.get('up_token')}
        response = requests.get(self.endpoint + self.from_timestamp(1), headers=headers)
        payload = self.format_payload(response)
        if payload:
            logging.info('Pushing new payload to Influx - {}'.format(payload))
            influxdb.post_to_influx(payload)

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


if __name__ == "__main__":
    daily_collector = MetricsCollector()
    up_transaction_observer = UpBankingTransactionObserver()
    daily_collector.attach(up_transaction_observer)

    # Daily Collection
    schedule.every().day.at("00:00").do(daily_collector.get_metrics)

    while True:
        schedule.run_pending()
        time.sleep(1)
