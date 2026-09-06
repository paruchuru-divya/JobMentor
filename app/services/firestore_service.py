import datetime
import logging
import os
import uuid
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class FirestoreService:
    def __init__(self):
        self.project_id = settings.GOOGLE_CLOUD_PROJECT or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.database_name = settings.FIRESTORE_DATABASE
        self._db = None
        self._in_memory_store: Dict[str, Dict[str, Any]] = {
            "documents": {},
            "ats_audits": {},
            "chat_sessions": {},
            "saved_emails": {}
        }
        self._init_client()

    def _init_client(self):
        """Initializes Google Cloud Firestore client if credentials/project are available."""
        try:
            from google.cloud import firestore
            if self.project_id:
                self._db = firestore.Client(project=self.project_id, database=self.database_name)
            else:
                # Try default client (works in Google Cloud Run automatically via ADC)
                self._db = firestore.Client()
            logger.info("Connected to Google Cloud Firestore successfully.")
        except Exception as e:
            logger.warning(f"Firestore not available locally ({e}). Operating in memory-backed mode.")
            self._db = None

    def is_cloud_connected(self) -> bool:
        return self._db is not None

    # ==================== DOCUMENTS ====================

    async def save_document_record(self, doc_data: Dict[str, Any]) -> str:
        doc_id = doc_data.get("id") or str(uuid.uuid4())
        doc_data["id"] = doc_id
        doc_data["created_at"] = doc_data.get("created_at") or datetime.datetime.utcnow().isoformat()

        if self._db:
            try:
                self._db.collection("documents").document(doc_id).set(doc_data)
                return doc_id
            except Exception as e:
                logger.error(f"Firestore save_document error: {e}")
        
        # Local fallback
        self._in_memory_store["documents"][doc_id] = doc_data
        return doc_id

    async def get_document_record(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if self._db:
            try:
                snap = self._db.collection("documents").document(doc_id).get()
                if snap.exists:
                    return snap.to_dict()
            except Exception as e:
                logger.error(f"Firestore get_document error: {e}")

        return self._in_memory_store["documents"].get(doc_id)

    async def list_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self._db:
            try:
                docs = self._db.collection("documents").order_by("created_at", direction="DESCENDING").limit(limit).stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                logger.error(f"Firestore list_documents error: {e}")

        items = list(self._in_memory_store["documents"].values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    # ==================== ATS AUDITS ====================

    async def save_ats_audit(self, audit_data: Dict[str, Any]) -> str:
        audit_id = audit_data.get("id") or str(uuid.uuid4())
        audit_data["id"] = audit_id
        audit_data["created_at"] = audit_data.get("created_at") or datetime.datetime.utcnow().isoformat()

        if self._db:
            try:
                self._db.collection("ats_audits").document(audit_id).set(audit_data)
                return audit_id
            except Exception as e:
                logger.error(f"Firestore save_ats_audit error: {e}")

        self._in_memory_store["ats_audits"][audit_id] = audit_data
        return audit_id

    async def list_ats_audits(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self._db:
            try:
                docs = self._db.collection("ats_audits").order_by("created_at", direction="DESCENDING").limit(limit).stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                logger.error(f"Firestore list_ats_audits error: {e}")

        items = list(self._in_memory_store["ats_audits"].values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

    # ==================== CHAT SESSIONS ====================

    async def save_chat_message(self, session_id: str, doc_id: str, role: str, message: str) -> Dict[str, Any]:
        session = await self.get_chat_session(session_id)
        if not session:
            session = {
                "id": session_id,
                "doc_id": doc_id,
                "messages": [],
                "created_at": datetime.datetime.utcnow().isoformat(),
                "updated_at": datetime.datetime.utcnow().isoformat()
            }

        session["messages"].append({
            "role": role,
            "content": message,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        session["updated_at"] = datetime.datetime.utcnow().isoformat()

        if self._db:
            try:
                self._db.collection("chat_sessions").document(session_id).set(session)
                return session
            except Exception as e:
                logger.error(f"Firestore save_chat_message error: {e}")

        self._in_memory_store["chat_sessions"][session_id] = session
        return session

    async def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self._db:
            try:
                snap = self._db.collection("chat_sessions").document(session_id).get()
                if snap.exists:
                    return snap.to_dict()
            except Exception as e:
                logger.error(f"Firestore get_chat_session error: {e}")

        return self._in_memory_store["chat_sessions"].get(session_id)

    # ==================== COLD EMAILS ====================

    async def save_cold_email(self, email_data: Dict[str, Any]) -> str:
        email_id = email_data.get("id") or str(uuid.uuid4())
        email_data["id"] = email_id
        email_data["created_at"] = datetime.datetime.utcnow().isoformat()

        if self._db:
            try:
                self._db.collection("saved_emails").document(email_id).set(email_data)
                return email_id
            except Exception as e:
                logger.error(f"Firestore save_cold_email error: {e}")

        self._in_memory_store["saved_emails"][email_id] = email_data
        return email_id

    async def list_saved_emails(self, limit: int = 20) -> List[Dict[str, Any]]:
        if self._db:
            try:
                docs = self._db.collection("saved_emails").order_by("created_at", direction="DESCENDING").limit(limit).stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                logger.error(f"Firestore list_saved_emails error: {e}")

        items = list(self._in_memory_store["saved_emails"].values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]


firestore_service = FirestoreService()
