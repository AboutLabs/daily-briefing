import streamlit as st
import pandas as pd
import altair as alt
import requests
import os
from datetime import datetime

# Example API keys, replace with your actual keys or use st.secrets for production
alpha_vantage_api_key = "your_alpha_vantage_api_key"
openai_api_key = "your_openai_api_key"

# Function to fetch data from Alpha Vantage
def fetch_stock_data(symbol, api_key):
    base_url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": api_key
    }
    response = requests.get(base_url, params=params)
    
    # Log the response for debugging
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Content: {response.content}")
    
    data = response.json()
    
    # Check for errors in the response
    if "Error Message" in data:
        st.error(f"Error fetching data: {data['Error Message']}")
        return pd.DataFrame()
    
    # Parse the JSON data
    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        st.error("Error fetching data. Please check the stock symbol and try again.")
        return pd.DataFrame()
    
    # Convert the data to a DataFrame
    df = pd.DataFrame.from_dict(time_series, orient='index')
    df = df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })
    df.index = pd.to_datetime(df.index)
    df = df.reset_index().rename(columns={'index': 'Date'})
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    
    return df

# Function to create an Altair candlestick chart with volume
def create_altair_candlestick_chart(df, filename):
    base = alt.Chart(df).encode(
        x='Date:T'
    )

    candlestick = base.mark_rule().encode(
        y='Low:Q',
        y2='High:Q'
    ).properties(width=800, height=400).mark_bar().encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Close:Q', title='Price', scale=alt.Scale(domain=[df['Low'].min(), df['High'].max()])),
        color=alt.condition(
            "datum.Open <= datum.Close", alt.value("green"), alt.value("red")
        ),
        tooltip=['Date:T', 'Open:Q', 'High:Q', 'Low:Q', 'Close:Q', 'Volume:Q']
    )

    volume = base.mark_bar().encode(
        y=alt.Y('Volume:Q', title='Volume', scale=alt.Scale(domain=[0, df['Volume'].max() * 1.1])),
        color=alt.value('blue')
    ).properties(width=800, height=150)

    chart = alt.vconcat(candlestick, volume).resolve_scale(y='independent')

    # Save the chart as an image
    chart.save(filename, format='png')

    return chart

# Function to generate the report
def generate_report(stock_symbol):
    df = fetch_stock_data(stock_symbol, alpha_vantage_api_key)
    if df.empty:
        return
    
    report_file_base = f'reports/{stock_symbol}_daily_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    image_filename = f"{report_file_base}.png"
    
    create_altair_candlestick_chart(df, image_filename)
    
    # Placeholder content for the report
    news_summary = "This is a placeholder for news summary. Integrate actual news summary here."
    stock_analysis = "This is a placeholder for stock analysis. Integrate actual analysis here."
    investment_analysis = "This is a placeholder for investment analysis. Integrate actual analysis here."
    
    report_content = f"""
    # {stock_symbol} Daily Briefing Report
    
    ![Candlestick Chart]({os.path.basename(image_filename)})
    
    ## News Summary
    {news_summary}
    
    ## Analytical Report 1
    {stock_analysis}
    
    ## Analytical Report 2
    {investment_analysis}
    """
    report_file = f'{report_file_base}.md'
    if not os.path.exists('reports'):
        os.makedirs('reports')
    with open(report_file, 'w') as f:
        f.write(report_content)

# Function to load the report
def load_report(report_filename):
    report_base_name = os.path.splitext(report_filename)[0]
    image_file = f'reports/{report_base_name}.png'
    
    if os.path.exists(f'reports/{report_filename}'):
        with open(f'reports/{report_filename}', 'r') as f:
            report_content = f.read()
        
        return report_content, image_file
    else:
        return None, None
