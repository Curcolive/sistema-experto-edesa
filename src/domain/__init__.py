"""
Paquete de Dominio - Modelos de Hechos y Sanitización PII
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (100001)
"""

from .fact_model import (
    FactCategory,
    Fact,
    ElectricFact,
    WaterFact,
    MunicipalFact,
    RegulatoryFact,
    AuditAnomalyFact
)
from .anonymizer import InvoiceAnonymizer

__all__ = [
    "FactCategory",
    "Fact",
    "ElectricFact",
    "WaterFact",
    "MunicipalFact",
    "RegulatoryFact",
    "AuditAnomalyFact",
    "InvoiceAnonymizer"
]
