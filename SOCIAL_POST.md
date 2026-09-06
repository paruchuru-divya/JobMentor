# 📢 Social Media Posts & Blog Drafts (#AccelerateAIwithCloudRun)

This file contains ready-to-publish social media announcements, video demo scripts, and blog post content for the **Google Cloud Run AI Challenge**.

> **Mandatory Hashtag Included**: `#AccelerateAIwithCloudRun`

---

## 1. LinkedIn Post (Recommended for High Engagement)

**Copy and paste directly into LinkedIn:**

```markdown
🚀 Excited to unveil JobMentor AI — built for the Google Cloud Run AI Challenge! #AccelerateAIwithCloudRun

Over 75% of resumes get rejected by automated Applicant Tracking Systems (ATS) before a human ever reads them. We wanted to solve this by building an end-to-end intelligent document assistant and career acceleration platform.

With JobMentor AI, you can:
📄 Chat with any PDF document — Ask complex questions with answers grounded in the document and cited excerpts.
🎯 Perform ATS Resume Compatibility Assessments — Get an instant 0–100% match score against any target job description with sub-scores for hard skills, soft skills, and experience.
✨ Transform weak bullet points using Google's XYZ formula ("Accomplished [X], measured by [Y], by doing [Z]") to showcase measurable business impact.
✉️ Generate personalized recruiter cold outreach emails & LinkedIn notes tailored to hiring managers with customizable tones and 1-click mail client launching.

Built on Google's modern cloud ecosystem:
🔹 Google Cloud Run: Autoscaling serverless container hosting the entire FastAPI full-stack application (service labeled `dev-tutorial=cloud-run-ai-challenge`)
🔹 Google Gemini 2.5 Flash: Ultra-fast multimodal document reasoning, ATS analysis, and outreach copywriting
🔹 Google Cloud Firestore & Firebase: Storing user documents, chat history, and audit records with strict security rules

Check out the live Cloud Run deployment and GitHub repository:
🔗 Live App: [INSERT YOUR LIVE CLOUD RUN URL]
💻 GitHub Repo: [INSERT YOUR GITHUB REPO URL]

Huge shoutout to the Google Cloud and Firebase teams for organizing this challenge!

#AccelerateAIwithCloudRun #GoogleCloud #GoogleCloudRun #GeminiAI #Firebase #Firestore #FastAPI #AI #CareerTech #GenerativeAI #BuildWithAI
```

---

## 2. X (Twitter) Thread

**Tweet 1 (Main Announcement):**
```
🚀 Introducing JobMentor AI — an AI document assistant & ATS career accelerator built for the Google Cloud Run AI Challenge!

📄 Chat with PDFs
🎯 ATS compatibility score (0-100%)
✨ Google XYZ formula resume rewrites
✉️ 1-click recruiter cold emails

Powered by @GoogleCloud & #Gemini!
#AccelerateAIwithCloudRun 🧵👇
```

**Tweet 2 (Architecture):**
```
Why @GoogleCloud?
⚡ Cloud Run handles container autoscaling from 0 to N with sub-second latency
🧠 Gemini 2.5 Flash powers deep multimodal extraction & grounded Q&A
🔥 Firestore & Firebase secure and persist user audit reports & sessions

Label: dev-tutorial=cloud-run-ai-challenge
#AccelerateAIwithCloudRun
```

**Tweet 3 (Links & Video):**
```
Try it out live & inspect the open-source codebase:
🌐 Live Cloud Run: [INSERT CLOUD RUN URL]
💻 GitHub: [INSERT REPO URL]

Demo video below 👇
#AccelerateAIwithCloudRun #GoogleCloud
```

---

## 3. Video Demo Script (60 to 90 Seconds)

**Visual**: Screen recording showing JobMentor AI UI.

- **[0:00 - 0:15] Hook**:  
  *"Did you know that 75% of job seekers are rejected by automated ATS screeners before a recruiter even looks at their resume? Meet JobMentor AI, an intelligent document assistant and career accelerator built for the Google Cloud Run AI Challenge."*

- **[0:15 - 0:35] Chat with PDF**:  
  *(Screen: Uploading resume PDF and chatting)*  
  *"First, our Chat with PDF studio ingests any PDF—from resumes to technical whitepapers. Powered by Google Gemini 2.5 Flash, it delivers grounded answers with cited excerpts and dynamic follow-up suggestions."*

- **[0:35 - 0:55] ATS Resume Matcher**:  
  *(Screen: Clicking Evaluate ATS Compatibility)*  
  *"Next, paste any target job description. JobMentor AI performs an ATS-grade audit—calculating an overall match score, breaking down hard vs. soft skills, identifying missing keywords, and automatically rewriting weak bullets using Google's proven XYZ formula: Accomplished [X], measured by [Y], by doing [Z]."*

- **[0:55 - 1:15] Cold Email Studio & Firestore Vault**:  
  *(Screen: Generating cold email and saving to Firestore)*  
  *"Finally, the Cold Email Studio crafts tailored outreach emails to recruiters with multiple subject lines and a 1-click 'Open in Mail' button. Everything is persisted in Google Cloud Firestore and served serverlessly on Google Cloud Run."*

- **[1:15 - 1:25] Conclusion**:  
  *"JobMentor AI demonstrates the speed, scalability, and intelligence of combining Google Cloud Run, Gemini, and Firestore. Check out the live link below! #AccelerateAIwithCloudRun"*

---

## 4. Dev.to / Medium Blog Post Outline

### Title: How I Built an AI Document Assistant & ATS Resume Scorer on Google Cloud Run and Gemini

#### Sections:
1. **Introduction & The Problem**: Why traditional document parsing and resume submission is broken.
2. **System Architecture**: How FastAPI, Gemini 2.5 Flash, Cloud Firestore, and Cloud Run interact.
3. **Implementing Grounded PDF Chat**: Using PyPDF and Gemini system prompts for zero hallucination.
4. **Building the ATS Scoring Engine**: Evaluating keyword vectors and generating Google XYZ formula bullet point rewrites.
5. **Deploying to Cloud Run with `dev-tutorial=cloud-run-ai-challenge`**: Containerization, secrets, and Cloud Build pipeline.
6. **Securing Candidate Data**: Firebase security rules for user document privacy.
7. **Key Takeaways & What's Next**: Scalability benefits of serverless containers on Google Cloud.
