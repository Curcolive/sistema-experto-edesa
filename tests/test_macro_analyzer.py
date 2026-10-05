"""
Batería de Pruebas Unitarias para el Módulo de Analítica Macroeconómica (MacroAnalyzer)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)
"""

import unittest
import json
from pathlib import Path
from src.engine.macro_analyzer import MacroAnalyzer, PeriodShareRecord, CumulativeTaxBreakdown, MacroVarianceReport

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestMacroAnalyzer(unittest.TestCase):
    """Pruebas unitarias y de robustez para MacroAnalyzer."""

    @classmethod
    def setUpClass(cls):
        """Carga las 4 facturas reales del cuatrimestre."""
        cls.invoices = []
        for period in ["06_2026", "07_2026", "08_2026", "09_2026"]:
            file_path = DATA_DIR / f"factura_{period}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    cls.invoices.append(json.load(f))

    def setUp(self):
        self.analyzer = MacroAnalyzer(self.invoices)

    def test_invoices_loaded_and_ordered(self):
        """Verifica que se hayan cargado y ordenado cronológicamente los 4 comprobantes."""
        self.assertEqual(len(self.analyzer.ordered_periods), 4)
        self.assertEqual(self.analyzer.ordered_periods, ["06/2026", "07/2026", "08/2026", "09/2026"])

    def test_calculate_service_shares_integrity(self):
        """Verifica que el cálculo de participaciones sea coherente y sume 100%."""
        shares = self.analyzer.calculate_service_shares()
        self.assertEqual(len(shares), 4)

        for s in shares:
            self.assertGreater(s.total_factura, 0.0)
            self.assertGreater(s.edesa_ars, 0.0)
            self.assertGreater(s.aguas_ars, 0.0)
            self.assertGreater(s.muni_ars, 0.0)
            # Suma de participaciones debe aproximarse al 100%
            pct_sum = s.pct_edesa + s.pct_aguas + s.pct_muni + s.pct_lusal
            self.assertAlmostEqual(pct_sum, 100.0, delta=0.5)

        # En agosto y septiembre, la participación no eléctrica supera el 50%
        share_08 = next(s for s in shares if s.period == "08/2026")
        self.assertGreater(share_08.pct_no_electrico, 60.0)

    def test_cumulative_tax_breakdown(self):
        """Verifica la liquidación acumulada de la carga impositiva cuatrimestral."""
        tax = self.analyzer.calculate_cumulative_tax_breakdown()
        self.assertIsInstance(tax, CumulativeTaxBreakdown)
        self.assertGreater(tax.total_facturado_cuatrimestre_ars, 1_600_000.0)
        self.assertGreater(tax.total_tributos_acumulados_ars, 450_000.0)
        # Presión tributaria efectiva debe rondar el 30%
        self.assertGreaterEqual(tax.presion_tributaria_efectiva_pct, 25.0)
        self.assertLessEqual(tax.presion_tributaria_efectiva_pct, 38.0)
        # Tributos evitables por falta de categorización en agua
        self.assertGreater(tax.tributos_castigo_evitables_ars, 80_000.0)

    def test_macro_variance_decomposition(self):
        """Verifica la detección del pico de invierno y la trayectoria del cargo fijo de agua."""
        rep = self.analyzer.analyze_macro_variance()
        self.assertIsInstance(rep, MacroVarianceReport)
        self.assertEqual(rep.pico_invernal_periodo, "07/2026")
        self.assertEqual(rep.pico_invernal_kwh, 847.0)
        self.assertEqual(rep.periodo_maximo_pico[0], "07/2026")
        self.assertEqual(rep.periodo_minimo[0], "08/2026")
        self.assertGreater(rep.amplitud_variacion_ars, 150_000.0)
        # Incremento acumulado en cargo fijo de Aguas del Norte debe ser positivo (+11.6%)
        self.assertGreater(rep.incremento_acumulado_tarifa_agua_pct, 10.0)
        self.assertIn("estacionalidad", rep.diagnostico_macro.lower())

    def test_stacked_chart_dataset(self):
        """Verifica que el dataset estructurado para gráficos apilados sea válido."""
        ds = self.analyzer.generate_stacked_chart_dataset()
        self.assertEqual(len(ds), 4)
        for item in ds:
            self.assertIn("period", item)
            self.assertIn("total", item)
            self.assertIn("edesa", item)
            self.assertIn("aguas", item)
            self.assertIn("muni", item)
            self.assertIn("lusal", item)

    def test_edge_case_empty_invoices(self):
        """Caso de Borde: Analizador con lista vacía sin divisiones por cero."""
        empty_analyzer = MacroAnalyzer([])
        shares = empty_analyzer.calculate_service_shares()
        self.assertEqual(len(shares), 0)

        tax = empty_analyzer.calculate_cumulative_tax_breakdown()
        self.assertEqual(tax.total_facturado_cuatrimestre_ars, 0.0)
        self.assertEqual(tax.presion_tributaria_efectiva_pct, 0.0)

        rep = empty_analyzer.analyze_macro_variance()
        self.assertEqual(rep.total_cuatrimestre_ars, 0.0)
        self.assertIn("No hay facturas", rep.diagnostico_macro)


    def test_arbitrary_period_series_trajectory(self):
        """
        Robustez: Verifica que la trayectoria tarifaria y el pico se calculen correctamente
        incluso si los períodos no son exactamente '06/2026' y '09/2026'.
        """
        sub_invoices = [inv for inv in self.invoices if inv.get("bloque_a_identificacion", {}).get("periodo_facturado") in ("07/2026", "08/2026")]
        analyzer = MacroAnalyzer(sub_invoices)
        rep = analyzer.analyze_macro_variance()
        self.assertEqual(rep.periodo_maximo_pico[0], "07/2026")
        self.assertEqual(rep.periodo_minimo[0], "08/2026")
        self.assertGreater(rep.incremento_acumulado_tarifa_agua_pct, 0.0)
        self.assertIn("07/2026", rep.diagnostico_macro)


if __name__ == "__main__":
    unittest.main()
