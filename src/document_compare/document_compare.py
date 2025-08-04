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
import pandas as pd

class DocumentCompareLLM:
    """
        Document Compare Class
    """

    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(name=__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY.get("document_comparison")
        self.chain = self.prompt | self.llm | self.parser | self.fixing_parser
        self.log.info("DocumentCompareLLM class initialized")

    def compare_document(self, combined_docs: str):
        """
            Compare two documents
        """
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions()
            }
            self.log.info("Starting document comparison", inputs=inputs)
            response = self.chain.invoke(inputs)
            self.log.info("Document comparison completed", response=response)
            return self._format_response(response)
        except Exception as e:
            self.log.error(f"Error comparing the document {e}")
            raise DocumentPortalException(error_message="Error comparing the document", error_details=e) from e


    def _format_response(self, response_parsed: list[dict]) -> pd.DataFrame: #type: ignore
        """
            Format the response from LLM into structured format
        """
        try:
            df = pd.DataFrame(response_parsed)
            self.log.info("Response formatted into DataFrame", dataframe=df)
            return df
        except Exception as e:
            self.log.error(f"Error formatting the response {str(e)}")
            raise DocumentPortalException(error_message="Error formatting the response", error_details=sys) from e
