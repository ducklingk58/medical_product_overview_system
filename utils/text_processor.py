from typing import List, Dict, Any, Tuple, Optional
from llm.ollama_client import generate_overview_with_llm, test_ollama_connection
import re
import json
from collections import Counter
import unicodedata

def clean_foreign_languages(text: str) -> str:
    """외국어, 한자, 특수기호를 제거하고 한국어만 남깁니다."""
    if not text:
        return ""
    
    # 한자 제거 (CJK Unified Ideographs)
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    
    # 일본어 히라가나 제거
    text = re.sub(r'[\u3040-\u309f]', '', text)
    
    # 일본어 가타카나 제거
    text = re.sub(r'[\u30a0-\u30ff]', '', text)
    
    # 태국어 제거
    text = re.sub(r'[\u0e00-\u0e7f]', '', text)
    
    # 아랍어 제거
    text = re.sub(r'[\u0600-\u06ff]', '', text)
    
    # 그리스어 제거
    text = re.sub(r'[\u0370-\u03ff]', '', text)
    
    # 러시아어 제거
    text = re.sub(r'[\u0400-\u04ff]', '', text)
    
    # 특수기호 제거 (의약품 관련 기호는 제외)
    text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ\-\.\,\:\;\(\)\[\]\{\}\+\-\=\*\/\@\#\$\%\&\?\!]', '', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text

def is_korean_text(text: str) -> bool:
    """텍스트가 한국어인지 확인합니다."""
    if not text:
        return False
    
    # 한글 문자 비율 계산
    korean_chars = len(re.findall(r'[가-힣ㄱ-ㅎㅏ-ㅣ]', text))
    total_chars = len(text.replace(' ', ''))
    
    if total_chars == 0:
        return False
    
    return korean_chars / total_chars > 0.3  # 30% 이상이 한글이면 한국어로 간주

def split_into_tokens(text: str) -> List[str]:
    """텍스트를 토큰(단어/글자) 단위로 분할합니다."""
    # 한글, 영문, 숫자, 특수문자를 모두 포함하여 토큰화
    # 한글: 완성형 한글 문자
    # 영문: 알파벳
    # 숫자: 0-9
    # 특수문자: 의약품 관련 특수문자 (mg, g, ml, %, 등)
    
    # 먼저 의약품 관련 특수 패턴을 보호
    protected_patterns = [
        r'\d+\.?\d*\s*(mg|g|ml|mcg|IU|단위|정|캡슐|주사제)',
        r'\d+%',
        r'USP|EP|JP',
        r'필름코팅정',
        r'아세트아미노펜|이부프로펜|아스피린|세마글루타이드|메트포르민|글리메피리드|파세타민'
    ]
    
    # 보호할 패턴들을 임시 마커로 교체
    protected_tokens = []
    token_to_marker = {}
    
    for i, pattern in enumerate(protected_patterns):
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            marker = f"__PROTECTED_{i}_{len(protected_tokens)}__"
            token_to_marker[marker] = match.group()
            protected_tokens.append(match.group())
    
    # 보호된 패턴들을 마커로 교체
    for marker, token in token_to_marker.items():
        text = text.replace(token, marker)
    
    # 일반적인 토큰화 (공백, 구두점 기준)
    tokens = re.split(r'[\s\.,;:!?()\[\]{}"\']+', text)
    
    # 빈 토큰 제거 및 정리
    cleaned_tokens = []
    for token in tokens:
        token = token.strip()
        if token and len(token) >= 1:  # 1글자 이상인 토큰만 포함
            cleaned_tokens.append(token)
    
    # 보호된 토큰들을 원래 값으로 복원
    final_tokens = []
    for token in cleaned_tokens:
        if token.startswith("__PROTECTED_"):
            # 마커에서 원래 토큰 복원
            if token in token_to_marker:
                final_tokens.append(token_to_marker[token])
            else:
                final_tokens.append(token)
        else:
            final_tokens.append(token)
    
    return final_tokens

