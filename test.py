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

import io
from pathlib import Path
from src.document_compare.data_ingestion import DocumentIngestion
from src.document_compare.document_compare import DocumentCompareLLM

def load_fake_uploaded_file(file_path: Path):
    return io.BytesIO(file_path.read_bytes())

def test_compare_documents():
    """
    Test Document comparison method
    """
    print("Document Comparison Started.")
    ref_path = Path("D:\\Data\\Projects\\document_portal\\data\\document_compare\\Long_Report_V1.pdf")
    act_path = Path("D:\\Data\\Projects\\document_portal\\data\\document_compare\\Long_Report_V2.pdf")

    class FakeUpload:
        """
        Upload Raker Class
        """
        def __init__(self, file_path: Path):
            self.name = file_path.name
            self._buffer = file_path.read_bytes()

        def getbuffer(self):
            return self._buffer
    
    comparer = DocumentIngestion()
    ref_upload = FakeUpload(ref_path)
    act_upload = FakeUpload(act_path)

    ref_file, act_file = comparer.save_uploaded_file(reference_file=ref_upload, actual_file=act_upload)
    combined_text = comparer.combine_documents()

    print("\n Combined text preview (First 100 chars):\n")
    print(combined_text)

    llm_comparor = DocumentCompareLLM()
    comparison_diff = llm_comparor.compare_document(combined_text)

    print("\n Comparison Result \n")
    print(comparison_diff.head())


# Invoke Test
if __name__ == "__main__":
        test_compare_documents()

