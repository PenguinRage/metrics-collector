from __future__ import annotations
import logging
import schedule
import time

from collector import MetricsCollector
from observers.upbanking.up_expenses import UpBankingExpensesObserver
from observers.upbanking.up_accounts import UpBankingAccountsObserver
from observers.upbanking.up_income import UpBankingIncomeObserver

if __name__ == "__main__":
    minutely_collector = MetricsCollector()
    up_expenses_observer = UpBankingExpensesObserver()
    up_accounts_observer = UpBankingAccountsObserver()
    up_income_observer = UpBankingIncomeObserver()

    minutely_collector.attach(up_expenses_observer)
    minutely_collector.attach(up_accounts_observer)
    minutely_collector.attach(up_income_observer)

    print('Starting Metric Scheduler')
    print("Pulling Metrics ..................")
    minutely_collector.get_metrics()

    schedule.every(5).minutes.do(minutely_collector.get_metrics)

    while True:
        schedule.run_pending()
        time.sleep(1)
