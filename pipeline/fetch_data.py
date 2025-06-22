# pipeline/fetch_data.py

from core.data.fetcher_factory import get_provider
from core.data.models import MarketDataRequest
from utils.config_loader import load_yaml
from utils.logger import log 
from pathlib import Path
import pandas as pd


def get_output_path(request: MarketDataRequest) -> Path:
    symbol_clean = request.symbol.replace("/", "")
    path = Path(f"shared/data/{symbol_clean}/{request.interval}")
    path.mkdir(parents=True, exist_ok=True)
    file_name = f"{request.start_date}_to_{request.end_date}_{request.provider}.csv"
    return path / file_name


def main():
    config = load_yaml("config/example_experiment.yaml")
    md = config["market_data"]

    request = MarketDataRequest(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"],
    )

    provider = get_provider(request.provider)
    log.info(f"[cyan]Obteniendo datos de {request.symbol} desde {request.provider}...[/cyan]")

    candles = provider.get_historical_data(request)
    df = pd.DataFrame([c.__dict__ for c in candles])

    log.info(f"[green]{len(df)} registros descargados.[/green]")
    log.debug(df.head())

    if md.get("save_to_csv", False):
        output_path = get_output_path(request)
        df.to_csv(output_path, index=False)
        log.info(f"[bold green]✅ Guardado en {output_path}[/bold green]")


if __name__ == "__main__":
    main()
