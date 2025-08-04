import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentAnalyzer:
    """
        DocumentAnalyzer Class
    """
    def __init__(self, base_dir):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def delete_existing_file(self):
        """
        Delete existing file
        """
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                        self.log.info("File deleted", directory=str(self.base_dir))
        except Exception as e:
            self.log.error("Error deleting document. {e}")
            raise DocumentPortalException(error_message="Error deleting document", error_details=e) from e

    def save_uploaded_file(self, reference_file, actual_file):
        """
        Save uploaded 
        """
        try:
            self.delete_existing_file()
            self.log.info("Existing file deleted successfully")
            
            ref_path = self.base_dir/reference_file
            act_path = self.base_dir/actual_file

            if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
                raise ValueError("Only PDF file are allowed")
            
            with open(act_path, "wb") as f:
                f.write(actual_file.getbuffer())
            
            with open(ref_path, "wb") as f:
                f.write(reference_file.getbuffer())

            self.log.info("Files saved", reference=str(ref_path), actual=str(act_path))
            return ref_path, act_path

        except Exception as e:
            self.log.error("Error saving document. {e}")
            raise DocumentPortalException(error_message="Error saving document", error_details=e) from e

    def read_pdf(self, pdf_path: Path)-> str:
        """
        Read PDF Document
        """
        try:
            with fitz.open(self, pdf_path) as doc:
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