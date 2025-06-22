import yaml
import pandas as pd
from core.data.fetcher_factory import get_provider
from core.data.models import MarketDataRequest
from utils.config_loader import load_yaml
from pathlib import Path

def main():
    config = load_yaml("config/example_experiment.yaml")
    md = config["market_data"]

    request = MarketDataRequest(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],  # aún no usado, ccxt solo toma start
        provider=md["provider"],
    )

    provider = get_provider(request.provider)
    candles = provider.get_historical_data(request)

    # Convertir a DataFrame para visualización o guardado
    df = pd.DataFrame([c.__dict__ for c in candles])

    print(df.head())

    if md.get("save_to_csv", False):
        symbol_clean = request.symbol.replace("/", "")
        path = Path(f"data/{symbol_clean}/{request.interval}")
        path.mkdir(parents=True, exist_ok=True)

        file_name = f"{request.start_date}_to_{request.end_date}_{request.provider}.csv"
        full_path = path / file_name

        df.to_csv(full_path, index=False)
        print(f"✅ Datos guardados en {full_path}")


if __name__ == "__main__":
    main()
