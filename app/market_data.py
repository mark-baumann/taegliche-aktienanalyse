from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

DISPLAY_COLUMNS = {
    "date": "Datum",
    "open": "Eröffnung",
    "high": "Hoch",
    "low": "Tief",
    "close": "Schlusskurs",
    "volume": "Volumen",
}

_EUR_SUFFIXES = (
    ".DE",
    ".F",
    ".PA",
    ".AS",
    ".BR",
    ".MI",
    ".MC",
    ".LS",
    ".HE",
    ".ST",
    ".OL",
    ".IR",
    ".VI",
)
_CURRENCY_SYMBOLS = {
    "EUR": "€",
    "USD": "$",
    "GBP": "£",
    "HKD": "HK$",
    "JPY": "¥",
    "CNY": "¥",
    "KRW": "₩",
    "TWD": "NT$",
}


def quote_currency(symbol: str) -> str:
    code = (symbol or "").strip().upper()
    if not code:
        return "USD"
    if code.endswith(_EUR_SUFFIXES):
        return "EUR"
    if code.endswith(".L"):
        return "GBP"
    if code.endswith(".HK") or (code.startswith("HK") and code[2:].isdigit()):
        return "HKD"
    if code.endswith(".T"):
        return "JPY"
    if code.endswith((".KS", ".KQ")):
        return "KRW"
    if code.endswith((".TW", ".TWO")):
        return "TWD"
    if code.endswith((".SS", ".SZ", ".BJ")):
        return "CNY"
    if code.isdigit() and len(code) == 6:
        return "CNY"
    return "USD"


def currency_symbol(currency_code: str) -> str:
    return _CURRENCY_SYMBOLS.get(currency_code, currency_code)


def format_price(value: float, symbol: str, signed: bool = False) -> str:
    code = quote_currency(symbol)
    number = f"{float(value):+.2f}" if signed else f"{float(value):.2f}"
    return f"{number} {currency_symbol(code)}"


def to_display_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise RuntimeError("Keine Kursdaten gefunden")

    out = df.copy()
    if "date" not in out.columns:
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index()
            out = out.rename(columns={out.columns[0]: "date"})
        else:
            raise RuntimeError("Kursdaten enthalten keine Datumsspalte")

    out = out.rename(columns={src: dst for src, dst in DISPLAY_COLUMNS.items() if src in out.columns})
    keep = [col for col in ("Datum", "Eröffnung", "Hoch", "Tief", "Schlusskurs", "Volumen") if col in out.columns]
    out = out[keep]
    out["Datum"] = pd.to_datetime(out["Datum"])
    return out.set_index("Datum")


@lru_cache(maxsize=1)
def _default_manager() -> Any:
    from data_provider.base import DataFetcherManager

    return DataFetcherManager()


def fetch_real_data(symbol: str, days: int = 90, manager: Any | None = None) -> tuple[pd.DataFrame, str]:
    ticker = (symbol or "").strip().upper()
    if not ticker:
        raise RuntimeError("Kein Aktien-Symbol angegeben")

    source_manager = manager if manager is not None else _default_manager()
    df, source = source_manager.get_daily_data(ticker, days=days)
    if df is None or df.empty:
        raise RuntimeError(f"Keine Kursdaten für {ticker} gefunden")
    return to_display_frame(df), source or "unbekannt"