def extract_keywords_from_tokens(tokens: List[str]) -> List[str]:
    """토큰 리스트에서 의약품 관련 키워드를 추출합니다."""
    keywords = []
    
    # 의약품 관련 키워드 패턴
    medical_patterns = [
        r'\b\d+\.?\d*\s*(mg|g|ml|mcg|IU|단위|정|캡슐|주사제)\b',
        r'\b(정제|주사제|캡슐|시럽|연고|크림|액제|분말|과립|정|필름코팅정)\b',
        r'\b(아세트아미노펜|이부프로펜|아스피린|세마글루타이드|메트포르민|글리메피리드|파세타민)\b',
        r'\b(USP|EP|JP|순도|함량|성분|주성분|첨가제|결합제|희석제)\b',
        r'\b(용기|포장|병|앰플|바이알|플라스틱|유리|알루미늄|블리스터|포일)\b',
        r'\b(용출|붕해|생체이용률|안정성|성능|특성|분해|용해도)\b',
        r'\b(보존제|멸균|미생물|무균|살균|방부제)\b',
        r'\b(개발|연구|제형개발|처방개발|선택근거|개발근거)\b',
        r'\b(외형|모양|색상|색깔|흰색|노란색|각인|표시|마크)\b',
        r'\b(경구용|주사용|외용|내용|투여|복용)\b',
    ]
    
    # 각 토큰을 검사
    for token in tokens:
        token_lower = token.lower()
        
        # 패턴 매칭
        for pattern in medical_patterns:
            if re.search(pattern, token, re.IGNORECASE):
                keywords.append(token)
                break
        
        # 일반적인 의약품 관련 단어들
        medical_words = [
            '제품명', '제형', '함량', '성분', '용기', '포장', '용출', '붕해',
            '안정성', '보존제', '멸균', '개발', '연구', '특성', '성능', '외형',
            '투여', '복용', '경구', '주사', '외용', '내용', '정제', '주사제',
            '캡슐', '시럽', '연고', '크림', '액제', '분말', '과립', '정',
            '필름코팅정', '아세트아미노펜', '이부프로펜', '아스피린', '세마글루타이드',
            '메트포르민', '글리메피리드', '파세타민', 'USP', 'EP', 'JP', '순도',
            '주성분', '첨가제', '결합제', '희석제', '병', '앰플', '바이알',
            '플라스틱', '유리', '알루미늄', '블리스터', '포일', '생체이용률',
            '분해', '용해도', '미생물', '무균', '살균', '방부제', '제형개발',
            '처방개발', '선택근거', '개발근거', '색상', '색깔', '흰색', '노란색',
            '각인', '표시', '마크', '원형', '타원형', '임상', '시험', '흡수',
            '배설', '세균', '균'
        ]
        
        if token_lower in medical_words:
            keywords.append(token)
        
        # 숫자가 포함된 토큰 (함량 정보)
        if re.search(r'\d', token):
            keywords.append(token)
        
        # 한글 의약품 관련 단어 (2글자 이상)
        if len(token) >= 2 and re.search(r'[가-힣]', token):
            # 의약품 관련 한글 단어들
            korean_medical_words = [
                '제품', '제형', '함량', '성분', '용기', '포장', '용출', '붕해',
                '안정', '보존', '멸균', '개발', '연구', '특성', '성능', '외형',
                '투여', '복용', '경구', '주사', '외용', '내용', '정제', '주사',
                '캡슐', '시럽', '연고', '크림', '액제', '분말', '과립', '정',
                '필름', '코팅', '순도', '주성', '첨가', '결합', '희석', '병',
                '앰플', '바이알', '플라스틱', '유리', '알루미늄', '블리스터',
                '포일', '생체', '이용률', '분해', '용해', '미생물', '무균',
                '살균', '방부', '제형', '처방', '선택', '근거', '색상', '색깔',
                '흰색', '노란색', '각인', '표시', '마크', '원형', '타원형',
                '임상', '시험', '흡수', '배설', '세균', '균', '아세트', '아미노',
                '펜', '이부', '프로', '펜', '아스피', '린', '세마', '글루',
                '타이드', '메트', '포르민', '글리', '메피', '리드', '파세',
                '타민'
            ]
            
            if token in korean_medical_words:
                keywords.append(token)
    
    # 중복 제거 및 정리
    unique_keywords = list(set(keywords))
    return [kw.strip() for kw in unique_keywords if len(kw.strip()) >= 1]

