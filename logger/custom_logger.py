import os
from datetime import datetime
import logging

class CustomLogger:

    def __init__(self):
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Create a log file with the current timestamp
        LOG_FILE_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        LOG_FILE_PATH = os.path.join(log_dir, LOG_FILE_NAME)

        # Configure the logging
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] - %(name)s (Line: %(lineno)d) - %(levelname)s - %(message)s",
            filename=LOG_FILE_PATH
        )

    # Create a logger instance
    def get_logger(self, name=__file__):
        return logging.getLogger(os.path.basename(name))
    
if __name__ == "__main__":
    logger = CustomLogger()
    logger = logger.get_logger(__file__)
    logger.info("Custom logger initialized.")