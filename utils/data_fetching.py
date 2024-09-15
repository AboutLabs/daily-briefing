import pandas as pd
import requests
import streamlit as st
from .logging_config import logger

def fetch_stock_data(symbol, api_key, start_date=None, end_date=None):
    # Default to a 1-year range if no date range is provided
    if start_date is None:
        start_date = (pd.Timestamp.now() - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = pd.Timestamp.now().strftime('%Y-%m-%d')

    base_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": "5000",
        "apiKey": api_key
    }

    try:
        logger.info(f"Request URL: {base_url} with params: {params}")
        response = requests.get(base_url, params=params)
        logger.info(f"Fetching stock data for {symbol}: Status code {response.status_code}")

        if response.status_code != 200:
            error_message = response.json().get("error", response.text)
            logger.error(f"Error fetching data: {error_message}")
            st.error(f"Error fetching data: {error_message}")
            return pd.DataFrame()
        
        data = response.json()
        
        # Check for 'status' key and handle non-OK statuses
        if data.get("status") != "OK":
            status = data.get("status", "Unknown status")
            logger.warning(f"Non-OK status received: {status}")
            if status == "DELAYED":
                st.warning("Data retrieval is delayed. The data may not be up-to-date.")
            else:
                st.error(f"Error fetching data: {status}")
                return pd.DataFrame()

        if "results" not in data or not data["results"]:
            logger.error(f"No data found for stock symbol: {symbol} between {start_date} and {end_date}.")
            st.error("No data found for the specified stock symbol. Please try again.")
            return pd.DataFrame()

        # Parsing data as per Polygon.io documentation
        results = data["results"]
        df = pd.DataFrame(results)
        df['Date'] = pd.to_datetime(df['t'], unit='ms')
        df = df.rename(columns={
            'o': 'Open',
            'h': 'High',
            'l': 'Low',
            'c': 'Close',
            'v': 'Volume'
        })
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        logger.info(f"Successfully fetched and processed data for {symbol} between {start_date} and {end_date}.")
        return df
    
    except requests.exceptions.RequestException as e:
        logger.exception(f"RequestException occurred: {str(e)}")
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")
        return pd.DataFrame()
