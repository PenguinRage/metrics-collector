from __future__ import annotations
from abc import ABC, abstractmethod
from collector import Collector


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


