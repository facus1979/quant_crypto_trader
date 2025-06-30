import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import argparse
import pandas as pd
from ta import trend, momentum, volatility, volume
from utils.config_loader import load_yaml
from core.features.shared.utils import build_data_path
from utils.logger import log


def generate_ohlcv_features(df: pd.DataFrame, indicators: list) -> pd.DataFrame:
    df = df.copy()

    if 'rsi' in indicators:
        df['rsi_14'] = momentum.RSIIndicator(close=df['close']).rsi()
    if 'ema' in indicators:
        df['ema_10'] = trend.EMAIndicator(close=df['close'], window=10).ema_indicator()
    if 'sma' in indicators:
        df['sma_10'] = trend.SMAIndicator(close=df['close'], window=10).sma_indicator()
    if 'macd' in indicators:
        macd = trend.MACD(close=df['close'])
        df['macd_line'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
    if 'bollinger' in indicators:
        bb = volatility.BollingerBands(close=df['close'])
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
    if 'williams_r' in indicators:
        df['williams_r'] = momentum.WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close']).williams_r()
    if 'stoch' in indicators:
        stoch = momentum.StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
    if 'atr' in indicators:
        df['atr_14'] = volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
    if 'adx' in indicators:
        df['adx'] = trend.ADXIndicator(high=df['high'], low=df['low'], close=df['close']).adx()
    if 'obv' in indicators:
        df['obv'] = volume.OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    if 'cci' in indicators:
        df['cci'] = trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close']).cci()
    if 'roc' in indicators:
        df['roc'] = momentum.ROCIndicator(close=df['close']).roc()

    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    md = config["market_data"]
    ohlcv_cfg = config["features"]["ohlcv"]
    indicators = ohlcv_cfg.get("indicators", [])

    if indicators == "all":
        indicators = [
            "rsi", "ema", "sma", "macd", "bollinger", "williams_r", "stoch",
            "atr", "adx", "obv", "cci", "roc"
        ]

    data_path = build_data_path(
        symbol=md["symbol"],
        interval=md["interval"],
        start_date=md["start_date"],
        end_date=md["end_date"],
        provider=md["provider"]
    )

    df = pd.read_csv(data_path)
    log.info(f"[cyan]📈 Calculando features OHLCV...[/cyan]")

    df_feat = generate_ohlcv_features(df, indicators)

    output_file = "core/features/shared/temp/ohlcv_features.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_feat.to_csv(output_file, index=False)

    log.info(f"[green]✅ Features OHLCV guardadas en {output_file} ({df_feat.shape[1]} columnas)[/green]")


if __name__ == "__main__":
    main()
