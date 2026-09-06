import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    print("Testing /health endpoint...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    assert data["status"] == "healthy"
    assert data["cloud_run_label"] == "dev-tutorial=cloud-run-ai-challenge"
    print("[PASS] /health passed! Output:", data)

def test_chat():
    print("\nTesting /api/chat/ endpoint...")
    payload = {
        "question": "What is the candidate's experience with Cloud Run?",
        "document_text": "Alex Chen has 4 years of experience building applications on Google Cloud Run and FastAPI."
    }
    res = client.post("/api/chat/", json=payload)
    assert res.status_code == 200, f"Chat failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "answer" in data
    print("[PASS] /api/chat/ passed! Answer preview:", data["answer"][:120])

def test_ats_evaluation():
    print("\nTesting /api/ats/evaluate endpoint...")
    payload = {
        "resume_text": "Experienced Python and Cloud Run engineer with Docker, FastAPI, and Firestore skills.",
        "job_description": "Looking for a Senior Python engineer with Cloud Run, Docker, and Kubernetes experience.",
        "job_title": "Senior Cloud Engineer",
        "company_name": "Google Partner"
    }
    res = client.post("/api/ats/evaluate", json=payload)
    assert res.status_code == 200, f"ATS evaluation failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert "evaluation" in data
    eval_data = data["evaluation"]
    assert "overall_score" in eval_data
    assert "sub_scores" in eval_data
    assert "bullet_point_rewrites" in eval_data
    print(f"✓ /api/ats/evaluate passed! Score: {eval_data['overall_score']}%, Rating: {eval_data.get('rating')}")

def test_cold_email():
    print("\nTesting /api/email/generate endpoint...")
    payload = {
        "resume_text": "Cloud developer specializing in Google Cloud Run and FastAPI microservices.",
        "job_description": "We need an engineer to scale our cloud services and integrate AI agents.",
        "recruiter_name": "Sarah",
        "company_name": "InnovateAI",
        "tone": "Professional & Confident"
    }
    res = client.post("/api/email/generate", json=payload)
    assert res.status_code == 200, f"Email generation failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    pkg = data["email_package"]
    assert len(pkg.get("subject_lines", [])) > 0
    assert "email_body" in pkg
    print("[PASS] /api/email/generate passed! Subject lines count:", len(pkg["subject_lines"]))

def test_saved_email_flow():
    print("\nTesting /api/email/save and /api/email/saved...")
    save_payload = {
        "recruiter_name": "Alex",
        "company_name": "CloudTech",
        "subject": "Inquiry regarding role",
        "body": "Hi Alex, this is a test email.",
        "tone": "Professional"
    }
    res_save = client.post("/api/email/save", json=save_payload)
    assert res_save.status_code == 200
    res_list = client.get("/api/email/saved")
    assert res_list.status_code == 200
    saved = res_list.json()["saved_emails"]
    assert len(saved) > 0
    print("[PASS] Saved email flow passed! Total saved emails:", len(saved))

if __name__ == "__main__":
    test_health()
    test_chat()
    test_ats_evaluation()
    test_cold_email()
    test_saved_email_flow()
    print("\n🎉 ALL LOCAL API TESTS PASSED SUCCESSFULLY!")
