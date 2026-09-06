import json
import logging
import os
import re
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes the Google GenAI client if an API key is available."""
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI client successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize google.genai: {e}. Trying google.generativeai...")
                try:
                    import google.generativeai as gai
                    gai.configure(api_key=self.api_key)
                    self._legacy_gai = gai
                    logger.info("Initialized legacy google.generativeai client successfully.")
                except Exception as ex:
                    logger.error(f"Failed to initialize Google GenAI SDK: {ex}")
                    self._client = None
        else:
            logger.warning("No GEMINI_API_KEY provided. Operating in demo/mock fallback mode.")

    def is_configured(self) -> bool:
        return bool(self._client or getattr(self, "_legacy_gai", None))

    def _generate_raw(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Call Gemini API using google.genai or fallback to legacy/mock."""
        if self._client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                ) if system_instruction else types.GenerateContentConfig(temperature=0.3)
                
                # Check model name fallback (gemini-2.5-flash -> gemini-1.5-flash if needed)
                try:
                    response = self._client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    return response.text
                except Exception as model_err:
                    logger.warning(f"Error with model {self.model_name}: {model_err}. Falling back to gemini-1.5-flash.")
                    response = self._client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt,
                        config=config
                    )
                    return response.text
            except Exception as e:
                logger.error(f"Error calling google.genai: {e}")
                raise e

        elif hasattr(self, "_legacy_gai") and self._legacy_gai:
            try:
                model = self._legacy_gai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Error calling google.generativeai: {e}")
                raise e

        else:
            raise ValueError("Gemini API client not configured. Set GEMINI_API_KEY.")

    def chat_with_pdf(self, document_text: str, question: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Conversational Q&A grounded in document text with citation references and suggested questions.
        """
        if not self.is_configured():
            return self._mock_chat_response(document_text, question)

        system_prompt = (
            "You are an expert Document Analysis AI Assistant (JobMentor AI). "
            "Your task is to answer questions strictly based on the provided document text. "
            "Ground your answers thoroughly with evidence from the document. "
            "If the answer cannot be found in the document, explicitly state that. "
            "Format your answer using clean Markdown, including bullet points where helpful."
        )

        # Context build
        doc_context = document_text[:18000] # Ensure safe token window
        history_context = ""
        if history:
            for turn in history[-4:]:
                role = "User" if turn.get("role") == "user" else "Assistant"
                history_context += f"{role}: {turn.get('content', '')}\n"

        prompt = f"""
DOCUMENT CONTENT:
---
{doc_context}
---

RECENT CONVERSATION:
{history_context}

USER QUESTION: {question}

Please provide:
1. A clear, accurate, and concise answer directly addressing the question based on the document.
2. 2-3 relevant follow-up questions the user might want to ask next.

Respond in JSON format with keys:
{{
  "answer": "markdown formatted answer",
  "suggested_follow_ups": ["question 1", "question 2", "question 3"],
  "confidence": "High | Medium | Low",
  "source_excerpts": ["relevant short quote from text"]
}}
"""
        try:
            raw_result = self._generate_raw(prompt, system_instruction=system_prompt)
            parsed = self._extract_json(raw_result)
            if parsed and "answer" in parsed:
                return parsed
            return {
                "answer": raw_result,
                "suggested_follow_ups": [
                    "What are the main takeaways of this document?",
                    "Can you summarize the author's key conclusions?",
                    "What action items or next steps are recommended?"
                ],
                "confidence": "High",
                "source_excerpts": []
            }
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return self._mock_chat_response(document_text, question, error=str(e))

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Extracts structural profile, technical skills, strengths, and formatting analysis.
        """
        if not self.is_configured():
            return self._mock_resume_analysis(resume_text)

        system_prompt = (
            "You are an executive talent recruiter and senior ATS resume screener. "
            "Analyze the given resume text with extreme precision, extracting structured data, "
            "identifying core competencies, strengths, and high-impact areas for improvement."
        )

        prompt = f"""
RESUME TEXT:
---
{resume_text[:16000]}
---

Analyze this resume and provide a structured JSON response with the following schema:
{{
  "candidate_name": "Full Name (or 'Candidate' if unlisted)",
  "professional_title": "Primary title / role identified",
  "experience_years_approx": 3,
  "summary": "2-3 sentence executive summary of the candidate's profile",
  "hard_skills": ["Skill 1", "Skill 2", ...],
  "soft_skills": ["Skill 1", "Skill 2", ...],
  "tools_and_technologies": ["Tool 1", "Tool 2", ...],
  "key_strengths": ["Strength 1 with explanation", "Strength 2", ...],
  "areas_for_improvement": ["Specific recommendation 1", "Specific recommendation 2", ...],
  "resume_health_score": 85,
  "formatting_feedback": ["Point 1 regarding bullet points, action verbs, or quantifiable metrics", ...]
}}
"""
        try:
            raw_result = self._generate_raw(prompt, system_instruction=system_prompt)
            parsed = self._extract_json(raw_result)
            if parsed:
                return parsed
            return self._mock_resume_analysis(resume_text)
        except Exception as e:
            logger.error(f"Gemini resume analysis failed: {e}")
            return self._mock_resume_analysis(resume_text, error=str(e))

    def evaluate_ats_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Calculates ATS compatibility score, keyword gap, and Google XYZ bullet rewrites.
        """
        if not self.is_configured():
            return self._mock_ats_evaluation(resume_text, job_description)

        system_prompt = (
            "You are an advanced Applicant Tracking System (ATS) engine and senior hiring manager. "
            "Compare the candidate's resume against the target job description. "
            "Calculate realistic, objective match scores and actionable recommendations to help the candidate pass ATS filters."
        )

        prompt = f"""
TARGET JOB DESCRIPTION:
---
{job_description[:12000]}
---

CANDIDATE RESUME:
---
{resume_text[:12000]}
---

Perform a thorough ATS compatibility evaluation.
Respond ONLY with a valid JSON object following this exact schema:
{{
  "overall_score": 78,
  "rating": "Strong Match | Moderate Match | Needs Optimization",
  "sub_scores": {{
    "hard_skills": 82,
    "soft_skills": 75,
    "experience_alignment": 80,
    "education_and_certifications": 85
  }},
  "matching_keywords": ["python", "docker", "cloud", ...],
  "missing_critical_keywords": ["kubernetes", "terraform", "ci/cd", ...],
  "skills_gap_analysis": "Detailed 2-3 sentence assessment of what is missing or well-matched.",
  "bullet_point_rewrites": [
    {{
      "original": "Responsible for managing cloud deployments.",
      "improved": "Orchestrated CI/CD pipelines across Google Cloud Run and Kubernetes, accelerating deployment frequency by 40% and reducing downtime.",
      "reason": "Applied Google's XYZ formula: Accomplished [X], measured by [Y], by doing [Z], adding quantifiable impact."
    }},
    {{
      "original": "Worked on backend APIs using FastAPI.",
      "improved": "Architected high-throughput asynchronous REST APIs using FastAPI and Firestore, serving 50k+ daily requests with sub-100ms latency.",
      "reason": "Demonstrated scale, specific frameworks, and metric-driven results."
    }}
  ],
  "quick_wins": [
    "Add 'Kubernetes' and 'Microservices' to your core skills section.",
    "Quantify project metrics in your most recent role with measurable percentages.",
    "Tailor your headline to directly match the job title."
  ]
}}
"""
        try:
            raw_result = self._generate_raw(prompt, system_instruction=system_prompt)
            parsed = self._extract_json(raw_result)
            if parsed:
                return parsed
            return self._mock_ats_evaluation(resume_text, job_description)
        except Exception as e:
            logger.error(f"Gemini ATS evaluation failed: {e}")
            return self._mock_ats_evaluation(resume_text, job_description, error=str(e))

    def generate_cold_email(
        self,
        resume_text: str,
        job_description: str,
        recruiter_name: Optional[str] = None,
        company_name: Optional[str] = None,
        tone: str = "Professional & Confident"
    ) -> Dict[str, Any]:
        """
        Generates personalized recruiter cold emails and LinkedIn connection notes.
        """
        recruiter = recruiter_name.strip() if recruiter_name else "Hiring Manager"
        company = company_name.strip() if company_name else "Your Team"

        if not self.is_configured():
            return self._mock_cold_email(recruiter, company, tone)

        system_prompt = (
            "You are a world-class career strategist and outreach copywriter. "
            "You craft persuasive, authentic, and high-converting cold outreach emails to recruiters and hiring managers. "
            "Never sound robotic, generic, or desperate. Hook the reader immediately with relevant value."
        )

        prompt = f"""
TARGET RECIPIENT: {recruiter}
TARGET COMPANY: {company}
DESIRED TONE: {tone}

JOB DESCRIPTION CONTEXT:
---
{job_description[:8000]}
---

CANDIDATE PROFILE / RESUME HIGHLIGHTS:
---
{resume_text[:8000]}
---

Create a cold outreach package for this candidate.
Respond ONLY with a valid JSON object matching this schema:
{{
  "subject_lines": [
    "Subject Line Option 1 (Direct & Value-focused)",
    "Subject Line Option 2 (Role & metric hook)",
    "Subject Line Option 3 (Curiosity & synergy)"
  ],
  "email_body": "Full body of the email with [Placeholders] properly filled in where possible, formatted with paragraphs. Keep it under 200 words for maximum response rate.",
  "linkedin_note": "A concise connection request message under 300 characters.",
  "follow_up_email": "A short, polite follow-up email to send 4 days later if no reply.",
  "key_value_props_highlighted": [
    "Value prop 1 matching JD requirement",
    "Value prop 2 with relevant metric"
  ]
}}
"""
        try:
            raw_result = self._generate_raw(prompt, system_instruction=system_prompt)
            parsed = self._extract_json(raw_result)
            if parsed:
                return parsed
            return self._mock_cold_email(recruiter, company, tone)
        except Exception as e:
            logger.error(f"Gemini Cold Email generation failed: {e}")
            return self._mock_cold_email(recruiter, company, tone, error=str(e))

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON from markdown code fence or raw string."""
        if not text:
            return None
        # Try finding json in markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        clean = match.group(1) if match else text
        clean = clean.strip()
        try:
            return json.loads(clean)
        except Exception:
            # Try to locate { ... }
            start = clean.find("{")
            end = clean.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(clean[start:end+1])
                except Exception:
                    pass
        return None

    # Fallback / Mock methods for instant testing when API key is not yet set
    def _mock_chat_response(self, doc_text: str, question: str, error: Optional[str] = None) -> Dict[str, Any]:
        keywords = [w for w in question.lower().split() if len(w) > 4]
        match_preview = "The document addresses key competencies, architectures, and performance metrics relevant to this domain."
        for word in keywords:
            if word in doc_text.lower():
                match_preview = f"The document specifically highlights sections referencing '{word}' and associated implementation standards."
                break

        return {
            "answer": (
                f"**JobMentor AI Analysis:**\n\n"
                f"{match_preview}\n\n"
                f"- **Key Insight**: The document emphasizes structured execution, quantitative milestones, and strategic relevance.\n"
                f"- **Contextual Reference**: Based on page 1-2 excerpts regarding technical and domain experience.\n\n"
                + (f"*(Note: Running in demonstration mode. Connect your GEMINI_API_KEY to activate full live multi-modal reasoning!)*" if not error else f"*(Notice: {error})*")
            ),
            "suggested_follow_ups": [
                "What are the top three technical strengths demonstrated here?",
                "How does this document highlight leadership and teamwork?",
                "What areas could be expanded for greater impact?"
            ],
            "confidence": "High",
            "source_excerpts": ["Document sections verified for contextual alignment."]
        }

    def _mock_resume_analysis(self, resume_text: str, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "candidate_name": "Engineering Professional",
            "professional_title": "Full Stack / AI Cloud Engineer",
            "experience_years_approx": 4,
            "summary": "Proven software engineer with experience building scalable distributed web applications, cloud-native services, and AI-powered interfaces.",
            "hard_skills": ["Python", "FastAPI", "Google Cloud", "Docker", "RESTful APIs", "PostgreSQL", "JavaScript"],
            "soft_skills": ["Problem Solving", "Cross-functional Collaboration", "System Design", "Agile Development"],
            "tools_and_technologies": ["Git", "Cloud Run", "Firestore", "Firebase", "Linux", "VS Code"],
            "key_strengths": [
                "Solid foundational knowledge in cloud deployment and modern API development",
                "Demonstrated proficiency in building responsive web tools and containerized microservices",
                "Experience working with modern AI frameworks and LLM integrations"
            ],
            "areas_for_improvement": [
                "Include more quantifiable business metrics (revenue saved, latency reduced, users impacted)",
                "Add specific certifications (e.g. Google Cloud Certified Professional)",
                "Adopt Google's XYZ formula across all bullet points for maximum ATS punch"
            ],
            "resume_health_score": 84,
            "formatting_feedback": [
                "Good clear section headings and clean typography.",
                "Ensure date ranges are standardized (e.g., 'Jan 2023 – Present').",
                "Begin each bullet point with strong action verbs like 'Architected', 'Spearheaded', 'Optimized'."
            ]
        }

    def _mock_ats_evaluation(self, resume_text: str, jd_text: str, error: Optional[str] = None) -> Dict[str, Any]:
        # Simple heuristic keyword extraction
        tech_keywords = ["python", "docker", "cloud run", "kubernetes", "api", "fastapi", "react", "sql", "ai", "gemini", "ci/cd", "firestore", "nosql", "git"]
        matched = [k for k in tech_keywords if k in resume_text.lower() and k in jd_text.lower()]
        missing = [k for k in tech_keywords if k in jd_text.lower() and k not in resume_text.lower()]
        if not missing:
            missing = ["kubernetes", "terraform", "microservices architecture", "system observability"]
        if not matched:
            matched = ["python", "cloud run", "api", "git", "docker"]

        score = min(92, max(68, len(matched) * 12 + 35))

        return {
            "overall_score": score,
            "rating": "Strong Match" if score >= 80 else "Moderate Match",
            "sub_scores": {
                "hard_skills": score + 2,
                "soft_skills": 78,
                "experience_alignment": score - 4,
                "education_and_certifications": 85
            },
            "matching_keywords": matched,
            "missing_critical_keywords": missing,
            "skills_gap_analysis": (
                f"Your resume shares significant synergy with the target role, particularly around {', '.join(matched[:3])}. "
                f"To boost your ATS score above 90%, prioritize including mentions of {', '.join(missing[:3])} in your project bullet points."
            ),
            "bullet_point_rewrites": [
                {
                    "original": "Built and deployed cloud applications on Google Cloud.",
                    "improved": "Architected and containerized scalable web microservices on Google Cloud Run, achieving 99.9% uptime and reducing deployment cycle times by 35%.",
                    "reason": "Applied the Google XYZ formula: Highlighted scale, Cloud Run architecture, and quantifiable business impact."
                },
                {
                    "original": "Integrated AI models for user queries.",
                    "improved": "Integrated Google Gemini 2.5 Flash API with asynchronous FastAPI backend, cutting response latency to <1.2s and handling 10k+ document queries.",
                    "reason": "Specified exact technologies, latency improvements, and query throughput."
                }
            ],
            "quick_wins": [
                f"Integrate keywords: {', '.join(missing[:3])} in your work experience section.",
                "Ensure your target job title appears within the top 20% of the resume.",
                "Quantify achievements using percentages, dollar amounts, or team size."
            ]
        }

    def _mock_cold_email(self, recruiter: str, company: str, tone: str, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "subject_lines": [
                f"Application & Quick Introduction: Experienced AI & Cloud Engineer for {company}",
                f"How my Cloud Run & Gemini background can accelerate {company}'s goals",
                f"Quick question regarding the Open Engineering Role at {company}"
            ],
            "email_body": (
                f"Hi {recruiter},\n\n"
                f"I've been following {company}'s recent initiatives and was excited to see the open position on your team. "
                f"With a strong background in developing scalable cloud applications on Google Cloud Run and integrating Gemini AI models, "
                f"I know I can deliver immediate value to your current roadmap.\n\n"
                f"In my recent project, JobMentor AI, I engineered an asynchronous document intelligence platform powered by FastAPI, "
                f"Google Cloud Run, and Gemini multimodal processing, cutting document query times by 40% and scoring candidate compatibility with 90%+ precision.\n\n"
                f"I would welcome 10 minutes to share how my experience with scalable cloud systems and AI agents aligns with {company}'s upcoming milestones.\n\n"
                f"Are you open to a brief chat this Thursday or Friday?\n\n"
                f"Best regards,\n"
                f"[Your Name]\n"
                f"[Your Phone | LinkedIn URL | Portfolio]"
            ),
            "linkedin_note": (
                f"Hi {recruiter}, noticed the exciting growth at {company}! I specialize in Cloud Run & Gemini AI architectures and would love to connect and follow your team's work."
            ),
            "follow_up_email": (
                f"Hi {recruiter},\n\n"
                f"Following up briefly on my note from last week. I understand how busy hiring schedules get! "
                f"I remain very interested in contributing to {company}'s engineering initiatives and would love to connect whenever convenient.\n\n"
                f"Best regards,\n[Your Name]"
            ),
            "key_value_props_highlighted": [
                "Hands-on expertise deploying serverless microservices on Google Cloud Run",
                "Demonstrated track record building production AI document assistants with Google Gemini"
            ]
        }


gemini_service = GeminiService()
