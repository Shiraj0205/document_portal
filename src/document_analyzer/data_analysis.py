import os
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import *


class DocumentAnalyzer:

    """Document Analyzer Class
    """
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            # Prepare parsers
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)

            self.prompt = prompt
            self.log.info("Document analyzer initialized successfully.")
            
        except Exception as e:
            self.log.error(f"Error in initialzing document analyzer. {e}")
            raise DocumentPortalException(error_message="Error in initialzing document analyzer.", error_details=e) from e

    def analyze_document(self, document_text: str) -> dict:
        """Analyze the document
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            self.log.info("Meta data analysis chain initialized")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            self.log.info("Meta data execution successful", keys=list(response.keys()))
            return response

        except Exception as e:
            self.log.error("Meta data analysis failed", error=str(e))
            raise DocumentPortalException(error_message="Meta data analysis failed", error_details=e) from e
        
