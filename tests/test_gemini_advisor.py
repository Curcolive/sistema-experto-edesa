"""
Batería de Pruebas Unitarias para el Módulo de Integración con Gemini (GeminiAdvisor)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)
"""

import unittest
from unittest.mock import MagicMock, patch
from src.integrations.gemini_advisor import GeminiAdvisor
from src.engine.working_memory import WorkingMemory
from src.domain.fact_model import Fact, FactCategory


class TestGeminiAdvisor(unittest.TestCase):
    """Pruebas de robustez y resiliencia para la integración neuro-simbólica con Gemini."""

    def test_default_initialization_without_key_operates_in_local_heuristic_mode(self):
        """
        Garantía de Robustez: Sin API Key, el sistema debe operar en modo local heurístico
        sin lanzar excepciones ni degradarse.
        """
        advisor = GeminiAdvisor(api_key="")
        self.assertFalse(advisor.has_api_key())

        status = advisor.get_api_key_status()
        self.assertFalse(status["configured"])
        self.assertEqual(status["mode"], "LOCAL_HEURISTIC")
        self.assertIn("setup_instructions", status)

    def test_enrich_appliance_diagnostic_local_fallback(self):
        """Verifica que el enriquecimiento de diagnóstico devuelva la inferencia local si no hay clave."""
        advisor = GeminiAdvisor(api_key="")
        mock_audit = {
            "total_theoretical_kwh": 350.0,
            "invoice_real_kwh": 428.0,
            "coverage_percentage": 81.8,
            "excess_over_rase_subsidy_kwh": 228.0,
            "culprit_subsidy_loss_appliance": "Caloventor Eléctrico",
            "diagnostic_summary": "El caloventor explica el desborde.",
            "potential_savings_recommendations": ["Reducir 2 horas diarias de caloventor."]
        }

        res = advisor.enrich_appliance_diagnostic(mock_audit)
        self.assertEqual(res["mode"], "LOCAL_HEURISTIC")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("caloventor", res["diagnostic_text"].lower())
        self.assertEqual(len(res["recommendations"]), 1)

    def test_draft_personalized_claim_letter_local_fallback(self):
        """Verifica que la redacción de reclamo genere el escrito pericial legal formal si no hay clave."""
        advisor = GeminiAdvisor(api_key="")
        wm = WorkingMemory()
        wm.assert_fact(Fact(name="factura_periodo", value="09/2026"))
        wm.assert_fact(Fact(name="ahorro_potencial_mensual_estimado_ars", value=64210.15))

        claimant = {
            "nombre": "Estudiante UGD",
            "dni": "42.123.456",
            "nis": "3024***",
            "domicilio": "Avda. Solís Pizarro 14XX, Salta Capital"
        }

        res = advisor.draft_personalized_claim_letter(wm, claimant)
        self.assertEqual(res["mode"], "LOCAL_LEGAL_TEMPLATE")
        self.assertIn("ESCRITO ADMINISTRATIVO", res["letter_text"])
        self.assertIn("Ley Nacional 24.240", res["letter_text"])
        self.assertIn("Resolución ENRESP Nro. 1590/24", res["letter_text"])
        self.assertIn("Estudiante UGD", res["letter_text"])
        self.assertIn("64,210.15", res["letter_text"])

    def test_mocked_gemini_api_key_configuration(self):
        """Verifica que una clave simulada sea detectada y enmascarada adecuadamente."""
        advisor = GeminiAdvisor(api_key="AIzaSyFAKEKEYFORTESTING123456789")
        self.assertTrue(advisor.has_api_key())
        status = advisor.get_api_key_status()
        self.assertTrue(status["configured"])
        self.assertEqual(status["mode"], "GEMINI_ACTIVE")
        self.assertTrue(status["masked_key"].startswith("AIzaSy"))
        self.assertTrue(status["masked_key"].endswith("6789"))

    def test_default_model_is_gemini_3_8_flash(self):
        """Verifica que el modelo predeterminado configurado sea Gemini 3.8 Flash según consigna."""
        advisor = GeminiAdvisor(api_key="")
        self.assertEqual(advisor.model_name, "gemini-3.8-flash")


if __name__ == "__main__":
    unittest.main()
