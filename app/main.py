import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.routers import documents, chat, ats, email
from app.services.gemini_service import gemini_service
from app.services.firestore_service import firestore_service

app = FastAPI(
    title="JobMentor AI - AI Document Assistant & Career Acceleration Platform",
    description="Multimodal Document Chat, ATS Resume Assessment, and Cold Outreach Generator built for Google Cloud Run AI Challenge",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(ats.router)
app.include_router(email.router)

# Healthcheck for Google Cloud Run probes
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "JobMentor AI",
        "cloud_run_label": "dev-tutorial=cloud-run-ai-challenge",
        "gemini_configured": gemini_service.is_configured(),
        "gemini_model": gemini_service.model_name,
        "firestore_connected": firestore_service.is_cloud_connected(),
        "project_id": settings.GOOGLE_CLOUD_PROJECT or "local-development",
        "version": settings.APP_VERSION
    }

# Static Assets and SPA Route
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["UI"])
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "JobMentor AI API is running. Static UI not found."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
