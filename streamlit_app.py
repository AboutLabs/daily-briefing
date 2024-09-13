import openai
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from alpha_vantage.timeseries import TimeSeries
import os

# Retrieve the API keys from Streamlit secrets
alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to fetch NASDAQ data from Alpha Vantage
def fetch_nasdaq_data(api_key):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol='NASDAQ:IXIC', interval='60min', outputsize='full')
    data.reset_index(inplace=True)
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    return data

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
    
    df = fetch_nasdaq_data(alpha_vantage_api_key)
    
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
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    st.success("Report generated and saved successfully!")

# Streamlit UI
st.set_page_config(layout="centered")  # Set layout to centered

# Display the logo
logo_path = "/mnt/data/dtb-logo.jpg"
st.image(logo_path, use_column_width=True)

st.title("Daily Trading Briefing")

if st.button("Generate Briefing for Today"):
    generate_report()

st.write("### Available Reports")
if not os.path.exists('reports'):
    os.makedirs('reports')
reports = os.listdir('reports')
selected_report = st.selectbox("Select a report", reports)

if st.button("Delete Selected Report"):
    os.remove(f'reports/{selected_report}')
    st.success(f"Report {selected_report} deleted successfully!")

if selected_report:
    with open(f'reports/{selected_report}', 'r') as f:
        st.markdown(f.read())
