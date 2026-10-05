"""
Módulo de Modelado Formal de Hechos (Fact Models)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Proporciona la ontología formal de hechos para la Base de Conocimiento
y la Memoria de Trabajo del Sistema Experto de Auditoría Tarifaria.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime, timezone


class FactCategory(str, Enum):
    """Categorías ontológicas de hechos dentro del sistema experto."""
    GENERAL = "GENERAL"
    ELECTRIC = "ELECTRIC"
    WATER = "WATER"
    MUNICIPAL = "MUNICIPAL"
    REGULATORY = "REGULATORY"
    AUDIT_DERIVED = "AUDIT_DERIVED"


class AnomalySeverity(str, Enum):
    """Nivel de severidad de anomalías detectadas por el motor de inferencia."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    RECLAIMABLE = "RECLAIMABLE"


@dataclass
class Fact:
    """
    Representación atómica formal de un hecho en la Memoria de Trabajo.
    Corresponde a la tupla <Atributo, Valor, Confianza, Procedencia>.
    """
    name: str
    value: Any
    confidence: float = 1.0
    source: str = "INVOICE_PERCEPTION"
    category: FactCategory = FactCategory.GENERAL
    unit: Optional[str] = None
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el hecho a un diccionario estándar."""
        d = asdict(self)
        d["category"] = self.category.value
        return d

    def matches(self, query_name: str, expected_value: Any = None) -> bool:
        """Comprueba si el hecho coincide en nombre y valor esperado."""
        if self.name != query_name:
            return False
        if expected_value is not None:
            return self.value == expected_value
        return True

    def __repr__(self) -> str:
        unit_str = f" {self.unit}" if self.unit else ""
        return f"Fact({self.name} = {self.value}{unit_str} [{self.category.value}])"


@dataclass
class ElectricFact(Fact):
    """Hecho correspondiente al subsistema eléctrico (EDESA S.A.)."""
    category: FactCategory = FactCategory.ELECTRIC

    def __post_init__(self):
        if self.category != FactCategory.ELECTRIC:
            self.category = FactCategory.ELECTRIC


@dataclass
class WaterFact(Fact):
    """Hecho correspondiente al subsistema de agua y saneamiento (Aguas del Norte)."""
    category: FactCategory = FactCategory.WATER

    def __post_init__(self):
        if self.category != FactCategory.WATER:
            self.category = FactCategory.WATER


@dataclass
class MunicipalFact(Fact):
    """Hecho correspondiente a tasas municipales e impuestos descentralizados."""
    category: FactCategory = FactCategory.MUNICIPAL

    def __post_init__(self):
        if self.category != FactCategory.MUNICIPAL:
            self.category = FactCategory.MUNICIPAL


@dataclass
class RegulatoryFact(Fact):
    """Hecho normativo o regulatorio dictado por el ENRESP u ordenanzas."""
    category: FactCategory = FactCategory.REGULATORY

    def __post_init__(self):
        if self.category != FactCategory.REGULATORY:
            self.category = FactCategory.REGULATORY


@dataclass
class AuditAnomalyFact(Fact):
    """
    Hecho derivado por inferencia deductiva que señala una anomalía,
    sobrefacturación o derecho a reclamo administrativo formal.
    """
    category: FactCategory = FactCategory.AUDIT_DERIVED
    rule_id: str = "UNKNOWN_RULE"
    severity: AnomalySeverity = AnomalySeverity.WARNING
    financial_impact_ars: float = 0.0
    legal_basis: str = ""
    remedy_action: str = ""

    def __post_init__(self):
        self.category = FactCategory.AUDIT_DERIVED
        if self.rule_id and self.rule_id != "UNKNOWN_RULE":
            self.source = self.rule_id
        if "rule_id" not in self.metadata and self.rule_id:
            self.metadata["rule_id"] = self.rule_id
        if "severity" not in self.metadata:
            self.metadata["severity"] = self.severity.value if isinstance(self.severity, AnomalySeverity) else str(self.severity)
        if "financial_impact_ars" not in self.metadata:
            self.metadata["financial_impact_ars"] = self.financial_impact_ars
        if "legal_basis" not in self.metadata:
            self.metadata["legal_basis"] = self.legal_basis
        if "remedy_action" not in self.metadata:
            self.metadata["remedy_action"] = self.remedy_action
