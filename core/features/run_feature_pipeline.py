import sys
import os
sys.path.insert(0, os.path.abspath("."))
import subprocess
import pandas as pd
from pathlib import Path

from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path, merge_feature_files
from core.features.selection.auto_selector import run_auto_feature_selection
from utils.logger import log


def run_env_generator(env_name: str, script_name: str, config_path: str):
    venv_path = (
        f"envs/{env_name}/.venv/Scripts/python.exe"
        if os.name == "nt"
        else f"envs/{env_name}/.venv/bin/python"
    )
    
    script_path = f"core/features/{env_name}/{script_name}"
    subprocess.run([venv_path, script_path, "--config", config_path], check=True)


def main(config_path: str):
    config = load_yaml(config_path)
    md = config["market_data"]

    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )
    df = pd.read_csv(data_path)
    log.info(f"[cyan]📥 Datos cargados desde {data_path} ({df.shape[0]} filas)[/cyan]")

    temp_path = Path("core/features/shared/temp")
    temp_path.mkdir(parents=True, exist_ok=True)
    for f in temp_path.glob("*_features.csv"):
        f.unlink()

    for env in ["ohlcv", "stats", "relational", "nonlinear"]:
        if config["features"].get(env, {}).get("enabled", False):
            log.info(f"[blue]⚙️ Ejecutando features: {env}[/blue]")
            run_env_generator(env_name=env, script_name="generate_features.py", config_path=config_path)

    log.info("[bold]🔗 Unificando features en X_full...[/bold]")
    df_full = merge_feature_files(temp_path)
    output_dir = Path(config["output_path"])
    df_full.to_csv(output_dir / "X_full.csv", index=False)

    if config.get("selection", {}).get("enabled", True):
        log.info("[bold]🧠 Ejecutando selección automática de features...[/bold]")
        df_selected, metadata = run_auto_feature_selection(df_full, config["selection"])
        df_selected.to_csv(output_dir / "X_selected.csv", index=False)
        metadata["columns"] = list(df_selected.columns)
        pd.Series(metadata).to_json(output_dir / "metadata.json")

    log.info("[green]✅ Pipeline de features completado[/green]")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        log.error("⚠️  Debes indicar el path del archivo YAML.")
        exit(1)
    main(sys.argv[1])