def classify_keywords_by_section(keywords: List[str]) -> Dict[str, List[str]]:
    """추출된 키워드를 7개 항목 중 하나에 분류합니다 (가중치 기반)."""
    
    # 각 항목별 대표 키워드 세트 정의 (한국 의약품 설명서 구조에 최적화)
    section_keyword_sets = {
        "성분 및 함량": {
            "keywords": ["성분", "주성분", "첨가제", "결합제", "희석제", "아세트아미노펜", "이부프로펜", "아스피린", "세마글루타이드", "메트포르민", "파세타민", "USP", "EP", "JP", "순도", "아세트", "아미노", "펜", "이부", "프로", "세마", "글루", "타이드", "메트", "포르민", "글리", "메피", "리드", "파세", "타민", "mg", "g", "ml", "mcg", "단위", "함량", "배합목적", "주성분", "첨가성분", "보조성분", "기준", "분량", "투여단위", "함량", "순도", "함유량", "포함량", "규격"],
            "weight": 1.2
        },
        "성상": {
            "keywords": ["외형", "모양", "색상", "색깔", "흰색", "노란색", "각인", "표시", "마크", "원형", "타원형", "정사각형", "직사각형", "무색", "투명", "불투명", "외관", "형태", "크기", "무게", "두께", "지름", "길이", "폭", "성상"],
            "weight": 1.0
        },
        "효능 및 효과": {
            "keywords": ["효능", "효과", "작용", "약리작용", "치료효과", "치료작용", "약효", "효과성", "치료", "개선", "완화", "해열", "진통", "소염", "항염증", "항생", "항균", "항바이러스", "항암", "항고혈압", "항당뇨", "항혈전"],
            "weight": 1.1
        },
        "용법 및 용량": {
            "keywords": ["용법", "용량", "투여", "복용", "투여량", "복용량", "투여방법", "복용방법", "투여간격", "복용간격", "투여기간", "복용기간", "적응증", "투여경로", "복용경로", "경구", "주사", "점적", "도포", "흡입"],
            "weight": 1.1
        },
        "사용상 주의사항": {
            "keywords": ["주의사항", "경고", "금기", "주의", "이상반응", "부작용", "부정반응", "알레르기", "과민반응", "중독", "중독성", "의존성", "습관성", "내성", "내약성", "내성발생", "내약성발생", "주의환자", "주의필요", "주의대상"],
            "weight": 1.0
        },
        "상호작용": {
            "keywords": ["상호작용", "약물상호작용", "약물간상호작용", "약물조합", "약물병용", "약물배합", "약물결합", "약물반응", "약물효과", "약물영향", "약물작용", "약물반응성", "약물민감성"],
            "weight": 0.9
        },
        "임부 및 수유부 사용": {
            "keywords": ["임부", "임신부", "임신", "수유부", "수유", "태아", "태아기", "태아발달", "태아영향", "태아독성", "태아기형", "태아기형성", "태아발달장애", "태아발달지연", "태아발달영향"],
            "weight": 0.9
        },
        "고령자 사용": {
            "keywords": ["고령자", "노인", "노년", "고령", "노화", "노인성", "노년성", "고령자용", "노인용", "노년용", "고령자적합", "노인적합", "노년적합"],
            "weight": 0.8
        },
        "적용 시 주의사항": {
            "keywords": ["적용", "적용시", "적용시주의", "적용주의", "적용시주의사항", "적용주의사항", "적용시주의점", "적용주의점", "적용시주의할점", "적용주의할점"],
            "weight": 0.8
        },
        "보관 및 취급": {
            "keywords": ["보관", "보관조건", "보관방법", "보관온도", "보관습도", "보관장소", "보관기간", "보관주의", "보관주의사항", "보관주의점", "보관주의할점", "취급", "취급방법", "취급주의", "취급주의사항", "취급주의점", "취급주의할점", "포장", "포장단위", "포장방법", "포장주의", "포장주의사항"],
            "weight": 1.0
        },
        "제조 및 판매사 정보": {
            "keywords": ["제조사", "제조업체", "제조회사", "제조기업", "제조공장", "제조시설", "제조설비", "제조라인", "제조공정", "제조과정", "제조방법", "제조기술", "제조품질", "제조관리", "판매사", "판매업체", "판매회사", "판매기업", "판매점", "판매소", "판매처", "판매망", "판매네트워크", "공장", "공장주소", "공장위치", "공장소재지", "공장소재", "소비자상담실", "고객상담실", "상담실", "상담소", "상담센터"],
            "weight": 0.7
        }
    }
    
    section_keywords = {
        "성분 및 함량": [],
        "성상": [],
        "효능 및 효과": [],
        "용법 및 용량": [],
        "사용상 주의사항": [],
        "상호작용": [],
        "임부 및 수유부 사용": [],
        "고령자 사용": [],
        "적용 시 주의사항": [],
        "보관 및 취급": [],
        "제조 및 판매사 정보": []
    }
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        best_section = None
        best_score = 0.0
        
        # 각 항목별로 유사도 점수 계산
        for section, config in section_keyword_sets.items():
            section_keywords_list = config["keywords"]
            weight = config["weight"]
            
            # Jaccard 유사도 계산
            keyword_tokens = set(keyword_lower.split())
            section_tokens = set()
            
            for section_keyword in section_keywords_list:
                section_tokens.update(section_keyword.lower().split())
            
            # 직접 매칭 점수
            direct_match_score = 0.0
            for section_keyword in section_keywords_list:
                if section_keyword.lower() in keyword_lower or keyword_lower in section_keyword.lower():
                    direct_match_score += 1.0
            
            # 부분 매칭 점수
            partial_match_score = 0.0
            for section_keyword in section_keywords_list:
                if any(token in keyword_lower for token in section_keyword.lower().split()):
                    partial_match_score += 0.5
            
            # 숫자가 포함된 키워드는 성분 정보에 높은 점수
            number_bonus = 0.0
            if re.search(r'\d+', keyword) and section == "성분 정보":
                number_bonus = 0.3
            
            # 최종 점수 계산
            total_score = (direct_match_score + partial_match_score + number_bonus) * weight
            
            if total_score > best_score:
                best_score = total_score
                best_section = section
        
        # 최고 점수 항목에 키워드 배정 (점수가 0.5 이상인 경우만)
        if best_section and best_score >= 0.5:
            section_keywords[best_section].append(keyword)
        else:
            # 점수가 낮은 경우 기본 분류 규칙 적용
            if re.search(r'\d+', keyword):
                section_keywords["성분 및 함량"].append(keyword)
            elif any(word in keyword_lower for word in ['정', '캡슐', '주사제', '제형']):
                section_keywords["성상"].append(keyword)
            elif any(word in keyword_lower for word in ['색상', '모양', '각인']):
                section_keywords["성상"].append(keyword)
            elif any(word in keyword_lower for word in ['용기', '포장']):
                section_keywords["보관 및 취급"].append(keyword)
            else:
                # 기본값으로 성분 및 함량에 배정
                section_keywords["성분 및 함량"].append(keyword)
    
    return section_keywords

