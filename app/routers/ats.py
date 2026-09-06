from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gemini_service import gemini_service
from app.services.firestore_service import firestore_service

router = APIRouter(prefix="/api/ats", tags=["ATS Assessment"])


class ResumeAnalysisRequest(BaseModel):
    document_id: Optional[str] = None
    resume_text: Optional[str] = None


class ATSEvaluationRequest(BaseModel):
    document_id: Optional[str] = None
    resume_text: Optional[str] = None
    job_description: str
    job_title: Optional[str] = "Target Role"
    company_name: Optional[str] = "Target Company"
    user_id: Optional[str] = "guest-user"


@router.post("/analyze-resume")
async def analyze_resume(req: ResumeAnalysisRequest):
    """
    Perform deep structural and skills extraction on a resume.
    """
    resume_text = req.resume_text or ""
    if req.document_id:
        doc = await firestore_service.get_document_record(req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Referenced resume document not found.")
        resume_text = doc.get("full_text", "")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required.")

    analysis = gemini_service.analyze_resume(resume_text)
    return {
        "success": True,
        "analysis": analysis
    }


@router.post("/evaluate")
async def evaluate_ats_compatibility(req: ATSEvaluationRequest):
    """
    Evaluate candidate resume against a job description.
    Returns ATS match score, keyword breakdown, and bullet point improvements.
    Saves the audit in Firestore.
    """
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required for ATS assessment.")

    resume_text = req.resume_text or ""
    if req.document_id:
        doc = await firestore_service.get_document_record(req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Referenced resume document not found.")
        resume_text = doc.get("full_text", "")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required.")

    # Call Gemini ATS evaluation
    evaluation = gemini_service.evaluate_ats_match(
        resume_text=resume_text,
        job_description=req.job_description
    )

    # Prepare audit record for Firestore
    audit_record = {
        "job_title": req.job_title,
        "company_name": req.company_name,
        "document_id": req.document_id,
        "overall_score": evaluation.get("overall_score", 0),
        "rating": evaluation.get("rating", "Evaluated"),
        "sub_scores": evaluation.get("sub_scores", {}),
        "matching_keywords": evaluation.get("matching_keywords", []),
        "missing_critical_keywords": evaluation.get("missing_critical_keywords", []),
        "bullet_point_rewrites": evaluation.get("bullet_point_rewrites", []),
        "quick_wins": evaluation.get("quick_wins", []),
        "skills_gap_analysis": evaluation.get("skills_gap_analysis", ""),
        "user_id": req.user_id
    }

    audit_id = await firestore_service.save_ats_audit(audit_record)
    audit_record["id"] = audit_id

    return {
        "success": True,
        "audit_id": audit_id,
        "evaluation": evaluation
    }


@router.get("/audits")
async def list_audits(limit: int = 20):
    """List previous ATS audit reports stored in Firestore."""
    audits = await firestore_service.list_ats_audits(limit=limit)
    return {"audits": audits}
