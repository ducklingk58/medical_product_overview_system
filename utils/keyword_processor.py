from typing import List, Dict, Tuple, Any
import re
from collections import Counter
from difflib import SequenceMatcher

def tokenize_product_name(product_name: str) -> List[str]:
    if not product_name:
        return []
    tokens = []
    number_unit_pattern = r'\d+\.?\d*\s*(mg|g|ml|mcg|IU|단위|정|캡슐|주사제)'
    number_units = re.findall(number_unit_pattern, product_name, re.IGNORECASE)
    remaining_text = re.sub(number_unit_pattern, '', product_name, flags=re.IGNORECASE)
    remaining_tokens = re.split(r'\s+', remaining_text.strip())
    tokens.extend(remaining_tokens)
    tokens.extend(number_units)
    tokens = [token.strip() for token in tokens if token.strip()]
    return tokens

def extract_medical_keywords_from_text(text: str) -> List[str]:
    medical_patterns = [
        r'\b\d+\.?\d*\s*(mg|g|ml|mcg|IU|단위)\b',
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
    keywords = []
    for pattern in medical_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)
    common_words = [
        '제품명', '제형', '함량', '성분', '용기', '포장', '용출', '붕해',
        '안정성', '보존제', '멸균', '개발', '연구', '특성', '성능', '외형',
        '투여', '복용', '경구', '주사', '외용', '내용'
    ]
    for word in common_words:
        if word in text:
            keywords.append(word)
    unique_keywords = list(set(keywords))
    return [kw.strip() for kw in unique_keywords if len(kw.strip()) >= 2]

def classify_keywords_by_section(keywords: List[str]) -> Dict[str, List[str]]:
    section_keywords = {
        "dosage_form": [],
        "strength": [],
        "appearance": [],
        "composition": [],
        "container": [],
        "development": [],
        "performance": [],
        "microbiological": []
    }
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if any(word in keyword_lower for word in ['정제', '주사제', '캡슐', '시럽', '연고', '크림', '정', '필름코팅정', '경구용']):
            section_keywords["dosage_form"].append(keyword)
        elif any(word in keyword_lower for word in ['mg', 'g', 'ml', 'mcg', '단위', '함량']) or re.search(r'\d+', keyword):
            section_keywords["strength"].append(keyword)
        elif any(word in keyword_lower for word in ['외형', '모양', '색상', '색깔', '흰색', '노란색', '각인', '표시', '마크']):
            section_keywords["appearance"].append(keyword)
        elif any(word in keyword_lower for word in ['성분', '주성분', '첨가제', '결합제', '희석제', '아세트아미노펜', '이부프로펜', '아스피린', '세마글루타이드', '메트포르민', '파세타민']):
            section_keywords["composition"].append(keyword)
        elif any(word in keyword_lower for word in ['용기', '포장', '병', '앰플', '바이알', '플라스틱', '유리', '알루미늄', '블리스터', '포일']):
            section_keywords["container"].append(keyword)
        elif any(word in keyword_lower for word in ['개발', '연구', '제형개발', '처방개발', '선택근거', '개발근거']):
            section_keywords["development"].append(keyword)
        elif any(word in keyword_lower for word in ['용출', '붕해', '생체이용률', '안정성', '성능', '특성', '분해', '용해도']):
            section_keywords["performance"].append(keyword)
        elif any(word in keyword_lower for word in ['보존제', '멸균', '미생물', '무균', '살균', '방부제']):
            section_keywords["microbiological"].append(keyword)
    return section_keywords

def calculate_keyword_weights(keywords: List[str], product_tokens: List[str], keyword_frequency: Dict[str, int]) -> List[Tuple[str, float]]:
    keyword_weights = []
    for keyword in keywords:
        weight = 0.0
        frequency = keyword_frequency.get(keyword, 1)
        frequency_score = min(frequency * 0.2, 0.4)
        similarity_score = 0.0
        for token in product_tokens:
            similarity = SequenceMatcher(None, keyword.lower(), token.lower()).ratio()
            similarity_score = max(similarity_score, similarity)
        similarity_score *= 0.4
        length_score = 0.0
        if len(keyword) >= 3:
            has_number = bool(re.search(r'\d', keyword))
            has_special = bool(re.search(r'[^\w\s]', keyword))
            length_score = (0.5 + 0.3 * has_number + 0.2 * has_special) * 0.2
        weight = frequency_score + similarity_score + length_score
        keyword_weights.append((keyword, weight))
    keyword_weights.sort(key=lambda x: x[1], reverse=True)
    return keyword_weights

def get_top_keywords_by_section(section_keywords: Dict[str, List[str]], product_tokens: List[str], keyword_frequency: Dict[str, int], top_n: int = 3) -> Dict[str, List[str]]:
    top_keywords = {}
    for section, keywords in section_keywords.items():
        if not keywords:
            continue
        keyword_weights = calculate_keyword_weights(keywords, product_tokens, keyword_frequency)
        top_n_keywords = [kw for kw, weight in keyword_weights[:top_n]]
        top_keywords[section] = top_n_keywords
    return top_keywords 