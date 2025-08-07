import sys
import uuid
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class SingleDocIngestor:

    def __init__(self):
        try:
            self.log = CustomLogger().get_logger(__name__)

        except Exception as e:
            self.log.error("Error in initializing SingleDocIngestor", error = str(e))
            raise DocumentPortalException(error_message="Error in initializing SingleDocIngestor", error_details=sys) from e
        

    def ingest_files(self):
        try:
            pass        
        except Exception as e:
            self.log.error("Error in ingesting files", str(e))
            raise DocumentPortalException(error_message="Error in ingesting files", error_details=sys) from e
        
    def create_retriever(self):
        try:
            pass        
        except Exception as e:
            self.log.error("Failed to create retriever", str(e))
            raise DocumentPortalException(error_message="Failed to create retriever", error_details=sys) from e


