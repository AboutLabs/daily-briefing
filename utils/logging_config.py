# utils/logging_config.py

import logging

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
