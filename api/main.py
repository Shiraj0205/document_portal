import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


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

@app.post("/analysis")
async def analyze_document(file: UploadFile = File(...)) -> Any:
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {e}")

@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document comparison failed: {e}")
    

@app.post("/chat/index")
async def chat_build_index() -> Any:
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat indexing failed: {e}")
    

@app.post("/chat/query")
async def chat_query() -> Any:
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat query failed: {e}")

# To execute fast API
# uvicorn api.main:app --reload