def calculate_keyword_weights(keywords: List[str], product_tokens: List[str], keyword_frequency: Dict[str, int]) -> List[Tuple[str, float]]:
    """키워드에 가중치를 계산합니다."""
    from difflib import SequenceMatcher
    
    keyword_weights = []
    
    for keyword in keywords:
        weight = 0.0
        
        # 1. 출현 빈도 점수 (40%)
        frequency = keyword_frequency.get(keyword, 1)
        frequency_score = min(frequency * 0.4, 0.4)
        
        # 2. 제품명과의 유사도 점수 (40%)
        similarity_score = 0.0
        for token in product_tokens:
            similarity = SequenceMatcher(None, keyword.lower(), token.lower()).ratio()
            similarity_score = max(similarity_score, similarity)
        similarity_score *= 0.4
        
        # 3. 문맥적 관련성 점수 (20%)
        context_score = 0.0
        if len(keyword) >= 1:  # 1글자 이상인 토큰도 포함
            has_number = bool(re.search(r'\d', keyword))
            has_special = bool(re.search(r'[^\w\s]', keyword))
            has_korean = bool(re.search(r'[가-힣]', keyword))
            has_english = bool(re.search(r'[a-zA-Z]', keyword))
            
            # 한글이나 영문이 포함된 토큰에 더 높은 점수
            context_score = (0.3 + 0.2 * has_number + 0.2 * has_special + 0.2 * has_korean + 0.1 * has_english) * 0.2
        
        weight = frequency_score + similarity_score + context_score
        keyword_weights.append((keyword, weight))
    
    # 가중치 순으로 정렬
    keyword_weights.sort(key=lambda x: x[1], reverse=True)
    return keyword_weights

def get_top_keywords_by_section(section_keywords: Dict[str, List[str]], product_tokens: List[str], keyword_frequency: Dict[str, int], top_n: int = 3) -> Dict[str, List[str]]:
    """각 항목별로 상위 키워드를 선정합니다."""
    top_keywords = {}
    
    for section, keywords in section_keywords.items():
        if not keywords:
            continue
        
        keyword_weights = calculate_keyword_weights(keywords, product_tokens, keyword_frequency)
        top_n_keywords = [kw for kw, weight in keyword_weights[:top_n]]
        top_keywords[section] = top_n_keywords
    
    return top_keywords

def generate_section_sentences(product_name: str, section_keywords: Dict[str, List[str]]) -> Dict[str, str]:
    """각 항목별로 LLM 프롬프트로 문장을 생성합니다."""
    generated_sentences = {}
    
    # 항목별 프롬프트 템플릿 (한국 의약품 설명서 구조에 맞춤)
    section_prompts = {
        "성분 및 함량": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "성분 및 함량" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- 아스피린: "이 제품은 아스피린을 주성분으로 포함하고 있습니다."
- 파세타민: "이 제품은 파세타민을 주성분으로 포함하고 있습니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "성분 및 함량": "[키워드 기반 또는 일반적인 성분 및 함량 설명]"
}}""",

        "성상": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "성상" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- 정제: "이 제품은 일반적인 정제 형태로 제조되었습니다."
- 캡슐: "이 제품은 일반적인 캡슐 형태로 제조되었습니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "성상": "[키워드 기반 또는 일반적인 성상 설명]"
}}""",

        "효능 및 효과": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "효능 및 효과" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- 아스피린: "이 제품은 해열, 진통, 소염 작용을 나타냅니다."
- 파세타민: "이 제품은 해열 및 진통 효과를 나타냅니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "효능 및 효과": "[키워드 기반 또는 일반적인 효능 및 효과 설명]"
}}""",

        "용법 및 용량": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "용법 및 용량" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- 정제: "성인 1회 1정을 1일 3회 식후에 복용합니다."
- 캡슐: "성인 1회 1캡슐을 1일 2회 식후에 복용합니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "용법 및 용량": "[키워드 기반 또는 일반적인 용법 및 용량 설명]"
}}""",

        "사용상 주의사항": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "사용상 주의사항" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "이 제품은 알레르기 반응이 나타날 수 있으므로 주의가 필요합니다."
- "이 제품은 위장 장애를 일으킬 수 있으므로 식후 복용을 권장합니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "사용상 주의사항": "[키워드 기반 또는 일반적인 사용상 주의사항 설명]"
}}""",

        "상호작용": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "상호작용" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "이 제품은 다른 약물과 상호작용할 수 있으므로 의사와 상담 후 복용하세요."
- "이 제품은 항응고제와 함께 복용 시 출혈 위험이 증가할 수 있습니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "상호작용": "[키워드 기반 또는 일반적인 상호작용 설명]"
}}""",

        "임부 및 수유부 사용": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "임부 및 수유부 사용" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "임신 중에는 의사와 상담 후 복용하세요."
