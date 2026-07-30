"""
Tägliche Aktienanalyse — Streamlit App
=======================================
Web-Oberfläche für Aktienkurs-Analyse mit Charts und Kennzahlen.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────
# Konfiguration
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tägliche Aktienanalyse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Demo-Daten Generator
# ──────────────────────────────────────────────────────────────

def generate_stock_data(symbol: str, days: int = 90) -> pd.DataFrame:
    """Erzeugt realistische historische Kursdaten."""
    np.random.seed(hash(symbol) % 2**31)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq="B")
    
    # Basis-Preis je nach Symbol
    base_prices = {
        "AAPL": 185.0, "MSFT": 420.0, "GOOGL": 175.0, "AMZN": 195.0,
        "TSLA": 250.0, "NVDA": 120.0, "META": 520.0, "SAP.DE": 190.0,
        "SIE.DE": 180.0, "VOW3.DE": 115.0, "DAX": 18500.0, "BTC-USD": 65000.0,
    }
    base = base_prices.get(symbol, 100.0)
    volatility = 0.02 if "DE" in symbol else 0.018
    
    returns = np.random.normal(0.0003, volatility, len(date_range))
    prices = base * np.exp(np.cumsum(returns))
    
    # OHLC
    df = pd.DataFrame({
        "Datum": date_range,
        "Schlusskurs": prices,
    })
    
    daily_vol = prices * volatility * 0.8
    df["Eröffnung"] = df["Schlusskurs"].shift(1).fillna(prices[0])
    df["Hoch"] = df[["Schlusskurs", "Eröffnung"]].max(axis=1) + np.abs(np.random.normal(0, daily_vol * 0.5, len(df)))
    df["Tief"] = df[["Schlusskurs", "Eröffnung"]].min(axis=1) - np.abs(np.random.normal(0, daily_vol * 0.5, len(df)))
    df["Volumen"] = np.random.randint(1_000_000, 50_000_000, len(df))
    
    return df.set_index("Datum")


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Berechnet technische Indikatoren."""
    close = df["Schlusskurs"]
    
    # SMA
    df["SMA_20"] = close.rolling(window=20).mean()
    df["SMA_50"] = close.rolling(window=50).mean()
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Bollinger Bänder
    df["BB_Mitte"] = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    df["BB_Oben"] = df["BB_Mitte"] + 2 * bb_std
    df["BB_Unten"] = df["BB_Mitte"] - 2 * bb_std
    
    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema_12 - ema_26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Histogramm"] = df["MACD"] - df["MACD_Signal"]
    
    return df


def analyze_stock(df: pd.DataFrame) -> dict:
    """Fundamentale Analyse-Kennzahlen."""
    close = df["Schlusskurs"]
    current = close.iloc[-1]
    
    # Renditen
    returns = {}
    for period, days in [("1 Woche", 5), ("1 Monat", 21), ("3 Monate", 63), ("6 Monate", 126), ("1 Jahr", 252)]:
        if len(close) > days:
            past = close.iloc[-days-1] if len(close) > days + 1 else close.iloc[0]
            ret = (current - past) / past * 100
            returns[period] = round(ret, 2)
    
    # Volatilität
    daily_returns = close.pct_change().dropna()
    volatility = round(float(daily_returns.std() * np.sqrt(252) * 100), 2)
    
    # Max Drawdown
    rolling_max = close.expanding().max()
    drawdown = (close - rolling_max) / rolling_max
    max_drawdown = round(float(drawdown.min() * 100), 2)
    
    # Sharpe Ratio (vereinfacht)
    sharpe = round(float(daily_returns.mean() / daily_returns.std() * np.sqrt(252)), 2) if daily_returns.std() > 0 else 0
    
    return {
        "Aktueller Kurs": f"{current:.2f} €",
        "Volatilität (annual.)": f"{volatility}%",
        "Max. Drawdown": f"{max_drawdown}%",
        "Sharpe Ratio": f"{sharpe}",
        **{f"Rendite {k}": f"{v}%" for k, v in returns.items()},
    }


# ──────────────────────────────────────────────────────────────
# Streamlit UI
# ──────────────────────────────────────────────────────────────

st.title("📈 Tägliche Aktienanalyse")
st.markdown("**Aktienkurse, technische Indikatoren und Performance-Analyse**")

