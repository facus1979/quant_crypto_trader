# 🧠 Quant Crypto Trader

Sistema algorítmico de trading para criptomonedas, modular, robusto y extensible.

## 🎯 Objetivo General

Desarrollar un sistema algorítmico de trading para criptomonedas que permita:

- **Generación de señales** basadas en indicadores técnicos y modelos de Machine Learning
- **Evaluación de estrategias** mediante backtesting riguroso
- **Ejecución de estrategias** en paper trading o live trading
- **Adaptabilidad futura** con fuentes de datos exógenas
- **Experimentación estructurada** mediante configuración YAML

## 🧱 Arquitectura del Sistema

### Componentes Modulares

| Módulo | Rol Principal |
|--------|---------------|
| **Data Layer** | Adquisición, limpieza y estructuración de datos históricos y live (CCXT) |
| **Feature Engineering** | Cálculo de indicadores, creación de alphas, normalización |
| **Modeling Layer** | Entrenamiento y predicción con modelos ML (XGBoost, etc.) |
| **Signal Generator** | Aplicación del modelo para generar señales de compra/venta |
| **Strategy Layer** | Traducción de señales en decisiones de trading (reglas, pesos, thresholds) |
| **Backtesting Engine** | Simulación histórica con métricas de rendimiento y riesgo |
| **Execution Layer** | Ejecución en tiempo real (paper o live) con control de riesgo |
| **Analysis & Monitoring** | Métricas, visualizaciones, reportes, logs y alertas |

## 🔁 Flujos Operativos

### 🧪 Flujo de Experimentación (Offline)
Para desarrollo y validación de estrategias:

```
[ DATA HISTÓRICA ]
        ↓
[ FEATURE ENGINEERING ]
        ↓
[ MODEL TRAINING ]
        ↓
[ SIGNAL GENERATION ]
        ↓
[ STRATEGY LOGIC ]
        ↓
[ BACKTESTING ENGINE ]
        ↓
[ ANALYSIS & REPORT ]
```

### 🚀 Flujo de Ejecución (Realtime)
Para operar en tiempo real (paper o real):

```
[ LIVE DATA FEED ]
        ↓
[ FEATURE ENGINEERING ]
        ↓
[ SIGNAL GENERATION (con modelo entrenado) ]
        ↓
[ STRATEGY LOGIC ]
        ↓
[ EXECUTION ENGINE (paper_broker / live_broker) ]
        ↓
[ MONITORING & LOGGING ]
```

## ⚙️ Configuración

El sistema utiliza archivos YAML para definir cada experimento o configuración de producción, incluyendo:

- Dataset y timeframe
- Features a utilizar
- Modelo y parámetros
- Configuración de estrategia
- Parámetros de ejecución
- Configuración de análisis y logging

## 📁 Estructura del Proyecto

```
quant_crypto_trader/
├── config/                 # Configuración YAML de experimentos
├── core/
│   ├── data/              # Fetcher, cleaner, preprocessor
│   ├── features/          # Técnicos, personalizados, futuros NLP
│   ├── models/            # Modelos ML, base classes
│   ├── signals/           # Signal generator
│   ├── strategy/          # Rule-based y ML-based strategies
│   ├── backtest/          # Engine y métricas
│   ├── execution/         # Paper/live broker, kill switch
│   └── analysis/          # Visualización, reporter, logs
├── experiments/           # Scripts orquestadores
├── models/               # Modelos serializados
├── logs/                 # Logs estructurados
├── reports/              # Análisis generados
├── notebooks/            # Exploración y análisis
└── requirements.txt
```
config/: configuración centralizada en archivos YAML para experimentos.

core/: núcleo del sistema, con submódulos que implementan cada parte del pipeline.

experiments/: scripts que ejecutan experimentos usando la configuración YAML.

utils/: funciones utilitarias como logging y carga de configuración.

tests/: carpeta vacía para futuros tests unitarios/integración.

core/
| Subcarpeta   | Rol                                                                           | Relación con README       |
| ------------ | ----------------------------------------------------------------------------- | ------------------------- |
| `data/`      | Carga, validación y limpieza de datos históricos o en vivo.                   | **Data Layer**            |
| `features/`  | Cálculo de indicadores técnicos, normalización, generación de factores alpha. | **Feature Engineering**   |
| `models/`    | Entrenamiento, guardado y predicción de modelos ML.                           | **Modeling Layer**        |
| `signals/`   | Generación de señales de compra/venta a partir del modelo.                    | **Signal Generator**      |
| `strategy/`  | Traducción de señales en órdenes con lógica de posición, SL/TP, sizing.       | **Strategy Layer**        |
| `backtest/`  | Simulación histórica de la estrategia con métricas de performance.            | **Backtesting Engine**    |
| `execution/` | Ejecución de órdenes en broker real o paper trading.                          | **Execution Layer**       |
| `analysis/`  | Reportes, gráficos, métricas, visualizaciones y logs.                         | **Analysis & Monitoring** |



## 🚀 Inicio Rápido

### Requisitos
```bash
pip install -r requirements.txt
```

### Ejecución
El proyecto está diseñado para comenzar con:

1. **Flujo funcional completo**: `data → model → signal → backtest`
2. **Entorno de paper trading**: `start_paper_trading.py`
3. **Configuración reproducible**: archivos `.yaml`

## 🔌 Extensibilidad Futura

El sistema está diseñado desde el inicio para incorporar:

- **Modelos adaptativos**: regime switching, meta-learning, Reinforcement Learning
- **Fuentes exógenas**: noticias, eventos macro, datos on-chain
- **Auto-retraining**: pipelines autoevaluados
- **Estrategias multi-activo y multi-modelo**
- **NLP y embeddings** de contexto financiero

## 🛠️ Desarrollo

### Filosofía de Diseño
- **Modularidad**: cada componente es independiente y reemplazable
- **Extensibilidad**: arquitectura preparada para crecer sin refactorización
- **Reproducibilidad**: configuración versionada y determinística
- **Escalabilidad**: desde experimentos simples hasta sistemas complejos

### Contribución
El proyecto está estructurado para facilitar:
- Desarrollo iterativo de componentes
- Testing unitario por módulo
- Integración continua de nuevas estrategias
- Experimentación controlada y documentada

