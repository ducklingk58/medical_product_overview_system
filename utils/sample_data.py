from typing import Dict, Any

def create_sample_semaglutide_data() -> Dict[str, Any]:
    """세마글루타이드 개요서 샘플 데이터를 생성합니다."""
    return {
        "3.2.P.1": {
            "product_name": "세마글루타이드 (Semaglutide)",
            "dosage_form": "주사제",
            "strength": "1mg",
            "appearance": {
                "description": "무색 투명한 액체",
                "identification_mark": "없음"
            },
            "composition_per_unit": [
                {
                    "component_name": "세마글루타이드",
                    "role": "주성분",
                    "amount": "1mg",
                    "standard": "USP"
                },
                {
                    "component_name": "메타크레졸",
                    "role": "보존제",
                    "amount": "1.72mg",
                    "standard": "USP"
                },
                {
                    "component_name": "프로필렌글라이콜",
                    "role": "용매",
                    "amount": "1.42mg",
                    "standard": "USP"
                },
                {
                    "component_name": "페놀",
                    "role": "보존제",
                    "amount": "5.5mg",
                    "standard": "USP"
                }
            ],
            "container_closure_system": {
                "primary": {
                    "material": "유리",
                    "type": "프리필드 시린지"
                },
                "secondary": {
                    "description": "알루미늄 호일 파우치"
                }
            }
        },
        "3.2.P.2": {
            "development_history": {
                "justification_for_formulation": "GLP-1 수용체 작용제로서 인슐린 분비 촉진 및 글루카곤 분비 억제를 통한 혈당 조절 효과",
                "critical_materials": [
                    {
                        "name": "세마글루타이드",
                        "impact": "주성분으로 혈당 조절 효과의 핵심"
                    },
                    {
                        "name": "메타크레졸",
                        "impact": "제제의 안정성 및 보존 효과"
                    }
                ],
                "clinical_batch_info": {
                    "difference_from_commercial": "임상시험용과 상업용 제제는 동일한 제조 공정 사용"
                }
            },
            "performance_characteristics": {
                "dissolution": "주사제이므로 해당 없음",
                "disintegration": "주사제이므로 해당 없음",
                "bioavailability": "절대 생체이용률 약 89%",
                "other_properties": [
                    "반감기: 약 7일",
                    "주 1회 투여",
                    "위장관 운동 지연 효과"
                ]
            },
            "microbiological_attributes": {
                "preservative": {
                    "name": "메타크레졸, 페놀",
                    "efficacy": "미생물 오염 방지"
                },
                "sterility_info": "무균 제제로 제조"
            }
        }
    }

def create_sample_mechanism_data() -> Dict[str, Any]:
    """작용기전 정보를 포함한 샘플 데이터를 생성합니다."""
    return {
        "3.2.P.1": {
            "product_name": "세마글루타이드 (Semaglutide)",
            "dosage_form": "주사제 및 경구정",
            "strength": "1mg (주사제), 3mg/7mg/14mg (경구정)",
            "appearance": {
                "description": "주사제: 무색 투명한 액체, 경구정: 흰색 정제",
                "identification_mark": "경구정에 각인 있음"
            },
            "composition_per_unit": [
                {
                    "component_name": "세마글루타이드",
                    "role": "주성분",
                    "amount": "1mg (주사제), 3-14mg (경구정)",
                    "standard": "USP"
                }
            ],
            "container_closure_system": {
                "primary": {
                    "material": "유리 (주사제), 알루미늄 블리스터 (경구정)",
                    "type": "프리필드 시린지 (주사제), 정제 (경구정)"
                }
            }
        },
        "3.2.P.2": {
            "development_history": {
                "justification_for_formulation": "GLP-1 수용체 작용제로 인슐린 분비 촉진, 글루카곤 분비 억제, 위 배출 지연, 식욕 억제 효과",
                "critical_materials": [
                    {
                        "name": "세마글루타이드",
                        "impact": "GLP-1 수용체 작용을 통한 혈당 조절"
                    }
                ]
            },
            "performance_characteristics": {
                "bioavailability": "주사제: 89%, 경구정: 0.4-1%",
                "other_properties": [
                    "반감기: 약 7일",
                    "주 1회 투여 (주사제), 1일 1회 투여 (경구정)",
                    "위 배출 속도 지연",
                    "식욕 억제 및 포만감 증가"
                ]
            }
        }
    } 