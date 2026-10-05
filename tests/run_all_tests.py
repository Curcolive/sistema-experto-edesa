"""
Ejecutor Unificado de Pruebas Unitarias del Sistema Experto
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)
"""

import unittest
import sys
import time
from pathlib import Path

# Configurar codificación segura de salida en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configurar ruta base
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from tests.test_domain_and_anonymizer import TestDomainAndAnonymizer
from tests.test_working_memory import TestWorkingMemory
from tests.test_inference_engine import TestInferenceEngine
from tests.test_rules_enresp import TestRulesEnresp
from tests.test_explanation_module import TestExplanationModule
from tests.test_visualizer import TestReportCharts
from tests.test_comparative_analyzer import TestComparativeAnalyzer
from tests.test_duplication_and_history import TestDuplicationAndHistory
from tests.test_macro_analyzer import TestMacroAnalyzer
from tests.test_appliance_analyzer import TestApplianceAnalyzer
from tests.test_pdf_extractor import TestPDFBillExtractor
from tests.test_gemini_advisor import TestGeminiAdvisor


def build_test_suite() -> unittest.TestSuite:
    """Construye la suite unificada con todas las clases de prueba."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestDomainAndAnonymizer,
        TestWorkingMemory,
        TestInferenceEngine,
        TestRulesEnresp,
        TestExplanationModule,
        TestReportCharts,
        TestComparativeAnalyzer,
        TestDuplicationAndHistory,
        TestMacroAnalyzer,
        TestApplianceAnalyzer,
        TestPDFBillExtractor,
        TestGeminiAdvisor
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    return suite


def run_tests() -> bool:
    """Ejecuta toda la batería de pruebas y retorna True si todas pasaron."""
    print("=" * 80)
    print("BATERÍA DE PRUEBAS UNITARIAS AUTOMATIZADAS — SISTEMA EXPERTO EDESA/AGUAS")
    print("Principios de Inteligencia Artificial (GT110) — 1º Parcial — UGD 2026")
    print("Estudiante: Estudiante UGD (Matrícula: 100001)")
    print("=" * 80)

    start_time = time.time()
    suite = build_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print(f"RESUMEN DE EJECUCIÓN: {result.testsRun} pruebas ejecutadas en {elapsed:.3f}s")
    print(f"Éxitos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("ESTADO: [PASS] TODAS LAS PRUEBAS PASARON EXITOSAMENTE (100% OK)")
    else:
        print("ESTADO: [FAIL] SE DETECTARON PROBLEMAS EN LAS PRUEBAS")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
