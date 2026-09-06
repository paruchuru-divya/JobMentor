# 🚀 JobMentor AI — Intelligent Document Assistant & Career Accelerator

[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Google Cloud Firestore](https://img.shields.io/badge/Firestore-NoSQL_Cloud-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/docs/firestore)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)

> Built for the **Google Cloud Run AI Challenge**  
> Mandatory Cloud Run Service Label: `dev-tutorial=cloud-run-ai-challenge`

**JobMentor AI** is an AI-powered document intelligence and career acceleration platform designed to empower job seekers, researchers, and professionals. It enables users to **chat directly with PDF documents**, **perform deep ATS-style resume evaluations against target job descriptions**, and **generate personalized, high-converting cold outreach emails to recruiters**.

---

## 🌟 Live Demo & Video Presentation

- **Live Cloud Run URL**: `https://jobmentor-ai-<hash>-uc.a.run.app` *(Replace with your deployed URL)*
- **Cloud Run Service Label**: `dev-tutorial=cloud-run-ai-challenge`
- **Social Post / Video Demo**: [#AccelerateAIwithCloudRun on LinkedIn & X](#social-post--video-demo)

---

## 🏗️ Architecture & Ecosystem

```mermaid
flowchart TD
    User([User / Job Seeker]) -->|HTTPS / REST| CloudRun[Google Cloud Run<br/>FastAPI Container Service<br/>dev-tutorial=cloud-run-ai-challenge]

    subgraph Frontend [Single-Page Responsive Application]
        UI1[📄 PDF Document Chat Studio]
        UI2[🎯 ATS Resume Matcher & Scorer]
        UI3[✉️ Recruiter Cold Email Studio]
        UI4[🗂️ Firestore Cloud Vault]
    end

    subgraph Backend [FastAPI Services Layer]
        DocRouter[/api/documents: PyPDF Parsing]
        ChatRouter[/api/chat: Contextual Q&A]
        ATSRouter[/api/ats: Resume vs JD Evaluation]
        EmailRouter[/api/email: Outreach Synthesizer]
        FirestoreClient[Firestore Service Engine]
        GeminiClient[Google GenAI SDK Engine]
    end

    subgraph Google Cloud Ecosystem
        Gemini[Google Gemini 2.5 / 1.5 Flash<br/>Multimodal & Reasoning API]
        Firestore[(Google Cloud Firestore<br/>Documents, Audits, History)]
        FirebaseSec[Firebase Security Rules<br/>firestore.rules]
    end

    CloudRun --> Frontend
    Frontend --> Backend
    DocRouter --> GeminiClient
    ChatRouter --> GeminiClient
    ATSRouter --> GeminiClient
    EmailRouter --> GeminiClient
    Backend --> FirestoreClient
    FirestoreClient --> Firestore
    FirestoreClient -.-> FirebaseSec
    GeminiClient --> Gemini
```

---

## 🚀 Key Features

### 1. 📄 Conversational PDF Document Chat
- **Instant PDF Extraction**: Ingests resumes, whitepapers, financial reports, or technical specifications using PyPDF.
- **Grounded Q&A**: Answers user questions strictly using the document context with verified excerpts and citations.
- **Dynamic Follow-Up Prompts**: Gemini suggests 3 contextually relevant follow-up questions after every turn.

### 2. 🎯 ATS Resume Compatibility Engine
- **Algorithmic & AI Compatibility Scoring (0–100%)**: Evaluates overall fit and 4 sub-scores:
  - Hard Skills Match (0–100%)
  - Soft Skills Match (0–100%)
  - Experience Alignment (0–100%)
  - Education & Certifications Match (0–100%)
- **Keyword Gap Analysis**: Highlights matching target keywords (green pills) versus missing critical keywords (red pills).
- **Google XYZ Formula Bullet Rewrites**: Automatically translates weak resume bullet points into Google's recommended XYZ format (*Accomplished [X], measured by [Y], by doing [Z]*).
- **Actionable Quick Wins**: Concrete, immediate adjustments to pass automated screening filters.

### 3. ✉️ Recruiter Cold Outreach Studio
- **Personalized Cold Emails**: Generates bespoke outreach emails connecting the candidate's verified accomplishments to the hiring team's exact pain points.
- **Tone Customization**: Choose between *Professional & Confident*, *Direct & Metric-driven*, *Enthusiastic & Innovative*, or *Executive & Strategic*.
- **3 Hook-Driven Subject Lines**: Multiple A/B options for maximum open rate.
- **1-Click Mail Client Integration**: "Open in Mail" pre-fills your native email client via `mailto:` with subject line and body.
- **LinkedIn Connection Note (<300 chars)**: Quick intro note ready for connection requests.
- **4-Day Follow-Up Message**: Follow-up email ready to send if no response is received.

### 4. 🗂️ Google Cloud Firestore Data Vault
- Persists document metadata, ATS audits, chat session histories, and saved email drafts.
- Secured using production-ready `firestore.rules`.
- Includes graceful in-memory fallback for immediate zero-config local testing.

---

## 🛠️ Tech Stack & Google Cloud Services

| Technology | Role in JobMentor AI |
|---|---|
| **Google Cloud Run** | Fully managed serverless container runtime hosting the application with autoscaling (0 to N) and the label `dev-tutorial=cloud-run-ai-challenge`. |
| **Google Gemini 2.5 / 1.5 Flash** | Core intelligence engine providing multimodal document understanding, grounded document Q&A, ATS scoring heuristics, and cold email copywriting. |
| **Google Cloud Firestore** | Serverless NoSQL document database storing user files, audit scores, chat histories, and outreach templates. |
| **Firebase Security Rules** | Enforces row-level security and access control over documents, chats, audits, and email collections. |
| **FastAPI (Python 3.11)** | High-performance asynchronous REST backend serving endpoints and static web assets. |
| **Tailwind CSS & Lucide** | Modern responsive dark-mode user interface with glassmorphism styling and zero Node build dependencies. |

---

## 📋 Project Directory Structure

```
d:/JobMentor_project/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entrypoint & static routes
│   ├── config.py                   # Pydantic settings & environment configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py          # PyPDF extraction, page count & chunking
│   │   ├── gemini_service.py       # Google GenAI SDK (Chat, ATS, Cold Email)
│   │   └── firestore_service.py    # Firestore client with graceful fallback
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── documents.py            # PDF upload & metadata APIs
│   │   ├── chat.py                 # Grounded document Q&A APIs
│   │   ├── ats.py                  # ATS evaluation & scoring APIs
│   │   └── email.py                # Recruiter cold outreach APIs
│   └── static/
│       ├── index.html              # Responsive single-page application
│       ├── css/style.css           # Glassmorphism accents & score gauge animation
│       └── js/app.js               # Frontend controller & API interactions
├── firestore.rules                 # Production Firestore security rules
├── firebase.json                   # Firebase configuration
├── Dockerfile                      # Cloud Run container definition
├── .dockerignore                   # Build ignore definitions
├── deploy-cloudrun.sh              # Cloud Run bash deployment script
├── deploy-cloudrun.ps1             # Cloud Run PowerShell deployment script
├── cloudbuild.yaml                 # Google Cloud Build CI/CD pipeline
├── requirements.txt                # Production Python dependencies
├── .env.example                    # Environment template
├── README.md                       # Comprehensive repository documentation
├── SUBMISSION.md                   # Ideathon Prototype Submission answers
└── SOCIAL_POST.md                  # Social announcement & blog drafts
```

---

## ⚡ Local Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/jobmentor-ai.git
cd jobmentor-ai
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your **Google Gemini API Key** (obtain free from [Google AI Studio](https://aistudio.google.com/)):
```env
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
PORT=8080
```
*(Note: JobMentor AI includes a demonstration mode with realistic mock responses if tested without an immediate API key).*

### 4. Run the Application
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```
Open your browser at **http://localhost:8080** to use JobMentor AI.

---

## ☁️ Deployment to Google Cloud Run

To satisfy the hackathon criteria, the deployment must include the label `dev-tutorial=cloud-run-ai-challenge`.

### Automated Deployment (Recommended)

#### Using Bash (Linux / macOS / Google Cloud Shell):
```bash
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh
```

#### Using PowerShell (Windows):
```powershell
.\deploy-cloudrun.ps1
```

### Manual Deployment via `gcloud` CLI

1. **Authenticate and set your active project**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable required services**:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com
   ```

3. **Deploy with mandatory challenge label**:
   ```bash
   gcloud run deploy jobmentor-ai \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --labels=dev-tutorial=cloud-run-ai-challenge \
     --set-env-vars="GEMINI_API_KEY=YOUR_GEMINI_API_KEY,GEMINI_MODEL=gemini-2.5-flash,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
     --memory=1Gi \
     --cpu=1
   ```

4. **Verify Deployment & Label**:
   ```bash
   gcloud run services describe jobmentor-ai --region us-central1 --format="value(metadata.labels)"
   ```
   *Expected Output: `dev-tutorial: cloud-run-ai-challenge`*

---

## 🔒 Firestore Security Rules

Production security rules are located in [firestore.rules](file:///d:/JobMentor_project/firestore.rules).
They enforce:
- Authenticated user isolation on personal documents (`request.auth.uid == resource.data.user_id`).
- Input schema validation on created documents, audits, and email drafts.
- Default deny-all on unspecified collections.

Deploy rules via Firebase CLI:
```bash
firebase deploy --only firestore:rules
```

---

## 🧪 Testing

Run the automated test suite locally:
```bash
python test_app.py
```
Expected output:
```
[PASS] /health passed! Output: {'status': 'healthy', 'service': 'JobMentor AI', 'cloud_run_label': 'dev-tutorial=cloud-run-ai-challenge', ...}
[PASS] /api/chat/ passed!
[PASS] /api/ats/evaluate passed! Score: 71%, Rating: Moderate Match
[PASS] /api/email/generate passed! Subject lines count: 3
[PASS] Saved email flow passed! Total saved emails: 1
🎉 ALL LOCAL API TESTS PASSED SUCCESSFULLY!
```

---

## 📄 License

Licensed under the [Apache 2.0 License](LICENSE).
Built with ❤️ for the Google Cloud Run AI Challenge.
