#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
개선된 키워드 분석 시스템
Ollama의 키워드 구분 및 연관성 파악 능력 향상을 위한 모듈
"""

import re
import json
from typing import List, Dict, Any, Tuple
from collections import Counter
from difflib import SequenceMatcher
from llm.ollama_client import generate_overview_with_llm, test_ollama_connection
from utils.improved_prompts import (
    IMPROVED_SECTION_PROMPTS, 
    CONTEXT_ANALYSIS_PROMPT, 
    KEYWORD_RELATIONSHIP_PROMPT
)

class EnhancedKeywordAnalyzer:
    """개선된 키워드 분석기"""
    
    def __init__(self):
        self.medical_knowledge_base = self._load_medical_knowledge()
    
    def _load_medical_knowledge(self) -> Dict[str, Any]:
        """의약품 전문 지식 베이스 로드"""
        return {
            "active_ingredients": {
                "analgesics": ["아스피린", "아세트아미노펜", "이부프로펜", "파세타민"],
                "antidiabetics": ["세마글루타이드", "메트포르민", "글리메피리드"],
                "antibiotics": ["아목시실린", "세파졸린", "독시사이클린"],
                "antihypertensives": ["암로디핀", "로사르탄", "리시노프릴"]
            },
            "dosage_forms": {
                "oral": ["정제", "캡슐", "시럽", "액제", "분말", "과립", "정", "필름코팅정"],
                "injectable": ["주사제", "액제", "분말주사제"],
                "topical": ["연고", "크림", "젤", "로션"],
                "special": ["장용정", "서방정", "구강붕해정"]
            },
            "containers": {
                "primary": ["병", "앰플", "바이알", "블리스터", "포일"],
                "materials": ["플라스틱", "유리", "알루미늄", "종이"],
                "secondary": ["카톤", "포일", "블리스터"]
            },
            "performance_indicators": {
                "dissolution": ["용출", "용해도", "용해율"],
                "disintegration": ["붕해", "붕해도", "붕해시간"],
                "bioavailability": ["생체이용률", "흡수율", "흡수도"],
                "stability": ["안정성", "분해", "변질"]
            }
        }
    
    def analyze_keyword_context(self, text: str, keyword: str) -> Dict[str, Any]:
        """키워드의 컨텍스트를 분석합니다."""
        if not test_ollama_connection():
            return self._fallback_context_analysis(text, keyword)
        
        try:
            prompt = CONTEXT_ANALYSIS_PROMPT.format(
                text=text[:1000],  # 텍스트 길이 제한
                keyword=keyword
            )
            
            result = generate_overview_with_llm(prompt, "")
            
            if isinstance(result, dict):
                return result
            else:
                return self._fallback_context_analysis(text, keyword)
                
        except Exception as e:
            print(f"컨텍스트 분석 오류: {e}")
            return self._fallback_context_analysis(text, keyword)
    
    def _fallback_context_analysis(self, text: str, keyword: str) -> Dict[str, Any]:
        """Ollama 연결 실패 시 기본 컨텍스트 분석"""
        # 키워드 주변 텍스트 추출
        keyword_index = text.find(keyword)
        if keyword_index == -1:
            return {
                "context": "키워드를 찾을 수 없음",
                "sentiment": "neutral",
                "relevance": "low",
                "confidence": 0.3,
                "reasoning": "키워드가 텍스트에 없음"
            }
        
        # 키워드 주변 100자 추출
        start = max(0, keyword_index - 50)
        end = min(len(text), keyword_index + len(keyword) + 50)
        context_text = text[start:end]
        
        # 기본 감정 분석
        negative_words = ["부작용", "위험", "주의", "금기", "중단", "중지"]
        positive_words = ["효과", "개선", "치료", "완화", "효능"]
        
        sentiment = "neutral"
        for word in negative_words:
            if word in context_text:
                sentiment = "negative"
                break
        for word in positive_words:
            if word in context_text:
                sentiment = "positive"
                break
        
        return {
            "context": context_text,
            "sentiment": sentiment,
            "relevance": "medium",
            "confidence": 0.6,
            "reasoning": "기본 텍스트 분석으로 추정"
        }
    
    def analyze_keyword_relationships(self, product_name: str, keywords: List[str]) -> Dict[str, Any]:
        """키워드들 간의 연관성을 분석합니다."""
        if not test_ollama_connection():
            return self._fallback_relationship_analysis(product_name, keywords)
        
        try:
            prompt = KEYWORD_RELATIONSHIP_PROMPT.format(
                product_name=product_name,
                keywords=str(keywords)
            )
            
            result = generate_overview_with_llm(prompt, "")
            
            if isinstance(result, dict):
                return result
            else:
                return self._fallback_relationship_analysis(product_name, keywords)
                
        except Exception as e:
            print(f"키워드 연관성 분석 오류: {e}")
            return self._fallback_relationship_analysis(product_name, keywords)
    
    def _fallback_relationship_analysis(self, product_name: str, keywords: List[str]) -> Dict[str, Any]:
        """Ollama 연결 실패 시 기본 연관성 분석"""
        keyword_groups = []
        
        # 의약품 성분 그룹화
        ingredient_keywords = []
        for keyword in keywords:
            for category, ingredients in self.medical_knowledge_base["active_ingredients"].items():
                if keyword in ingredients:
                    ingredient_keywords.append(keyword)
                    break
        
        if ingredient_keywords:
            keyword_groups.append({
                "group_name": "의약품 성분",
                "keywords": ingredient_keywords,
                "relationship": "주성분 및 활성 성분",
                "importance": "high"
            })
        
        # 제형 그룹화
        dosage_form_keywords = []
        for keyword in keywords:
            for category, forms in self.medical_knowledge_base["dosage_forms"].items():
                if keyword in forms:
                    dosage_form_keywords.append(keyword)
                    break
        
        if dosage_form_keywords:
            keyword_groups.append({
                "group_name": "제형",
                "keywords": dosage_form_keywords,
                "relationship": "투여 형태 및 제형",
                "importance": "high"
            })
        
        # 용기 그룹화
        container_keywords = []
        for keyword in keywords:
            for category, containers in self.medical_knowledge_base["containers"].items():
                if keyword in containers:
                    container_keywords.append(keyword)
                    break
        
        if container_keywords:
            keyword_groups.append({
                "group_name": "용기 및 포장",
                "keywords": container_keywords,
                "relationship": "포장 재질 및 형태",
                "importance": "medium"
            })
        
        return {
            "keyword_groups": keyword_groups,
            "overall_analysis": f"총 {len(keywords)}개 키워드에서 {len(keyword_groups)}개 그룹으로 분류됨"
        }
    
    def enhanced_classify_keywords(self, keywords: List[str], text: str, product_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """개선된 키워드 분류 (컨텍스트 분석 포함)"""
        classified_keywords = {
            "제품 기본 정보": [],
            "외형 정보": [],
            "성분 정보": [],
            "용기 정보": [],
            "개발 이력": [],
            "성능 특성": [],
            "미생물학적 특성": []
        }
        
        # 각 키워드에 대해 컨텍스트 분석 수행
        for keyword in keywords:
            context_analysis = self.analyze_keyword_context(text, keyword)
            
            # 기본 분류 (기존 로직)
            section = self._basic_classify_keyword(keyword)
            
            # 컨텍스트 분석 결과를 반영하여 분류 조정
            if context_analysis["confidence"] > 0.7:
                # 높은 신뢰도의 컨텍스트 분석 결과를 반영
                if context_analysis["sentiment"] == "negative":
                    # 부정적 맥락에서는 해당 섹션에서 제외하거나 다른 섹션으로 이동
                    if section == "성분 정보" and "부작용" in context_analysis["context"]:
                        section = "개발 이력"  # 부작용은 개발 이력에 포함
            
            # 분류된 키워드에 컨텍스트 정보 추가
            classified_keywords[section].append({
                "keyword": keyword,
                "context": context_analysis,
                "confidence": context_analysis["confidence"]
            })
        
        return classified_keywords
    
    def _basic_classify_keyword(self, keyword: str) -> str:
        """기본 키워드 분류 (기존 로직)"""
        keyword_lower = keyword.lower()
        
        # 제품 기본 정보
        if any(word in keyword_lower for word in ['제품명', '제형', '정제', '주사제', '캡슐', '시럽', '연고', '크림', '정', '필름코팅정', '경구용', '필름', '코팅']):
            return "제품 기본 정보"
        
        # 외형 정보
        elif any(word in keyword_lower for word in ['외형', '모양', '색상', '색깔', '흰색', '노란색', '각인', '표시', '마크', '원형', '타원형']):
            return "외형 정보"
        
        # 성분 정보
        elif any(word in keyword_lower for word in ['성분', '주성분', '첨가제', '결합제', '희석제', '아세트아미노펜', '이부프로펜', '아스피린', '세마글루타이드', '메트포르민', '파세타민', 'USP', 'EP', 'JP', '순도']):
            return "성분 정보"
        
        # 용기 정보
        elif any(word in keyword_lower for word in ['용기', '포장', '병', '앰플', '바이알', '플라스틱', '유리', '알루미늄', '블리스터', '포일']):
            return "용기 정보"
        
        # 개발 이력
        elif any(word in keyword_lower for word in ['개발', '연구', '제형개발', '처방개발', '선택근거', '개발근거', '임상', '시험', '제형', '처방', '선택', '근거']):
            return "개발 이력"
        
        # 성능 특성
        elif any(word in keyword_lower for word in ['용출', '붕해', '생체이용률', '안정성', '성능', '특성', '분해', '용해도', '흡수', '배설', '생체', '이용률', '용해', '안정']):
            return "성능 특성"
        
        # 미생물학적 특성
        elif any(word in keyword_lower for word in ['보존제', '멸균', '미생물', '무균', '살균', '방부제', '세균', '균', '보존', '멸균', '미생물', '무균', '살균', '방부']):
            return "미생물학적 특성"
        
        # 함량 정보는 성분 정보에 포함
        elif any(word in keyword_lower for word in ['mg', 'g', 'ml', 'mcg', '단위', '함량']) or re.search(r'\d+', keyword):
            return "성분 정보"
        
        # 기본값
        return "제품 기본 정보"
    
    def get_enhanced_top_keywords(self, classified_keywords: Dict[str, List[Dict[str, Any]]], top_n: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """컨텍스트 분석을 반영한 상위 키워드 선정"""
        top_keywords = {}
        
        for section, keywords_with_context in classified_keywords.items():
            if not keywords_with_context:
                continue
            
            # 신뢰도와 관련성을 고려하여 정렬
            sorted_keywords = sorted(
                keywords_with_context,
                key=lambda x: (
                    x["context"]["confidence"],
                    x["context"]["relevance"] == "high",
                    x["context"]["sentiment"] != "negative"
                ),
                reverse=True
            )
            
            # 상위 N개 선택
            top_keywords[section] = sorted_keywords[:top_n]
        
        return top_keywords
    
    def generate_enhanced_sentences(self, product_name: str, top_keywords: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """개선된 프롬프트를 사용한 문장 생성"""
        generated_sentences = {}
        
        for section, keywords_with_context in top_keywords.items():
            if not keywords_with_context:
                continue
            
            try:
                # 키워드만 추출
                keywords = [kw["keyword"] for kw in keywords_with_context]
                
                # 개선된 프롬프트 사용
                prompt_template = IMPROVED_SECTION_PROMPTS.get(section, "")
                if not prompt_template:
                    continue
                
                prompt = prompt_template.format(
                    product_name=product_name or "정보 없음",
                    keywords=str(keywords)
                )
                
                # LLM 호출
                result = generate_overview_with_llm(prompt, "")
                
                # 결과 파싱
                if isinstance(result, dict):
                    if section in result:
                        generated_sentences[section] = result[section]
                    else:
                        # 다른 형태의 JSON 응답 처리
                        for key, value in result.items():
                            if isinstance(value, str):
                                generated_sentences[section] = value
                                break
                elif isinstance(result, str):
                    try:
                        parsed = json.loads(result)
                        if section in parsed:
                            generated_sentences[section] = parsed[section]
                        else:
                            generated_sentences[section] = f"이 제품의 {section}에 대한 정보가 있습니다."
                    except json.JSONDecodeError:
                        generated_sentences[section] = result
                
            except Exception as e:
                print(f"개선된 문장 생성 오류 ({section}): {e}")
                keywords_str = ", ".join([kw["keyword"] for kw in keywords_with_context])
                generated_sentences[section] = f"이 제품의 {section}에 대한 정보가 있습니다. 주요 키워드: {keywords_str}"
        
        return generated_sentences 