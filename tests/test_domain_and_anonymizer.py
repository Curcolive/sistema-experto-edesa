"""
Pruebas Unitarias del Dominio y Módulo de Anonimización PII
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
"""

import unittest
from pathlib import Path
import json
import sys

# Asegurar path de importación
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domain.fact_model import (
    Fact,
    ElectricFact,
    WaterFact,
    MunicipalFact,
    RegulatoryFact,
    AuditAnomalyFact,
    FactCategory,
    AnomalySeverity
)
from src.domain.anonymizer import InvoiceAnonymizer


class TestDomainAndAnonymizer(unittest.TestCase):
    """Pruebas de verificación de clases de hechos y sanitización PII."""

    def test_fact_creation_and_matching(self):
        f = Fact(name="test_fact", value=123.45, unit="ARS", category=FactCategory.GENERAL)
        self.assertEqual(f.name, "test_fact")
        self.assertEqual(f.value, 123.45)
        self.assertEqual(f.unit, "ARS")
        self.assertTrue(f.matches("test_fact"))
        self.assertTrue(f.matches("test_fact", 123.45))
        self.assertFalse(f.matches("test_fact", 999))
        self.assertFalse(f.matches("otro_hecho"))

    def test_fact_subclasses_categories(self):
        ef = ElectricFact(name="luz", value=100)
        self.assertEqual(ef.category, FactCategory.ELECTRIC)

        wf = WaterFact(name="agua", value=50)
        self.assertEqual(wf.category, FactCategory.WATER)

        mf = MunicipalFact(name="tasa", value=20)
        self.assertEqual(mf.category, FactCategory.MUNICIPAL)

        rf = RegulatoryFact(name="norma", value="1590/24")
        self.assertEqual(rf.category, FactCategory.REGULATORY)

        af = AuditAnomalyFact(
            name="alerta",
            value=True,
            rule_id="R01",
            severity=AnomalySeverity.CRITICAL,
            financial_impact_ars=25000.0
        )
        self.assertEqual(af.category, FactCategory.AUDIT_DERIVED)
        self.assertEqual(af.metadata.get("severity"), "CRITICAL")
        self.assertEqual(af.metadata.get("financial_impact_ars"), 25000.0)

    def test_anonymizer_masking_functions(self):
        name = "VELARDE SARA JOSEFINA"
        self.assertEqual(InvoiceAnonymizer.mask_name(name), "USUARIO_ANON_01")

        nis = "3024122"
        masked_nis = InvoiceAnonymizer.mask_nis(nis)
        self.assertTrue(masked_nis.startswith("3024"))
        self.assertIn("*", masked_nis)

        medidor = "1688895"
        masked_med = InvoiceAnonymizer.mask_meter(medidor)
        self.assertTrue(masked_med.startswith("1688"))
        self.assertIn("*", masked_med)

        catastro = "43038"
        masked_cat = InvoiceAnonymizer.mask_catastro(catastro)
        self.assertTrue(masked_cat.startswith("430"))
        self.assertIn("*", masked_cat)

        dir_orig = "Avda. San Martín 1250, Salta Capital"
        masked_dir = InvoiceAnonymizer.mask_address(dir_orig)
        self.assertNotIn("1250", masked_dir)
        self.assertIn("12XX", masked_dir)

    def test_sanitized_json_file_validity(self):
        json_path = Path(__file__).resolve().parent.parent / "data" / "factura_sanitizada.json"
        self.assertTrue(json_path.exists(), "El archivo data/factura_sanitizada.json debe existir")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata_sanitizacion", data)
        self.assertEqual(data["metadata_sanitizacion"]["titular_sanitizado"], "USUARIO_ANON_01")
        self.assertIn("bloque_a_identificacion", data)
        self.assertIn("bloque_b_electricidad_edesa", data)
        self.assertIn("bloque_c_agua_aguas_del_norte", data)
        self.assertIn("bloque_d_tributos_municipales_y_concesiones", data)
        self.assertIn("bloque_e_marco_regulatorio_enresp", data)

    def test_anonymizer_edge_cases_empty_and_short_inputs(self):
        """Caso de Borde: Manejo seguro de entradas vacías o None en el enmascarador."""
        self.assertEqual(InvoiceAnonymizer.mask_name(""), "USUARIO_ANON_01")
        self.assertEqual(InvoiceAnonymizer.mask_name(None), "USUARIO_ANON_01")
        self.assertIn("Anonimizado", InvoiceAnonymizer.mask_address(""))
        self.assertIn("Anonimizado", InvoiceAnonymizer.mask_address(None))
        self.assertEqual(InvoiceAnonymizer.mask_identifier(""), "******")
        self.assertEqual(InvoiceAnonymizer.mask_identifier(None), "******")
        # Identificador muy corto (menor o igual a prefix)
        short_masked = InvoiceAnonymizer.mask_identifier("12", visible_prefix=4)
        self.assertTrue(short_masked.startswith("1"))
        self.assertIn("*", short_masked)

    def test_fact_serialization_and_repr(self):
        """Prueba de serialización a diccionario y representación en texto de hechos."""
        f = Fact(name="test_f", value=42, unit="kWh")
        d = f.to_dict()
        self.assertEqual(d["name"], "test_f")
        self.assertEqual(d["value"], 42)
        self.assertEqual(d["unit"], "kWh")
        self.assertEqual(d["category"], "GENERAL")
        repr_str = repr(f)
        self.assertIn("test_f", repr_str)
        self.assertIn("42", repr_str)


if __name__ == "__main__":
    unittest.main()
