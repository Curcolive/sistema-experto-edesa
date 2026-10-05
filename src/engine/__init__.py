"""
Paquete del Motor de Inferencia (Inference Engine) y Memoria de Trabajo
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (100001)
"""

from .working_memory import WorkingMemory
from .inference_engine import InferenceEngine, InferenceResult, RuleFiringRecord
from .explanation_module import ExplanationModule

__all__ = [
    "WorkingMemory",
    "InferenceEngine",
    "InferenceResult",
    "RuleFiringRecord",
    "ExplanationModule"
]
