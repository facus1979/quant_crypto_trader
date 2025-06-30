import sys
import os
sys.path.insert(0, os.path.abspath("."))
from core.data.fetcher_factory import get_provider
from core.data.models import MarketDataRequest
from utils.config_loader import load_yaml
from utils.logger import log

from subprocess import run
from pathlib import Path
import pandas as pd


def build_data_path(symbol: str, interval: str, start_date: str, end_date: str, provider: str) -> Path:
    symbol_clean = symbol.replace("/", "")
    folder = Path(f"core/features/shared/data/{symbol_clean}/{interval}")
    folder.mkdir(parents=True, exist_ok=True)
    file_name = f"{start_date}_to_{end_date}_{provider}.csv"
    return folder / file_name


def build_output_path(symbol: str, interval: str) -> Path:
    folder = Path(f"core/features/shared/output/{symbol.replace('/', '')}_{interval}")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def fetch_data_if_needed(request: MarketDataRequest, save_to_csv: bool) -> Path:
    path = build_data_path(
        symbol=request.symbol,
        interval=request.interval,
        start_date=request.start_date,
        end_date=request.end_date,
        provider=request.provider
    )
    if path.exists():
        log.info(f"[yellow]🟡 Datos ya existen en {path}, se omite descarga.[/yellow]")
        return path

    log.info(f"[cyan]🔍 Datos no encontrados, descargando desde {request.provider}...[/cyan]")
    provider = get_provider(request.provider)
    candles = provider.get_historical_data(request)
    df = pd.DataFrame([c.__dict__ for c in candles])

    log.info(f"[green]⬇️  {len(df)} registros descargados.[/green]")
    if save_to_csv:
        df.to_csv(path, index=False)
        log.info(f"[bold green]✅ Guardado en {path}[/bold green]")
    return path


def main(config_path: str):
    config = load_yaml(config_path)
    md = config["market_data"]

    log.info(f"[bold blue]🚀 Iniciando experimento para {md['symbol']} ({md['interval']})[/bold blue]")

    request = MarketDataRequest(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"],
    )

    fetch_data_if_needed(request, save_to_csv=md.get("save_to_csv", True))

    output_path = build_output_path(request.symbol, request.interval)
    config["output_path"] = str(output_path)

    temp_config_path = Path("temp_config.yaml")
    with open(temp_config_path, "w") as f:
        import yaml
        yaml.dump(config, f)

    log.info(f"[bold magenta]🧠 Ejecutando pipeline de features...[/bold magenta]")
    run([sys.executable, "core/features/run_feature_pipeline.py", str(temp_config_path)], check=True)


    log.info(f"[bold green]🎯 Experimento completo.[/bold green]")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        log.error("⚠️  Debes indicar el path del archivo YAML.")
        exit(1)
    main(sys.argv[1])
