"""
Pruebas Unitarias del Módulo XAI de Explicabilidad (HOW, WHY y Dictamen)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.engine.explanation_module import ExplanationModule
from src.knowledge_base.default_facts import load_default_facts_from_json
from src.knowledge_base.rules_enresp import get_all_enresp_rules
from src.knowledge_base.concept_glossary import ConceptGlossary


class TestExplanationModule(unittest.TestCase):
    """Verificación de generación de explicaciones HOW, WHY y dictámenes."""

    def setUp(self):
        self.facts = load_default_facts_from_json()
        self.wm = WorkingMemory(self.facts)
        self.rules = get_all_enresp_rules()
        self.engine = InferenceEngine(self.rules)
        self.result = self.engine.forward_chain(self.wm)
        self.xai = ExplanationModule(self.rules)

    def test_how_perceived_fact(self):
        expl = self.xai.how("factura_monto_total", self.wm, self.result)
        self.assertTrue(expl["found"])
        self.assertEqual(expl["derivation_type"], "PERCEPTION")
        self.assertEqual(expl["value"], 377559.51)

    def test_how_deduced_fact(self):
        expl = self.xai.how("alerta_inconsistencia_tarifaria", self.wm, self.result)
        self.assertTrue(expl["found"])
        self.assertEqual(expl["derivation_type"], "DEDUCTION")
        self.assertEqual(expl["rule_id"], "R02_INCONSISTENCIA_CATEGORIA_CATASTRAL")
        self.assertIn("Marco Regulatorio", expl["legal_basis"])

    def test_why_rule(self):
        why_r01 = self.xai.why("R01_CASTIGO_FISCAL_IVA_NO_CATEGORIZADO")
        self.assertTrue(why_r01["found"])
        self.assertEqual(why_r01["priority"], 100)
        self.assertIn("2126", why_r01["legal_basis"])

    def test_concept_glossary_lookup(self):
        concept_card = self.xai.explain_concept("CARGO_FIJO_AGUA")
        self.assertIn("NO RESIDENCIAL 1", concept_card)
        self.assertIn("69,404.04", concept_card)
        self.assertIn("Aguas del Norte", concept_card)

    def test_split_totals_calculation(self):
        totals = ConceptGlossary.calculate_split_totals()
        self.assertEqual(totals["total_factura"], 377559.51)
        self.assertGreater(totals["total_desdoblable"], 200000.0)
        self.assertLess(totals["total_electrico_esencial"], 160000.0)

    def test_generate_audit_report_contents(self):
        report = self.xai.generate_audit_report(self.wm, self.result)
        self.assertIn("Estudiante UGD", report)
        self.assertIn("100001", report)
        self.assertIn("Agustín Encina", report)
        self.assertIn("Dante Sicardi", report)
        self.assertIn("64,210.15", report)  # Ahorro mensual
        self.assertIn("770,521.80", report)  # Ahorro anualizado
        self.assertIn("1590/24", report)     # Resolución ENRESP

    def test_how_non_existent_fact(self):
        """Caso de Borde: Consulta HOW para un hecho que no existe en WM."""
        expl = self.xai.how("hecho_fantasma_no_existente", self.wm)
        self.assertFalse(expl["found"])
        self.assertIn("no existe", expl["explanation"])

    def test_why_non_existent_rule(self):
        """Caso de Borde: Consulta WHY para una regla no registrada."""
        why = self.xai.why("REGLA_INEXISTENTE_999")
        self.assertFalse(why["found"])
        self.assertIn("no se encuentra registrada", why["explanation"])

    def test_explain_unknown_concept(self):
        """Caso de Borde: Consulta ontológica de concepto inexistente."""
        card = self.xai.explain_concept("CONCEPTO_DESCONOCIDO")
        self.assertIn("no identificado", card)

    def test_generate_audit_report_empty_memory_zero_division_safe(self):
        """Caso de Borde: Generación de dictamen con memoria vacía o total 0 sin división por cero."""
        empty_wm = WorkingMemory()
        empty_wm.assert_fact("factura_monto_total", 0.0)
        report = self.xai.generate_audit_report(empty_wm)
        self.assertIn("DICTAMEN PERICIAL", report)
        self.assertIn("$0.00 ARS", report)

    def test_generate_enresp_claim_letter_contents(self):
        """Verifica la redacción del escrito administrativo formal con citas de Ley 24.240 y Res. 1590/24."""
        claimant = {
            "nombre": "Estudiante UGD",
            "dni": "42.123.456",
            "nis": "3024***",
            "domicilio": "Avda. San Martín 12XX, Salta Capital"
        }
        letter = self.xai.generate_enresp_claim_letter(self.wm, claimant)
        self.assertIn("ESCRITO ADMINISTRATIVO DE FORMAL RECLAMO", letter)
        self.assertIn("Estudiante UGD", letter)
        self.assertIn("42.123.456", letter)
        self.assertIn("3024***", letter)
        self.assertIn("Ley Nacional 24.240", letter)
        self.assertIn("Resolución ENRESP Nro. 1590/24", letter)
        self.assertIn("64,210.15", letter)
        self.assertIn("PETITORIO", letter)
        self.assertIn("SERÁ JUSTICIA", letter)



if __name__ == "__main__":
    unittest.main()