- "수유 중에는 의사와 상담 후 복용하세요."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "임부 및 수유부 사용": "[키워드 기반 또는 일반적인 임부 및 수유부 사용 설명]"
}}""",

        "고령자 사용": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "고령자 사용" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "고령자는 신장 기능 저하로 인해 용량 조정이 필요할 수 있습니다."
- "고령자는 의사와 상담 후 복용하세요."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "고령자 사용": "[키워드 기반 또는 일반적인 고령자 사용 설명]"
}}""",

        "적용 시 주의사항": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "적용 시 주의사항" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "이 제품은 차량 운전 시 주의가 필요합니다."
- "이 제품은 기계 조작 시 주의가 필요합니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "적용 시 주의사항": "[키워드 기반 또는 일반적인 적용 시 주의사항 설명]"
}}""",

        "보관 및 취급": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "보관 및 취급" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "이 제품은 서늘하고 건조한 곳에 보관하세요."
- "이 제품은 직사광선을 피해 보관하세요."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "보관 및 취급": "[키워드 기반 또는 일반적인 보관 및 취급 설명]"
}}""",

        "제조 및 판매사 정보": """너는 의약품 개요서를 작성하는 전문가야.
제품명은 "{product_name}"이고, 지금은 "제조 및 판매사 정보" 항목을 작성 중이야.

이 항목에 대한 키워드는 다음과 같아:
{keywords}

만약 문서에서 추출된 키워드가 부족하거나 없다면,
**의약품 상식과 제품명 정보를 기반으로 일반적인 문장을 생성**해줘.

예시:
- "이 제품은 [제조사명]에서 제조하고 [판매사명]에서 판매합니다."
- "이 제품의 제조사는 [제조사명]입니다."

응답은 반드시 JSON 형식으로, 아래 구조로 반환해:

{{
  "제조 및 판매사 정보": "[키워드 기반 또는 일반적인 제조 및 판매사 정보 설명]"
}}"""
    }
    
    for section, keywords in section_keywords.items():
        try:
            if keywords:
                # 키워드가 있는 경우: 키워드 기반 문장 생성
                prompt_template = section_prompts.get(section, "")
                if prompt_template:
                    prompt = prompt_template.format(
                        product_name=product_name or "정보 없음",
                        keywords=str(keywords)
                    )
                    
                    print(f"🔍 {section} 항목 처리 중...")
                    print(f"   제품명: {product_name}")
                    print(f"   키워드: {keywords}")
                    
                    # LLM 호출
                    result = generate_overview_with_llm(prompt, "")
                    print(f"   LLM 응답: {result}")
                    
                    # 결과 파싱
                    if isinstance(result, dict) and result:
                        # JSON 응답인 경우
                        if section in result:
                            generated_sentences[section] = result[section]
                            print(f"   ✅ {section} 문장 생성 성공: {result[section]}")
                        else:
                            # 다른 형태의 JSON 응답 처리
                            for key, value in result.items():
                                if isinstance(value, str):
                                    generated_sentences[section] = value
                                    print(f"   ✅ {section} 문장 생성 성공 (대체 키): {value}")
                                    break
                            else:
                                # 키워드로 직접 문장 생성
                                keywords_str = ", ".join(keywords)
                                generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                                print(f"   ✅ {section} 키워드 기반 문장 생성")
                    elif isinstance(result, str) and result.strip():
                        # 문자열 응답인 경우 JSON 파싱 시도
                        try:
                            json_start = result.find('{')
                            json_end = result.rfind('}')
                            if json_start != -1 and json_end != -1:
                                json_str = result[json_start:json_end+1]
                                parsed = json.loads(json_str)
                                if section in parsed:
                                    generated_sentences[section] = parsed[section]
                                    print(f"   ✅ {section} 문장 생성 성공 (JSON 추출): {parsed[section]}")
                                else:
                                    # 키워드로 직접 문장 생성
                                    keywords_str = ", ".join(keywords)
                                    generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                                    print(f"   ✅ {section} 키워드 기반 문장 생성")
                            else:
                                # 키워드로 직접 문장 생성
                                keywords_str = ", ".join(keywords)
                                generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                                print(f"   ✅ {section} 키워드 기반 문장 생성")
                        except json.JSONDecodeError:
                            # 키워드로 직접 문장 생성
                            keywords_str = ", ".join(keywords)
                            generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                            print(f"   ✅ {section} 키워드 기반 문장 생성")
                    else:
                        # 빈 응답인 경우 키워드로 직접 문장 생성
                        keywords_str = ", ".join(keywords)
                        generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                        print(f"   ✅ {section} 키워드 기반 문장 생성")
                else:
                    # 키워드로 직접 문장 생성
                    keywords_str = ", ".join(keywords)
                    generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
                    print(f"   ✅ {section} 키워드 기반 문장 생성")
            else:
                # 키워드가 없는 경우: LLM에게 해당 항목에 맞는 문장 생성 요청
                no_keyword_prompt = f"""너는 식약처 CTD 기반 의약품 개요서를 작성하는 AI야.
제품명은 "{product_name}"이고, 지금은 "{section}" 항목을 작성 중이야.
이 항목에 대한 정보가 문서에서 추출되지 않았어.

이 제품의 {section}에 대해 일반적인 의약품 개요서 형식으로 문장을 작성해줘.
응답 형식은 반드시 JSON으로, 아래 구조를 따르도록 해:

{{
  "{section}": "[해당 항목에 맞는 일반적인 설명 문장]"
}}"""
                
                print(f"🔍 {section} 항목 처리 중... (정보 없음)")
                print(f"   제품명: {product_name}")
                print(f"   키워드: 없음 - LLM에게 문장 생성 요청")
                
                # LLM 호출
                result = generate_overview_with_llm(no_keyword_prompt, "")
                print(f"   LLM 응답: {result}")
                
                # 결과 파싱
                if isinstance(result, dict) and result:
                    if section in result:
                        generated_sentences[section] = result[section]
                        print(f"   ✅ {section} LLM 문장 생성 성공: {result[section]}")
                    else:
                        # 기본 문장 생성
                        generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
                        print(f"   ⚠️ {section} 기본 문장 생성")
                elif isinstance(result, str) and result.strip():
                    try:
                        json_start = result.find('{')
                        json_end = result.rfind('}')
                        if json_start != -1 and json_end != -1:
                            json_str = result[json_start:json_end+1]
                            parsed = json.loads(json_str)
                            if section in parsed:
                                generated_sentences[section] = parsed[section]
                                print(f"   ✅ {section} LLM 문장 생성 성공: {parsed[section]}")
                            else:
                                generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
                                print(f"   ⚠️ {section} 기본 문장 생성")
                        else:
                            generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
                            print(f"   ⚠️ {section} 기본 문장 생성")
                    except json.JSONDecodeError:
                        generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
                        print(f"   ⚠️ {section} 기본 문장 생성")
                else:
                    generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
                    print(f"   ⚠️ {section} 기본 문장 생성")
            
        except Exception as e:
            print(f"❌ 문장 생성 오류 ({section}): {e}")
            if keywords:
                # 키워드가 있는 경우 키워드 기반 문장 생성
                keywords_str = ", ".join(keywords)
                generated_sentences[section] = f"{product_name}의 {section}는 {keywords_str}를 포함합니다."
            else:
                # 키워드가 없는 경우 기본 문장
                generated_sentences[section] = f"{product_name}의 {section}에 대한 정보가 제공되지 않았습니다."
    
    return generated_sentences

