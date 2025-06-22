from datetime import datetime
from dataclasses import dataclass

@dataclass
class MarketDataRequest:
    symbol: str
    interval: str
    start_date: str
    end_date: str
    provider: str

@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
