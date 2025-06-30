import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import argparse
import pandas as pd
from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path
from utils.logger import log


def generate_stats_features(df: pd.DataFrame, windows: list) -> pd.DataFrame:
    df_feat = pd.DataFrame(index=df.index)

    for window in windows:
        # Rolling mean
        df_feat[f'close_mean_{window}'] = df['close'].rolling(window).mean()
        df_feat[f'volume_mean_{window}'] = df['volume'].rolling(window).mean()

        # Rolling std
        df_feat[f'close_std_{window}'] = df['close'].rolling(window).std()
        df_feat[f'volume_std_{window}'] = df['volume'].rolling(window).std()

        # Z-score
        df_feat[f'close_zscore_{window}'] = (df['close'] - df_feat[f'close_mean_{window}']) / df_feat[f'close_std_{window}']
        df_feat[f'volume_zscore_{window}'] = (df['volume'] - df_feat[f'volume_mean_{window}']) / df_feat[f'volume_std_{window}']

        # Min / Max
        df_feat[f'close_min_{window}'] = df['close'].rolling(window).min()
        df_feat[f'close_max_{window}'] = df['close'].rolling(window).max()

        # Skewness / Kurtosis
        df_feat[f'close_skew_{window}'] = df['close'].rolling(window).skew()
        df_feat[f'close_kurt_{window}'] = df['close'].rolling(window).kurt()

    return df_feat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    md = config["market_data"]
    stats_cfg = config["features"]["stats"]
    windows = stats_cfg.get("windows", [5, 10, 20])

    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )

    df = pd.read_csv(data_path)
    log.info(f"[cyan]📊 Calculando stats rolling...[/cyan]")

    df_feat = generate_stats_features(df, windows)

    output_file = "core/features/shared/temp/stats_features.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_feat.to_csv(output_file, index=False)

    log.info(f"[green]✅ Features stats guardadas en {output_file} ({df_feat.shape[1]} columnas)[/green]")


if __name__ == "__main__":
    main()
