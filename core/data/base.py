from abc import ABC, abstractmethod
from .models import MarketDataRequest, Candle
from typing import List

class MarketDataProvider(ABC):
    @abstractmethod
    def get_historical_data(self, request: MarketDataRequest) -> List[Candle]:
        pass
