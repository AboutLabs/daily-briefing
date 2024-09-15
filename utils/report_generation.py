import os
import pandas as pd
import requests
import streamlit as st
from .data_fetching import fetch_stock_data
from .charting import create_altair_candlestick_chart
from .agents import create_investment_crew
from .logging_config import logger

def generate_report(stock_symbol):
    # Display status feedback to the user
    st.info("Creating report...")

    # Access the API keys from Streamlit secrets
    polygon_api_key = st.secrets["POLYGON_API_KEY"]
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    serper_api_key = st.secrets["SERPER_API_KEY"]

    # Fetch stock data using Polygon.io
    try:
        df = fetch_stock_data(stock_symbol, polygon_api_key)
        if df.empty:
            logger.error(f"No data found for stock symbol: {stock_symbol}.")
            st.error("No data found for the specified stock symbol. Please try again.")
            return None  # Return None if no data is found
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error while fetching data: {e}")
        st.error("Connection error occurred. Please check your network and try again.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching data: {e}")
        st.error("An unexpected error occurred while fetching data. Please try again later.")
        return None

    # Create a base filename for the report and chart image
    report_file_base = f'reports/{stock_symbol}_daily_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    image_filename = f"{report_file_base}.png"

    # Generate and save the candlestick chart
    try:
        create_altair_candlestick_chart(df, image_filename)
    except Exception as e:
        logger.error(f"Error creating or saving chart: {e}")
        st.error("Error occurred while creating or saving the chart. Please try again.")
        return None  # Return None if chart creation fails

    # Trigger Crew AI agents to perform analysis using the OpenAI API key
    try:
        investment_crew = create_investment_crew(stock_symbol, openai_api_key)
        res = investment_crew.kickoff()
        logger.debug(f"Task output: {res}")

        # Assuming res is a dictionary or a similar structure
        stock_analysis = res.get('analysis', "Analysis placeholder.") if isinstance(res, dict) else str(res)
        investment_recommendation = res.get('recommendation', "Recommendation placeholder.") if isinstance(res, dict) else "No recommendation available."
    except AttributeError as e:
        logger.error(f"AttributeError: {e}. The CrewOutput object may not contain the expected keys.")
        st.error("Error occurred during analysis. Please try again.")
        return None  # Return None if analysis fails
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        st.error("An unexpected error occurred during analysis. Please try again.")
        return None  # Return None if any other exception occurs

    # Generate the report content
    report_content = f"""
    # {stock_symbol} Daily Briefing Report

    ![Candlestick Chart]({os.path.basename(image_filename)})

    ## Analysis
    {stock_analysis}

    ## Recommendation
    {investment_recommendation}
    """

    # Save the report to a markdown file
    report_file = f'{report_file_base}.md'
    if not os.path.exists('reports'):
        os.makedirs('reports')  # Create the reports directory if it doesn't exist
    try:
        with open(report_file, 'w') as f:
            f.write(report_content)
    except Exception as e:
        logger.error(f"Error writing report to file: {e}")
        st.error("Error occurred while saving the report. Please try again.")
        return None  # Return None if report saving fails

    logger.info(f"Report generated successfully: {report_file}")
    st.success(f"Report generated successfully: {os.path.basename(report_file)}")
    return report_file  # Return the path to the generated report