def extract_medical_data_from_text(text: str, user_product_name: str = "") -> Dict[str, Any]:
    """텍스트에서 의약품 관련 데이터를 추출합니다 (토큰 단위 키워드 수집 구조)."""
    from utils.keyword_processor import tokenize_product_name
    
    # Ollama 연결 상태 확인
    if not test_ollama_connection():
        print("⚠️ Ollama에 연결할 수 없습니다. Ollama 서비스를 시작해주세요.")
        return {"3.2.P.1": {}, "3.2.P.2": {}}
    
    # 제품명이 없으면 오류 반환
    if not user_product_name:
        print("❌ 제품명이 입력되지 않았습니다.")
        return {"3.2.P.1": {}, "3.2.P.2": {}}
    
    product_name = user_product_name
    print(f"사용자 입력 제품명: {product_name}")
    
    # 1단계: 제품명 토큰화
    print("1단계: 제품명 토큰화 중...")
    product_tokens = tokenize_product_name(product_name)
    print(f"제품명 토큰: {product_tokens}")
    
    # 2단계: 텍스트를 토큰 단위로 분할
    print("2단계: 텍스트를 토큰 단위로 분할 중...")
    tokens = split_into_tokens(text)
    print(f"총 {len(tokens)}개의 토큰으로 분할됨")
    
    # 3단계: 토큰에서 키워드 추출
    print("3단계: 토큰에서 키워드 추출 중...")
    all_keywords = extract_keywords_from_tokens(tokens)
    print(f"추출된 총 키워드 수: {len(all_keywords)}")
    
    # 4단계: 키워드 출현 빈도 계산
    print("4단계: 키워드 출현 빈도 계산 중...")
    keyword_frequency = Counter(all_keywords)
    
    # 5단계: 키워드를 항목별로 분류
    print("5단계: 키워드 항목별 분류 중...")
    section_keywords = classify_keywords_by_section(all_keywords)
    
    # 6단계: 각 항목별 상위 3개 키워드 선택
    print("6단계: 각 항목별 상위 키워드 선택 중...")
    top_keywords_by_section = get_top_keywords_by_section(
        section_keywords, product_tokens, keyword_frequency, top_n=3
    )
    
    # 7단계: 각 항목별 문장 생성
    print("7단계: 항목별 문장 생성 중...")
    generated_sentences = generate_section_sentences(product_name, top_keywords_by_section)
    
    # 8단계: 한국 의약품 설명서 구조로 변환
    print("8단계: 한국 의약품 설명서 구조로 변환 중...")
    final_data = create_korean_medicine_structure(product_name, generated_sentences)
    
    # 디버깅 정보 저장 (Streamlit 세션에 저장)
    try:
        import streamlit as st
        if 'st' in globals():
            st.session_state['debug_keywords'] = {
                'all_keywords': all_keywords,
                'product_tokens': product_tokens,
                'section_keywords': section_keywords,
                'top_keywords_by_section': top_keywords_by_section,
                'keyword_frequency': dict(keyword_frequency),
                'token_info': {
                    'total_tokens': len(tokens),
                    'processing_method': '토큰 단위 키워드 수집'
                }
            }
            st.session_state['debug_sentences'] = generated_sentences
    except ImportError:
        # Streamlit이 없는 환경에서는 디버깅 정보를 출력만
        print("디버깅 정보:")
        print(f"전체 키워드: {all_keywords}")
        print(f"제품명 토큰: {product_tokens}")
        print(f"항목별 키워드: {section_keywords}")
        print(f"상위 키워드: {top_keywords_by_section}")
        print(f"생성된 문장: {generated_sentences}")
        print(f"토큰 정보: {len(tokens)}개 토큰")
    
    print(f"최종 결과: {final_data}")
    return final_data

