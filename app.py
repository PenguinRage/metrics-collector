from __future__ import annotations
import logging
import schedule
import time

from collector import MetricsCollector
from observers.upbanking import UpBankingTransactionObserver

if __name__ == "__main__":
    daily_collector = MetricsCollector()
    up_transaction_observer = UpBankingTransactionObserver()
    daily_collector.attach(up_transaction_observer)

    daily_collector.get_metrics()
    # Daily Collection
    #logging.info('Starting Metric Scheduler')
    #schedule.every().day.at("00:00").do(daily_collector.get_metrics)

    #while True:
     #   schedule.run_pending()
      #  time.sleep(1)
