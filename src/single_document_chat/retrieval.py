import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
#from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
import uuid

class ConversationalRAG:

    def __init__(self, session_id, retriever) -> None:
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = uuid.uuid4()

        except Exception as e:
            self.log.error("Error in initializing ConversationalRAG.", error = str(e))
            raise DocumentPortalException(error_message="Error in initializing ConversationalRAG.", error_details=sys) from e
        
    def _load_llm(self):
        """
        Load LLM
        """
        try:
            pass

        except Exception as e:
            self.log.error("Failed to load LLM", error = str(e))
            raise DocumentPortalException(error_message="Failed to load LLM.", error_details=sys) from e
        
    def _get_session_history(self, session_id: str):
        """
        Get Session History
        """
        try:
            pass

        except Exception as e:
            self.log.error("Failed to access session history.", error = str(e))
            raise DocumentPortalException(error_message="Failed to access session history.", error_details=sys) from e
        
    def load_retriever_from_files(self):
        """
        Load Retriever from Files
        """
        try:
            pass

        except Exception as e:
            self.log.error("Failed to load retriever from FAISS.", error = str(e))
            raise DocumentPortalException(error_message="Failed to load retriever from FAISS.", error_details=sys) from e
        
    def invoke(self):
        """
        Invoke conversational RAG
        """
        try:
            pass

        except Exception as e:
            self.log.error("Failed to invoke conversational RAG.", error = str(e))
            raise DocumentPortalException(error_message="Failed to invoke conversational RAG.", error_details=sys) from e
