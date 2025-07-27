import sys
import traceback
from logger.custom_logger import CustomLogger
logger = CustomLogger().get_logger(__file__)


class DocumentPortalException(Exception):
    """Base class for all exceptions in the Document Portal application."""

    def __init__(self, error_message, error_details: sys):
        # Exception Traceback
        _, _, exc_tb = error_details.exc_info()
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.line_number = exc_tb.tb_lineno
        self.error_message = str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
        #super().__init__(self.error_message)

    def __str__(self):
        return f"""
        Error in [{self.file_name}] at line [{self.line_number}]
        Message: {self.error_message}
        Traceback: 
        {self.traceback_str}
        """

if __name__ == "__main__":
    try:
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc = DocumentPortalException(e,sys)
        logger.error(app_exc)
        raise app_exc