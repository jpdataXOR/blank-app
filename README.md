import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# App title
st.title("Bitcoin (BTC) Hourly Price Chart")

# Define the BTC ticker symbol
btc_ticker = "BTC-USD"

# Define the date range (e.g., last 48 hours)
end_date = datetime.now()
start_date = end_date - timedelta(days=2)  # Last 2 days

# Fetch hourly data for BTC
btc_data = yf.download(btc_ticker, start=start_date, end=end_date, interval="1h")

# Check if data was fetched successfully
if btc_data.empty:
    st.write("Failed to retrieve BTC data. Please try again later.")
else:
    # Create a Plotly line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=btc_data.index, y=btc_data['Close'], mode='lines+markers', name='BTC-USD'))

    # Chart layout
    fig.update_layout(
        title="BTC Hourly Price Chart (Last 48 Hours)",
        xaxis_title="Date/Time",
        yaxis_title="Price (USD)",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )

    # Display the chart in the app
    st.plotly_chart(fig)

    # Show latest BTC price
    latest_price = btc_data['Close'].iloc[-1]
    st.subheader(f"Latest BTC Price: ${latest_price:.2f}")