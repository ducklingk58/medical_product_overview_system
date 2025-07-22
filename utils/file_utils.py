import os
import tempfile
from typing import Optional

def get_file_extension(file_path: str) -> str:
    """파일 확장자를 반환합니다."""
    return os.path.splitext(file_path)[1].lower()

def is_supported_file(file_path: str) -> bool:
    """지원되는 파일 형식인지 확인합니다."""
    supported_extensions = ['.json', '.docx', '.pdf']
    return get_file_extension(file_path) in supported_extensions

def create_temp_file(content: str, extension: str = '.txt') -> str:
    """임시 파일을 생성하고 경로를 반환합니다."""
    with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name

def cleanup_temp_file(file_path: str) -> None:
    """임시 파일을 삭제합니다."""
    try:
        os.unlink(file_path)
    except OSError:
        pass 