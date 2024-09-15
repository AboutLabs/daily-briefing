import os
from .logging_config import logger
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
