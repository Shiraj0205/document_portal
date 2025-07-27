import os
from datetime import datetime
import logging

class CustomLogger:

    def __init__(self, log_dir="logs"):
        log_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(log_dir, exist_ok=True)

        # Create a log file with the current timestamp
        log_file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        log_file_path = os.path.join(log_dir, log_file_name)

        # Configure the logging
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] - %(name)s (Line: %(lineno)d) - %(levelname)s - %(message)s",
            filename=log_file_path
        )

    # Create a logger instance
    def get_logger(self, name=__file__):
        return logging.getLogger(os.path.basename(name))
    
if __name__ == "__main__":
    logger = CustomLogger()
    logger = logger.get_logger(__file__)
    logger.info("Custom logger initialized.")