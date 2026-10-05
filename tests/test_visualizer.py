"""
Pruebas Unitarias del Visualizador y Generador de Gráficos Analíticos
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.visualizer.report_charts import ReportChartsGenerator


class TestReportCharts(unittest.TestCase):
    """Verificación de generación de gráficos analíticos para el informe del parcial."""

    def setUp(self):
        self.output_dir = Path(__file__).resolve().parent.parent / "output_graficos"
        self.generator = ReportChartsGenerator(self.output_dir)

    def test_generate_all_charts(self):
        results = self.generator.generate_all_charts()
        self.assertEqual(len(results), 4)

        # Verificar que los archivos existan y tengan tamaño no nulo
        for key, filepath_str in results.items():
            p = Path(filepath_str)
            self.assertTrue(p.exists(), f"El archivo generado {p} debe existir")
            self.assertGreater(p.stat().st_size, 0, f"El archivo {p} no debe estar vacío")

        # Verificar específicamente los 4 archivos vectoriales SVG
        svg1 = self.output_dir / "grafico_1_distribucion_gasto.svg"
        svg2 = self.output_dir / "grafico_2_historico_consumo_subsidio.svg"
        svg3 = self.output_dir / "grafico_3_ahorro_potencial_desdoblamiento.svg"
        svg4 = self.output_dir / "grafico_4_arbol_inferencia_anomalias.svg"

        self.assertTrue(svg1.exists())
        self.assertTrue(svg2.exists())
        self.assertTrue(svg3.exists())
        self.assertTrue(svg4.exists())


if __name__ == "__main__":
    unittest.main()
