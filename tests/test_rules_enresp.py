"""
Pruebas Unitarias de Reglas Regulatorias (ENRESP / Salta) sobre Factura Real
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.knowledge_base.default_facts import load_default_facts_from_json
from src.knowledge_base.rules_enresp import get_all_enresp_rules


class TestRulesEnresp(unittest.TestCase):
    """Verificación de activación de las 14 reglas sobre la factura sanitizada de Salta."""

    def setUp(self):
        self.facts = load_default_facts_from_json()
        self.wm = WorkingMemory(self.facts)
        self.rules = get_all_enresp_rules()
        self.engine = InferenceEngine(self.rules)

    def test_default_facts_count(self):
        # Debe haber al menos 18-20 hechos iniciales
        self.assertGreaterEqual(len(self.wm), 20)
        self.assertEqual(self.wm.get("factura_monto_total"), 377559.51)
        self.assertEqual(self.wm.get("electricidad_tipo_inmueble"), "RESIDENCIAL")
        self.assertEqual(self.wm.get("agua_tipo_inmueble"), "NO_RESIDENCIAL")
        self.assertEqual(self.wm.get("agua_condicion_fiscal"), "SUJETO_NO_CATEGORIZADO")

    def test_forward_chaining_fires_expected_rules(self):
        result = self.engine.forward_chain(self.wm)

        # Se deben disparar al menos 12 a 14 reglas
        self.assertGreaterEqual(result.rules_fired_count, 12)
        self.assertTrue(result.is_quiescent)

        # 1. Alerta de Castigo Fiscal por IVA No Categorizado (R01)
        self.assertTrue(self.wm.has("alerta_castigo_fiscal_iva"))

        # 2. Inconsistencia Cruzada Catastral (R02)
        self.assertTrue(self.wm.has("alerta_inconsistencia_tarifaria"))

        # 3. Sobrefacturación de Cargo Fijo de Agua (R03)
        self.assertTrue(self.wm.has("alerta_sobrefacturacion_cargo_fijo_agua"))

        # 4. Ahorro Potencial Mensual Estimado (R04)
        self.assertTrue(self.wm.has("ahorro_potencial_mensual_estimado_ars"))
        ahorro = self.wm.get("ahorro_potencial_mensual_estimado_ars")
        self.assertAlmostEqual(ahorro, 64210.15, places=2)

        # 5. Factor de Potencia Óptimo (R05)
        self.assertTrue(self.wm.has("dictamen_factor_potencia_optimo"))
        self.assertGreaterEqual(self.wm.get("dictamen_factor_potencia_optimo"), 0.95)

        # 6. Exceso de Bloque Subsidio RASE (R06)
        self.assertTrue(self.wm.has("alerta_pulverizacion_subsidio_rase"))
        self.assertEqual(self.wm.get("alerta_pulverizacion_subsidio_rase"), 228.0)

        # 7. Habilitación Derecho a Desdoblamiento Res. 1590/24 (R07)
        self.assertTrue(self.wm.has("derecho_desdoblamiento_habilitado"))

        # 8. Segregación Alumbrado Público (R08)
        self.assertTrue(self.wm.has("dictamen_segregacion_alumbrado"))

        # 9. Predominancia Servicios No Eléctricos (R09)
        self.assertTrue(self.wm.has("alerta_predominancia_servicios_no_electricos"))

        # 10. Prorrateo Bicuadro Tarifario (R10)
        self.assertTrue(self.wm.has("informe_prorrateo_bicuadro"))

        # 11. Usuario Libre de Deuda (R11)
        self.assertTrue(self.wm.has("usuario_habilitado_formalizar_reclamo"))

        # 12. Dictamen Formal ENRESP Aprobado (R12)
        self.assertTrue(self.wm.has("dictamen_enresp_formal_generado"))
        self.assertEqual(self.wm.get("dictamen_enresp_formal_generado"), "DICTAMEN_EXPEDIENTE_RECLAMO_APROBADO")

        # 13. Auditoría de Volumen Elevado de Agua (R13)
        self.assertTrue(self.wm.has("alerta_volumen_agua_elevado"))

        # 14. Coeficiente de Presión Tributaria (R14)
        self.assertTrue(self.wm.has("ratio_presion_tributaria_pct"))
        self.assertGreater(self.wm.get("ratio_presion_tributaria_pct"), 30.0)

    def test_debt_blocks_claim_approval(self):
        """Caso de Borde: Si el usuario registra deuda vencida, R11 y R12 quedan bloqueadas."""
        wm_debt = WorkingMemory(self.facts)
        # Inyectar deuda vencida pendiente
        wm_debt.assert_fact("factura_deuda_anterior", 45000.0)

        result = self.engine.forward_chain(wm_debt)
        
        # R11 no debe haberse disparado
        self.assertFalse(wm_debt.has("usuario_habilitado_formalizar_reclamo"))
        # R12 no debe emitir el dictamen formal por falta de legitimación libre de deuda
        self.assertFalse(wm_debt.has("dictamen_enresp_formal_generado"))

    def test_low_water_consumption_no_leak_alert(self):
        """Caso de Borde: Si el volumen de agua es normal (<30 m³), R13 no debe disparar alerta de fuga."""
        wm_low_water = WorkingMemory(self.facts)
        wm_low_water.assert_fact("agua_consumo_volumen_m3", 18.0)

        result = self.engine.forward_chain(wm_low_water)
        self.assertFalse(wm_low_water.has("alerta_volumen_agua_elevado"))

    def test_low_power_factor_no_optimal_dictamen(self):
        """Caso de Borde: Si el cos(phi) cae por debajo de 0.95, R05 no debe certificar condición óptima."""
        wm_cos = WorkingMemory(self.facts)
        wm_cos.assert_fact("electricidad_factor_potencia_cos_phi", 0.88)

        result = self.engine.forward_chain(wm_cos)
        self.assertFalse(wm_cos.has("dictamen_factor_potencia_optimo"))

    def test_low_total_amount_no_split_right(self):
        """Caso de Borde: Si la boleta es de bajo monto (<150.000 ARS), R07 no habilita desdoblamiento preventivo."""
        wm_low_amt = WorkingMemory(self.facts)
        wm_low_amt.assert_fact("factura_monto_total", 85000.0)

        result = self.engine.forward_chain(wm_low_amt)
        self.assertFalse(wm_low_amt.has("derecho_desdoblamiento_habilitado"))

    def test_retiree_social_tariff_rule_r18_does_not_fire_by_default(self):
        """Verifica que sin condición de jubilado, la regla R18 no se dispare."""
        result = self.engine.forward_chain(self.wm)
        self.assertFalse(self.wm.has("alerta_condicion_jubilado_tarifa_social"))

    def test_retiree_social_tariff_rule_r18_fires_and_calculates_subsidy(self):
        """
        Regla R18: Si el titular es jubilado/pensionado, se asertan los beneficios
        de Tarifa Social (50% en cargo fijo de agua) y tutela previsional.
        """
        wm_retiree = WorkingMemory(self.facts)
        wm_retiree.assert_fact("titular_es_jubilado", True)

        result = self.engine.forward_chain(wm_retiree)
        self.assertTrue(wm_retiree.has("alerta_condicion_jubilado_tarifa_social"))
        fact = wm_retiree.get_fact("alerta_condicion_jubilado_tarifa_social")
        self.assertEqual(fact.rule_id, "R18_CONDICION_JUBILADO_TARIFA_SOCIAL")
        # 50% de $69.404,04 = $34.702,02
        self.assertAlmostEqual(fact.financial_impact_ars, 34702.02, places=2)
        self.assertIn("Jubilado", fact.description)

    def test_claim_letter_includes_retiree_vulnerability_when_applicable(self):
        """Verifica que el escrito formal de reclamo integre la tutela previsional para jubilados."""
        from src.engine.explanation_module import ExplanationModule
        wm_retiree = WorkingMemory(self.facts)
        wm_retiree.assert_fact("titular_es_jubilado", True)
        self.engine.forward_chain(wm_retiree)

        explainer = ExplanationModule()
        letter = explainer.generate_enresp_claim_letter(wm_retiree)
        self.assertIn("JUBILADO / PENSIONADO", letter)
        self.assertIn("Tarifa Social", letter)
        self.assertIn("50%", letter)

    def test_retiree_social_tariff_rule_r18_backward_chaining(self):
        """
        Verifica la demostración de la meta 'alerta_condicion_jubilado_tarifa_social'
        mediante encadenamiento hacia atrás (Backward Chaining).
        """
        wm_retiree = WorkingMemory(self.facts)
        wm_retiree.assert_fact("titular_es_jubilado", True)

        res_proven = self.engine.backward_chain(wm_retiree, "alerta_condicion_jubilado_tarifa_social")
        self.assertTrue(res_proven.goal_proven)
        self.assertEqual(res_proven.proof_tree["status"], "PROVEN_BY_RULE_FIRING")
        self.assertEqual(res_proven.proof_tree["rule_id"], "R18_CONDICION_JUBILADO_TARIFA_SOCIAL")
        self.assertTrue(wm_retiree.has("alerta_condicion_jubilado_tarifa_social"))

        wm_standard = WorkingMemory(self.facts)
        res_unproven = self.engine.backward_chain(wm_standard, "alerta_condicion_jubilado_tarifa_social")
        self.assertFalse(res_unproven.goal_proven)
        self.assertEqual(res_unproven.proof_tree["status"], "UNPROVABLE")


if __name__ == "__main__":
    unittest.main()
