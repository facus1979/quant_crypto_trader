import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import argparse
import pandas as pd
from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path
from utils.logger import log


def generate_relational_features(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = pd.DataFrame(index=df.index)

    # Spread close - open
    df_feat['spread_close_open'] = df['close'] - df['open']

    # Ratio high / low
    df_feat['ratio_high_low'] = df['high'] / df['low']

    # Amplitud relativa
    df_feat['range_relative'] = (df['high'] - df['low']) / df['close']

    # Close / high
    df_feat['close_over_high'] = df['close'] / df['high']

    # Close / low
    df_feat['close_over_low'] = df['close'] / df['low']

    return df_feat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    md = config["market_data"]

    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )

    df = pd.read_csv(data_path)
    log.info(f"[cyan]📊 Calculando relational features...[/cyan]")

    df_feat = generate_relational_features(df)

    output_file = "core/features/shared/temp/relational_features.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_feat.to_csv(output_file, index=False)

    log.info(f"[green]✅ Features relational guardadas en {output_file} ({df_feat.shape[1]} columnas)[/green]")


if __name__ == "__main__":
    main()
