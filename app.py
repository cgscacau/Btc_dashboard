import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import ta

# Page configuration
st.set_page_config(
    page_title="Bitcoin Technical Analysis Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("₿ Bitcoin Technical Analysis Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Time period selection
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y",
        "Max": "max"
    }
    
    selected_period = st.selectbox(
        "Select Time Period",
        options=list(period_options.keys()),
        index=3
    )
    
    # Interval selection
    interval_options = {
        "1 Day": "1d",
        "1 Week": "1wk",
        "1 Month": "1mo"
    }
    
    selected_interval = st.selectbox(
        "Select Interval",
        options=list(interval_options.keys()),
        index=0
    )
    
    # Technical indicators
    st.subheader("Technical Indicators")
    show_sma = st.checkbox("Simple Moving Average (SMA)", value=True)
    show_ema = st.checkbox("Exponential Moving Average (EMA)", value=True)
    show_bb = st.checkbox("Bollinger Bands", value=True)
    show_rsi = st.checkbox("RSI", value=True)
    show_macd = st.checkbox("MACD", value=True)
    show_volume = st.checkbox("Volume", value=True)
    
    # Moving average periods
    if show_sma or show_ema:
        st.subheader("MA Periods")
        ma_short = st.slider("Short Period", 5, 50, 20)
        ma_long = st.slider("Long Period", 50, 200, 50)

# Function to fetch Bitcoin data
@st.cache_data(ttl=300)
def get_bitcoin_data(period, interval):
    try:
        btc = yf.Ticker("BTC-USD")
        df = btc.history(period=period, interval=interval)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Function to calculate technical indicators
def calculate_indicators(df, ma_short=20, ma_long=50):
    if df is None or df.empty:
        return df
    
    # Simple Moving Averages
    df['SMA_short'] = ta.trend.sma_indicator(df['Close'], window=ma_short)
    df['SMA_long'] = ta.trend.sma_indicator(df['Close'], window=ma_long)
    
    # Exponential Moving Averages
    df['EMA_short'] = ta.trend.ema_indicator(df['Close'], window=ma_short)
    df['EMA_long'] = ta.trend.ema_indicator(df['Close'], window=ma_long)
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_upper'] = bollinger.bollinger_hband()
    df['BB_middle'] = bollinger.bollinger_mavg()
    df['BB_lower'] = bollinger.bollinger_lband()
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    
    return df

# Fetch data
with st.spinner("Fetching Bitcoin data..."):
    df = get_bitcoin_data(period_options[selected_period], interval_options[selected_interval])

