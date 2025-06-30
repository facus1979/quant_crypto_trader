import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import argparse
import pandas as pd
from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path
from utils.logger import log

from autofeat import AutoFeatRegressor  # asumimos que este env tiene autofeat instalado


def generate_nonlinear_features(df: pd.DataFrame, method: str) -> pd.DataFrame:
    # Eliminamos columnas no numéricas si existieran
    df_num = df.select_dtypes(include='number').dropna()

    if method == "autofeat":
        model = AutoFeatRegressor(verbose=1, feateng_steps=2)
        X_new = model.fit_transform(df_num.drop(columns=['close'], errors='ignore'), df_num['close'] if 'close' in df_num else None)
        return pd.DataFrame(X_new, index=df_num.index)
    
    raise NotImplementedError(f"Método {method} no implementado en nonlinear features.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    md = config["market_data"]
    nonlinear_cfg = config["features"]["nonlinear"]
    method = nonlinear_cfg.get("method", "autofeat")

    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )

    df = pd.read_csv(data_path)
    log.info(f"[cyan]⚡ Calculando nonlinear features ({method})...[/cyan]")

    df_feat = generate_nonlinear_features(df, method)

    output_file = "core/features/shared/temp/nonlinear_features.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_feat.to_csv(output_file, index=False)

    log.info(f"[green]✅ Features nonlinear guardadas en {output_file} ({df_feat.shape[1]} columnas)[/green]")


if __name__ == "__main__":
    main()
