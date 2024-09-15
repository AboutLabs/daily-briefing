# utils/data_fetching.py

import requests
import pandas as pd
import streamlit as st
from .logging_config import logger

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
