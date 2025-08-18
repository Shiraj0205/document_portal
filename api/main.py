import os
from pathlib import Path
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.document_ingestion.data_ingestion import (
    DocHandler, 
    DocumentComparator,
    ChatIngestor
)

from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_compare import DocumentCompareLLM
from src.document_chat.retrieval import ConversationalRAG
from utils.document_ops import FastAPIFileAdapter, read_pdf_handler
#from logger import GLOBAL_LOGGER as log

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

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    """Render Index.html

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, str]:
    """Api Health Endpoint

    Returns:
        Dict[str, str]: _description_
    """
    #log.info("Health check passed.")
    return { "status": "ok", "service": "document_portal" }


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    """Analyze Document Action

    Args:
        file (UploadFile, optional): _description_. Defaults to File(...).

    Raises:
        HTTPException: _description_

    Returns:
        Any: _description_
    """
    try:
        dh = DocHandler()
        saved_path = dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf_handler(dh, saved_path)
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    except Exception as e:
        #log.info(f"Document analysis failed. {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {e}") from e


@app.post("/compare")
async def compare_documents(
    reference: UploadFile = File(...), 
    actual: UploadFile = File(...)
    ) -> Any:
    """_summary_

    Args:
        reference (UploadFile, optional): _description_. Defaults to File(...).
        actual (UploadFile, optional): _description_. Defaults to File(...).

    Raises:
        HTTPException: _description_

    Returns:
        Any: _description_
    """
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
    """Generate Chat Index

    Args:
        files (List[UploadFile], optional): _description_. Defaults to File(...).
        session_id (Optional[str], optional): _description_. Defaults to Form(None).
        use_session_dirs (bool, optional): _description_. Defaults to Form(True).
        chunk_size (int, optional): _description_. Defaults to Form(1000).
        chunk_overlap (int, optional): _description_. Defaults to Form(200).
        k (int, optional): _description_. Defaults to Form(5).

    Raises:
        HTTPException: _description_

    Returns:
        Any: _description_
    """
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
    """Generate Response to user Chat Query

    Args:
        question (str, optional): _description_. Defaults to Form(...).
        session_id (Optional[str], optional): _description_. Defaults to Form(None).
        use_session_dirs (bool, optional): _description_. Defaults to Form(True).
        k (int, optional): _description_. Defaults to Form(5).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        Any: _description_
    """
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400,
                                detail="session_id is required when use_session_dirs=True")

        # Prepare FAISS Index Path
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore

        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, 
                                detail=f"FAISS index not found at: {index_dir}")

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
# uvicorn api.main:app --host 0.0.0.0 --port 8083 --reload
# uvicorn api.main:app --port 8083 --reload
