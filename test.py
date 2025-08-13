# import os
# from pathlib import Path
# from src.document_analyzer.data_ingestion import DocumentHandler       # Your PDFHandler class
# from src.document_analyzer.data_analysis import DocumentAnalyzer  # Your DocumentAnalyzer class

# # Path to the PDF you want to test
# PDF_PATH = r"D:\\Data\\Projects\\document_portal\\data\document_analysis\\Aurora Dynamics.pdf"

# # Dummy file wrapper to simulate uploaded file (Streamlit style)
# class DummyFile:
#     """_summary_
#     """
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self):
#         """_summary_

#         Returns:
#             _type_: _description_
#         """
#         return open(self._file_path, "rb").read()

# def main():
#     try:
#         # ---------- STEP 1: DATA INGESTION ----------
#         print("Starting PDF ingestion...")
#         dummy_pdf = DummyFile(PDF_PATH)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")
        
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         # ---------- STEP 2: DATA ANALYSIS ----------
#         print("Starting metadata analysis...")
#         analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
#         analysis_result = analyzer.analyze_document(text_content)

#         # ---------- STEP 3: DISPLAY RESULTS ----------
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")

# if __name__ == "__main__":
#     main()



# Test Document Comparer
# import io
# from pathlib import Path
# from src.document_compare.data_ingestion import DocumentIngestion
# from src.document_compare.document_compare import DocumentCompareLLM

# def load_fake_uploaded_file(file_path: Path):
#     return io.BytesIO(file_path.read_bytes())

# def test_compare_documents():
#     """
#     Test Document comparison method
#     """
#     print("Document Comparison Started.")
#     ref_path = Path("D:\\Data\\Projects\\document_portal\\data\\document_compare\\Long_Report_V1.pdf")
#     act_path = Path("D:\\Data\\Projects\\document_portal\\data\\document_compare\\Long_Report_V2.pdf")

#     class FakeUpload:
#         """
#         Upload Raker Class
#         """
#         def __init__(self, file_path: Path):
#             self.name = file_path.name
#             self._buffer = file_path.read_bytes()

#         def getbuffer(self):
#             return self._buffer
    
#     comparer = DocumentIngestion()
#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)

#     # Save Files and Combine Text
#     ref_file, act_file = comparer.save_uploaded_file(reference_file=ref_upload, actual_file=act_upload)
#     combined_text = comparer.combine_documents()
#     comparer.clean_old_session(keep_latest=3)

#     print("\n Combined text preview (First 100 chars):\n")
#     print(combined_text)

#     llm_comparor = DocumentCompareLLM()
#     comparison_diff = llm_comparor.compare_document(combined_text)

#     print("\n Comparison Result \n")
#     print(comparison_diff.head())


# # Invoke Test
# if __name__ == "__main__":
#         test_compare_documents()


# Test Single Document Q&A
# import sys
# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from src.single_document_chat.data_ingestion import SingleDocIngestor
# from src.single_document_chat.retrieval import ConversationalRAG
# from utils.model_loader import ModelLoader
# from datetime import datetime
# import uuid

# FAISS_INDEX_PATH = Path("faiss_index")

# def test_conversation_rag_on_pdf(pdf_path: str, question: str):
#     """
#     Test Conversational RAG
#     """
#     try:
#         model_loader = ModelLoader()
#         if FAISS_INDEX_PATH.exists():
#             print("Loading faiss index.")
#             embeddings = model_loader.load_embeddings()
#             vectorstore = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH), embeddings=embeddings, allow_dangerous_deserialization=True)
#             retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":5})
#         else:
#             print("FAISS index not found. Ingesting PDF and creating index.")
#             with open(pdf_path, "rb") as file:
#                 uploaded_files = [file]
#                 ingestor = SingleDocIngestor()
#                 retriever = ingestor.ingest_files(uploaded_files)

#         print("Running Conversational RAG")
#         #session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
#         session_id = "session_test_conventional_rag"
#         rag = ConversationalRAG(retriever=retriever, session_id=session_id)
#         response = rag.invoke(question)
#         print(f"\nQuestion: {question} \nAnswer: {response}")

#     except Exception as e:
#         print("Test failed:", str(e))
#         sys.exit(1)

# if __name__ == "__main__":
#     PDF_PATH = "D:\\Data\\Projects\\document_portal\\data\\single_document_chat\\Aurora_Dynamics.pdf"
#     QUESTION = "When does Aurora Dynamics formed?"

#     if not Path(PDF_PATH).exists():
#         print(f"PDF file does not exist. {PDF_PATH}")
#         sys.exit(1)

#     # Run the test
#     test_conversation_rag_on_pdf(pdf_path=PDF_PATH, question=QUESTION)



## testing for multidoc chat
import sys
from pathlib import Path
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConversationalRAG

def test_document_ingestion_and_rag():
    try:
        test_files = [
            "data\\multi_document_chat\\market_analysis_report.docx",
            "data\\multi_document_chat\\NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "data\\multi_document_chat\\sample.pdf",
            "data\\multi_document_chat\\state_of_the_union.txt"
        ]
        
        uploaded_files = []
        
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File does not exist: {file_path}")
                
        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)
            
        ingestor = DocumentIngestor()
        retriever = ingestor.ingest_files(uploaded_files)
        
        for f in uploaded_files:
            f.close()
                
        session_id = "test_multi_doc_chat"
        rag = ConversationalRAG(session_id=session_id, retriever=retriever)
        
        question = "what is attention is all you need?"
        answer=rag.invoke(question)
        
        print("\n Question:", question)
        print("Answer:", answer)
        
        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    test_document_ingestion_and_rag()
