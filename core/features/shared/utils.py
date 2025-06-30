from pathlib import Path
import pandas as pd


def build_data_path(symbol: str, interval: str, start_date: str, end_date: str, provider: str) -> Path:
    symbol_clean = symbol.replace("/", "")
    folder = Path(f"core/features/shared/data/{symbol_clean}/{interval}")
    file_name = f"{start_date}_to_{end_date}_{provider}.csv"
    return folder / file_name


def merge_feature_files(folder: Path) -> pd.DataFrame:
    dfs = []
    for file in folder.glob("*_features.csv"):
        df = pd.read_csv(file)
        dfs.append(df)
    return pd.concat(dfs, axis=1)
