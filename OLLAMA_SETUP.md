# 🦙 Ollama 설치 및 설정 가이드

## 📋 개요
Ollama는 로컬에서 LLM을 실행할 수 있는 무료 도구입니다. Gemini API 할당량 문제를 해결하기 위해 Ollama로 전환하는 것을 추천합니다.

## 🚀 설치 방법

### Windows에서 설치
1. **Ollama 다운로드**: https://ollama.ai/download
2. **설치 파일 실행**: 다운로드한 `.exe` 파일 실행
3. **설치 완료 후**: 명령 프롬프트에서 `ollama` 명령어 사용 가능

### macOS에서 설치
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux에서 설치
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 🔧 모델 다운로드

### 한국어 지원 모델 (추천)
```bash
# Llama 3.2 (3B) - 빠르고 가벼움
ollama pull llama3.2:3b

# Qwen2 (3B) - 한국어 성능 우수
ollama pull qwen2:3b

# Llama 3.1 (8B) - 더 정확함
ollama pull llama3.1:8b
```

### 의약품 분석에 특화된 모델
```bash
# Code Llama - 구조화된 출력에 강함
ollama pull codellama:7b

# Mistral - 일반적인 성능 우수
ollama pull mistral:7b
```

## 🏃‍♂️ 서비스 시작

### 1. Ollama 서비스 시작
```bash
ollama serve
```

### 2. 백그라운드에서 실행 (Windows)
```bash
# 새 명령 프롬프트 창에서
ollama serve
```

### 3. 서비스 상태 확인
```bash
ollama list
```

## 🧪 테스트

### 1. 간단한 테스트
```bash
ollama run llama3.2:3b "안녕하세요. 간단한 테스트입니다."
```

### 2. Python에서 테스트
```bash
cd medical_product_overview_system
python llm/ollama_client.py
```

## ⚙️ 설정 변경

### Streamlit 앱에서 Ollama 사용
`app.py`에서 다음 부분을 수정:

```python
# 기존 Gemini import를 Ollama로 변경
from llm.ollama_client import generate_overview_with_llm, test_ollama_connection
```

### 모델 변경
```python
# 더 큰 모델 사용 (더 정확하지만 느림)
client = OllamaClient(model="llama3.1:8b")

# 더 작은 모델 사용 (빠르지만 덜 정확함)
client = OllamaClient(model="llama3.2:3b")
```

## 📊 성능 비교

| 모델 | 크기 | 속도 | 정확도 | 한국어 | 메모리 |
|------|------|------|--------|--------|--------|
| llama3.2:3b | 3B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 4GB |
| qwen2:3b | 3B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 4GB |
| llama3.1:8b | 8B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8GB |
| codellama:7b | 7B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 7GB |

## 🔧 문제 해결

### 1. Ollama 서비스가 시작되지 않음
```bash
# Windows에서 관리자 권한으로 실행
# 또는 방화벽 설정 확인
```

### 2. 모델 다운로드 실패
```bash
# 인터넷 연결 확인
# 프록시 설정 확인
ollama pull llama3.2:3b --insecure
```

### 3. 메모리 부족
```bash
# 더 작은 모델 사용
ollama pull llama3.2:3b
```

### 4. 응답이 느림
```bash
# GPU 가속 활성화 (NVIDIA GPU 필요)
# 또는 더 작은 모델 사용
```

## 💡 팁

1. **첫 실행 시**: 모델 다운로드에 시간이 걸릴 수 있습니다
2. **메모리 사용량**: 모델 크기에 따라 4-8GB RAM 필요
3. **GPU 가속**: NVIDIA GPU가 있으면 더 빠른 응답 가능
4. **오프라인 사용**: 모델 다운로드 후 인터넷 연결 불필요

## 🎯 추천 설정

의약품 개요서 생성에 최적화된 설정:

```python
# 빠른 응답을 위한 설정
client = OllamaClient(
    model="llama3.2:3b",  # 빠르고 가벼운 모델
    base_url="http://localhost:11434"
)

# 더 정확한 결과를 위한 설정
client = OllamaClient(
    model="qwen2:3b",  # 한국어 성능 우수
    base_url="http://localhost:11434"
)
```

## 🔄 Gemini에서 Ollama로 전환

1. **Ollama 설치 및 모델 다운로드**
2. **Ollama 서비스 시작**: `ollama serve`
3. **Streamlit 앱 수정**: import 경로 변경
4. **테스트**: 새로운 클라이언트로 테스트

이제 할당량 제한 없이 무제한으로 LLM을 사용할 수 있습니다! 🎉 