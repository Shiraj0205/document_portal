import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
import uuid
import streamlit as st

class ConversationalRAG:

    def __init__(self, session_id: str, retriever):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            
            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            self.log.info("Create history aware retriever", session_id=self.session_id)
            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)

            self.log.info("Created RAG chain", session_id=self.session_id)
            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            self.log.info("Created RunnableWithMessageHistory", session_id=session_id)

        except Exception as e:
            self.log.error("Error in initializing ConversationalRAG.", error = str(e))
            raise DocumentPortalException(error_message="Error in initializing ConversationalRAG.", error_details=sys) from e
        
    def _load_llm(self):
        """
        Load LLM
        """
        try:
            llm = ModelLoader().load_llm()
            #self.log.info("LLM loaded successfully.", class_name=llm.__class__.__name__)
            self.log.info("LLM loaded successfully.")
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM", error = str(e))
            raise DocumentPortalException(error_message="Failed to load LLM.", error_details=sys) from e
        
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """
        Get Session History
        """
        try:
            if "store" not in st.session_state:
                st.session_state.store = {}

            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
                self.log.info("New chat session history created", session_id=session_id)

            return st.session_state.store[session_id]
        except Exception as e:
            self.log.error("Failed to access session history", session_id=session_id, error=str(e))
            raise DocumentPortalException("Failed to retrieve session history", sys) from e

        
    def load_retriever_from_files(self, index_path: str):
        """
        Load Retriever from Files
        """
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found", index_path)
            
            vectorstore = FAISS.load_local(folder_path=index_path, embeddings=embeddings)
            self.log.info("Loaded retriever from FAISS index", index_path=index_path)
            return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

        except Exception as e:
            self.log.error("Failed to load retriever from FAISS.", error = str(e))
            raise DocumentPortalException(error_message="Failed to load retriever from FAISS.", error_details=sys) from e
        
    def invoke(self, user_input: str) -> str:
        """
        Invoke conversational RAG
        """
        try:
            response = self.chain.invoke(
                { "input": user_input }, 
                config={"configurable": {"session_id": self.session_id}}
                )
            answer = response.get("answer", "No answer")
            
            if not answer:
                self.log.warning("No answer received", session_id = self.session_id)

            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:200])
            return answer


        except Exception as e:
            self.log.error("Failed to invoke conversational RAG.", error = str(e))
            raise DocumentPortalException(error_message="Failed to invoke conversational RAG.", error_details=sys) from e
