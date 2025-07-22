from typing import List
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    """docx 파일에서 텍스트를 추출합니다."""
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text



