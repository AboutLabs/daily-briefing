import openai
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Retrieve the API keys from Streamlit secrets
alpaca_api_key = st.secrets["ALPACA_API_KEY"]
alpaca_secret_key = st.secrets["ALPACA_SECRET_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to fetch NASDAQ data from Alpaca
def fetch_nasdaq_data(api_key, secret_key):
    api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
    
    # Fetch the data for the QQQ ETF (which tracks NASDAQ) for the last week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Format dates correctly for the API
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Get bars data with IEX feed (Free Tier)
    bars = api.get_bars('QQQ', tradeapi.TimeFrame.Hour, 
                        start=start_date_str, 
                        end=end_date_str, 
                        feed='iex').df
    
    # Reset the index and return the required columns
    bars = bars.reset_index()
    bars = bars[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    bars.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    return bars


# Function to create a larger candlestick chart with smaller candles and volume
def create_candlestick_chart(df):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         increasing_line_width=0.5, decreasing_line_width=0.5),
                          go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='blue', yaxis='y2', opacity=0.3)])

    fig.update_layout(title='NASDAQ 1h Candlestick Chart with Volume',
                      yaxis_title='Price',
                      xaxis_title='Date',
                      xaxis_rangeslider_visible=False,
                      yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
                      width=1200, height=800)  # Set the size of the chart

    # Save the chart as an image
    fig.write_image("candlestick_chart.png")

    return fig

# Function to generate the report
def generate_report():
    st.write("### NASDAQ Daily Briefing Report")
    
    df = fetch_nasdaq_data(alpaca_api_key, alpaca_secret_key)
    
    fig = create_candlestick_chart(df)
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("#### News Summary")
    news_summary = "This is a placeholder for news summary. Integrate actual news summary here."
    st.write(news_summary)
    
    st.write("#### Analytical Report 1")
    stock_analysis = "This is a placeholder for stock analysis. Integrate actual analysis here."
    st.write(stock_analysis)
    
    st.write("#### Analytical Report 2")
    investment_analysis = "This is a placeholder for investment analysis. Integrate actual analysis here."
    st.write(investment_analysis)
    
    report_content = f"""
    # NASDAQ Daily Briefing Report
    
    ## Candlestick Chart
    ![Candlestick Chart](candlestick_chart.png)
    
    ## News Summary
    {news_summary}
    
    ## Analytical Report 1
    {stock_analysis}
    
    ## Analytical Report 2
    {investment_analysis}
    """
    report_file = f'reports/nasdaq_daily_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.md'
    if not os.path.exists('reports'):
        os.makedirs('reports')
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    st.success("Report generated and saved successfully!")

# Streamlit UI
st.set_page_config(layout="centered")  # Set layout to centered

# Display the logo
logo_path = "assets/dtb-logo.jpg"
st.image(logo_path, width=256)

st.title("Daily Trading Briefing")

if st.button("Generate Briefing for Today"):
    generate_report()

st.write("### Available Reports")
reports = os.listdir('reports')
selected_report = st.selectbox("Select a report", reports)

if st.button("Delete Selected Report"):
    os.remove(f'reports/{selected_report}')
    st.success(f"Report {selected_report} deleted successfully!")

if selected_report:
    with open(f'reports/{selected_report}', 'r') as f:
        st.markdown(f.read())
