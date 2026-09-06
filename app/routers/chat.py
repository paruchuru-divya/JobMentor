import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gemini_service import gemini_service
from app.services.firestore_service import firestore_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    document_id: Optional[str] = None
    document_text: Optional[str] = None
    question: str
    session_id: Optional[str] = None


class ChatTurn(BaseModel):
    role: str
    content: str


@router.post("/")
async def chat_with_document(req: ChatRequest):
    """
    Chat with an uploaded PDF document or raw document text using Google Gemini.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Retrieve document text
    doc_text = req.document_text or ""
    if req.document_id:
        doc = await firestore_service.get_document_record(req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Referenced document not found.")
        doc_text = doc.get("full_text", "")

    if not doc_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No document text available. Please upload a PDF or supply text."
        )

    session_id = req.session_id or str(uuid.uuid4())

    # Fetch prior turns if session exists
    session = await firestore_service.get_chat_session(session_id)
    history = session.get("messages", []) if session else []

    # Call Gemini
    result = gemini_service.chat_with_pdf(
        document_text=doc_text,
        question=req.question,
        history=history
    )

    # Save to Firestore session
    await firestore_service.save_chat_message(session_id, req.document_id or "direct", "user", req.question)
    await firestore_service.save_chat_message(session_id, req.document_id or "direct", "assistant", result.get("answer", ""))

    return {
        "success": True,
        "session_id": session_id,
        "answer": result.get("answer", ""),
        "suggested_follow_ups": result.get("suggested_follow_ups", []),
        "confidence": result.get("confidence", "High"),
        "source_excerpts": result.get("source_excerpts", [])
    }


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve full conversation history for a chat session."""
    session = await firestore_service.get_chat_session(session_id)
    if not session:
        return {"session_id": session_id, "messages": []}
    return {"session_id": session_id, "messages": session.get("messages", [])}
