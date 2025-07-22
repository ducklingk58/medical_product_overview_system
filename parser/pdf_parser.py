from typing import Optional
import pdfplumber

def extract_text_from_pdf(file_path: str) -> Optional[str]:
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        print(f"PDF 파싱 오류: {e}")
        return None 