if df is not None and not df.empty:
    # Calculate indicators
    df = calculate_indicators(df, ma_short, ma_long)
    
    # Current price and metrics
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Current Price",
            f"${current_price:,.2f}",
            f"{price_change_pct:+.2f}%"
        )
    
    with col2:
        st.metric(
            "24h High",
            f"${df['High'].iloc[-1]:,.2f}"
        )
    
    with col3:
        st.metric(
            "24h Low",
            f"${df['Low'].iloc[-1]:,.2f}"
        )
    
    with col4:
        st.metric(
            "Volume",
            f"{df['Volume'].iloc[-1]:,.0f}"
        )
    
    with col5:
        if not pd.isna(df['RSI'].iloc[-1]):
            rsi_value = df['RSI'].iloc[-1]
            rsi_status = "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral"
            st.metric(
                "RSI",
                f"{rsi_value:.2f}",
                rsi_status
            )
    
    st.markdown("---")
    
    # Create main chart
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.2, 0.15, 0.15],
        subplot_titles=('Price Chart', 'Volume', 'RSI', 'MACD')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='BTC-USD',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # Add moving averages
    if show_sma:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_short'],
                name=f'SMA {ma_short}',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA_long'],
                name=f'SMA {ma_long}',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    if show_ema:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA_short'],
                name=f'EMA {ma_short}',
                line=dict(color='purple', width=1, dash='dash')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA_long'],
                name=f'EMA {ma_long}',
                line=dict(color='red', width=1, dash='dash')
            ),
            row=1, col=1
        )
    
    # Add Bollinger Bands
    if show_bb:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_upper'],
                name='BB Upper',
                line=dict(color='gray', width=1),
                opacity=0.3
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_lower'],
                name='BB Lower',
                line=dict(color='gray', width=1),
                fill='tonexty',
                opacity=0.3
            ),
            row=1, col=1
        )
    
    # Volume
    if show_volume:
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )
    
    # RSI
    if show_rsi:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # MACD
    if show_macd:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD'],
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                name='Signal',
                line=dict(color='orange', width=2)
            ),
            row=4, col=1
        )
        # MACD histogram
        colors_macd = ['green' if val >= 0 else 'red' for val in df['MACD_diff']]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['MACD_diff'],
                name='MACD Histogram',
                marker_color=colors_macd,
                opacity=0.5
            ),
            row=4, col=1
        )
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Technical Analysis',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        height=1000,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trading signals
    st.markdown("---")
    st.subheader("📊 Trading Signals")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Trend Analysis")
        if not pd.isna(df['SMA_short'].iloc[-1]) and not pd.isna(df['SMA_long'].iloc[-1]):
            if df['SMA_short'].iloc[-1] > df['SMA_long'].iloc[-1]:
                st.success("🟢 Bullish (Short MA > Long MA)")
            else:
                st.error("🔴 Bearish (Short MA < Long MA)")
    
    with col2:
        st.markdown("### RSI Signal")
        if not pd.isna(df['RSI'].iloc[-1]):
            rsi_current = df['RSI'].iloc[-1]
            if rsi_current > 70:
                st.warning("⚠️ Overbought (RSI > 70)")
            elif rsi_current < 30:
                st.info("💡 Oversold (RSI < 30)")
            else:
                st.success("✅ Neutral (30 < RSI < 70)")
    
    with col3:
        st.markdown("### MACD Signal")
        if not pd.isna(df['MACD'].iloc[-1]) and not pd.isna(df['MACD_signal'].iloc[-1]):
            if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
                st.success("🟢 Bullish (MACD > Signal)")
            else:
                st.error("🔴 Bearish (MACD < Signal)")
    
    # Price prediction section
    st.markdown("---")
    st.subheader("🔮 Price Analysis")
    
    # Calculate support and resistance levels
    recent_high = df['High'].tail(30).max()
    recent_low = df['Low'].tail(30).min()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("30-Day Resistance", f"${recent_high:,.2f}")
        st.metric("30-Day Support", f"${recent_low:,.2f}")
    
    with col2:
        avg_volume = df['Volume'].tail(30).mean()
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = (current_volume / avg_volume) * 100
        st.metric("Volume vs 30-Day Avg", f"{volume_ratio:.2f}%")
        
        volatility = df['Close'].tail(30).std()
        st.metric("30-Day Volatility", f"${volatility:,.2f}")
    
    # Historical data table
    st.markdown("---")
    st.subheader("📈 Historical Data")
    
    # Date range selector for table
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=df.index[-30].date() if len(df) > 30 else df.index[0].date(),
            min_value=df.index[0].date(),
            max_value=df.index[-1].date()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=df.index[-1].date(),
            min_value=df.index[0].date(),
            max_value=df.index[-1].date()
        )
    
    # Filter data based on date range - FIX APPLIED HERE
    if not df.empty and len(df) > 0:
        try:
            start_date_ts = pd.Timestamp(start_date)
            end_date_ts = pd.Timestamp(end_date)
            
            # Ensure dates are within range
            if start_date_ts < df.index[0]:
                start_date_ts = df.index[0]
            if end_date_ts > df.index[-1]:
                end_date_ts = df.index[-1]
            
            filtered_df = df.loc[start_date_ts:end_date_ts]
            
            # Display table
            display_df = filtered_df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            display_df = display_df.round(2)
            display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                display_df.style.format({
                    'Open': '${:,.2f}',
                    'High': '${:,.2f}',
                    'Low': '${:,.2f}',
                    'Close': '${:,.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = filtered_df.to_csv()
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"bitcoin_data_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error filtering data: {str(e)}")
    else:
        st.warning("No data available for the selected date range")
    
else:
    st.error("Unable to fetch Bitcoin data. Please try again later.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Data provided by Yahoo Finance | Updated every 5 minutes</p>
        <p><small>This dashboard is for educational purposes only. Not financial advice.</small></p>
    </div>
    """, unsafe_allow_html=True)

# Main function
def main():
    pass

if __name__ == "__main__":
    main()
