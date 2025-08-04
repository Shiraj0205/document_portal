import sys
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentCompareLLM:
    """
        Document Compare Class
    """

    def __init__(self):
        pass

    def compare_document(self):
        """
            Compare two documents
        """
        pass

    def _format_response(self):
        """
            Format the response from LLM into structured format
        """
        pass
