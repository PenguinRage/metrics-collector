from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


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


