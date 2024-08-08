import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.colors as mcolors

def get_spy_data(days):
  """Fetches SPY data from Yahoo Finance for the specified number of days.

  Args:
    days: Number of days of data to fetch.

  Returns:
    A pandas DataFrame containing the SPY data.
  """
  spy = yf.Ticker("SPY")
  hist = spy.history(period=f"{days}d")
  hist = hist.sort_index(ascending=False)
  return hist

def calculate_percentage_change(df):
  """Calculates the percentage change between consecutive prices.

  Args:
    df: A pandas DataFrame containing the SPY data.

  Returns:
    A pandas DataFrame with an additional column for percentage change.
  """
  df['Percentage Change'] = df['Close'].pct_change() * 100
  return df

def format_date(date):
  return date.strftime('%d-%b-%Y')

def color_percentage_change(val):
  color = 'red' if val < 0 else 'green' if val > 0 else 'black'
  return f'color: {color}'

def main():
  st.title("SPY Price and Percentage Change")

  days = st.slider("Select number of days", min_value=1, max_value=365, value=5)

  spy_data = get_spy_data(days)
  spy_data_with_change = calculate_percentage_change(spy_data)

  spy_data_with_change.index = spy_data_with_change.index.map(format_date)

  spy_data_with_change = spy_data_with_change[['Open', 'High', 'Low', 'Close', 'Percentage Change']]

  styled_df = spy_data_with_change.style.format(
      {'Percentage Change': '{:.2f}%'},
      precision=2
  ).map(color_percentage_change, subset=['Percentage Change'])

  st.dataframe(styled_df)

if __name__ == "__main__":
  main()
