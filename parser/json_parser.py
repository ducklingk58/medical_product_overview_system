import json
from typing import Any

def load_json_file(file_path: str) -> Any:
    """json 파일을 로드합니다."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)



