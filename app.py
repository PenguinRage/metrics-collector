from __future__ import annotations
import logging
import schedule
import time

from collector import MetricsCollector
from observers.upbanking import UpBankingExpensesObserver

if __name__ == "__main__":
    daily_collector = MetricsCollector()
    up_expenses_observer = UpBankingExpensesObserver()
    daily_collector.attach(up_expenses_observer)

    #daily_collector.get_metrics()
    # Daily Collection
    print('Starting Metric Scheduler')
    schedule.every().day.at("00:00").do(daily_collector.get_metrics)

    while True:
        schedule.run_pending()
        time.sleep(1)
