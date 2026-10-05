"""
Pruebas Unitarias del Motor de Inferencia (Forward & Backward Chaining)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.knowledge_base.rules_enresp import Rule


class TestInferenceEngine(unittest.TestCase):
    """Pruebas unitarias de algoritmos de encadenamiento y resolución de conflictos."""

    def test_forward_chaining_basic_derivation(self):
        wm = WorkingMemory()
        wm.assert_fact("temperatura", 38.5)

        rule1 = Rule(
            id="R_FIEBRE",
            name="Regla Fiebre",
            description="Detecta fiebre alta",
            priority=10,
            condition=lambda m: m.get("temperatura", 0) > 37.5,
            action=lambda m: m.assert_fact("tiene_fiebre", True, author="R_FIEBRE")
        )

        engine = InferenceEngine([rule1])
        result = engine.forward_chain(wm)

        self.assertEqual(result.rules_fired_count, 1)
        self.assertTrue(wm.has("tiene_fiebre"))
        self.assertTrue(wm.get("tiene_fiebre"))
        self.assertEqual(result.rules_fired_sequence[0].rule_id, "R_FIEBRE")

    def test_forward_chaining_multi_cycle_cascade(self):
        # A -> B, luego B -> C
        wm = WorkingMemory()
        wm.assert_fact("A", True)

        r1 = Rule(
            id="R1_A_TO_B",
            name="A implica B",
            description="",
            priority=50,
            condition=lambda m: m.has("A"),
            action=lambda m: m.assert_fact("B", True, author="R1_A_TO_B")
        )

        r2 = Rule(
            id="R2_B_TO_C",
            name="B implica C",
            description="",
            priority=40,
            condition=lambda m: m.has("B"),
            action=lambda m: m.assert_fact("C", True, author="R2_B_TO_C")
        )

        engine = InferenceEngine([r1, r2])
        result = engine.forward_chain(wm)

        self.assertEqual(result.rules_fired_count, 2)
        self.assertTrue(wm.has("C"))
        fired_ids = [rec.rule_id for rec in result.rules_fired_sequence]
        self.assertEqual(fired_ids, ["R1_A_TO_B", "R2_B_TO_C"])

    def test_refraction_prevents_infinite_loops(self):
        wm = WorkingMemory()
        wm.assert_fact("x", 1)

        # Regla cuya condición sigue siendo verdadera
        loop_rule = Rule(
            id="R_LOOP",
            name="Regla Potencial Loop",
            description="",
            priority=10,
            condition=lambda m: m.get("x") == 1,
            action=lambda m: m.assert_fact("x_procesado", True, author="R_LOOP")
        )

        engine = InferenceEngine([loop_rule])
        result = engine.forward_chain(wm, max_cycles=10)

        # Debe disparar exactamente una vez debido a la refracción
        self.assertEqual(result.rules_fired_count, 1)
        self.assertTrue(result.is_quiescent)

    def test_conflict_resolution_by_priority(self):
        wm = WorkingMemory()
        wm.assert_fact("flag", True)

        order_fired = []

        r_low = Rule(
            id="R_LOW",
            name="Baja Prioridad",
            description="",
            priority=10,
            condition=lambda m: m.has("flag"),
            action=lambda m: order_fired.append("LOW")
        )

        r_high = Rule(
            id="R_HIGH",
            name="Alta Prioridad",
            description="",
            priority=100,
            condition=lambda m: m.has("flag"),
            action=lambda m: order_fired.append("HIGH")
        )

        engine = InferenceEngine([r_low, r_high])
        engine.forward_chain(wm)

        self.assertEqual(order_fired, ["HIGH", "LOW"])

    def test_backward_chaining_goal_proven(self):
        wm = WorkingMemory()
        wm.assert_fact("luz_residencial", True)
        wm.assert_fact("agua_comercial", True)

        rule = Rule(
            id="R_INCONSISTENCIA",
            name="Inconsistencia de Tarifa",
            description="",
            priority=50,
            target_hypothesis="anomalia_catastral",
            condition=lambda m: m.get("luz_residencial") and m.get("agua_comercial"),
            action=lambda m: m.assert_fact("anomalia_catastral", True, author="R_INCONSISTENCIA")
        )

        engine = InferenceEngine([rule])
        result = engine.backward_chain(wm, goal_fact_name="anomalia_catastral")

        self.assertTrue(result.goal_proven)
        self.assertTrue(wm.has("anomalia_catastral"))
        self.assertEqual(result.proof_tree["status"], "PROVEN_BY_RULE_FIRING")

    def test_backward_chaining_unprovable_goal(self):
        wm = WorkingMemory()
        wm.assert_fact("luz_residencial", True)
        # Falta agua_comercial

        rule = Rule(
            id="R_INCONSISTENCIA",
            name="Inconsistencia",
            description="",
            target_hypothesis="anomalia_catastral",
            condition=lambda m: m.get("luz_residencial") and m.get("agua_comercial"),
            action=lambda m: m.assert_fact("anomalia_catastral", True)
        )

        engine = InferenceEngine([rule])
        result = engine.backward_chain(wm, goal_fact_name="anomalia_catastral")

        self.assertFalse(result.goal_proven)
        self.assertFalse(wm.has("anomalia_catastral"))
        self.assertEqual(result.proof_tree["status"], "UNPROVABLE")

    def test_backward_chaining_multi_level_recursion(self):
        """Prueba de Backward Chaining con sub-metas recursivas en cascada: A -> B -> C."""
        wm = WorkingMemory()
        wm.assert_fact("hecho_base_A", True)

        r1 = Rule(
            id="R_A_TO_B",
            name="Regla A genera B",
            description="",
            target_hypothesis="submeta_B",
            condition=lambda m: m.get("hecho_base_A") is True,
            action=lambda m: m.assert_fact("submeta_B", True, author="R_A_TO_B")
        )

        r2 = Rule(
            id="R_B_TO_C",
            name="Regla B genera C",
            description="",
            target_hypothesis="meta_final_C",
            prerequisites=["submeta_B"],
            condition=lambda m: m.get("submeta_B") is True,
            action=lambda m: m.assert_fact("meta_final_C", "EXITO", author="R_B_TO_C")
        )

        engine = InferenceEngine([r1, r2])
        res = engine.backward_chain(wm, goal_fact_name="meta_final_C")

        self.assertTrue(res.goal_proven)
        self.assertEqual(wm.get("meta_final_C"), "EXITO")
        self.assertTrue(wm.has("submeta_B"))
        self.assertEqual(res.proof_tree["status"], "PROVEN_BY_RULE_FIRING")

    def test_backward_chaining_cycle_prevention(self):
        """Verifica que el detector de ciclos impida loops infinitos en Backward Chaining."""
        wm = WorkingMemory()

        r_cycle1 = Rule(
            id="R_CYCLE_1",
            name="Regla Ciclo 1",
            description="",
            target_hypothesis="meta_X",
            prerequisites=["meta_Y"],
            condition=lambda m: m.has("meta_Y"),
            action=lambda m: m.assert_fact("meta_X", True)
        )
        r_cycle2 = Rule(
            id="R_CYCLE_2",
            name="Regla Ciclo 2",
            description="",
            target_hypothesis="meta_Y",
            prerequisites=["meta_X"],
            condition=lambda m: m.has("meta_X"),
            action=lambda m: m.assert_fact("meta_Y", True)
        )

        engine = InferenceEngine([r_cycle1, r_cycle2])
        res = engine.backward_chain(wm, goal_fact_name="meta_X")

        self.assertFalse(res.goal_proven)
        self.assertFalse(wm.has("meta_X"))


if __name__ == "__main__":
    unittest.main()
