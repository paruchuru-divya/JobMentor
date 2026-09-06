import io
from typing import Dict, Any, List
import pypdf


class PDFService:
    @staticmethod
    def extract_text(file_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts full text, page-by-page text, and metadata from a PDF byte stream.
        """
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            num_pages = len(reader.pages)
            pages_content: List[Dict[str, Any]] = []
            full_text_list: List[str] = []

            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                clean_text = page_text.strip()
                pages_content.append({
                    "page_number": idx + 1,
                    "text": clean_text,
                    "char_count": len(clean_text)
                })
                if clean_text:
                    full_text_list.append(clean_text)

            full_text = "\n\n".join(full_text_list)
            
            # Extract document metadata if available
            raw_meta = reader.metadata or {}
            metadata = {
                "title": raw_meta.get("/Title", "") or "",
                "author": raw_meta.get("/Author", "") or "",
                "creator": raw_meta.get("/Creator", "") or "",
                "pages": num_pages,
                "total_chars": len(full_text),
                "word_count": len(full_text.split())
            }

            return {
                "success": True,
                "full_text": full_text,
                "pages": pages_content,
                "metadata": metadata,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "full_text": "",
                "pages": [],
                "metadata": {"pages": 0, "total_chars": 0, "word_count": 0},
                "error": f"Failed to parse PDF: {str(e)}"
            }

    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 1500, overlap: int = 200) -> List[str]:
        """
        Splits text into chunks with overlap for context-bounded processing.
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + max_chunk_size, text_len)
            chunk = text[start:end]
            chunks.append(chunk)
            if end == text_len:
                break
            start += max_chunk_size - overlap
            
        return chunks


pdf_service = PDFService()
