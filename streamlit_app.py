import streamlit as st
from utils.utils import generate_report

st.set_page_config(page_title="Main Page")

# Display the logo
logo_path = "assets/dtb-logo.jpg"
st.image(logo_path, width=128)

st.title("Daily Trading Briefing")

# Stock symbol input
stock_symbol = st.text_input("Enter Stock Symbol", "TSLA")

if st.button("Generate Briefing for Today"):
    generate_report(stock_symbol)
    st.success(f"Report for {stock_symbol} generated successfully!")
