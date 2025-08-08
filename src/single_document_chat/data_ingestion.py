import sys
import uuid
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone

class SingleDocIngestor:
    """
    Single Document Ingestor
    """

    def __init__(self, data_dir: str = "data\single_document_chat", faiss_dir: str = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            self.model_loader = ModelLoader()
            self.log.info("Single Doc Ingestor Initialized", data_dir=str(self.data_dir), faiss_dir=str(self.faiss_dir))

        except Exception as e:
            self.log.error("Error in initializing SingleDocIngestor", error = str(e))
            raise DocumentPortalException(error_message="Error in initializing SingleDocIngestor", error_details=sys) from e
        

    def ingest_files(self, uploaded_files):
        """
        Ingest Files
        """
        try:
            documents = []
            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = self.data_dir / unique_filename
                with open(temp_path, "wb") as file_out:
                    file_out.write(uploaded_file.read())
                
                self.log.info("PDF saved for ingestion", filename=unique_filename)
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            
            self.log.info("PDF file loaded", count=len(documents))
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error("Error in ingesting files", str(e))
            raise DocumentPortalException(error_message="Error in ingesting files", error_details=sys) from e
        

    def _create_retriever(self, documents):
        """
        Create Retriever
        """
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)    
            chunks = splitter.split_documents(documents=documents)
            self.log.info("Documents split into chunks", count=len(chunks))

            embeddings = self.model_loader.load_embeddings()

            # Save FAISS Index
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            vectorstore.save_local(str(self.faiss_dir))
            self.log.info("Faiss index created and saved", faiss_path=str(self.faiss_dir))
            
            # Create Retriever
            retriever = vectorstore.as_retriever(searchtype="similarity", search_kwargs={"k": 5})
            self.log.info("Retriever created successfully.", retriever_type=str(type(retriever)))
            return retriever

        except Exception as e:
            self.log.error("Failed to create retriever", str(e))
            raise DocumentPortalException(error_message="Failed to create retriever", error_details=sys) from e
        


