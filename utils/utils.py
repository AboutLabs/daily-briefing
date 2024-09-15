import os
import streamlit as st
import pandas as pd
import altair as alt
import requests
import logging
from datetime import datetime
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain.tools.render import render_text_description
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain_community.llms import HuggingFaceEndpoint
from composio_langchain import App, ComposioToolSet

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('app.log'),  # Logs to a file
    ]
)
logger = logging.getLogger(__name__)

# Safely retrieve secrets from secrets.toml or Streamlit Cloud's secret manager
alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]
hf_key = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

# Function to fetch data from Alpha Vantage
def fetch_stock_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        logger.info(f"Fetching stock data for {symbol}: Status code {response.status_code}")
        
        data = response.json()
        
        if "Error Message" in data:
            logger.error(f"Error fetching data: {data['Error Message']}")
            st.error(f"Error fetching data: {data['Error Message']}")
            return pd.DataFrame()
        
        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            logger.error("No data returned from API.")
            st.error("Error fetching data. Please check the stock symbol and try again.")
            return pd.DataFrame()

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
        
        logger.info(f"Successfully fetched and processed data for {symbol}.")
        return df
    
    except requests.exceptions.RequestException as e:
        logger.exception(f"RequestException occurred: {str(e)}")
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")
        return pd.DataFrame()

# Function to create an Altair candlestick chart with volume
def create_altair_candlestick_chart(df, filename):
    try:
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
        logger.info(f"Chart saved as {filename}")
        return chart
    
    except Exception as e:
        logger.exception(f"Error creating or saving chart: {str(e)}")
        st.error(f"Error creating or saving chart: {str(e)}")
        return None

# Function to generate news summary for a given symbol
def generate_news_summary(symbol):
    try:
        # Use the symbol to fetch relevant news
        logger.info(f"Fetching news summary for {symbol}")
        res = agent_executor.invoke({
            "input": f"Use SERP to find the latest news for {symbol}, take only the description of the article."
        })
        
        # Summarize the fetched news
        res2 = agent_executor.invoke({"input": res["output"] + " Summarize this"})
        
        logger.info(f"Successfully generated news summary for {symbol}")
        return res2["output"]
    
    except Exception as e:
        logger.exception(f"Error generating news summary for {symbol}: {str(e)}")
        st.error(f"Error generating news summary: {str(e)}")
        return "No news summary available."

# Function to generate the report
def generate_report(stock_symbol):
    df = fetch_stock_data(stock_symbol, alpha_vantage_api_key)
    if df.empty:
        return
    
    report_file_base = f'reports/{stock_symbol}_daily_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    image_filename = f"{report_file_base}.png"
    
    create_altair_candlestick_chart(df, image_filename)
    
    # Generate the news summary
    news_summary = generate_news_summary(stock_symbol)
    
    # Placeholder content for the report
    stock_analysis = "This is a placeholder for stock analysis. Integrate actual analysis here."
    investment_analysis = "This is a placeholder for investment analysis. Integrate actual analysis here."
    
    report_content = f"""
    # {stock_symbol} Daily Briefing Report
    
    ![Candlestick Chart]({os.path.basename(image_filename)})
    
    ## News Summary
    {news_summary}
    
    ## Analytical Report 1
    {investment_analysis}
    
    ## Analytical Report 2
    {stock_analysis}
    """
    report_file = f'{report_file_base}.md'
    if not os.path.exists('reports'):
        os.makedirs('reports')
    with open(report_file, 'w') as f:
        f.write(report_content)
    logger.info(f"Report generated and saved as {report_file}")

# Function to load the report
def load_report(report_filename):
    report_base_name = os.path.splitext(report_filename)[0]
    image_file = f'reports/{report_base_name}.png'
    
    if os.path.exists(f'reports/{report_filename}'):
        with open(f'reports/{report_filename}', 'r') as f:
            report_content = f.read()
        
        return report_content, image_file
    else:
        logger.warning(f"Report {report_filename} not found.")
        return None, None

# Setup Hugging Face LLM and LangChain agent
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta", huggingfacehub_api_token=hf_key
)

chat_model = ChatHuggingFace(llm=llm, huggingfacehub_api_token=hf_key)

# Import from composio_langchain
composio_toolset = ComposioToolSet()

# Set up tools using Composio
tools = composio_toolset.get_tools(apps=[App.SERPAPI])

# Set up ReAct style prompt
prompt = hub.pull("hwchase17/react-json")
prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)

# Define the agent
chat_model_with_stop = chat_model.bind(stop=["\nInvalidStop"])
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
    }
    | prompt
    | chat_model_with_stop
    | ReActJsonSingleInputOutputParser()
)

# Instantiate AgentExecutor
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)
