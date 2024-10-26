import streamlit as st
import ccxt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import pytz  # Import pytz for timezone handling

# Set the page config to wide mode
st.set_page_config(page_title="BTC Hourly Price Chart", layout="wide")

# App title
st.title("Simple BTC Hourly Price Chart from Kraken")

# Define the BTC ticker symbol
btc_ticker = 'BTC/USDT'  # Kraken uses pairs like BTC/USDT

# Define the date range (last 55 hours for the chart)
end_date = datetime.now()
start_date = end_date - timedelta(hours=55)  # Adjusting to 55 hours

# Initialize the Kraken exchange
kraken = ccxt.kraken()

# Function to fetch hourly data for BTC
def fetch_kraken_data(ticker, since, limit=50):
    # Convert datetime to timestamp in milliseconds
    since_timestamp = int(since.timestamp() * 1000)
    # Fetch OHLCV data (Open, High, Low, Close, Volume)
    ohlcv = kraken.fetch_ohlcv(ticker, timeframe='1h', since=since_timestamp, limit=limit)
    
    # Create a DataFrame from the fetched data
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to datetime
    df.set_index('timestamp', inplace=True)  # Set timestamp as index
    return df

# Fetch data
btc_data = fetch_kraken_data(btc_ticker, start_date)

# Check if data was fetched successfully
if not btc_data.empty:
    # Convert the timestamp index to the Sydney timezone
    timezone = 'Australia/Sydney'
    btc_data.index = btc_data.index.tz_localize('UTC').tz_convert(timezone)
    
    # Calculate percentage change from the last hour
    last_price = btc_data['close'].iloc[-1]
    previous_price = btc_data['close'].iloc[-2] if len(btc_data) > 1 else last_price
    price_difference = ((last_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0

    # Set Y-axis range with 3% buffer logic only for latest price
    upper_bound = last_price * 1.03  # Add 3% above
    lower_bound = last_price * 0.97  # Add 3% below

    # Create a step line chart
    fig = go.Figure(
        data=go.Scatter(
            x=btc_data.index, 
            y=btc_data['close'].astype(int), 
            mode='lines+markers', 
            name='BTC-USD', 
            line=dict(shape='hv', color='black'),  # Set line to material black
            marker=dict(size=4, color='black')  # Set marker dots to black
        )
    )
    
    # Generate tick values and tick text for every 2 hours
    tickvals = pd.date_range(start=btc_data.index[0], end=btc_data.index[-1] + timedelta(hours=24), freq='2h')
    ticktext = [tick.strftime('%H:%M') for tick in tickvals]

    # Add vertical line separators at each midnight UTC
    midnight_lines = []
    for ts in pd.date_range(start=start_date.date(), end=end_date.date(), freq='D'):
        utc_midnight = pd.Timestamp(ts).tz_localize('UTC')  # Midnight in UTC
        midnight_lines.append(dict(
            type="line",
            x0=utc_midnight,
            y0=btc_data['close'].min() * 0.97,  # Slightly below the minimum close value
            x1=utc_midnight,
            y1=btc_data['close'].max() * 1.03,  # Slightly above the maximum close value
            line=dict(color="gray", width=1, dash="dot")
        ))
    
    # Add the lines to the figure
    fig.update_layout(shapes=midnight_lines)

    # Customize the layout of the chart
    fig.update_layout(
        title="BTC Price (Last 55 Hours)",
        xaxis_title="Time (HH:mm)",
        yaxis_title="Price (USD)",  # Displaying in USD
        xaxis_tickformat='%H:%M',
        yaxis_ticks="outside",
        xaxis=dict(
            tickangle=-45, 
            tickvals=tickvals, 
            ticktext=ticktext,
            type='date'
        ),
        yaxis=dict(range=[lower_bound, upper_bound]),  # Set y-axis limits based on the last price
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background for a modern look
        width=1200,
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),  # Adjust margins
        xaxis_range=[btc_data.index[0], btc_data.index[-1] + timedelta(hours=24)]  # Extend only to the right by 24 hours
    )
    
    # Add a dot at the last price point with hover information always visible
    fig.add_trace(go.Scatter(
        x=[btc_data.index[-1]], 
        y=[last_price],
        mode='markers+text',
        marker=dict(size=10, color='darkred'),  # Dot at last price with dark red color
        text=[f"{last_price:.0f}"],  # Always show the price as text without needing hover
        textposition="top center",
        hoverinfo='skip',  # Skip hover for this last price point since it is always visible
        showlegend=False
    ))

    # Format the price difference string
    price_change_str = f"{abs(price_difference):.1f}%"
    price_change_color = "green" if price_difference >= 0 else "red"
    
    # Centering the content using a container
    with st.container():
        st.plotly_chart(fig)
        st.markdown(f"<h2 style='text-align: center;'>Latest BTC Price: <span style='color: {price_change_color};'>{last_price:.0f} USD</span> ({price_change_str})</h2>", unsafe_allow_html=True)
else:
    st.error("No data available to display.")