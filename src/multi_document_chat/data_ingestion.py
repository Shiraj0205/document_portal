import os
import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from datetime import datetime, timezone
import uuid
from utils.model_loader import ModelLoader
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class DocumentIngestor:
    """
    Document Ingestor
    """

    SUPPORTED_FILE_TYPES = {'.pdf', '.docx', '.txt', '.md'}

    def __init__(self, temp_dir: str = "data/mult_document_chat", faiss_dir: str = "faiss_index", session_id: str | None = None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            # Session Directories
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.temp_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info("Document initialized", 
                            temp_base = str(self.session_temp_dir),
                            faiis_base = str(self.faiss_dir),
                            session_id = session_id
                            temp_session_dir = str(self.session_temp_dir), 
                            faiss_session_dir=str(self.session_faiss_dir)
                          )

        except Exception as e:
            self.log.error("Error initilizing data ingestion. {e}")
            raise DocumentPortalException(error_message="Error initilizing data ingestion", error_details=e) from e


    def ingest_file(self, uploaded_files):
        try:
            documents = []
            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning("Unsupported file", file_name = uploaded_file.name)
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                self.log.info("File saved for ingestion", 
                              file_name = uploaded_file.name, 
                              saved_as = str(temp_path), 
                              session_id = self.session_id)
                
                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == ".txt":
                    loader = TextLoader(str(temp_path), encoding="utf-8")
                else:
                    self.log.warning("Unsupported file type encountered.", file_name = uploaded_file.name)

                docs= loader.load()
                documents.extend(docs)

            if not documents:
                raise DocumentPortalException(error_message="No valid documents found", error_details=sys)
                
            self.log.info("All Document loaded", total_docs = len(documents), session_id = self.session_id)
            return self._create_retriever(documents=documents)

        except Exception as e:
            self.log.error("Error ingesting a file. {e}")
            raise DocumentPortalException(error_message="Error ingesting a file", error_details=e) from e


    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents=documents)

            self.log.info("Document split into chunks", total_chunks=len(chunks), session_id = self.session_id)
            embeddings = self.model_loader.load_embeddings()
            vectorestore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            vectorestore.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index saved to disk", path=str(self.session_faiss_dir), session_id = self.session_id)
            retriever = vectorestore.as_retriever(search_type="similarity", search_kwargs = { "k": 5 })
            return retriever
        except Exception as e:
            self.log.error("Error creating retriever. {e}")
            raise DocumentPortalException(error_message="Error creating retriever.", error_details=e) from e

