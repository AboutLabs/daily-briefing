import streamlit as st
import os

st.set_page_config(page_title="Report Page")

# Display the logo
logo_path = "assets/dtb-logo.jpg"
st.image(logo_path, width=128)

st.title("Report Management")

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

    # Only try to read and display the selected report if it still exists
    if os.path.exists(f'reports/{selected_report}'):
        with open(f'reports/{selected_report}', 'r') as f:
            st.markdown(f.read())

        # Display the corresponding image if it exists
        if os.path.exists(image_file):
            st.image(image_file, caption="Candlestick Chart")
        else:
            st.write("No associated image found.")
