import ccxt
from datetime import datetime
from typing import List
from .base import MarketDataProvider
from .models import MarketDataRequest, Candle
from utils.logger import log

class CoinbaseFetcher(MarketDataProvider):
    def __init__(self):
        self.client = ccxt.coinbase()
        log.info("CoinbaseFetcher inicializado")

    def get_historical_data(self, request: MarketDataRequest) -> List[Candle]:
        log.info(f"Solicitando datos de {request.symbol} ({request.interval}) desde Coinbase...")
        symbol = request.symbol  # ccxt acepta formato 'ETH/USD'
        timeframe = request.interval
        since = int(datetime.strptime(request.start_date, "%Y-%m-%d").timestamp() * 1000)
        candles_raw = self.client.fetch_ohlcv(symbol, timeframe=timeframe, since=since)
        log.info(f"Recibidas {len(candles_raw)} velas de Coinbase")

        result = []
        for entry in candles_raw:
            candle = Candle(
                timestamp=datetime.fromtimestamp(entry[0] / 1000),
                open=entry[1],
                high=entry[2],
                low=entry[3],
                close=entry[4],
                volume=entry[5],
            )
            result.append(candle)

        return result