def clean_and_improve_text_with_ollama(product_name: str, original_text: str, section_name: str, subsection_name: str = None) -> str:
    """Ollama를 사용하여 텍스트를 정제하고 개선합니다. (최적화된 버전)"""
    try:
        # 기본 한국어 정제 (외국어 제거)
        cleaned_text = clean_foreign_languages(original_text)
        
        # 한국어가 아닌 경우 기본 문장 반환
        if not is_korean_text(cleaned_text) and not is_korean_text(original_text):
            return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
        # 텍스트가 이미 깨끗하고 한국어인 경우 그대로 반환
        if is_korean_text(cleaned_text) and len(cleaned_text.strip()) > 10:
            return cleaned_text
        
        # Ollama 호출이 필요한 경우에만 실행
        from llm.ollama_client import OllamaClient
        client = OllamaClient()
        
        # 간단한 프롬프트로 속도 향상
        if subsection_name:
            prompt = f"""제품명: {product_name}, 항목: {section_name}-{subsection_name}
원본: {cleaned_text}
자연스러운 한국어로 1-2문장으로 정제해주세요. JSON 형식: {{"{subsection_name}": "내용"}}"""
        else:
            prompt = f"""제품명: {product_name}, 항목: {section_name}
원본: {cleaned_text}
자연스러운 한국어로 1-2문장으로 정제해주세요. JSON 형식: {{"{section_name}": "내용"}}"""
        
        print(f"🔧 {section_name}{' - ' + subsection_name if subsection_name else ''} 항목 텍스트 정제 중...")
        
        result = client.generate_response(prompt)
        
        if result.get("error", False):
            print(f"   ❌ Ollama 오류: {result.get('text', 'Unknown error')}")
            return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
        response_text = result.get("text", "")
        if not response_text:
            return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
        # JSON 추출
        json_result = client.extract_json_from_response(response_text)
        
        if json_result:
            if subsection_name and subsection_name in json_result:
                content = json_result[subsection_name]
                print(f"   ✅ {subsection_name} 정제 성공: {content[:50]}...")
                return content
            elif section_name in json_result:
                content = json_result[section_name]
                print(f"   ✅ {section_name} 정제 성공: {content[:50]}...")
                return content
        
        # JSON 파싱 실패 시 기본 문장 반환
        return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
    except Exception as e:
        print(f"❌ Ollama 텍스트 정제 오류 ({section_name}): {e}")
        return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."

def generate_missing_content_with_ollama(product_name: str, section_name: str, subsection_name: str = None) -> str:
    """Ollama를 사용하여 누락된 내용을 생성합니다. (최적화된 버전)"""
    try:
        from llm.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        # 간단한 프롬프트로 속도 향상
        if subsection_name:
            prompt = f"""제품명: {product_name}, 항목: {section_name}-{subsection_name}
의약품 상식과 제품명 정보를 바탕으로 1-2문장으로 생성해주세요. JSON 형식: {{"{subsection_name}": "내용"}}"""
        else:
            prompt = f"""제품명: {product_name}, 항목: {section_name}
의약품 상식과 제품명 정보를 바탕으로 1-2문장으로 생성해주세요. JSON 형식: {{"{section_name}": "내용"}}"""
        
        print(f"🔍 {section_name}{' - ' + subsection_name if subsection_name else ''} 항목 Ollama 생성 중...")
        
        result = client.generate_response(prompt)
        
        if result.get("error", False):
            print(f"   ❌ Ollama 오류: {result.get('text', 'Unknown error')}")
            return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
        response_text = result.get("text", "")
        if not response_text:
            return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
        # JSON 추출
        json_result = client.extract_json_from_response(response_text)
        
        if json_result:
            if subsection_name and subsection_name in json_result:
                content = json_result[subsection_name]
                print(f"   ✅ {subsection_name} 생성 성공: {content[:50]}...")
                return content
            elif section_name in json_result:
                content = json_result[section_name]
                print(f"   ✅ {section_name} 생성 성공: {content[:50]}...")
                return content
        
        # JSON 파싱 실패 시 기본 문장 반환
        return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."
        
    except Exception as e:
        print(f"❌ Ollama 내용 생성 오류 ({section_name}): {e}")
        return f"{product_name}의 {section_name}{' - ' + subsection_name if subsection_name else ''}에 대한 정보입니다."

