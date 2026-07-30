# 📈 Tägliche Aktienanalyse

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![W&B](https://img.shields.io/badge/W%26B-Tracking-orange.svg)](https://wandb.ai/)

**LLM-gestützte tägliche Aktienanalyse** — Automatisierte technische Analyse mit Trend-Trading, Multi-Agent-Orchestrierung und Entscheidungssignalen.

## 📋 Beschreibung

Ein umfassendes System zur täglichen Aktienanalyse, das technische Indikatoren, LLM-basierte Reasoning-Agents und eine service-orientierte Architektur kombiniert. Das System analysiert Aktien nach strengen Trend-Trading-Kriterien (MA5>MA10>MA20), generiert Kauf-/Verkaufssignale und trackt die Entscheidungsqualität über Zeit.

- **Trend-Trading-Engine** — MA-basierte Trendanalyse mit 7 Trend-Status-Leveln
- **Multi-Agent-System** — Orchestrierte LLM-Agents für verschiedene Analyseschritte
- **Entscheidungssignale** — Strukturierte Buy/Sell/Hold-Signale mit Confidence-Scores
- **Datenquellen** — Alpha Vantage, AKShare, LongBridge für Marktdaten

## ✨ Features

- 📊 **Technische Analyse** — MA5/MA10/MA20, Volumenanalyse, Trend-Status
- 🤖 **LLM-Agenten** — Multi-Agent-Orchestrierung mit LiteLLM-Routing
- 🎯 **Entscheidungssignale** — Strong Buy → Strong Sell mit Sniper-Punkte-System
- 📡 **Multi-Source-Daten** — Alpha Vantage, AKShare (A-Shares), LongBridge
- 🔔 **Alert-System** — Schwellwert-basierte Benachrichtigungen
- 📋 **History-Tracking** — Vergleich historischer Analysen und Signal-Outcomes
- 🖥️ **WebUI** — Streamlit-Frontend für Analyse und Konfiguration
- 🧪 **Umfangreiche Tests** — 50+ Testdateien für alle Services und Komponenten

## 🚀 Installation

```bash
# Repository klonen
git clone https://github.com/mark-baumann/taegliche-aktienanalyse.git
cd taegliche-aktienanalyse

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# API-Keys konfigurieren
export ALPHA_VANTAGE_API_KEY="your_key"
export LITELLM_API_KEY="your_key"
```

## 🎮 Nutzung

### WebUI starten

```bash
streamlit run src/webui_frontend.py
```

### Analyse ausführen

```python
from src.stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze("AAPL")
print(f"Signal: {result.signal}, Confidence: {result.confidence}")
```

### Tests

```bash
pytest tests/ -v
```

## 🏗️ Tech-Stack

| Komponente | Technologie |
|---|---|
| **Sprache** | Python 3.10+ |
| **Analyse** | Pandas, NumPy |
| **LLM** | LiteLLM (Multi-Provider-Routing) |
| **Datenquellen** | Alpha Vantage, AKShare, LongBridge |
| **UI** | Streamlit |
| **Tracking** | Weights & Biases |
| **Testing** | pytest |

## 📁 Projektstruktur

```
taegliche-aktienanalyse/
├── src/
│   ├── stock_analyzer.py           # Trend-Trading-Engine
│   ├── webui_frontend.py           # Streamlit-WebUI
│   ├── storage.py                  # Datenpersistenz
│   ├── config.py                   # Konfiguration
│   ├── services/
│   │   ├── decision_signal_service.py
│   │   ├── intelligence_service.py
│   │   ├── history_service.py
│   │   ├── alert_worker.py
│   │   └── ...
│   ├── utils/
│   │   ├── sniper_points.py
│   │   ├── data_processing.py
│   │   └── ...
│   └── schemas/
├── tests/                          # 50+ Testdateien
│   ├── test_stock_analyzer.py
│   ├── test_agent_pipeline.py
│   ├── test_alert_worker.py
│   └── ...
└── wandb_utils.py
```

## 👤 Autor

**Mark Baumann** — [GitHub](https://github.com/mark-baumann)

---

*Für Fragen oder Beiträge: Issue erstellen oder Pull Request öffnen.*