# ── Seitenleiste ──────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Konfiguration")
    
    symbol = st.text_input(
        "Aktien-Symbol",
        value="AAPL",
        placeholder="z.B. AAPL, MSFT, SAP.DE, TSLA...",
        help="Geben Sie das Börsensymbol ein (z.B. AAPL für Apple).",
    ).upper()
    
    st.divider()
    
    st.markdown("### 📅 Zeitraum")
    period_options = {
        "1 Monat": 21,
        "3 Monate": 63,
        "6 Monate": 126,
        "1 Jahr": 252,
        "2 Jahre": 504,
    }
    selected_period = st.selectbox("Zeitraum", options=list(period_options.keys()), index=2)
    days = period_options[selected_period]
    
    st.divider()
    
    st.markdown("### 📊 Indikatoren")
    show_sma = st.checkbox("Gleitende Durchschnitte (SMA)", value=True)
    show_bollinger = st.checkbox("Bollinger Bänder", value=True)
    show_macd = st.checkbox("MACD", value=True)
    show_rsi = st.checkbox("RSI", value=True)
    show_volume = st.checkbox("Volumen", value=False)
    
    st.divider()
    
    if st.button("🔄 Analyse starten", type="primary", use_container_width=True):
        st.session_state.analysis_triggered = True
    else:
        if "analysis_triggered" not in st.session_state:
            st.session_state.analysis_triggered = False

# ── Hauptbereich ──────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Kurs-Chart",
    "📈 Technische Analyse",
    "📋 Kennzahlen",
    "🔍 Vergleich",
])

# ── Tab 1: Kurs-Chart ────────────────────────────────────────

with tab1:
    if st.session_state.analysis_triggered:
        with st.spinner(f"📡 Lade Kursdaten für {symbol}..."):
            df = generate_stock_data(symbol, days=days)
            df = calculate_indicators(df)
            st.session_state.stock_data = df
            st.session_state.current_symbol = symbol
        
        st.success(f"✅ Daten für **{symbol}** geladen — {len(df)} Handelstage")
        
        # Haupt-Chart
        st.markdown(f"### 📊 {symbol} — Kursverlauf ({selected_period})")
        
        chart_data = pd.DataFrame({"Schlusskurs": df["Schlusskurs"]})
        
        if show_sma:
            chart_data["SMA 20"] = df["SMA_20"]
            chart_data["SMA 50"] = df["SMA_50"]
        
        if show_bollinger:
            chart_data["BB Oben"] = df["BB_Oben"]
            chart_data["BB Unten"] = df["BB_Unten"]
        
        st.line_chart(chart_data, use_container_width=True)
        
        # Kurs-Info
        col1, col2, col3, col4 = st.columns(4)
        current = df["Schlusskurs"].iloc[-1]
        prev = df["Schlusskurs"].iloc[-2]
        change = current - prev
        change_pct = (change / prev) * 100
        
        with col1:
            st.metric("Aktueller Kurs", f"{current:.2f} €", delta=f"{change:+.2f} €")
        with col2:
            st.metric("Tageshoch", f"{df['Hoch'].iloc[-1]:.2f} €")
        with col3:
            st.metric("Tagestief", f"{df['Tief'].iloc[-1]:.2f} €")
        with col4:
            st.metric("Veränderung", f"{change_pct:+.2f}%")
        
        # Volumen
        if show_volume:
            st.markdown("### 📊 Handelsvolumen")
            st.bar_chart(df["Volumen"], use_container_width=True)
    else:
        st.info("👈 Geben Sie ein Aktien-Symbol ein und klicken Sie auf **Analyse starten**.")
        st.markdown("### 💡 Beispiel-Chart (AAPL)")
        demo_df = generate_stock_data("AAPL", days=126)
        demo_df = calculate_indicators(demo_df)
        st.line_chart(demo_df["Schlusskurs"], use_container_width=True)
        st.caption("Beispieldaten — starten Sie eine echte Analyse für aktuelle Kurse.")

# ── Tab 2: Technische Analyse ─────────────────────────────────

