# main.py

import streamlit as st
from utils.report_generation import generate_report

# Safely retrieve secrets from secrets.toml or Streamlit Cloud's secret manager
alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]

# Streamlit interface
st.title("Investment Analysis Report Generator")

stock_symbol = st.text_input("Enter stock symbol:", "AAPL")

if st.button("Generate Report"):
    report_file = generate_report(stock_symbol)
    if report_file:
        st.success(f"Report generated: {report_file}")
        with open(report_file, 'r') as f:
            st.markdown(f.read())
    else:
        st.error("Failed to generate report.")
