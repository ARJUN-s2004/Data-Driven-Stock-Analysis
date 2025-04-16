# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- Load Data ---
# @st.cache_data
# # def load_data():
# #     csv_path = Path(r"E:\Guvi Projects\project 2 stock\codes\data (1)\tickers_csv\all_tickers_combined.csv")
# #     df = pd.read_csv(csv_path)
# #     df['date'] = pd.to_datetime(df['date'])
# #     return df

df = pd.read_csv(r"E:\Guvi Projects\project 2 stock\codes\data (1)\tickers_csv\stock_price.csv")
df['date'] = pd.to_datetime(df['date'])
df.sort_values(by=['Ticker', 'date'], inplace=True)

# --- Sidebar Navigation ---
st.sidebar.title("📊 Stock Market Dashboard")
section = st.sidebar.radio("Go to:", ["Yearly Returns", "Volatility", "Cumulative Return", "Sector Performance", "Stock Correlation", "Monthly Gainers & Losers"])

# --- Yearly Return Section ---
if section == "Yearly Returns":
    st.title("📈 Top 10 Gainers and Losers (Yearly)")
    first_close = df.groupby('Ticker').first()['close']
    last_close = df.groupby('Ticker').last()['close']
    returns = ((last_close - first_close) / first_close * 100).reset_index()
    returns.columns = ['Ticker', 'Yearly Return %']
    top = returns.sort_values(by='Yearly Return %', ascending=False).head(10)
    bottom = returns.sort_values(by='Yearly Return %').head(10)
    st.subheader("🔝 Top 10 Gainers")
    st.bar_chart(top.set_index('Ticker'))
    st.subheader("🔻 Top 10 Losers")
    st.bar_chart(bottom.set_index('Ticker'))

# --- Volatility Section ---
elif section == "Volatility":
    st.title("📊 Volatility (Standard Deviation of Daily Returns)")
    df['prev_close'] = df.groupby('Ticker')['close'].shift(1)
    df['daily_return'] = (df['close'] - df['prev_close']) / df['prev_close']
    vol = df.groupby('Ticker')['daily_return'].std().reset_index(name='Volatility')
    top_vol = vol.sort_values(by='Volatility', ascending=False).head(10)
    st.bar_chart(top_vol.set_index('Ticker'))

# --- Cumulative Return Section ---
elif section == "Cumulative Return":
    st.title("📈 Cumulative Return of Top 5 Stocks")
    df['daily_return'] = df.groupby('Ticker')['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).groupby(df['Ticker']).cumprod()
    top_5 = df.groupby('Ticker').last()['cumulative_return'].sort_values(ascending=False).head(5).index.tolist()
    st.line_chart(df[df['Ticker'].isin(top_5)].pivot(index='date', columns='Ticker', values='cumulative_return'))

# --- Sector-wise Performance ---
elif section == "Sector Performance":
    st.title("🏭 Sector-wise Average Return")
    sector_df = pd.read_csv(r"E:\Guvi Projects\project 2 stock\Sector_data - Sheet1.csv")
    sector_df['Ticker'] = sector_df['Symbol'].str.extract(r':\s*([A-Z]+)')
    df_sector = pd.merge(df, sector_df[['Ticker', 'sector']], on='Ticker', how='left')
    first = df_sector.groupby('Ticker').first()['close']
    last = df_sector.groupby('Ticker').last()['close']
    sector_return = ((last - first) / first).reset_index(name='Return')
    merged = pd.merge(sector_return, sector_df[['Ticker', 'sector']], on='Ticker', how='left')
    avg_sector = merged.groupby('sector')['Return'].mean().sort_values(ascending=False)
    st.bar_chart(avg_sector)

# --- Stock Price Correlation ---
elif section == "Stock Correlation":
    st.title("📊 Stock Price Correlation Heatmap")

    # Drop duplicates to ensure unique (date, Ticker) for pivoting
    df_corr = df.drop_duplicates(subset=['date', 'Ticker'], keep='last')

    # Pivot to have dates as rows and Ticker as columns with 'close' prices
    close_prices = df_corr.pivot(index='date', columns='Ticker', values='close')

    # Calculate percentage change
    pct_change = close_prices.pct_change()

    # Compute correlation matrix
    correlation_matrix = pct_change.corr()

    # Plot heatmap using seaborn
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(correlation_matrix, cmap='coolwarm', center=0, annot=False, linewidths=0.5)
    plt.title("Stock Price Correlation Heatmap")
    st.pyplot(fig)

# --- Monthly Gainers & Losers ---
elif section == "Monthly Gainers & Losers":
    st.title("📅 Monthly Gainers and Losers")
    df['year_month'] = df['date'].dt.to_period('M')
    monthly = df.groupby(['Ticker', 'year_month']).agg(
        first_open=('open', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    monthly['monthly_return'] = (monthly['last_close'] - monthly['first_open']) / monthly['first_open'] * 100
    selected_month = st.selectbox("Select Month", sorted(monthly['year_month'].astype(str).unique()))
    month_data = monthly[monthly['year_month'].astype(str) == selected_month]
    top_5 = month_data.sort_values(by='monthly_return', ascending=False).head(5)
    bottom_5 = month_data.sort_values(by='monthly_return').head(5)

    st.subheader(f"📈 Top 5 Gainers - {selected_month}")
    st.bar_chart(top_5.set_index('Ticker')['monthly_return'])

    st.subheader(f"📉 Top 5 Losers - {selected_month}")
    st.bar_chart(bottom_5.set_index('Ticker')['monthly_return'])
