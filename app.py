from __future__ import annotations
import logging
import schedule
import time

from collector import MetricsCollector
from observers.upbanking.up_expenses import UpBankingExpensesObserver
from observers.upbanking.up_accounts import UpBankingAccountsObserver

if __name__ == "__main__":
    hourly_collector = MetricsCollector()
    up_expenses_observer = UpBankingExpensesObserver()
    up_accounts_observer = UpBankingAccountsObserver()
    hourly_collector.attach(up_expenses_observer)
    hourly_collector.attach(up_accounts_observer)

    print('Starting Metric Scheduler')
    hourly_collector.get_metrics()

    schedule.every().minute.do(hourly_collector.get_metrics)

    while True:
        schedule.run_pending()
        time.sleep(1)
