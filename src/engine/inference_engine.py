"""
Módulo de Motor de Inferencia Bimodal (Forward & Backward Chaining)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Motor de inferencia completamente desacoplado de la Base de Conocimiento.
Soporta:
1. Encadenamiento hacia Adelante (Forward Chaining - data-driven) con resolución de conflictos y refracción.
2. Encadenamiento hacia Atrás (Backward Chaining - goal-driven) con árbol de prueba deductivo.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from ..knowledge_base.rules_enresp import Rule
from .working_memory import WorkingMemory


@dataclass
class RuleFiringRecord:
    """Registro de ejecución de una regla durante el ciclo de inferencia."""
    cycle: int
    rule_id: str
    rule_name: str
    priority: int
    legal_basis: str
    new_facts_asserted: List[str] = field(default_factory=list)


@dataclass
class InferenceResult:
    """Resultado consolidado de una sesión de inferencia."""
    mode: str  # "FORWARD" o "BACKWARD"
    cycles_executed: int
    rules_fired_count: int
    rules_fired_sequence: List[RuleFiringRecord]
    final_facts_count: int
    is_quiescent: bool
    goal_proven: Optional[bool] = None
    proof_tree: Optional[Dict[str, Any]] = None


class InferenceEngine:
    """
    Motor de Inferencia simbólico modular y desacoplado.
    No contiene reglas hardcodeadas; recibe reglas y memoria de trabajo como argumentos.
    """

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules or []

    def set_rules(self, rules: List[Rule]) -> None:
        """Inyecta el conjunto de reglas de la base de conocimiento."""
        self.rules = list(rules)

    def forward_chain(
        self,
        working_memory: WorkingMemory,
        max_cycles: int = 50
    ) -> InferenceResult:
        """
        Ejecuta el algoritmo de Encadenamiento hacia Adelante (Data-Driven):
        1. Ciclo Match: Identifica reglas cuyas condiciones son verdaderas.
        2. Resolución de Conflictos: Ordena por prioridad y aplica Refracción (cada regla dispara una sola vez).
        3. Ciclo Act: Ejecuta la acción de la regla sobre la memoria de trabajo.
        4. Itera hasta alcanzar la quiescencia (ninguna regla nueva aplicable) o agotar max_cycles.
        """
        fired_rules: Set[str] = set()
        trace: List[RuleFiringRecord] = []
        cycle = 0

        while cycle < max_cycles:
            cycle += 1
            # 1. MATCH: Buscar reglas aplicables no disparadas previamente (Refracción)
            candidate_rules: List[Rule] = []
            for rule in self.rules:
                if rule.id in fired_rules:
                    continue
                if rule.evaluate(working_memory):
                    candidate_rules.append(rule)

            # Si no hay reglas candidatas, se alcanzó el estado de quiescencia
            if not candidate_rules:
                break

            # 2. RESOLUCIÓN DE CONFLICTOS: Mayor prioridad primero
            candidate_rules.sort(key=lambda r: r.priority, reverse=True)
            chosen_rule = candidate_rules[0]

            # 3. ACT: Registrar estado antes y después para detectar nuevos hechos
            facts_before = set(working_memory.get_all().keys())
            
            chosen_rule.execute(working_memory)
            fired_rules.add(chosen_rule.id)

            facts_after = set(working_memory.get_all().keys())
            newly_asserted = sorted(list(facts_after - facts_before))

            # Asegurar procedencia de la regla para los hechos derivados
            for f_name in newly_asserted:
                f_obj = working_memory.get_fact(f_name)
                if f_obj and (f_obj.source in ("INFERENCE_ENGINE", "INVOICE_PERCEPTION") or getattr(f_obj, "rule_id", None) == "UNKNOWN_RULE"):
                    f_obj.source = chosen_rule.id

            # Registrar en la bitácora de trazabilidad
            trace.append(RuleFiringRecord(
                cycle=cycle,
                rule_id=chosen_rule.id,
                rule_name=chosen_rule.name,
                priority=chosen_rule.priority,
                legal_basis=chosen_rule.legal_basis,
                new_facts_asserted=newly_asserted
            ))

        return InferenceResult(
            mode="FORWARD",
            cycles_executed=cycle,
            rules_fired_count=len(trace),
            rules_fired_sequence=trace,
            final_facts_count=len(working_memory),
            is_quiescent=True
        )

    def backward_chain(
        self,
        working_memory: WorkingMemory,
        goal_fact_name: str,
        expected_value: Any = None
    ) -> InferenceResult:
        """
        Ejecuta el algoritmo de Encadenamiento hacia Atrás (Goal-Driven):
        Dada una hipótesis o meta, busca recursivamente las reglas capaces
        de concluirla y verifica si las premisas se satisfacen con los hechos conocidos.
        """
        proof_tree: Dict[str, Any] = {}
        visited_goals: Set[str] = set()
        trace: List[RuleFiringRecord] = []

        success, tree = self._prove_goal(
            goal=goal_fact_name,
            expected_val=expected_value,
            wm=working_memory,
            visited_goals=visited_goals,
            trace=trace,
            depth=0
        )

        return InferenceResult(
            mode="BACKWARD",
            cycles_executed=len(trace),
            rules_fired_count=len(trace),
            rules_fired_sequence=trace,
            final_facts_count=len(working_memory),
            is_quiescent=True,
            goal_proven=success,
            proof_tree=tree
        )

    def _prove_goal(
        self,
        goal: str,
        expected_val: Any,
        wm: WorkingMemory,
        visited_goals: Set[str],
        trace: List[RuleFiringRecord],
        depth: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Procedimiento recursivo de prueba de metas para Backward Chaining."""
        # 1. Caso base directo: La meta ya existe en la memoria de trabajo
        if wm.has(goal):
            curr_val = wm.get(goal)
            if expected_val is None or curr_val == expected_val:
                return True, {
                    "goal": goal,
                    "status": "PROVEN_BY_KNOWN_FACT",
                    "value": curr_val,
                    "depth": depth
                }

        # Detección de ciclos en la cadena de metas
        if goal in visited_goals:
            return False, {
                "goal": goal,
                "status": "CYCLE_DETECTED",
                "depth": depth
            }

        visited_goals.add(goal)

        # 2. Buscar reglas que tengan a esta meta como target_hypothesis
        candidate_rules = [
            r for r in self.rules
            if (r.target_hypothesis == goal)
        ]

        if not candidate_rules:
            # Intentar también con forward matching oportunista si la condición se cumple
            for r in self.rules:
                if r.evaluate(wm):
                    # Probar si al disparar produce el hecho buscado
                    candidate_rules.append(r)

        # Ordenar por prioridad
        candidate_rules.sort(key=lambda r: r.priority, reverse=True)

        sub_trees = []
        for rule in candidate_rules:
            # Si la regla requiere prerrequisitos o sub-metas previas, probarlos recursivamente
            prereqs = getattr(rule, "prerequisites", [])
            prereqs_proven = True
            rule_sub_trees = []
            for prereq in prereqs:
                if not wm.has(prereq):
                    sub_proven, sub_tree = self._prove_goal(
                        goal=prereq,
                        expected_val=None,
                        wm=wm,
                        visited_goals=visited_goals,
                        trace=trace,
                        depth=depth + 1
                    )
                    rule_sub_trees.append(sub_tree)
                    if not sub_proven:
                        prereqs_proven = False
                        break
                else:
                    rule_sub_trees.append({
                        "goal": prereq,
                        "status": "PROVEN_BY_KNOWN_FACT",
                        "value": wm.get(prereq),
                        "depth": depth + 1
                    })

            if not prereqs_proven:
                continue

            sub_trees.extend(rule_sub_trees)

            # Evaluar condición de la regla
            if rule.evaluate(wm):
                # Disparar la regla para derivar la meta
                facts_before = set(wm.get_all().keys())
                rule.execute(wm)
                facts_after = set(wm.get_all().keys())
                newly_asserted = sorted(list(facts_after - facts_before))

                for f_name in newly_asserted:
                    f_obj = wm.get_fact(f_name)
                    if f_obj and (f_obj.source in ("INFERENCE_ENGINE", "INVOICE_PERCEPTION") or getattr(f_obj, "rule_id", None) == "UNKNOWN_RULE"):
                        f_obj.source = rule.id

                trace.append(RuleFiringRecord(
                    cycle=len(trace) + 1,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    priority=rule.priority,
                    legal_basis=rule.legal_basis,
                    new_facts_asserted=newly_asserted
                ))

                if wm.has(goal):
                    curr_val = wm.get(goal)
                    if expected_val is None or curr_val == expected_val:
                        visited_goals.remove(goal)
                        return True, {
                            "goal": goal,
                            "status": "PROVEN_BY_RULE_FIRING",
                            "rule_id": rule.id,
                            "value": curr_val,
                            "depth": depth,
                            "sub_trees": sub_trees
                        }

        visited_goals.remove(goal)
        return False, {
            "goal": goal,
            "status": "UNPROVABLE",
            "depth": depth,
            "attempted_rules": [r.id for r in candidate_rules]
        }
