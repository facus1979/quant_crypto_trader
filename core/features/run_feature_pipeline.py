import sys
import os
sys.path.insert(0, os.path.abspath("."))
import subprocess
import pandas as pd
from pathlib import Path

from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path, merge_feature_files
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

    # Carga de datos OHLCV
    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )
    df = pd.read_csv(data_path)
    log.info(f"[cyan]📥 Datos cargados desde {data_path} ({df.shape[0]} filas)[/cyan]")

    # Limpieza de temporales
    temp_path = Path("core/features/shared/temp")
    temp_path.mkdir(parents=True, exist_ok=True)
    for f in temp_path.glob("*_features.csv"):
        f.unlink()

    # Generación de features por ambiente
    for env in ["ohlcv", "stats", "relational", "nonlinear"]:
        if config["features"].get(env, {}).get("enabled", False):
            log.info(f"[blue]⚙️ Ejecutando features: {env}[/blue]")
            run_env_generator(env_name=env, script_name="generate_features.py", config_path=config_path)

    # Unificación de features
    log.info("[bold]🔗 Unificando features en X_full...[/bold]")
    df_full = merge_feature_files(temp_path)
    
    # Generar target si no existe
    if "target" not in df_full.columns:
        if "close" not in df_full.columns:
            log.error("❌ No se puede generar target: falta la columna 'close'")
            sys.exit(1)
        df_full["next_ret"] = df_full["close"].pct_change().shift(-1)
        df_full["target"] = (df_full["next_ret"] > 0).astype(int)
        df_full.drop(columns=["next_ret"], inplace=True)
        # Quitamos la última fila que queda con NaN
        df_full = df_full.iloc[:-1].reset_index(drop=True)
        log.info(f"✅ Target generado automáticamente. Shape nuevo: {df_full.shape}")


    output_dir = Path(config["output_path"]) / f"{md['symbol']}_{md['interval']}"
    output_dir.mkdir(parents=True, exist_ok=True)
    x_full_path = output_dir / "X_full.csv"
    df_full.to_csv(x_full_path, index=False)

    # Selección automática como un feature más
    if config.get("selection", {}).get("enabled", True):
        log.info(f"[blue]⚙️ Ejecutando features: selection[/blue]")

        # Armamos dinámicamente los paths
        sel_cfg = config["selection"]
        sel_cfg["x_full_path"] = str(x_full_path)
        sel_cfg["output_dir"] = str(output_dir)

        # Guardamos config selection temporal
        temp_sel_cfg_path = Path("temp_selection.yaml")
        import yaml
        with open(temp_sel_cfg_path, "w") as f:
            yaml.dump({"selection": sel_cfg}, f)

        # Ejecutamos el selector
        run_env_generator(
            env_name="selection",
            script_name="auto_selector.py",
            config_path=str(temp_sel_cfg_path)
        )

        # Eliminamos el YAML temporal
        temp_sel_cfg_path.unlink()

    log.info("[green]✅ Pipeline de features completado[/green]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.error("⚠️  Debes indicar el path del archivo YAML.")
        exit(1)
    main(sys.argv[1])
