import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from langchain_community.vectorstores import faiss
from src.document_ingestion.data_ingestion import (
    DocHandler, 
    DocumentComparator,
    ChatIngestor,
    FaissManager
)

from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_compare import DocumentCompareLLM
from src.document_chat.retrieval import ConversationalRAG

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")  # <--- keep consistent with save_local()

app = FastAPI(title="Document Portal API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, str]:
    return { "status": "ok", "service": "document_portal" }


class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename

    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()
    
    
def _read_pdf_handler(handler: DocHandler, path: str) -> str:
    """
    Helper function to read PDF using DocHandler
    """
    if hasattr(handler, "read_pdf"):
        return handler.read_pdf(path)
    
    if hasattr(handler, "read_"):
        return handler.read_(path)
    
    raise RuntimeError("DocHandler has neither read_pdf nor read_ method.")

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    """
    Analyze Document Action
    """
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = _read_pdf_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {e}") from e


@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        dc = DocumentComparator()
        ref_path, act_path = dc.save_uploaded_files(
            FastAPIFileAdapter(reference), FastAPIFileAdapter(actual)
        )
        _ = ref_path, act_path
        combined_text = dc.combine_documents()
        comp = DocumentCompareLLM()
        df = comp.compare_document(combined_text)
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document comparison failed: {e}") from e

    

@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
    ) -> Any:
    try:
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        # NOTE: ensure your ChatIngestor saves with index_name="index" or FAISS_INDEX_NAME
        # e.g., if it calls FAISS.save_local(dir, index_name=FAISS_INDEX_NAME)
        ci.built_retriver(
            wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k
        )
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}") from e
    

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
    ) -> Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        # Prepare FAISS Index Path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        # Initialize LCEL-style RAG pipeline
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME)  # build retriever + chain
        response = rag.invoke(question, chat_history=[])

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}") from e



# To execute fast API
# uvicorn api.main:app --reload