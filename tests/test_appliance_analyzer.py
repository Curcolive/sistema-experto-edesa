"""
Batería de Pruebas Unitarias para el Analizador de Dispositivos Eléctricos (ApplianceAnalyzer)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)
"""

import unittest
from src.engine.appliance_analyzer import (
    ApplianceAnalyzer,
    ApplianceModel,
    ApplianceUsageItem,
    ApplianceAuditResult
)


class TestApplianceAnalyzer(unittest.TestCase):
    """Pruebas analíticas y de correlación para ApplianceAnalyzer."""

    def setUp(self):
        self.analyzer = ApplianceAnalyzer()

    def test_catalog_structure_and_categories(self):
        """Verifica que el catálogo residencial contenga artefactos base y térmicos válidos."""
        cat = self.analyzer.get_catalog()
        self.assertGreaterEqual(len(cat), 10)

        ids = [a.id for a in cat]
        self.assertIn("heladera_freezer", ids)
        self.assertIn("caloventor_electrico", ids)
        self.assertIn("termotanque_electrico", ids)
        self.assertIn("iluminacion_led", ids)

    def test_analytical_formula_individual_appliance(self):
        """Verifica la fórmula analítica (W * h * duty * days) / 1000."""
        # Caloventor: 2000W * 4h * 1.0 * 30 / 1000 = 240.0 kWh
        caloventor = next(a for a in self.analyzer.get_catalog() if a.id == "caloventor_electrico")
        kwh = caloventor.calculate_monthly_kwh(hours_per_day=4.0, quantity=1)
        self.assertEqual(kwh, 240.0)

        # Heladera: 200W * 24h * 0.35 * 30 / 1000 = 50.4 kWh
        heladera = next(a for a in self.analyzer.get_catalog() if a.id == "heladera_freezer")
        kwh_heladera = heladera.calculate_monthly_kwh(hours_per_day=24.0, quantity=1)
        self.assertEqual(kwh_heladera, 50.4)

    def test_correlation_with_september_invoice_428kwh(self):
        """Correlaciona con la factura de Septiembre (428 kWh) y verifica el exceso RASE N3."""
        res = self.analyzer.correlate_with_invoice(invoice_kwh=428.0)
        self.assertIsInstance(res, ApplianceAuditResult)
        self.assertEqual(res.invoice_real_kwh, 428.0)
        self.assertEqual(res.excess_over_rase_subsidy_kwh, 228.0)  # 428 - 200
        self.assertGreater(res.excess_financial_impact_ars, 0.0)
        self.assertGreater(res.total_theoretical_kwh, 0.0)
        self.assertGreater(len(res.items), 0)

    def test_correlation_with_winter_peak_847kwh_identifies_culprit(self):
        """
        En el pico invernal de Julio (847 kWh), el analizador debe atribuir el desborde
        a las cargas térmicas de alta potencia.
        """
        res = self.analyzer.correlate_with_invoice(invoice_kwh=847.0)
        self.assertEqual(res.invoice_real_kwh, 847.0)
        self.assertEqual(res.excess_over_rase_subsidy_kwh, 647.0)
        self.assertIsNotNone(res.culprit_subsidy_loss_appliance)
        # El culpable debe ser un calefactor térmico
        self.assertIn(res.culprit_subsidy_loss_appliance, ["Caloventor Eléctrico", "Termotanque Eléctrico (80 Litros)"])
        # Debe contener recomendaciones concretas de ahorro
        self.assertGreater(len(res.potential_savings_recommendations), 0)
        self.assertTrue(any("Reducir" in r for r in res.potential_savings_recommendations))

    def test_custom_user_inventory(self):
        """Prueba con un inventario de electrodomésticos personalizado por el usuario."""
        custom_inputs = [
            {"id": "heladera_freezer", "quantity": 1, "hours_per_day": 24.0, "enabled": True},
            {"id": "caloventor_electrico", "quantity": 2, "hours_per_day": 6.0, "enabled": True},  # 2 caloventores a 6h = 720 kWh
        ]
        res = self.analyzer.correlate_with_invoice(invoice_kwh=847.0, custom_inputs=custom_inputs)
        # 50.4 kWh + 720.0 kWh = 770.4 kWh
        self.assertAlmostEqual(res.total_theoretical_kwh, 770.4, places=1)
        self.assertEqual(res.culprit_subsidy_loss_appliance, "Caloventor Eléctrico")
        self.assertGreater(res.coverage_percentage, 85.0)

    def test_edge_case_zero_consumption_guard(self):
        """Caso de Borde: Consumo 0 kWh no debe causar divisiones por cero ni fallos."""
        res = self.analyzer.correlate_with_invoice(invoice_kwh=0.0)
        self.assertEqual(res.invoice_real_kwh, 0.0)
        self.assertEqual(res.excess_over_rase_subsidy_kwh, 0.0)
        self.assertEqual(res.excess_financial_impact_ars, 0.0)

    def test_edge_case_negative_and_empty_inputs(self):
        """Caso de Borde: Parámetros negativos son saneados a cero."""
        custom_inputs = [
            {"id": "heladera_freezer", "quantity": -2, "hours_per_day": -5.0, "enabled": True}
        ]
        res = self.analyzer.correlate_with_invoice(invoice_kwh=200.0, custom_inputs=custom_inputs)
        self.assertEqual(res.total_theoretical_kwh, 0.0)


    def test_savings_formula_considers_duty_cycle(self):
        """
        Rigor Analítico: La recomendación de ahorro en artefactos con ciclado termostático
        (ej. Aire Acondicionado Frío/Calor con duty_cycle=0.60) debe incorporar el factor de marcha.
        """
        custom_inputs = [
            {"id": "aire_acondicionado_fc", "quantity": 1, "hours_per_day": 5.0, "enabled": True}
        ]
        res = self.analyzer.correlate_with_invoice(invoice_kwh=400.0, custom_inputs=custom_inputs)
        # Ahorro de 2 horas en equipo de 1400W con duty_cycle 0.60:
        # (1400 * 2 * 0.60 * 30) / 1000 = 50.4 kWh
        self.assertTrue(any("50.4 kWh" in r for r in res.potential_savings_recommendations))

    def test_frontend_camelcase_input_compatibility(self):
        """
        Compatibilidad Frontend-Backend: Debe aceptar los formatos de diccionario de JavaScript
        (watts, hours, qty, dutyCycle, isThermal y alias de id como 'caloventor').
        """
        js_style_inputs = [
            {
                "id": "caloventor",
                "watts": 2000,
                "hours": 4,
                "qty": 1,
                "dutyCycle": 1.0,
                "isThermal": True,
                "enabled": True
            }
        ]
        res = self.analyzer.correlate_with_invoice(invoice_kwh=428.0, custom_inputs=js_style_inputs)
        self.assertEqual(res.total_theoretical_kwh, 240.0)
        self.assertEqual(res.culprit_subsidy_loss_appliance, "Caloventor Eléctrico")

    def test_empty_appliances_with_excess_invoice_diagnostic(self):
        """
        Caso de Borde: Si no se configuran artefactos (lista vacía) pero la boleta tiene 428 kWh,
        el diagnóstico debe alertar sobre la falta de inventario para explicar el desborde.
        """
        res = self.analyzer.correlate_with_invoice(invoice_kwh=428.0, custom_inputs=[])
        self.assertEqual(res.total_theoretical_kwh, 0.0)
        self.assertIn("excediendo el tope subsidiado", res.diagnostic_summary.lower())
        self.assertNotIn("parámetros de alta eficiencia", res.diagnostic_summary.lower())


if __name__ == "__main__":
    unittest.main()