def create_korean_medicine_structure(product_name: str, generated_sentences: Dict[str, str]) -> Dict[str, Any]:
    """생성된 문장들을 한국 의약품 설명서 구조로 변환합니다 (Ollama 자동 생성 및 텍스트 정제 포함)."""
    
    def get_content_or_generate(section_name: str, subsection_name: str = None) -> str:
        """내용이 없으면 Ollama로 생성, 있으면 정제"""
        content = generated_sentences.get(section_name, "")
        if not content or content == "정보 없음" or "정보가 제공되지 않았습니다" in content:
            return generate_missing_content_with_ollama(product_name, section_name, subsection_name)
        else:
            # 기존 내용이 있으면 정제
            return clean_and_improve_text_with_ollama(product_name, content, section_name, subsection_name)
    
    medicine_structure = {
        "제품명": product_name,
        "성분 및 함량": [
            {
                "성분명": "주성분",
                "규격": get_content_or_generate("성분 및 함량"),
                "기준": get_content_or_generate("성분 및 함량", "기준")
            }
        ],
        "성상": get_content_or_generate("성상"),
        "효능 및 효과": [
            get_content_or_generate("효능 및 효과")
        ],
        "용법 및 용량": [
            {
                "적응증": get_content_or_generate("용법 및 용량", "적응증"),
                "용량": get_content_or_generate("용법 및 용량")
            }
        ],
        "사용상 주의사항": {
            "경고": [
                get_content_or_generate("사용상 주의사항", "경고")
            ],
            "금기": [
                get_content_or_generate("사용상 주의사항", "금기")
            ],
            "주의 필요 환자": [
                get_content_or_generate("사용상 주의사항", "주의 필요 환자")
            ],
            "이상반응": [
                get_content_or_generate("사용상 주의사항", "이상반응")
            ]
        },
        "상호작용": [
            get_content_or_generate("상호작용")
        ],
        "임부 및 수유부 사용": {
            "임신 1~2기": get_content_or_generate("임부 및 수유부 사용", "임신 1~2기"),
            "임신 3기": get_content_or_generate("임부 및 수유부 사용", "임신 3기"),
            "수유부": get_content_or_generate("임부 및 수유부 사용", "수유부")
        },
        "고령자 사용": get_content_or_generate("고령자 사용"),
        "적용 시 주의사항": [
            get_content_or_generate("적용 시 주의사항")
        ],
        "보관 및 취급": {
            "보관조건": get_content_or_generate("보관 및 취급", "보관조건"),
            "포장단위": get_content_or_generate("보관 및 취급", "포장단위"),
            "주의사항": [
                get_content_or_generate("보관 및 취급", "주의사항")
            ]
        },
        "제조 및 판매사 정보": {
            "제조사": get_content_or_generate("제조 및 판매사 정보", "제조사"),
            "판매사": get_content_or_generate("제조 및 판매사 정보", "판매사"),
            "공장 주소": get_content_or_generate("제조 및 판매사 정보", "공장 주소"),
            "소비자상담실": get_content_or_generate("제조 및 판매사 정보", "소비자상담실")
        }
    }
    
    return medicine_structure

def create_korean_ctd_structure(product_name: str, generated_sentences: Dict[str, str]) -> Dict[str, Any]:
    """기존 CTD 구조 (하위 호환성을 위해 유지)"""
    return create_korean_medicine_structure(product_name, generated_sentences)

# 기존 함수들은 호환성을 위해 유지하되 새로운 구조를 사용하도록 수정
def split_into_blocks(text: str) -> List[str]:
    """텍스트를 문단 단위로 분할합니다. (호환성 유지)"""
    return split_into_tokens(text)  # 새로운 구조 사용

def split_text_into_chunks(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """텍스트를 작은 청크로 분할합니다. (호환성 유지)"""
    return split_into_tokens(text)  # 새로운 구조 사용

def extract_medical_data_from_text_with_chunks(text: str, user_product_name: str, chunk_size: int = 200, overlap_size: int = 30) -> Dict[str, Any]:
    """청크 기반으로 텍스트에서 의약품 관련 데이터를 추출합니다. (호환성 유지)"""
    # 새로운 구조 사용 (청크 설정은 무시하고 토큰 단위 사용)
    return extract_medical_data_from_text(text, user_product_name) 