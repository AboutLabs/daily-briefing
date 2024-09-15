import streamlit as st
import os
from utils.report_generation import generate_report
from utils.helper import load_report
from utils.logging_config import logger

# Set page configuration
st.set_page_config(page_title="Daily Trading Briefing")

# Create a centered container with custom width
container = st.container()
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    # Set a max-width for the content in the middle column
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1200px;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Display the logo
    logo_path = "assets/dtb-logo.jpg"
    st.image(logo_path, width=128)

    # Title
    st.title("Daily Trading Briefing")

    # Input for stock symbol
    stock_symbol = st.text_input("Enter stock symbol:", "AAPL")

    # Generate Report Section
    if st.button("Generate Report"):
        report_file = generate_report(stock_symbol)
        if report_file:
            st.success(f"Report generated: {os.path.basename(report_file)}")
        else:
            st.error("Failed to generate report.")

    # Report Management Section
    st.write("### Available Reports")

    # List all .md reports in the reports directory
    reports = [report for report in os.listdir('reports') if report.endswith('.md')]
    selected_report = st.selectbox("Select a report to view or delete", reports)

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

        # Display the corresponding image if it exists
        if os.path.exists(image_file):
            st.image(image_file, caption="Candlestick Chart")

        # Load and display the selected report
        report_content, _ = load_report(selected_report)
        if report_content:
            st.markdown(report_content)
        else:
            st.error("Failed to load the report.")
