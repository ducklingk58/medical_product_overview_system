#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF 내보내기 모듈
의약품 개요서를 PDF 형식으로 생성하는 기능
참고 이미지의 스타일을 적용하여 전문적인 문서 생성
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from typing import Dict, Any, List
import os

class MedicalPDFExporter:
    """의약품 개요서 PDF 생성기"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """한국어 폰트 설정"""
        try:
            # Windows 기본 폰트 사용 (여러 경로 시도)
            font_paths = [
                'C:/Windows/Fonts/malgun.ttf',
                'C:/Windows/Fonts/malgun.ttc',
                'C:/Windows/Fonts/gulim.ttc',
                'C:/Windows/Fonts/batang.ttc',
                'malgun.ttf',
                'malgun.ttc',
                'gulim.ttc',
                'batang.ttc'
            ]
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                        self.korean_font = 'KoreanFont'
                        print(f"✅ 한국어 폰트 로드 성공: {font_path}")
                        return
                except Exception as e:
                    print(f"폰트 로드 실패 {font_path}: {e}")
                    continue
            
            # 폰트가 없으면 기본 폰트 사용
            self.korean_font = 'Helvetica'
            print("⚠️ 한국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
            
        except Exception as e:
            print(f"⚠️ 폰트 설정 오류: {e}")
            self.korean_font = 'Helvetica'
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 파란색 헤더 스타일 (참고 이미지의 파란색 박스)
        if 'BlueHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BlueHeader',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=white,
                backColor=HexColor('#1f4e79'),
                alignment=TA_CENTER,
                spaceAfter=12,
                spaceBefore=12,
                leftIndent=0,
                rightIndent=0,
                fontName='Helvetica-Bold'
            ))
        
        # 메인 섹션 제목 스타일 (파란색 박스 + 번호)
        if 'MainSection' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MainSection',
                parent=self.styles['Heading1'],
                fontSize=16,
                textColor=black,
                alignment=TA_LEFT,
                spaceAfter=8,
                spaceBefore=16,
                leftIndent=0,
                fontName='Helvetica-Bold'
            ))
        
        # 서브 섹션 제목 스타일 (1-1, 1-2 등)
        if 'SubSection' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubSection',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=black,
                alignment=TA_LEFT,
                spaceAfter=6,
                spaceBefore=12,
                leftIndent=10,
                fontName='Helvetica-Bold'
            ))
        
        # 본문 스타일 (기존 BodyText가 있으므로 MedicalBodyText로 변경)
        if 'MedicalBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MedicalBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=black,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
                spaceBefore=6,
                leftIndent=20,
                fontName='Helvetica'
            ))
        
        # 리스트 스타일
        if 'MedicalListText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='MedicalListText',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=black,
                alignment=TA_LEFT,
                spaceAfter=4,
                spaceBefore=4,
                leftIndent=30,
                fontName='Helvetica'
            ))
    
    def create_blue_header_box(self, title: str) -> Paragraph:
        """파란색 헤더 박스 생성 (참고 이미지 스타일)"""
        return Paragraph(f'<para backColor="#1f4e79" textColor="white" alignment="center" fontSize="18" fontName="{self.korean_font}" spaceAfter="12" spaceBefore="12">{title}</para>', self.styles['Normal'])
    
    def create_section_with_number(self, number: int, title: str) -> Paragraph:
        """번호가 있는 섹션 제목 생성"""
        return Paragraph(f'<para fontSize="16" fontName="{self.korean_font}" spaceAfter="8" spaceBefore="16">{number} {title}</para>', self.styles['Normal'])
    
    def create_subsection_with_number(self, main_num: int, sub_num: int, title: str) -> Paragraph:
        """서브 섹션 제목 생성 (1-1, 1-2 등)"""
        return Paragraph(f'<para fontSize="14" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="12" leftIndent="10">{main_num}-{sub_num}. {title}</para>', self.styles['Normal'])
    
    def create_list_item(self, number: int, text: str) -> Paragraph:
        """번호가 있는 리스트 아이템 생성"""
        return Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="30">{number}. {text}</para>', self.styles['Normal'])
    
    def create_circled_list_item(self, number: int, text: str) -> Paragraph:
        """원형 번호가 있는 리스트 아이템 생성 (①, ② 등)"""
        circled_numbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
        circled_num = circled_numbers[number - 1] if number <= len(circled_numbers) else f"{number}."
        return Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="30">{circled_num} {text}</para>', self.styles['Normal'])
    
    def export_overview_to_pdf(self, data: Dict[str, Any], output_path: str) -> str:
        """의약품 개요서를 PDF로 내보내기 (최적화된 버전)"""
        try:
            print("📄 PDF 생성 시작...")
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # 배치 처리를 위한 스토리 구성
            story = self._build_pdf_content(data)
            
            print("📄 PDF 빌드 중...")
            doc.build(story)
            
            print(f"✅ PDF 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"PDF 생성 오류: {e}")
            return ""
    
    def _build_pdf_content(self, data: Dict[str, Any]) -> List:
        """PDF 내용을 배치로 구성합니다."""
        story = []
        
        # 제품명 파란색 헤더 박스
        product_name = data.get('제품명', '의약품 제품 개요서')
        story.append(self.create_blue_header_box(product_name))
        story.append(Spacer(1, 20))
        
        # 섹션별 배치 처리
        sections = [
            ('작용기전', self._process_mechanism_section),
            ('주요 적응증 및 제품명', self._process_indication_section),
            ('성분 및 함량', self._process_composition_section),
            ('성상', self._process_appearance_section),
            ('효능 및 효과', self._process_effect_section),
            ('용법 및 용량', self._process_usage_section),
            ('사용상 주의사항', self._process_precaution_section),
            ('상호작용', self._process_interaction_section),
            ('임부 및 수유부 사용', self._process_pregnancy_section),
            ('고령자 사용', self._process_elderly_section),
            ('적용 시 주의사항', self._process_caution_section),
            ('보관 및 취급', self._process_storage_section),
            ('제조 및 판매사 정보', self._process_company_section)
        ]
        
        for section_name, processor in sections:
            if section_name in data and data[section_name]:
                story.extend(processor(data[section_name], section_name))
        
        # 페이지 번호 추가
        story.append(Spacer(1, 30))
        story.append(Paragraph(f'<para alignment="center" fontSize="10" fontName="{self.korean_font}">- 1 -</para>', self.styles['Normal']))
        
        return story
    
    def _process_mechanism_section(self, data: Dict[str, Any], section_name: str) -> List:
        """작용기전 섹션 처리"""
        story = []
        story.append(self.create_section_with_number(1, "작용기전"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for key, value in data.items():
            if value and value != "정보 없음":
                story.append(self.create_subsection_with_number(1, sub_num, key))
                story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{value}</para>', self.styles['Normal']))
                sub_num += 1
        
        return story
    
    def _process_indication_section(self, data: Dict[str, Any], section_name: str) -> List:
        """주요 적응증 및 제품명 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(2, "주요 적응증 및 제품명"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for key, value in data.items():
            if value and value != "정보 없음":
                story.append(self.create_subsection_with_number(2, sub_num, key))
                
                if isinstance(value, list):
                    for i, item in enumerate(value, 1):
                        if item and item != "정보 없음":
                            story.append(self.create_circled_list_item(i, item))
                else:
                    story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{value}</para>', self.styles['Normal']))
                sub_num += 1
        
        return story
    
    def _process_composition_section(self, data: List[Dict], section_name: str) -> List:
        """성분 및 함량 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(3, "성분 및 함량"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        for i, component in enumerate(data, 1):
            if component and isinstance(component, dict):
                component_name = component.get('성분명', '')
                specification = component.get('규격', '')
                standard = component.get('기준', '')
                
                if component_name and component_name != "정보 없음":
                    story.append(self.create_subsection_with_number(3, i, component_name))
                    
                    if specification and specification != "정보 없음":
                        story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="20">규격: {specification}</para>', self.styles['Normal']))
                    
                    if standard and standard != "정보 없음":
                        story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="20">기준: {standard}</para>', self.styles['Normal']))
        
        return story
    
    def _process_appearance_section(self, data: str, section_name: str) -> List:
        """성상 섹션 처리"""
        story = []
        if data and data != "정보 없음":
            story.append(Spacer(1, 20))
            story.append(self.create_section_with_number(4, "성상"))
            story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
            story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{data}</para>', self.styles['Normal']))
        
        return story
    
    def _process_effect_section(self, data: List[str], section_name: str) -> List:
        """효능 및 효과 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(5, "효능 및 효과"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        for i, effect in enumerate(data, 1):
            if effect and effect != "정보 없음":
                story.append(self.create_list_item(i, effect))
        
        return story
    
    def _process_usage_section(self, data: List[Dict], section_name: str) -> List:
        """용법 및 용량 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(6, "용법 및 용량"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        for i, usage in enumerate(data, 1):
            if usage and isinstance(usage, dict):
                indication = usage.get('적응증', '')
                dosage = usage.get('용량', '')
                
                if indication and indication != "정보 없음":
                    story.append(self.create_subsection_with_number(6, i, f"적응증: {indication}"))
                
                if dosage and dosage != "정보 없음":
                    story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="30">용량: {dosage}</para>', self.styles['Normal']))
        
        return story
    
    def _process_precaution_section(self, data: Dict[str, List], section_name: str) -> List:
        """사용상 주의사항 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(7, "사용상 주의사항"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for category, items in data.items():
            if items and isinstance(items, list):
                valid_items = [item for item in items if item and item != "정보 없음"]
                if valid_items:
                    story.append(self.create_subsection_with_number(7, sub_num, category))
                    for item in valid_items:
                        story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="30">• {item}</para>', self.styles['Normal']))
                    sub_num += 1
        
        return story
    
    def _process_interaction_section(self, data: List[str], section_name: str) -> List:
        """상호작용 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(8, "상호작용"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        for i, interaction in enumerate(data, 1):
            if interaction and interaction != "정보 없음":
                story.append(self.create_list_item(i, interaction))
        
        return story
    
    def _process_pregnancy_section(self, data: Dict[str, str], section_name: str) -> List:
        """임부 및 수유부 사용 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(9, "임부 및 수유부 사용"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for key, value in data.items():
            if value and value != "정보 없음":
                story.append(self.create_subsection_with_number(9, sub_num, key))
                story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{value}</para>', self.styles['Normal']))
                sub_num += 1
        
        return story
    
    def _process_elderly_section(self, data: str, section_name: str) -> List:
        """고령자 사용 섹션 처리"""
        story = []
        if data and data != "정보 없음":
            story.append(Spacer(1, 20))
            story.append(self.create_section_with_number(10, "고령자 사용"))
            story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
            story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{data}</para>', self.styles['Normal']))
        
        return story
    
    def _process_caution_section(self, data: List[str], section_name: str) -> List:
        """적용 시 주의사항 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(11, "적용 시 주의사항"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        for i, caution in enumerate(data, 1):
            if caution and caution != "정보 없음":
                story.append(self.create_list_item(i, caution))
        
        return story
    
    def _process_storage_section(self, data: Dict[str, Any], section_name: str) -> List:
        """보관 및 취급 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(12, "보관 및 취급"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for key, value in data.items():
            if value and value != "정보 없음":
                if key == '주의사항' and isinstance(value, list):
                    story.append(self.create_subsection_with_number(12, sub_num, key))
                    for item in value:
                        if item and item != "정보 없음":
                            story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="4" spaceBefore="4" leftIndent="30">• {item}</para>', self.styles['Normal']))
                    sub_num += 1
                elif key != '주의사항':
                    story.append(self.create_subsection_with_number(12, sub_num, key))
                    story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{value}</para>', self.styles['Normal']))
                    sub_num += 1
        
        return story
    
    def _process_company_section(self, data: Dict[str, str], section_name: str) -> List:
        """제조 및 판매사 정보 섹션 처리"""
        story = []
        story.append(Spacer(1, 20))
        story.append(self.create_section_with_number(13, "제조 및 판매사 정보"))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#cccccc')))
        
        sub_num = 1
        for key, value in data.items():
            if value and value != "정보 없음":
                story.append(self.create_subsection_with_number(13, sub_num, key))
                story.append(Paragraph(f'<para fontSize="11" fontName="{self.korean_font}" spaceAfter="6" spaceBefore="6" leftIndent="20" alignment="justify">{value}</para>', self.styles['Normal']))
                sub_num += 1
        
        return story

def export_overview_to_pdf(data: Dict[str, Any], output_path: str) -> str:
    """의약품 개요서를 PDF로 내보내기 (편의 함수)"""
    exporter = MedicalPDFExporter()
    return exporter.export_overview_to_pdf(data, output_path) 