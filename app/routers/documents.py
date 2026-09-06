import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel

from app.config import settings
from app.services.pdf_service import pdf_service
from app.services.firestore_service import firestore_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])


class DocumentResponse(BaseModel):
    id: str
    filename: str
    pages: int
    total_chars: int
    word_count: int
    text_preview: str
    created_at: str


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form("guest-user")
):
    """
    Upload a PDF document, extract text and structure, and save metadata to Firestore.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB.")

    # Extract text and metadata
    extraction = pdf_service.extract_text(content)
    if not extraction["success"]:
        raise HTTPException(status_code=422, detail=extraction["error"])

    doc_id = str(uuid.uuid4())
    filename = file.filename
    meta = extraction["metadata"]
    full_text = extraction["full_text"]

    # Optionally persist raw PDF file to local uploads directory
    local_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{filename}")
    try:
        with open(local_path, "wb") as f:
            f.write(content)
    except Exception:
        local_path = ""

    # Document record
    doc_record = {
        "id": doc_id,
        "filename": filename,
        "pages": meta["pages"],
        "total_chars": meta["total_chars"],
        "word_count": meta["word_count"],
        "full_text": full_text,
        "text_preview": full_text[:400] + ("..." if len(full_text) > 400 else ""),
        "user_id": user_id,
        "local_path": local_path
    }

    await firestore_service.save_document_record(doc_record)

    return {
        "success": True,
        "message": "Document parsed and saved successfully.",
        "document": {
            "id": doc_id,
            "filename": filename,
            "pages": meta["pages"],
            "total_chars": meta["total_chars"],
            "word_count": meta["word_count"],
            "text_preview": doc_record["text_preview"],
            "created_at": doc_record.get("created_at", "")
        }
    }


@router.get("/")
async def list_documents(limit: int = 20):
    """List recent documents saved in Firestore."""
    docs = await firestore_service.list_documents(limit=limit)
    # Exclude full_text from listing to keep payload small
    clean_docs = []
    for d in docs:
        clean_docs.append({
            "id": d.get("id"),
            "filename": d.get("filename"),
            "pages": d.get("pages", 0),
            "total_chars": d.get("total_chars", 0),
            "word_count": d.get("word_count", 0),
            "text_preview": d.get("text_preview", ""),
            "created_at": d.get("created_at", "")
        })
    return {"documents": clean_docs}


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Retrieve full text and metadata for a specific document."""
    doc = await firestore_service.get_document_record(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"document": doc}
