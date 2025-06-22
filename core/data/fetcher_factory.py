from .base import MarketDataProvider
from .binance_fetcher import BinanceFetcher
from .coinbase_fetcher import CoinbaseFetcher

def get_provider(name: str) -> MarketDataProvider:
    if name == "binance":
        return BinanceFetcher()
    elif name == "coinbase":
        return CoinbaseFetcher()
    else:
        raise ValueError(f"Proveedor '{name}' no soportado")
