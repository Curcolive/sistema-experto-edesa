"""
Pruebas Unitarias de la Memoria de Trabajo (Working Memory)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domain.fact_model import Fact, ElectricFact, WaterFact, FactCategory
from src.engine.working_memory import WorkingMemory


class TestWorkingMemory(unittest.TestCase):
    """Pruebas de aserción, actualización, retractación y log de procedencia."""

    def setUp(self):
        self.wm = WorkingMemory()

    def test_assert_and_get_fact(self):
        f = self.wm.assert_fact("potencia_kw", 2.0, author="TEST_AUTHOR")
        self.assertTrue(self.wm.has("potencia_kw"))
        self.assertEqual(self.wm.get("potencia_kw"), 2.0)
        self.assertEqual(f.source, "TEST_AUTHOR")

    def test_assert_fact_instance(self):
        ef = ElectricFact(name="consumo_kwh", value=428.0)
        self.wm.assert_fact(ef)
        self.assertEqual(self.wm.get("consumo_kwh"), 428.0)
        retrieved = self.wm.get_fact("consumo_kwh")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.category, FactCategory.ELECTRIC)

    def test_update_fact_records_in_history(self):
        self.wm.assert_fact("estado", "INICIAL")
        self.assertEqual(self.wm.get("estado"), "INICIAL")

        self.wm.assert_fact("estado", "ACTUALIZADO")
        self.assertEqual(self.wm.get("estado"), "ACTUALIZADO")

        history = self.wm.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["action"], "ASSERT")
        self.assertEqual(history[1]["action"], "UPDATE")
        self.assertEqual(history[1]["previous_value"], "INICIAL")
        self.assertEqual(history[1]["value"], "ACTUALIZADO")

    def test_retract_fact(self):
        self.wm.assert_fact("temporal", True)
        self.assertTrue(self.wm.has("temporal"))

        removed = self.wm.retract_fact("temporal")
        self.assertIsNotNone(removed)
        self.assertFalse(self.wm.has("temporal"))

        history = self.wm.get_history()
        self.assertEqual(history[-1]["action"], "RETRACT")

    def test_get_by_category(self):
        self.wm.assert_fact(ElectricFact(name="luz_1", value=10))
        self.wm.assert_fact(ElectricFact(name="luz_2", value=20))
        self.wm.assert_fact(WaterFact(name="agua_1", value=30))

        electric_facts = self.wm.get_by_category(FactCategory.ELECTRIC)
        self.assertEqual(len(electric_facts), 2)

        water_facts = self.wm.get_by_category(FactCategory.WATER)
        self.assertEqual(len(water_facts), 1)

    def test_snapshot(self):
        self.wm.assert_fact("a", 1)
        self.wm.assert_fact("b", 2)
        snap = self.wm.snapshot()
        self.assertIn("a", snap)
        self.assertIn("b", snap)

        # Modificar wm no debe alterar el snapshot
        self.wm.assert_fact("a", 999)
        self.assertEqual(snap["a"].value, 1)


if __name__ == "__main__":
    unittest.main()
