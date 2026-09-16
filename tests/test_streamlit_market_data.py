import unittest
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from app.market_data import fetch_real_data, format_price, quote_currency, to_display_frame


class TestQuoteCurrency(unittest.TestCase):
    def test_us_and_european_symbols(self):
        self.assertEqual(quote_currency("AAPL"), "USD")
        self.assertEqual(quote_currency("SAP.DE"), "EUR")
        self.assertEqual(quote_currency("7203.T"), "JPY")
        self.assertEqual(quote_currency("0700.HK"), "HKD")
        self.assertEqual(quote_currency("600519"), "CNY")

    def test_format_price_uses_native_currency(self):
        self.assertEqual(format_price(319.97, "AAPL"), "319.97 $")
        self.assertEqual(format_price(274.90, "APC.DE"), "274.90 €")
        self.assertEqual(format_price(-2.59, "AAPL", signed=True), "-2.59 $")


class TestDisplayFrame(unittest.TestCase):
    def test_renames_ohlc_columns_and_indexes_by_date(self):
        raw = pd.DataFrame(
            {
                "date": ["2026-09-04", "2026-09-05"],
                "open": [328.30, 320.00],
                "high": [328.93, 321.00],
                "low": [317.86, 318.00],
                "close": [319.97, 320.50],
                "volume": [10, 11],
            }
        )
        out = to_display_frame(raw)
        self.assertListEqual(list(out.columns), ["Eröffnung", "Hoch", "Tief", "Schlusskurs", "Volumen"])
        self.assertAlmostEqual(float(out["Schlusskurs"].iloc[-1]), 320.50)


class TestFetchRealData(unittest.TestCase):
    def test_uses_manager_and_rejects_empty(self):
        manager = MagicMock()
        manager.get_daily_data.return_value = (
            pd.DataFrame(
                {
                    "date": ["2026-09-04"],
                    "open": [328.30],
                    "high": [328.93],
                    "low": [317.86],
                    "close": [319.97],
                    "volume": [1],
                }
            ),
            "YfinanceFetcher",
        )
        df, source = fetch_real_data("AAPL", days=5, manager=manager)
        manager.get_daily_data.assert_called_once_with("AAPL", days=5)
        self.assertEqual(source, "YfinanceFetcher")
        self.assertAlmostEqual(float(df["Schlusskurs"].iloc[-1]), 319.97)

    def test_raises_when_manager_returns_empty(self):
        manager = MagicMock()
        manager.get_daily_data.return_value = (pd.DataFrame(), "YfinanceFetcher")
        with self.assertRaises(RuntimeError):
            fetch_real_data("AAPL", manager=manager)


class TestStreamlitAppRenders(unittest.TestCase):
    """Regression: ``app/app.py`` must not self-import and render twice.

    ``streamlit run app/app.py`` puts the script directory on ``sys.path``, where
    ``app.py`` shadows the ``app`` package. A ``from app.market_data import ...``
    inside the script therefore re-executed the whole file as the module ``app``,
    registering every widget twice and raising ``StreamlitDuplicateElementId``.
    """

    def test_app_runs_without_exceptions(self):
        try:
            from streamlit.testing.v1 import AppTest
        except ImportError:  # pragma: no cover - streamlit is a declared dependency
            self.skipTest("streamlit is not installed")

        app_path = Path(__file__).resolve().parents[1] / "app" / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30)
        app.run()

        self.assertEqual([], [str(exc.value) for exc in app.exception])
        self.assertEqual(
            ["Aktien-Symbol", "Vergleichs-Symbole (kommagetrennt)"],
            sorted(text_input.label for text_input in app.text_input),
        )


if __name__ == "__main__":
    unittest.main()
