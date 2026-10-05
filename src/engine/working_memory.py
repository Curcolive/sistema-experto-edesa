"""
Módulo de Memoria de Trabajo (Working Memory) con Trazabilidad Completa
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Gestiona el estado activo de hechos (Working Memory Element - WME),
control de versiones, historial de aserciones y procedencia causal.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from ..domain.fact_model import Fact, FactCategory


class WorkingMemory:
    """
    Memoria de Trabajo que almacena el conjunto dinámico de hechos validados.
    Implementa aserción, retractación, consultas y registro de procedencia (provenance).
    """

    def __init__(self, initial_facts: Optional[List[Fact]] = None):
        self._facts: Dict[str, Fact] = {}
        self._history: List[Dict[str, Any]] = []
        self._step_counter: int = 0

        if initial_facts:
            for f in initial_facts:
                self.assert_fact(f, author="INITIAL_PERCEPTION")

    def assert_fact(
        self,
        fact_or_name: Union[Fact, str],
        value: Any = None,
        author: str = "INFERENCE_ENGINE",
        category: FactCategory = FactCategory.GENERAL,
        description: str = "",
        unit: Optional[str] = None
    ) -> Fact:
        """
        Inserta o actualiza un hecho en la memoria de trabajo con registro de auditoría.
        Acepta una instancia de Fact o tuplas (nombre, valor).
        """
        self._step_counter += 1
        now = datetime.now(timezone.utc).isoformat()

        if isinstance(fact_or_name, Fact):
            fact_obj = fact_or_name
            # Si el hecho tiene rule_id explícito (como AuditAnomalyFact), usarlo como autor preferente
            fact_rule = getattr(fact_obj, "rule_id", None) or (fact_obj.metadata.get("rule_id") if hasattr(fact_obj, "metadata") else None)
            if fact_rule and fact_rule != "UNKNOWN_RULE":
                if author == "INFERENCE_ENGINE":
                    author = fact_rule
                fact_obj.source = author
            elif fact_obj.source and fact_obj.source not in ("INVOICE_PERCEPTION", "INITIAL_PERCEPTION") and author == "INFERENCE_ENGINE":
                author = fact_obj.source
            elif fact_obj.source == "INVOICE_PERCEPTION" and author != "INITIAL_PERCEPTION":
                fact_obj.source = author
        else:
            fact_obj = Fact(
                name=fact_or_name,
                value=value,
                source=author,
                category=category,
                description=description,
                unit=unit,
                timestamp=now
            )

        fact_name = fact_obj.name
        is_update = fact_name in self._facts
        old_val = self._facts[fact_name].value if is_update else None

        self._facts[fact_name] = fact_obj

        # Registrar en el log de auditoría
        self._history.append({
            "step": self._step_counter,
            "action": "UPDATE" if is_update else "ASSERT",
            "fact_name": fact_name,
            "value": fact_obj.value,
            "previous_value": old_val,
            "author": author,
            "timestamp": now,
            "category": fact_obj.category.value if hasattr(fact_obj.category, "value") else str(fact_obj.category)
        })

        return fact_obj

    def retract_fact(self, fact_name: str, author: str = "SYSTEM") -> Optional[Fact]:
        """Retira un hecho de la memoria de trabajo con registro en el historial."""
        if fact_name not in self._facts:
            return None

        self._step_counter += 1
        removed_fact = self._facts.pop(fact_name)
        now = datetime.utcnow().isoformat()

        self._history.append({
            "step": self._step_counter,
            "action": "RETRACT",
            "fact_name": fact_name,
            "value": removed_fact.value,
            "previous_value": removed_fact.value,
            "author": author,
            "timestamp": now,
            "category": removed_fact.category.value if hasattr(removed_fact.category, "value") else str(removed_fact.category)
        })

        return removed_fact

    def get(self, fact_name: str, default: Any = None) -> Any:
        """Obtiene el valor de un hecho almacenado. Si no existe, retorna default."""
        if fact_name in self._facts:
            return self._facts[fact_name].value
        return default

    def get_fact(self, fact_name: str) -> Optional[Fact]:
        """Obtiene el objeto Fact completo."""
        return self._facts.get(fact_name)

    def has(self, fact_name: str) -> bool:
        """Verifica si un hecho existe actualmente en la memoria de trabajo."""
        return fact_name in self._facts

    def get_all(self) -> Dict[str, Fact]:
        """Retorna una copia superficial del diccionario de hechos activos."""
        return dict(self._facts)

    def get_by_category(self, category: Union[FactCategory, str]) -> List[Fact]:
        """Filtra los hechos activos pertenecientes a una categoría específica."""
        cat_val = category.value if isinstance(category, FactCategory) else str(category)
        return [
            f for f in self._facts.values()
            if (f.category.value if hasattr(f.category, "value") else str(f.category)) == cat_val
        ]

    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna la bitácora completa de cambios para explicabilidad (XAI)."""
        return list(self._history)

    def snapshot(self) -> Dict[str, Any]:
        """Retorna una captura inmutable del estado actual de hechos."""
        return {name: deepcopy(f) for name, f in self._facts.items()}

    def clear(self) -> None:
        """Limpia los hechos almacenados y reinicia el estado."""
        self._facts.clear()
        self._history.clear()
        self._step_counter = 0

    def __len__(self) -> int:
        return len(self._facts)

    def __repr__(self) -> str:
        return f"WorkingMemory(total_facts={len(self._facts)}, steps={self._step_counter})"
