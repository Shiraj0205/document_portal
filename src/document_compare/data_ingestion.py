import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from datetime import datetime, timezone
import uuid


class DocumentIngestion:
    """
        DocumentAnalyzer Class
    """
    def __init__(self, base_dir: str ="data/document_compare", session_id = None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)

    # def delete_existing_file(self):
    #     """
    #     Delete existing file
    #     """
    #     try:
    #         if self.base_dir.exists() and self.base_dir.is_dir():
    #             for file in self.base_dir.iterdir():
    #                 if file.is_file():
    #                     file.unlink()
    #                     self.log.info("File deleted", directory=str(self.base_dir))
    #     except Exception as e:
    #         self.log.error("Error deleting document. {e}")
    #         raise DocumentPortalException(error_message="Error deleting document", error_details=e) from e

    def save_uploaded_file(self, reference_file, actual_file):
        """
        Save uploaded 
        """
        try:
            #self.delete_existing_file()
            self.log.info("Existing file deleted successfully")
            
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name

            if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
                raise ValueError("Only PDF file are allowed")
            
            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            self.log.info("Files saved", reference=str(ref_path), actual=str(act_path), session=self.session_id)
            return ref_path, act_path

        except Exception as e:
            self.log.error("Error saving document. {e}")
            raise DocumentPortalException(error_message="Error saving document", error_details=e) from e

    def read_pdf(self, pdf_path: Path)-> str:
        """
        Read PDF Document
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted {pdf_path.name}")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()

                    if text.strip():
                        all_text.append(f"\n --- Page {page_num + 1} ---\n {text}")

                self.log.info("PDF read successfully", file=str(pdf_path), pages=len(all_text))
                return "\n".join(all_text)
        except Exception as e:
            self.log.error("Error reading document. {e}")
            raise DocumentPortalException(error_message="Error reading document", error_details=e) from e
        
    def combine_documents(self) -> str:
        try:
            content_dict = {}
            doc_parts = []

            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix == ".pdf":
                    content_dict[filename.name] = self.read_pdf(filename)
            
            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")
            
            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined", count=len(doc_parts))
            return combined_text

        except Exception as e:
            self.log.error("An error occured combining documents", str(e))
            raise DocumentPortalException("An error occured combining documents", sys) from e
        
    def clean_old_session(self, keep_latest = 3):
        """
        Method to remove older session data folders. Keep latest n data folders
        """
        try:
            print(f"Base Dir : {self.base_dir}")
            session_folders_sorted = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
                )
            
            for folder in session_folders_sorted:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info("Old session folder deleted", path = str(folder))

        except Exception as e:
            self.log.error("Failed to remove old session data folders.", str(e))
            raise DocumentPortalException(error_message="Failed to remove old session data folders.", error_details=sys) from e
