"""
auto_selector.py

Realiza la selección automática de features sobre un DataFrame X_full.csv,
usando distintos modelos y métricas, y genera:
  - X_selected.csv  (dataset con el subset de features elegido)
  - metadata.json   (ranking, parámetros y tiempos)

Para usarlo como un feature más, se invoca desde run_feature_pipeline.py
bajo el env "selection", exactamente igual que los demás envs de features.
"""

import sys
import os

# -------------------------------------------------------------------
# 1) Aseguramos que el root del proyecto quede en sys.path
# -------------------------------------------------------------------
# __file__  = .../core/features/selection/auto_selector.py
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__),  # .../selection
                 os.pardir, os.pardir, os.pardir, )  # sube tres niveles a la raíz
)
sys.path.insert(0, project_root)

# -------------------------------------------------------------------
# 2) Importamos todo lo que necesitamos
# -------------------------------------------------------------------
import argparse
import time
import pandas as pd
from pathlib import Path

from utils.config_loader import load_yaml
from utils.logger import log

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    make_scorer,
    roc_auc_score,
    f1_score,
    accuracy_score
)
import numpy as np
import itertools
import json
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# -------------------------------------------------------------------
# 3) Funciones auxiliares
# -------------------------------------------------------------------
def sharpe_ratio(y_true, y_pred):
    """
    Sharpe ratio aproximado: E[retorno] / std[retorno]
    Aquí asumimos y_pred como series de 'retornos esperados'
    y y_true como retornos reales.
    """
    dr = np.array(y_true) * np.array(y_pred)  # señal * retorno
    if dr.std() == 0:
        return 0.0
    return dr.mean() / dr.std()

# scikit-learn scorers
SCORERS = {
    "roc_auc": make_scorer(roc_auc_score),
    "f1":      make_scorer(f1_score),
    "accuracy":make_scorer(accuracy_score),
    "sharpe":  make_scorer(sharpe_ratio)
}

MODELS = {
    "xgboost":          XGBClassifier,
    "random_forest":    RandomForestClassifier,
    "logistic_regression": LogisticRegression
}

# -------------------------------------------------------------------
# 4) Lógica principal
# -------------------------------------------------------------------
def run_auto_feature_selection(df_full: pd.DataFrame, cfg: dict):
    """
    df_full: DataFrame con TODAS las features más la columna 'target'
    cfg:     dict con la sección 'selection' del YAML
    """
    start_time = time.time()
    log.info("🧠 [selection] Cargando configuración...")
    top_k = cfg["top_k"]
    models = cfg["models"]
    metrics = cfg["metrics"]
    cv_splits = cfg.get("cv_splits", 5)

    # Separamos X y y
    if "target" not in df_full.columns:
        log.error("🛑 [selection] No encontré la columna 'target' en X_full.")
        sys.exit(1)
    y = df_full["target"]
    X = df_full.drop(columns=["target"])

    # Eliminamos columnas no numéricas
    valid_types = ["int64", "float64", "bool", "category"]
    non_numeric_cols = [col for col in X.columns if X[col].dtype.name not in valid_types]

    if non_numeric_cols:
        log.warning(f"⚠️ [selection] Eliminando columnas no numéricas: {non_numeric_cols}")
        X = X.drop(columns=non_numeric_cols)

    # Eliminamos filas con NaN
    nan_rows = X.isnull().any(axis=1).sum()
    if nan_rows > 0:
        log.warning(f"⚠️ [selection] Eliminando {nan_rows} filas con NaN antes de entrenamiento")
        X = X.dropna().reset_index(drop=True)
        y = y.loc[X.index].reset_index(drop=True)


    log.info(f"🔢 [selection] {X.shape[1]} features detectadas, {len(y)} muestras")

    best_score = -np.inf
    best_combo = None
    best_subset = None
    ranking = []

    # iteramos combinaciones modelo + métrica
    for model_name, metric_name in itertools.product(models, metrics):
        log.info(f"🔄 [selection] Probando {model_name} + {metric_name} ...")
        ModelCls = MODELS[model_name]
        params = cfg.get(f"{model_name}_params", {})
        model = make_pipeline(
            StandardScaler(),
            ModelCls(**params)
        )


        scorer = SCORERS[metric_name]
        # cross-validation
        scores = cross_val_score(
            model, X, y,
            cv=cv_splits,
            scoring=scorer,
            n_jobs=-1
        )
        mean_score = scores.mean()
        log.info(f"    • CV {metric_name}: {mean_score:.4f}")

        ranking.append({
            "model": model_name,
            "metric": metric_name,
            "score": mean_score
        })

        if mean_score > best_score:
            best_score = mean_score
            best_combo = (model_name, metric_name)

    # elegimos mejor combo
    model_name, metric_name = best_combo
    log.info(f"✅ [selection] Mejor: {model_name} + {metric_name} = {best_score:.4f}")


    # re-entrenamos con todo el dataset y extraemos importancias
    ModelCls = MODELS[model_name]
    clf = ModelCls()
    clf.fit(X, y)

    importances = None
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
    elif hasattr(clf, "coef_"):
        importances = np.abs(clf.coef_).ravel()
    else:
        log.warning("⚠️ [selection] El modelo no expone importancias ni coeficientes.")
        importances = np.ones(X.shape[1]) / X.shape[1]

    feat_imp = pd.DataFrame({
        "feature": X.columns,
        "importance": importances
    }).sort_values("importance", ascending=False)

    # seleccionamos top_k
    top_features = feat_imp["feature"].tolist()[:top_k]
    log.info(f"✂️ [selection] Seleccionando top {top_k} features")

    df_selected = df_full[top_features + ["target"]].copy()

    metadata = {
        "best_model": model_name,
        "best_metric": metric_name,
        "best_score": best_score,
        "top_features": top_features,
        "ranking": ranking,
        "elapsed_time_sec": time.time() - start_time
    }
    return df_selected, metadata

# -------------------------------------------------------------------
# 5) CLI
# -------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Selecciona automáticamente las features de X_full.csv"
    )
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="path al YAML de configuración (temp_config.yaml)"
    )
    args = parser.parse_args()

    # cargo config
    cfg = load_yaml(args.config)["selection"]
    # cargo X_full generado por merge
    df_full = pd.read_csv(cfg["x_full_path"])
    log.info("🧠 [selection] Iniciando selección automática de features...")

    df_sel, meta = run_auto_feature_selection(df_full, cfg)

    # guardo resultados
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    df_sel.to_csv(out_dir / "X_selected.csv", index=False)
    # metadata.json
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Imprimimos un resumen amigable al log
    log.info("📊 [selection] Resumen del resultado:")
    log.info(f"    Mejor modelo : {meta['best_model']}")
    log.info(f"    Mejor métrica: {meta['best_metric']}")
    log.info(f"    Mejor score  : {meta['best_score']:.4f}")
    log.info(f"    Top features : {', '.join(meta['top_features'])}")
    log.info("✅ [selection] Selección completada")


if __name__ == "__main__":
    main()
