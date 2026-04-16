#import
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# --- UI Setup ---
st.set_page_config(page_title="Low-Vol Trading Bot", layout="wide")
st.title("🛡️ Low-Volatility Anomaly Trading Bot")
st.markdown("Select your dates below to simulate the strategy's performance.")

# --- Interactive Sidebar Controls ---
st.sidebar.header("Bot Parameters")
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 11, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2024, 2, 1))
stock_universe = st.sidebar.text_input("Stock Universe (Comma separated)", "AAPL, MSFT, JNJ, PG, XOM, JPM, UNH, V, HD, KO, PEP, MRK, COST, MCD, WMT, TSLA, NVDA")
top_percent = st.sidebar.slider("Select Top % of Lowest Volatility", min_value=10, max_value=50, value=30, step=5)

# --- Core Logic ---
if st.sidebar.button("Run Simulation"):
    with st.spinner("Fetching data and running simulation..."):
        tickers = [t.strip() for t in stock_universe.split(',')]
        
        # Download Data (including SPY for benchmark)
        all_tickers = tickers + ['SPY']
        data = yf.download(all_tickers, start=start_date, end=end_date)['Adj Close']
        
        # Separate benchmark and universe
        spy_data = data['SPY']
        universe_data = data[tickers]
        
        # Calculate daily returns and rolling 30-day volatility
        daily_returns = universe_data.pct_change()
        rolling_vol = daily_returns.rolling(window=30).std()
        
        # Find the last day of the first month to make our selection
        # (Simplified single-period selection for the UI demonstration)
        selection_date = rolling_vol.dropna().index[0] 
        vol_on_selection = rolling_vol.loc[selection_date]
        
        # Select lowest volatility stocks
        num_stocks = max(1, int(len(tickers) * (top_percent / 100.0)))
        selected_stocks = vol_on_selection.nsmallest(num_stocks).index.tolist()
        
        # Calculate Returns from selection date to end date
        portfolio_returns = daily_returns.loc[selection_date:][selected_stocks].mean(axis=1)
        cumulative_portfolio = (1 + portfolio_returns).cumprod() - 1
        
        spy_returns = spy_data.pct_change().loc[selection_date:]
        cumulative_spy = (1 + spy_returns).cumprod() - 1

        # --- Display Interactive Results ---
        st.subheader(f"Portfolio Selected on {selection_date.strftime('%Y-%m-%d')}")
        st.write(f"**Selected Tickers:** {', '.join(selected_stocks)}")
        
        col1, col2 = st.columns(2)
        col1.metric("Bot Portfolio Return", f"{cumulative_portfolio.iloc[-1] * 100:.2f}%")
        col2.metric("S&P 500 (SPY) Return", f"{cumulative_spy.iloc[-1] * 100:.2f}%")
        
        st.subheader("Performance Chart")
        chart_data = pd.DataFrame({
            'Low-Vol Bot': cumulative_portfolio * 100,
            'S&P 500 Benchmark': cumulative_spy * 100
        })
        st.line_chart(chart_data)


