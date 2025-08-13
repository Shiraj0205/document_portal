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
from typing import List, Optional
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage


class ConversationalRAG:
    """
    Conversational RAG
    """

    def __init__(self, session_id: str, retriever = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]

            if retriever is None:
                raise ValueError("Retriever can not be None")
            
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info("ConversationalRAG RAG Initialized", session_id = self.session_id)
            
        except Exception as e:
            self.log.error("Error in initializing ConversationalRAG.", error = str(e))
            raise DocumentPortalException(error_message="Error in initializing ConversationalRAG.", error_details=sys) from e


    def load_retriever_from_faiss(self, index_path: str):
        """
        Load FAISS index from disk and convert to retriever
        """
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found", index_path = index_path)

            vectorstore = FAISS.load_local(index_path, 
                             embeddings, 
                             allow_dangerous_deserialization=True)
            
            self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs = {"k" : 5})
            #self._build_lcel_chain()
            return self.retriever

        except Exception as e:
            self.log.error("Error laoding retriever from FAISS", error = str(e))
            raise DocumentPortalException(error_message="Error laoding retriever from FAISS", error_details=sys) from e

    def invoke(self, user_input: str, chat_history: Optional[List[BaseMessage]] = None):
        try:
            chat_history = chat_history or []
            payload = { "input": user_input, "chat_history": chat_history }
            answer = self.chain.invoke(payload)
            
            if not answer:
                self.log.warning("No answer generated", user_input = user_input, session_id = self.session_id)
                return "No answer generated"

            self.log.info("Chain invoked successfully", 
                          session_id=self.session_id, 
                          user_input=user_input, 
                          answer_preview=answer[:200])
            
            return answer

        except Exception as e:
            self.log.error("Failed to invoke conversational RAG.", error = str(e))
            raise DocumentPortalException(error_message="Failed to invoke conversational RAG.", error_details=sys) from e

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()

            if not llm:
                raise ValueError("LLM could not be loaded")
            
            self.log.info("LLM loaded successfully.", session_id = self.session_id)
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM", error = str(e))
            raise DocumentPortalException(error_message="Failed to load LLM.", error_details=sys) from e

    @staticmethod
    def _format_documents(docs):
        return "\n\n".join(d.page_content for d in docs)

    def _build_lcel_chain(self):
        try:
            # 1. Rewrite question using chat history
            question_rewriter = (
                { "input": itemgetter("input"), "chat_history": itemgetter("chat_history") }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            # 2 . Retrieves docs for rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_documents

            # 3. Feed context, Original Input, Chat History into answer prompt
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()

            )

            self.log.info("LCEL graph built successfully.", session_id = self.session_id)

        except Exception as e:
            self.log.error("Failed to build lcel chain.", error = str(e))
            raise DocumentPortalException(error_message="Failed to build lcel chain.", error_details=sys) from e