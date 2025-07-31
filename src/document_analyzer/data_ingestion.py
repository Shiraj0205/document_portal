import os
import uuid
import fitz
from datetime import datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentHandler:
    """Handles PDF Save and Read operations
    """

    def __init__(self, data_dir=None, session_id=None):
        try:
            self.log = CustomLogger().get_logger(name=__name__)
            self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analysis"))
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)

            self.log.info("Document Handler Initialed", session_id=self.session_id, session_path=self.session_path)
        
        except Exception as e:
            self.log.error(f"Error in initializing DocumentHandler: {e}")
            raise DocumentPortalException(error_message="Error in initializing DocumentHandler", error_details=e) from e



    def save_pdf(self, uploaded_file):
        """_summary_

        Args:
            uploaded_file (_type_): _description_

        Raises:
            DocumentPortalException: _description_
        """
        try:
            filename = uploaded_file.name
            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException(error_message="Invalid file type. Only PDFs are allowed")
            
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            self.log.info("PDF file saved successfully", file=filename, save_path=save_path, sessionid=self.session_id)
            return save_path

        except Exception as e:
            self.log.error(f"Error is saving the pdf. {e}")
            raise DocumentPortalException(error_message="Error in saving the pdf", error_details=e) from e


    def read_pdf(self, pdf_path: str) -> str:
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"\n--- Page {page_num} ---\n{page.get_text()}")
            text = "\n".join(text_chunks)

            self.log.info("PDF read successfully", pdf_path=pdf_path, session_id=self.session_id)
            return text
        except Exception as e:
            self.log.error(f"Error is reading the pdf. {e}")
            raise DocumentPortalException(error_message="Error in reading the pdf", error_details=e) from e



if __name__ == "__main__":
    from pathlib import Path
    from io import BytesIO
    doc_analyzer = DocumentHandler()

    pdf_path=r"D:\\Data\\Projects\\document_portal\\data\\document_analysis\\Aurora Dynamics.pdf"

    class DummyFile:

        def __init__(self, file_path):
            self.name = Path(file_path).name
            self._file_path = file_path

        def getbuffer(self):
            return open(self._file_path, "rb").read()
        
    dummy_pdf = DummyFile(pdf_path)
    #handler = DocumentHandler(session_id="test_session")
    handler = DocumentHandler()
    try:
        saved_path = handler.save_pdf(dummy_pdf)
        print(saved_path)

        content = handler.read_pdf(saved_path)
        print(content[:500])

    except Exception as e:
        print(f"Error: {e}")


