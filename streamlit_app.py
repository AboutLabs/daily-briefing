import openai
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import alpaca_trade_api as tradeapi
import os

# Retrieve the API keys from Streamlit secrets
alpaca_api_key = st.secrets["ALPACA_API_KEY"]
alpaca_secret_key = st.secrets["ALPACA_SECRET_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to fetch NASDAQ data from Alpaca
def fetch_nasdaq_data(api_key, secret_key):
    api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
    
    # Fetch the data for the QQQ ETF (which tracks NASDAQ)
    bars = api.get_bars('QQQ', tradeapi.TimeFrame.Hour, limit=100).df
    
    # Reset the index and return the required columns
    bars = bars.reset_index()
    bars = bars[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    bars.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    return bars

# Function to analyze data with GPT-4
def analyze_chart_with_gpt4(data):
    data_str = data.to_string(index=False)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": f"Analyze the following NASDAQ data and identify support and resistance levels. Provide the support and resistance levels as numerical values. Data:\n{data_str}"}
        ]
    )
    
    analysis = response['choices'][0]['message']['content']
    
    support_levels = []
    resistance_levels = []
    
    for line in analysis.splitlines():
        if "Support levels" in line:
            support_levels = [float(x) for x in line.split(":")[1].split(",")]
        elif "Resistance levels" in line:
            resistance_levels = [float(x) for x in line.split(":")[1].split(",")]
    
    return support_levels, resistance_levels

# Function to create a candlestick chart with support/resistance zones
def create_candlestick_chart_with_analysis(df):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    
    support_levels, resistance_levels = analyze_chart_with_gpt4(df[['Date', 'Open', 'High', 'Low', 'Close']])
    
    for level in support_levels:
        fig.add_hline(y=level, line=dict(color='green', dash='dash'), annotation_text='Support', annotation_position="bottom right")
    
    for level in resistance_levels:
        fig.add_hline(y=level, line=dict(color='red', dash='dash'), annotation_text='Resistance', annotation_position="top right")
    
    fig.update_layout(title='NASDAQ 1h Candlestick Chart with Support/Resistance',
                      yaxis_title='Price',
                      xaxis_title='Date',
                      xaxis_rangeslider_visible=False)
    
    return fig

# Function to generate the report
def generate_report():
    st.write("### NASDAQ Daily Briefing Report")
    
    df = fetch_nasdaq_data(alpaca_api_key, alpaca_secret_key)
    
    fig = create_candlestick_chart_with_analysis(df)
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
