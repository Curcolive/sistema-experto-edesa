"""
Pruebas Unitarias del Módulo de Análisis Comparativo Multimes
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Verifica la descomposición formal de variaciones económicas:
Efecto Volumen vs. Efecto Tarifa / Inflación entre los 4 períodos de 2026.
"""

import unittest
from pathlib import Path
import sys
import copy

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.knowledge_base.default_facts import load_all_historical_invoices
from src.engine.comparative_analyzer import ComparativeAnalyzer, ServiceVarianceBreakdown, PeriodComparison


class TestComparativeAnalyzer(unittest.TestCase):
    """Verificación de la descomposición econométrica multimes (06/2026 a 09/2026)."""

    def setUp(self):
        self.invoices = load_all_historical_invoices()
        self.analyzer = ComparativeAnalyzer(self.invoices)

    def test_invoices_loaded_and_ordered(self):
        """Verifica que se hayan cargado las 4 facturas y ordenado cronológicamente."""
        self.assertEqual(len(self.analyzer.ordered_periods), 4)
        self.assertEqual(self.analyzer.ordered_periods, ["06/2026", "07/2026", "08/2026", "09/2026"])

    def test_winter_peak_decomposition_06_to_07(self):
        """
        Salto de invierno (Junio a Julio):
        El consumo eléctrico pasa de 718 kWh a 847 kWh (+129 kWh, +17,97%).
        La factura total sube de $439.863,51 a $516.720,99 (+ $76.857,48).
        El Efecto Volumen en luz debe ser positivo y ser el driver principal.
        """
        comp = self.analyzer.compare_periods("06/2026", "07/2026")
        self.assertEqual(comp.period_prev, "06/2026")
        self.assertEqual(comp.period_curr, "07/2026")
        self.assertAlmostEqual(comp.total_prev, 439863.51, places=2)
        self.assertAlmostEqual(comp.total_curr, 516720.99, places=2)
        self.assertAlmostEqual(comp.delta_total, 76857.48, places=2)

        # Desglose EDESA
        edesa = comp.edesa
        self.assertEqual(edesa.volume_prev, 718.0)
        self.assertEqual(edesa.volume_curr, 847.0)
        self.assertAlmostEqual(edesa.delta_volume, 129.0, places=1)
        self.assertGreater(edesa.volume_effect_ars, 35000.0)
        self.assertEqual(edesa.primary_driver, "VOLUMEN")
        self.assertEqual(comp.macro_driver, "PICO_INVERNAL_VOLUMEN")

    def test_post_winter_drop_decomposition_07_to_08(self):
        """
        Salto post-invierno (Julio a Agosto):
        El consumo eléctrico se desploma de 847 kWh a 357 kWh (-490 kWh, -57,85%).
        La factura total cae de $516.720,99 a $340.064,55 (- $176.656,44).
        El Efecto Volumen en luz debe ser fuertemente negativo.
        """
        comp = self.analyzer.compare_periods("07/2026", "08/2026")
        self.assertEqual(comp.period_prev, "07/2026")
        self.assertEqual(comp.period_curr, "08/2026")
        self.assertAlmostEqual(comp.delta_total, -176656.44, places=2)

        edesa = comp.edesa
        self.assertEqual(edesa.volume_prev, 847.0)
        self.assertEqual(edesa.volume_curr, 357.0)
        self.assertAlmostEqual(edesa.delta_volume, -490.0, places=1)
        self.assertLess(edesa.volume_effect_ars, -100000.0)
        self.assertEqual(comp.macro_driver, "CONTRACCION_POST_PICO")

    def test_water_variance_decomposition(self):
        """Verifica la descomposición de variaciones en Aguas del Norte."""
        comp = self.analyzer.compare_periods("06/2026", "07/2026")
        aguas = comp.aguas
        self.assertEqual(aguas.volume_prev, 31.0)
        self.assertEqual(aguas.volume_curr, 36.0)
        self.assertAlmostEqual(aguas.delta_volume, 5.0, places=1)
        self.assertGreater(aguas.delta_amount, 0.0)
        self.assertGreater(aguas.volume_effect_ars, 0.0)

    def test_all_consecutive_periods_comparison(self):
        """Verifica la ejecución de comparaciones consecutivas (3 transiciones)."""
        comparisons = self.analyzer.analyze_all_consecutive()
        self.assertEqual(len(comparisons), 3)

        # Transición 1: 06 -> 07 (Suba)
        self.assertEqual(comparisons[0].period_prev, "06/2026")
        self.assertEqual(comparisons[0].period_curr, "07/2026")
        self.assertGreater(comparisons[0].delta_total, 0)

        # Transición 2: 07 -> 08 (Baja pronunciada)
        self.assertEqual(comparisons[1].period_prev, "07/2026")
        self.assertEqual(comparisons[1].period_curr, "08/2026")
        self.assertLess(comparisons[1].delta_total, 0)

        # Transición 3: 08 -> 09 (Rebote moderado)
        self.assertEqual(comparisons[2].period_prev, "08/2026")
        self.assertEqual(comparisons[2].period_curr, "09/2026")
        self.assertGreater(comparisons[2].delta_total, 0)

    def test_multimonth_evolution_table_integrity(self):
        """Verifica que la tabla consolidada contenga las 4 filas con datos numéricos exactos."""
        table = self.analyzer.get_multimonth_evolution_table()
        self.assertEqual(len(table), 4)
        periods = [r["periodo"] for r in table]
        self.assertEqual(periods, ["06/2026", "07/2026", "08/2026", "09/2026"])

        # Verificar totales de cada período
        self.assertAlmostEqual(table[0]["total_factura"], 439863.51, places=2)
        self.assertAlmostEqual(table[1]["total_factura"], 516720.99, places=2)
        self.assertAlmostEqual(table[2]["total_factura"], 340064.55, places=2)
        self.assertAlmostEqual(table[3]["total_factura"], 377559.51, places=2)

    def test_edge_case_unknown_period_raises_keyerror(self):
        """Caso de Borde: Solicitar comparación con un período inexistente debe lanzar KeyError."""
        with self.assertRaises(KeyError):
            self.analyzer.compare_periods("01/2025", "06/2026")

    def test_zero_variation_identical_periods_zero_division_guard(self):
        """
        Caso de Borde Crítico:
        Verifica que comparar períodos con variación nula (ΔQ=0 y ΔP=0)
        no lance ZeroDivisionError y asigne split equilibrado de drivers (50%/50%).
        """
        dup_inv = copy.deepcopy(self.invoices[0])
        dup_inv["bloque_a_identificacion"]["periodo_facturado"] = "06_DUP/2026"
        custom_analyzer = ComparativeAnalyzer([self.invoices[0], dup_inv])

        comp = custom_analyzer.compare_periods("06/2026", "06_DUP/2026")
        self.assertAlmostEqual(comp.delta_total, 0.0, places=2)
        self.assertEqual(comp.pct_volume_driver, 50.0)
        self.assertEqual(comp.pct_tariff_driver, 50.0)

    def test_zero_initial_consumption_volume_effect_guard(self):
        """
        Caso de Borde Crítico:
        Si el consumo eléctrico del mes anterior fue 0 kWh (p_unit_prev indeterminado),
        el Efecto Volumen debe valorizarse con el precio unitario del período actual sin fallar.
        """
        zero_inv = copy.deepcopy(self.invoices[0])
        zero_inv["bloque_a_identificacion"]["periodo_facturado"] = "05/2026"
        zero_inv["bloque_b_electricidad_edesa"]["energia_activa"]["consumo_kwh"] = 0.0
        zero_inv["bloque_b_electricidad_edesa"]["desglose_costos"]["subtotal_edesa_neto"] = 8450.0
        zero_inv["bloque_b_electricidad_edesa"]["desglose_costos"]["cargo_fijo_total"] = 8450.0

        custom_analyzer = ComparativeAnalyzer([zero_inv, self.invoices[0]])
        comp = custom_analyzer.compare_periods("05/2026", "06/2026")
        self.assertGreater(comp.edesa.volume_effect_ars, 0.0)
        self.assertAlmostEqual(comp.edesa.tariff_effect_ars, 0.0, places=2)

    def test_zero_initial_water_consumption_guard(self):
        """
        Caso de Borde Crítico:
        Si el volumen de agua anterior fue 0 m³, el Efecto Volumen en agua debe
        calcularse correctamente sin división por cero ni omisión de impacto.
        """
        zero_inv = copy.deepcopy(self.invoices[0])
        zero_inv["bloque_a_identificacion"]["periodo_facturado"] = "05/2026"
        zero_inv["bloque_c_agua_aguas_del_norte"]["lecturas_volumen"]["consumo_m3"] = 0.0
        zero_inv["bloque_c_agua_aguas_del_norte"]["desglose_costos"]["consumo_variable"] = 0.0

        custom_analyzer = ComparativeAnalyzer([zero_inv, self.invoices[0]])
        comp = custom_analyzer.compare_periods("05/2026", "06/2026")
        self.assertGreater(comp.aguas.volume_effect_ars, 0.0)
        self.assertAlmostEqual(comp.aguas.tariff_effect_ars, 0.0, places=2)


if __name__ == "__main__":
    unittest.main()
