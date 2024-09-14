import openai
import pandas as pd
import plotly.graph_objs as go
import plotly.subplots as sp
import streamlit as st
import requests
import os
from datetime import datetime, timedelta

# Retrieve the API keys from Streamlit secrets
alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
    data = response.json()
    
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

# Function to create a candlestick chart with volume in a subchart
def create_candlestick_chart(df, filename):
    # Create a subplot with 2 rows, sharing the x-axis
    fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           row_heights=[0.7, 0.3], vertical_spacing=0.05,
                           subplot_titles=("Candlestick Chart", "Volume"))

    # Create the candlestick chart in the first row
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Stock'
    ), row=1, col=1)

    # Create the volume bar chart in the second row
    fig.add_trace(go.Bar(
        x=df['Date'], 
        y=df['Volume'], 
        name='Volume', 
        marker_color='blue',
        opacity=0.5
    ), row=2, col=1)

    # Layout configuration
    fig.update_layout(
        title='Daily Candlestick Chart with Volume',
        xaxis_title='Date',  # Adjust the x-axis title for better spacing
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        width=1200, 
        height=800,
        legend_title_text='Legend'
    )
    
    # Adjusting the position of the Volume chart's y-axis title to avoid overlap
    fig.update_yaxes(title_text='Volume', row=2, col=1, side='right', automargin=True)

    # Save the chart as an image
    fig.write_image(filename)

    return fig

# Function to generate the report
def generate_report(stock_symbol):
    st.write(f"### {stock_symbol} Daily Briefing Report")
    
    df = fetch_stock_data(stock_symbol, alpha_vantage_api_key)
    if df.empty:
        return
    
    report_file_base = f'reports/{stock_symbol}_daily_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    image_filename = f"{report_file_base}.png"
    
    fig = create_candlestick_chart(df, image_filename)
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
    # {stock_symbol} Daily Briefing Report
    
    ## Candlestick Chart
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
    
    st.success("Report generated and saved successfully!")

# Streamlit UI
st.set_page_config(layout="wide")  # Set layout to wide for maximum use of space

# Apply custom CSS to control the main column width
st.markdown(
    """
    <style>
    .main {
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the logo
logo_path = "assets/dtb-logo.jpg"
st.image(logo_path, width=128)

st.title("Daily Trading Briefing")

# Stock symbol input
stock_symbol = st.text_input("Enter Stock Symbol", "QQQ")

if st.button("Generate Briefing for Today"):
    generate_report(stock_symbol)

st.write("### Available Reports")

# Filter reports to show only .md files
reports = [report for report in os.listdir('reports') if report.startswith(stock_symbol) and report.endswith('.md')]
selected_report = st.selectbox("Select a report", reports)

if selected_report:
    report_base_name = os.path.splitext(selected_report)[0]
    image_file = f'reports/{report_base_name}.png'
    
    if st.button("Delete Selected Report"):
        # Check if the report file exists before attempting to delete
        if os.path.exists(f'reports/{selected_report}'):
            os.remove(f'reports/{selected_report}')
            
            # Delete the corresponding image
            if os.path.exists(image_file):
                os.remove(image_file)
            
            st.success(f"Report {selected_report} and its associated image deleted successfully!")
        else:
            st.error(f"Report {selected_report} not found. It may have already been deleted.")

# Only try to read and display the selected report if it still exists
if os.path.exists(f'reports/{selected_report}'):
    with open(f'reports/{selected_report}', 'r') as f:
        st.markdown(f.read())

    # Display the corresponding image if it exists
    if os.path.exists(image_file):
        st.image(image_file, caption="Candlestick Chart")
    else:
        st.write("No associated image found.")
