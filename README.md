# 의약품 제품 개요서 자동 생성 시스템

## 📋 개요
의약품 관련 문서를 분석하여 한국 의약품 설명서 표준 구조에 맞는 개요서를 자동으로 생성하는 시스템입니다.

## 🚀 주요 기능
- **문서 분석**: PDF, DOCX, JSON 파일에서 의약품 정보 추출
- **키워드 추출**: 토큰 단위로 키워드를 추출하고 분류
- **자동 생성**: Ollama LLM을 사용한 누락 정보 자동 보완
- **다양한 출력**: PDF, Word, JSON 형식으로 내보내기
- **텍스트 정제**: 외국어 제거 및 자연스러운 한국어로 정제

## 🛠️ 기술 스택
- **Backend**: Python 3.8+
- **Web Framework**: Streamlit
- **LLM**: Ollama (로컬 실행)
- **PDF 생성**: ReportLab
- **문서 처리**: python-docx, pdfplumber

## 📦 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd medical_product_overview_system
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Ollama 설치 및 설정
```bash
# Ollama 설치 (Windows)
# https://ollama.ai/download 에서 다운로드

# 모델 다운로드
ollama pull llama3.2:3b

# 서비스 시작
ollama serve
```

## 🏃‍♂️ 실행 방법

### 1. Ollama 서비스 시작
```bash
# 새 터미널에서
ollama serve
```

### 2. Streamlit 앱 실행
```bash
streamlit run app.py
```

### 3. 브라우저에서 접속
```
http://localhost:8501
```

## 📁 프로젝트 구조
```
medical_product_overview_system/
├── app.py                 # 메인 Streamlit 앱
├── requirements.txt       # Python 의존성
├── README.md             # 프로젝트 설명서
├── OLLAMA_SETUP.md       # Ollama 설정 가이드
├── FREE_LLM_OPTIONS.md   # 무료 LLM 옵션 가이드
├── install_ollama.py     # Ollama 설치 스크립트
├── llm/                  # LLM 클라이언트
│   ├── __init__.py
│   └── ollama_client.py  # Ollama 클라이언트
├── parser/               # 문서 파서
│   ├── __init__.py
│   ├── docx_parser.py    # DOCX 파서
│   ├── json_parser.py    # JSON 파서
│   └── pdf_parser.py     # PDF 파서
├── schema/               # 데이터 스키마
│   └── overview_schema.py
├── utils/                # 유틸리티 모듈
│   ├── __init__.py
│   ├── config.py         # 설정 관리
│   ├── embedding.py      # 임베딩 처리
│   ├── file_utils.py     # 파일 처리
│   ├── keyword_processor.py # 키워드 처리
│   ├── llm.py           # LLM 유틸리티
│   ├── output_format.py # 출력 형식
│   ├── parallel.py      # 병렬 처리
│   ├── pdf_exporter.py  # PDF 내보내기
│   ├── prompt_templates.py # 프롬프트 템플릿
│   ├── sample_data.py   # 샘플 데이터
│   ├── search.py        # 검색 기능
│   ├── text_processor.py # 텍스트 처리
│   └── word_exporter.py # Word 내보내기
└── requirement_package/  # 패키지 파일들
```

## 🎯 사용 방법

### 1. 제품명 입력
- 필수 입력 항목
- 예시: "경동아스피린장용정", "세마글루타이드 주사제"

### 2. 문서 업로드
- 지원 형식: PDF, DOCX, JSON
- 문서에서 의약품 관련 정보 추출

### 3. 자동 생성
- 키워드 추출 및 분류
- Ollama를 통한 누락 정보 자동 보완
- 텍스트 정제 및 자연스러운 한국어 변환

### 4. 결과 다운로드
- PDF: 참고 이미지 스타일의 전문 문서
- Word: 편집 가능한 DOCX 형식
- JSON: 구조화된 데이터

## 🔧 주요 특징

### 토큰 단위 키워드 수집 시스템
- 텍스트를 토큰(단어/글자) 단위로 분할
- 각 토큰에서 키워드 추출
- 11개 항목으로 자동 분류
- 항목별 상위 키워드 선정

### Ollama 기반 자동 생성
- 로컬에서 실행되는 무료 LLM
- 할당량 제한 없음
- 개인정보 보호
- "정보 없음" 항목 자동 보완

### 전문적인 PDF 출력
- 참고 이미지 스타일 적용
- 파란색 헤더 박스
- 번호 매기기 (1-1, 1-2 등)
- 원형 번호 (①, ② 등)
- 복사 가능한 텍스트

## 📊 생성되는 JSON 구조
```json
{
  "제품명": "",
  "성분 및 함량": [],
  "성상": "",
  "효능 및 효과": [],
  "용법 및 용량": [],
  "사용상 주의사항": {
    "경고": [],
    "금기": [],
    "주의 필요 환자": [],
    "이상반응": []
  },
  "상호작용": [],
  "임부 및 수유부 사용": {
    "임신 1~2기": "",
    "임신 3기": "",
    "수유부": ""
  },
  "고령자 사용": "",
  "적용 시 주의사항": [],
  "보관 및 취급": {
    "보관조건": "",
    "포장단위": "",
    "주의사항": []
  },
  "제조 및 판매사 정보": {
    "제조사": "",
    "판매사": "",
    "공장 주소": "",
    "소비자상담실": ""
  }
}
```

## 🐛 문제 해결

### Ollama 연결 실패
1. Ollama 서비스가 실행 중인지 확인
2. `ollama serve` 명령어로 서비스 시작
3. 모델이 다운로드되었는지 확인: `ollama list`

### PDF 생성 실패
1. ReportLab 라이브러리 설치 확인
2. 한국어 폰트 설정 확인
3. 파일 권한 확인

### 메모리 부족
1. 더 작은 모델 사용: `llama3.2:3b`
2. 시스템 메모리 확인
3. 다른 프로세스 종료

## 📝 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의
프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요. 
