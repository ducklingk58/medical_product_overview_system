from pydantic import BaseModel, Field
from typing import List, Optional


class Appearance(BaseModel):
    description: str = Field(..., description="제형 외형 설명")
    identification_mark: Optional[str] = Field(None, description="각인 정보")

class CompositionPerUnit(BaseModel):
    component_name: str
    role: str
    amount: str
    standard: Optional[str]

class Overages(BaseModel):
    component_name: str
    amount_overage: str
    justification: str

class ContainerClosurePrimary(BaseModel):
    material: str
    type: str

class ContainerClosureSecondary(BaseModel):
    description: str

class ContainerClosureSystem(BaseModel):
    primary: ContainerClosurePrimary
    secondary: Optional[ContainerClosureSecondary]

class ReconstitutionDiluent(BaseModel):
    name: Optional[str]
    compatibility: Optional[str]
    in_use_storage: Optional[str]

class PerformanceCharacteristics(BaseModel):
    dissolution: Optional[str]
    disintegration: Optional[str]
    bioavailability: Optional[str]
    other_properties: Optional[List[str]]

class Preservative(BaseModel):
    name: Optional[str]
    efficacy: Optional[str]

class MicrobiologicalAttributes(BaseModel):
    preservative: Optional[Preservative]
    sterility_info: Optional[str]

class CriticalMaterial(BaseModel):
    name: str
    impact: str

class ClinicalBatchInfo(BaseModel):
    difference_from_commercial: Optional[str]

class DevelopmentHistory(BaseModel):
    justification_for_formulation: Optional[str]
    critical_materials: Optional[List[CriticalMaterial]]
    clinical_batch_info: Optional[ClinicalBatchInfo]

class ProductOverview(BaseModel):
    product_name: str
    dosage_form: str
    strength: str
    appearance: Appearance
    composition_per_unit: List[CompositionPerUnit]
    overages: Optional[List[Overages]]
    container_closure_system: ContainerClosureSystem
    reconstitution_diluent: Optional[ReconstitutionDiluent]
    performance_characteristics: Optional[PerformanceCharacteristics]
    microbiological_attributes: Optional[MicrobiologicalAttributes]
    development_history: Optional[DevelopmentHistory]


