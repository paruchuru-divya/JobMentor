from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gemini_service import gemini_service
from app.services.firestore_service import firestore_service

router = APIRouter(prefix="/api/email", tags=["Recruiter Outreach"])


class ColdEmailGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_description: str
    recruiter_name: Optional[str] = "Hiring Manager"
    company_name: Optional[str] = "Target Company"
    tone: Optional[str] = "Professional & Confident"
    user_id: Optional[str] = "guest-user"


class ColdEmailSaveRequest(BaseModel):
    recruiter_name: str
    company_name: str
    subject: str
    body: str
    tone: Optional[str] = "Professional"
    linkedin_note: Optional[str] = None
    user_id: Optional[str] = "guest-user"


@router.post("/generate")
async def generate_cold_email(req: ColdEmailGenerateRequest):
    """
    Generate tailored cold outreach emails to recruiters and hiring managers.
    """
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description context is required.")

    resume_text = req.resume_text or ""
    if req.document_id:
        doc = await firestore_service.get_document_record(req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Referenced resume document not found.")
        resume_text = doc.get("full_text", "")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required to personalize outreach.")

    email_package = gemini_service.generate_cold_email(
        resume_text=resume_text,
        job_description=req.job_description,
        recruiter_name=req.recruiter_name,
        company_name=req.company_name,
        tone=req.tone
    )

    return {
        "success": True,
        "email_package": email_package
    }


@router.post("/save")
async def save_cold_email(req: ColdEmailSaveRequest):
    """
    Save a generated cold email draft to Firestore.
    """
    email_data = {
        "recruiter_name": req.recruiter_name,
        "company_name": req.company_name,
        "subject": req.subject,
        "body": req.body,
        "tone": req.tone,
        "linkedin_note": req.linkedin_note,
        "user_id": req.user_id
    }
    email_id = await firestore_service.save_cold_email(email_data)
    return {
        "success": True,
        "email_id": email_id,
        "message": "Cold email saved to Firestore successfully."
    }


@router.get("/saved")
async def list_saved_emails(limit: int = 20):
    """List saved cold outreach emails from Firestore."""
    emails = await firestore_service.list_saved_emails(limit=limit)
    return {"saved_emails": emails}