with tab2:
    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        symbol = st.session_state.current_symbol
        
        if show_rsi:
            st.markdown("### 📉 RSI (Relative Strength Index)")
            rsi_df = pd.DataFrame({"RSI": df["RSI"]})
            st.line_chart(rsi_df, use_container_width=True)
            
            # RSI Interpretation
            last_rsi = df["RSI"].iloc[-1]
            if last_rsi > 70:
                st.warning(f"⚠️ RSI = {last_rsi:.1f} — **Überkauft** (über 70)")
            elif last_rsi < 30:
                st.success(f"✅ RSI = {last_rsi:.1f} — **Überverkauft** (unter 30)")
            else:
                st.info(f"ℹ️ RSI = {last_rsi:.1f} — Neutraler Bereich")
        
        if show_macd:
            st.markdown("### 📊 MACD")
            macd_df = pd.DataFrame({
                "MACD": df["MACD"],
                "Signal": df["MACD_Signal"],
                "Histogramm": df["MACD_Histogramm"],
            })
            st.line_chart(macd_df[["MACD", "Signal"]], use_container_width=True)
            st.bar_chart(macd_df["Histogramm"], use_container_width=True)
            
            # MACD Signal
            last_macd = df["MACD"].iloc[-1]
            last_signal = df["MACD_Signal"].iloc[-1]
            if last_macd > last_signal:
                st.success("📈 MACD über Signal-Linie — **Bullisches Signal**")
            else:
                st.warning("📉 MACD unter Signal-Linie — **Bärisches Signal**")
        
        if show_bollinger:
            st.markdown("### 🎯 Bollinger Bänder")
            bb_df = pd.DataFrame({
                "Schlusskurs": df["Schlusskurs"],
                "BB Mitte": df["BB_Mitte"],
                "BB Oben": df["BB_Oben"],
                "BB Unten": df["BB_Unten"],
            })
            st.line_chart(bb_df, use_container_width=True)
            
            # Position in Bändern
            last_close = df["Schlusskurs"].iloc[-1]
            bb_oben = df["BB_Oben"].iloc[-1]
            bb_unten = df["BB_Unten"].iloc[-1]
            bb_range = bb_oben - bb_unten
            if bb_range > 0:
                position = (last_close - bb_unten) / bb_range * 100
                st.progress(int(position) / 100, text=f"Position im Band: {position:.0f}%")
    else:
        st.info("Führen Sie zuerst eine Analyse aus (Tab 1).")

# ── Tab 3: Kennzahlen ─────────────────────────────────────────

with tab3:
    if "stock_data" in st.session_state:
        df = st.session_state.stock_data
        symbol = st.session_state.current_symbol
        stats = analyze_stock(df)
        
        st.markdown(f"### 📋 Fundamentaldaten — {symbol}")
        
        cols = st.columns(3)
        for i, (key, value) in enumerate(stats.items()):
            with cols[i % 3]:
                st.metric(label=key, value=value)
        
        st.divider()
        
        # Rendite-Tabelle
        st.markdown("### 📊 Rendite-Übersicht")
        returns_data = {k: float(v.replace("%", "")) for k, v in stats.items() if k.startswith("Rendite")}
        if returns_data:
            df_returns = pd.DataFrame({
                "Zeitraum": list(returns_data.keys()),
                "Rendite (%)": list(returns_data.values()),
            })
            st.bar_chart(df_returns.set_index("Zeitraum"), use_container_width=True)
        
        # Tägliche Renditen
        st.markdown("### 📈 Tägliche Renditen")
        daily_ret = df["Schlusskurs"].pct_change().dropna() * 100
        st.line_chart(daily_ret, use_container_width=True)
    else:
        st.info("Führen Sie zuerst eine Analyse aus (Tab 1).")

# ── Tab 4: Vergleich ──────────────────────────────────────────

with tab4:
    st.markdown("### 🔍 Aktien-Vergleich")
    
    compare_symbols = st.text_input(
        "Vergleichs-Symbole (kommagetrennt)",
        value="MSFT, GOOGL",
        placeholder="z.B. MSFT, GOOGL, AMZN",
    )
    
    if st.button("📊 Vergleichen", type="primary"):
        symbols = [s.strip().upper() for s in compare_symbols.split(",") if s.strip()]
        
        if "stock_data" in st.session_state:
            symbols = [st.session_state.current_symbol] + symbols
        
        if symbols:
            st.markdown(f"### 📊 Vergleich: {', '.join(symbols)}")
            
            # Normalisierte Performance
            comparison_data = {}
            for sym in symbols:
                df_sym = generate_stock_data(sym, days=126)
                normalized = df_sym["Schlusskurs"] / df_sym["Schlusskurs"].iloc[0] * 100
                comparison_data[sym] = normalized
            
            df_comp = pd.DataFrame(comparison_data)
            st.line_chart(df_comp, use_container_width=True)
            
            # Performance-Tabelle
            perf_data = []
            for sym in symbols:
                df_sym = generate_stock_data(sym, days=126)
                current = df_sym["Schlusskurs"].iloc[-1]
                start = df_sym["Schlusskurs"].iloc[0]
                perf = (current - start) / start * 100
                perf_data.append({"Symbol": sym, "Performance 6M (%)": f"{perf:+.2f}%"})
            
            st.dataframe(pd.DataFrame(perf_data), use_container_width=True, hide_index=True)
        else:
            st.warning("Bitte geben Sie mindestens ein Vergleichs-Symbol ein.")

# ── Footer ────────────────────────────────────────────────────

st.divider()
st.caption(f"📈 Tägliche Aktienanalyse v1.0 | Daten simuliert für Demo-Zwecke | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
