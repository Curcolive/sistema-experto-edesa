"""
Pruebas Unitarias de Detección de Duplicación, Solapamiento y Cadena de Pagos
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Verifica:
1. Detección de boletas duplicadas por período o número de liquidación (R15).
2. Detección de solapamiento temporal de lecturas y saltos de medidor (R16).
3. Verificación de la cadena de pagos según Art. 25 Ley 24.240 y régimen ENRESP (R17).
4. Auditoría integral individual de las 4 boletas reales (Jun-26, Jul-26, Ago-26, Sep-26).
"""

import unittest
from pathlib import Path
import sys
import copy

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.knowledge_base.default_facts import (
    load_all_historical_invoices,
    load_facts_for_period,
    load_default_facts_from_json
)
from src.knowledge_base.rules_enresp import get_all_enresp_rules
from src.persistence.history_store import HistoryStore
from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.domain.fact_model import AnomalySeverity


class TestDuplicationAndHistory(unittest.TestCase):
    """Pruebas unitarias de mecanismos de persistencia, integridad y no duplicación."""

    def setUp(self):
        self.invoices = load_all_historical_invoices()
        self.history = HistoryStore()
        self.history.load_historical_invoices(self.invoices)
        self.rules = get_all_enresp_rules()
        self.engine = InferenceEngine(self.rules)

    def test_duplicate_period_detection(self):
        """Verifica que se rechace una factura que repita un período ya existente (ej: 09/2026)."""
        dup_inv = copy.deepcopy(self.invoices[3])  # 09/2026
        dup_inv["bloque_a_identificacion"]["nro_liquidacion"] = "9999-NUEVA-LIQ"

        result = self.history.check_duplication(dup_inv)
        self.assertTrue(result["is_duplicate"])
        self.assertEqual(result["conflict_type"], "PERIODO_DUPLICADO")
        self.assertEqual(result["conflicting_period"], "09/2026")
        self.assertIn("ya se encuentra registrado", result["message"])

    def test_duplicate_liquidation_number_detection(self):
        """Verifica que se rechace una factura con nro de liquidación idéntico aunque cambie el período."""
        dup_inv = copy.deepcopy(self.invoices[1])  # 07/2026
        dup_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"  # Período ficticio nuevo
        # Mantiene la liquidación 0101-52062202 de 07/2026

        result = self.history.check_duplication(dup_inv)
        self.assertTrue(result["is_duplicate"])
        self.assertEqual(result["conflict_type"], "LIQUIDACION_DUPLICADA")
        self.assertIn("0101-52062202", result["message"])

    def test_unique_invoice_passes_duplication_check(self):
        """Una factura con período y liquidación genuinamente nuevos debe ser admitida."""
        new_inv = copy.deepcopy(self.invoices[3])
        new_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
        new_inv["bloque_a_identificacion"]["nro_liquidacion"] = "0101-52065505"

        result = self.history.check_duplication(new_inv)
        self.assertFalse(result["is_duplicate"])
        self.assertEqual(result["conflict_type"], "NONE")

    def test_reading_dates_overlap_detection(self):
        """Detecta si las fechas de lectura de un nuevo comprobante se solapan con uno previo."""
        # Tomar boleta de Sep-2026 y forzar que su período de lectura arranque antes del fin de Ago-2026
        bad_inv = copy.deepcopy(self.invoices[3])
        bad_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
        bad_inv["bloque_a_identificacion"]["nro_liquidacion"] = "0101-52065505"
        # En Ago-2026 EDESA leyó hasta 2026-08-14. Ponemos que la nueva empieza en 2026-08-01 (13 días solapados)
        bad_inv["bloque_b_electricidad_edesa"]["periodo_lectura"]["desde"] = "2026-08-01"

        result = self.history.check_reading_overlap(bad_inv)
        self.assertTrue(result["has_overlap"])
        self.assertTrue(any("EDESA: Solapamiento temporal" in d for d in result["details"]))

    def test_meter_discontinuity_detection(self):
        """Detecta discordancia física entre la lectura anterior declarada y la actual previa."""
        bad_inv = copy.deepcopy(self.invoices[3])
        bad_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
        bad_inv["bloque_a_identificacion"]["nro_liquidacion"] = "0101-52065505"
        # En 09/2026 la lectura actual fue 30224.0. La nueva declara lectura anterior 28000.0 (salto inexplicable)
        bad_inv["bloque_b_electricidad_edesa"]["energia_activa"]["lectura_anterior"] = 28000.0

        result = self.history.check_reading_overlap(bad_inv)
        self.assertTrue(result["has_overlap"])
        self.assertTrue(any("Discontinuidad en medidor" in d for d in result["details"]))

    def test_real_payment_chain_is_100_percent_valid(self):
        """
        Verificación de la Cadena de Pagos Real (Art. 25 Ley 24.240):
        En los 4 meses aportados:
        - Boleta 07/2026 acredita pago previo: $439.863,51 (exacto total Boleta 06/2026).
        - Boleta 08/2026 acredita pago previo: $516.720,99 (exacto total Boleta 07/2026).
        - Boleta 09/2026 acredita pago previo: $340.064,55 (exacto total Boleta 08/2026).
        La cadena de pagos debe ser 100% íntegra y válida.
        """
        chain_res = self.history.verify_payment_chain(self.invoices)
        self.assertTrue(chain_res["is_chain_valid"])
        self.assertEqual(len(chain_res["discrepancies"]), 0)
        self.assertEqual(len(chain_res["verified_transitions"]), 3)

        t1 = chain_res["verified_transitions"][0]
        self.assertEqual(t1["periodo_previo"], "06/2026")
        self.assertEqual(t1["periodo_actual"], "07/2026")
        self.assertAlmostEqual(t1["total_factura_previa"], 439863.51, places=2)
        self.assertAlmostEqual(t1["pago_anterior_acreditado"], 439863.51, places=2)

        t2 = chain_res["verified_transitions"][1]
        self.assertEqual(t2["periodo_previo"], "07/2026")
        self.assertEqual(t2["periodo_actual"], "08/2026")
        self.assertAlmostEqual(t2["total_factura_previa"], 516720.99, places=2)
        self.assertAlmostEqual(t2["pago_anterior_acreditado"], 516720.99, places=2)

        t3 = chain_res["verified_transitions"][2]
        self.assertEqual(t3["periodo_previo"], "08/2026")
        self.assertEqual(t3["periodo_actual"], "09/2026")
        self.assertAlmostEqual(t3["total_factura_previa"], 340064.55, places=2)
        self.assertAlmostEqual(t3["pago_anterior_acreditado"], 340064.55, places=2)

    def test_payment_chain_discrepancy_detection(self):
        """Caso de Borde: Si se adultera el pago acreditado, se debe detectar la inconsistencia."""
        tampered_invoices = copy.deepcopy(self.invoices)
        # En Sep-2026 se facturó 340.064,55 en Ago. Simulamos que la distribuidora sólo acreditó 200.000,00
        tampered_invoices[3]["bloque_a_identificacion"]["pago_anterior_registrado"] = 200000.00

        chain_res = self.history.verify_payment_chain(tampered_invoices)
        self.assertFalse(chain_res["is_chain_valid"])
        self.assertEqual(len(chain_res["discrepancies"]), 1)
        disc = chain_res["discrepancies"][0]
        self.assertEqual(disc["periodo_previo"], "08/2026")
        self.assertEqual(disc["periodo_actual"], "09/2026")
        self.assertAlmostEqual(disc["diferencia"], 140064.55, places=2)

    def test_rule_r15_fires_on_duplicate_assertion(self):
        """Prueba que el Motor de Inferencia dispare R15 cuando se detecta factura duplicada."""
        facts = load_facts_for_period("09/2026")
        wm = WorkingMemory(facts)
        # Asertar hecho de detección de duplicación
        wm.assert_fact("factura_duplicada_detectada", True)

        result = self.engine.forward_chain(wm)
        self.assertTrue(wm.has("alerta_factura_duplicada"))
        fact_dup = wm.get_fact("alerta_factura_duplicada")
        self.assertEqual(fact_dup.source, "R15_DETECCION_FACTURA_DUPLICADA")
        self.assertEqual(fact_dup.metadata.get("severity"), AnomalySeverity.CRITICAL.value)

    def test_rule_r16_fires_on_reading_overlap(self):
        """Prueba que el Motor de Inferencia dispare R16 ante solapamiento de lecturas."""
        facts = load_facts_for_period("09/2026")
        wm = WorkingMemory(facts)
        wm.assert_fact("lectura_solapamiento_detectado", True)

        result = self.engine.forward_chain(wm)
        self.assertTrue(wm.has("alerta_solapamiento_lectura"))
        fact_sol = wm.get_fact("alerta_solapamiento_lectura")
        self.assertEqual(fact_sol.source, "R16_SOLAPAMIENTO_LECTURAS_MEDIDOR")
        self.assertEqual(fact_sol.metadata.get("severity"), AnomalySeverity.CRITICAL.value)

    def test_rule_r17_fires_on_payment_chain_inconsistency(self):
        """Prueba que el Motor de Inferencia dispare R17 ante inconsistencia en cadena de pagos."""
        facts = load_facts_for_period("09/2026")
        wm = WorkingMemory(facts)
        wm.assert_fact("cadena_pagos_inconsistente", True)

        result = self.engine.forward_chain(wm)
        self.assertTrue(wm.has("alerta_inconsistencia_cadena_pagos"))
        fact_cad = wm.get_fact("alerta_inconsistencia_cadena_pagos")
        self.assertEqual(fact_cad.source, "R17_INCONSISTENCIA_CADENA_PAGOS")

    def test_all_four_individual_invoices_audited_successfully(self):
        """
        Verifica que las 4 facturas individuales (06/2026, 07/2026, 08/2026, 09/2026)
        puedan ser cargadas y procesadas por el motor de inferencia sin excepciones.
        """
        for p in ["06/2026", "07/2026", "08/2026", "09/2026"]:
            facts = load_facts_for_period(p)
            self.assertGreaterEqual(len(facts), 18)
            wm = WorkingMemory(facts)
            res = self.engine.forward_chain(wm)
            self.assertTrue(res.is_quiescent)
            self.assertGreaterEqual(res.rules_fired_count, 10)
            # En todas debe existir la inconsistencia catastral (Residencial en EDESA vs Comercial en Agua)
            self.assertTrue(wm.has("alerta_inconsistencia_tarifaria"))
            # En todas debe existir castigo fiscal de IVA 27% + 13.5%
            self.assertTrue(wm.has("alerta_castigo_fiscal_iva"))
            # En todas debe tener derecho a desdoblamiento
            self.assertTrue(wm.has("derecho_desdoblamiento_habilitado"))

    def test_sequential_addition_of_all_real_invoices_has_no_false_positives(self):
        """
        Prueba crítica de no regresión:
        Verifica que al insertar secuencialmente las 4 facturas reales consecutivas (06 -> 07 -> 08 -> 09),
        el almacén de persistencia NO arroje falsos positivos de solapamiento ni discontinuidad física.
        """
        fresh_store = HistoryStore()
        for idx, inv in enumerate(self.invoices):
            period = inv["bloque_a_identificacion"]["periodo_facturado"]
            dup_check = fresh_store.check_duplication(inv)
            self.assertFalse(dup_check["is_duplicate"], f"Falso positivo de duplicación en período {period}")

            overlap_check = fresh_store.check_reading_overlap(inv)
            self.assertFalse(
                overlap_check["has_overlap"],
                f"Falso positivo de solapamiento/discontinuidad al insertar período {period}: {overlap_check['details']}"
            )
            fresh_store.add_invoice(inv)

        self.assertEqual(len(fresh_store._invoices), 4)

    def test_reverse_order_addition_handles_meter_continuity_seamlessly(self):
        """
        Verifica que insertar comprobantes en orden cronológico inverso (09 -> 08 -> 07 -> 06)
        valide correctamente la continuidad hacia adelante con el sucesor inmediato sin arrojar errores.
        """
        fresh_store = HistoryStore()
        for inv in reversed(self.invoices):
            period = inv["bloque_a_identificacion"]["periodo_facturado"]
            overlap_check = fresh_store.check_reading_overlap(inv)
            self.assertFalse(
                overlap_check["has_overlap"],
                f"Falso positivo en inserción inversa para {period}: {overlap_check['details']}"
            )
            fresh_store.add_invoice(inv)
        self.assertEqual(len(fresh_store._invoices), 4)

    def test_aguas_del_norte_meter_discontinuity_detected(self):
        """
        Verifica que una discrepancia física en el medidor de Aguas del Norte
        (Lec. Anterior del nuevo período != Lec. Actual del período anterior) sea detectada formalmente.
        """
        bad_inv = copy.deepcopy(self.invoices[3])  # 09/2026 (Lec Act fue 4543.0 m³)
        bad_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
        bad_inv["bloque_a_identificacion"]["nro_liquidacion"] = "0101-52069999"
        # Alterar lectura anterior en Aguas del Norte
        bad_inv["bloque_c_agua_aguas_del_norte"]["lecturas_volumen"]["lectura_anterior_m3"] = 4000.0

        overlap_check = self.history.check_reading_overlap(bad_inv)
        self.assertTrue(overlap_check["has_overlap"])
        self.assertTrue(
            any("Aguas del Norte: Discontinuidad en medidor" in d for d in overlap_check["details"]),
            f"No se detectó discontinuidad en Aguas: {overlap_check['details']}"
        )

    def test_inverted_reading_dates_detected(self):
        """
        Verifica que si la fecha de inicio de lectura es posterior a la fecha de fin (desde > hasta),
        el sistema rechace el comprobante por inconsistencia cronológica interna.
        """
        bad_inv = copy.deepcopy(self.invoices[3])
        bad_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
        bad_inv["bloque_a_identificacion"]["nro_liquidacion"] = "0101-52069999"
        # Invertir fechas en EDESA
        bad_inv["bloque_b_electricidad_edesa"]["periodo_lectura"]["desde"] = "2026-10-20"
        bad_inv["bloque_b_electricidad_edesa"]["periodo_lectura"]["hasta"] = "2026-09-20"

        overlap_check = self.history.check_reading_overlap(bad_inv)
        self.assertTrue(overlap_check["has_overlap"])
        self.assertTrue(
            any("Fechas de lectura invertidas" in d for d in overlap_check["details"]),
            f"No se detectó inversión de fechas: {overlap_check['details']}"
        )


    def test_history_store_two_digit_period_order_05_26(self):
        """
        Verifica que parse_period_key resuelva '05/26' como año 2026 y mes 5,
        ordenándose cronológicamente antes de '06/2026' (y no en el año 26 D.C.).
        """
        from src.persistence.history_store import parse_period_key
        key_05_26 = parse_period_key("05/26")
        key_06_2026 = parse_period_key("06/2026")
        self.assertEqual(key_05_26, (2026, 5))
        self.assertEqual(key_06_2026, (2026, 6))
        self.assertLess(key_05_26, key_06_2026)

    def test_history_store_payment_chain_and_meter_continuity_with_may_2026(self):
        """
        Verifica que al incorporar la factura canónica de Mayo 2026 ($315.798,64),
        la cadena de pagos y la continuidad de medidor con Junio 2026 sean 100% íntegras.
        """
        may_inv = {
            "bloque_a_identificacion": {
                "periodo_facturado": "05/2026",
                "nro_liquidacion": "0101-52060000",
                "total_factura": 315798.64,
                "fecha_emision": "2026-05-20",
                "fecha_vencimiento": "2026-06-16",
                "pago_anterior_registrado": 285400.00
            },
            "bloque_b_electricidad_edesa": {
                "periodo_lectura": {"desde": "2026-04-15", "hasta": "2026-05-14"},
                "energia_activa": {
                    "lectura_anterior": 27499.0,
                    "lectura_actual": 27874.0,
                    "consumo_kwh": 375.0
                }
            },
            "bloque_c_agua_aguas_del_norte": {
                "periodo_lectura": {"desde": "2026-03-27", "hasta": "2026-04-25"},
                "lecturas_volumen": {
                    "lectura_anterior_m3": 4415.0,
                    "lectura_actual_m3": 4444.0,
                    "consumo_m3": 29.0
                }
            }
        }

        # Verificar no solapamiento ni discontinuidad al insertar Mayo antes de Junio
        overlap_res = self.history.check_reading_overlap(may_inv)
        self.assertFalse(overlap_res["has_overlap"])

        # Verificar cadena de pagos incorporando Mayo a la lista de facturas
        extended_invoices = [may_inv] + list(self.invoices)
        chain_res = self.history.verify_payment_chain(extended_invoices)
        self.assertTrue(chain_res["is_chain_valid"])
        self.assertEqual(len(chain_res["discrepancies"]), 0)

        # Transición 05/2026 ➔ 06/2026 debe estar entre las transiciones verificadas
        transitions = chain_res["verified_transitions"]
        may_to_june = [t for t in transitions if t["periodo_previo"] == "05/2026" and t["periodo_actual"] == "06/2026"]
        self.assertEqual(len(may_to_june), 1)
        self.assertEqual(may_to_june[0]["total_factura_previa"], 315798.64)
        self.assertEqual(may_to_june[0]["pago_anterior_acreditado"], 315798.64)

    def test_duplicate_period_detection_normalized_formats(self):
        """Verifica que se detecte duplicación independientemente del formato del período (09-26, 09-2026, Sep-26)."""
        for bad_p in ["09-26", "09-2026", "Sep-26", "09/26"]:
            dup_inv = copy.deepcopy(self.invoices[3])  # 09/2026
            dup_inv["bloque_a_identificacion"]["periodo_facturado"] = bad_p
            dup_inv["bloque_a_identificacion"]["nro_liquidacion"] = "9999-NUEVA-LIQ"
            result = self.history.check_duplication(dup_inv)
            self.assertTrue(result["is_duplicate"], f"Falló detección de duplicado para formato {bad_p}")
            self.assertEqual(result["conflict_type"], "PERIODO_DUPLICADO")

    def test_parse_period_key_formats_coverage(self):
        """Verifica el comportamiento de parse_period_key frente a toda la gama de formatos válidos."""
        from src.persistence.history_store import parse_period_key
        test_cases = [
            ("05/2026", (2026, 5)),
            ("05/26", (2026, 5)),
            ("5/26", (2026, 5)),
            ("05-2026", (2026, 5)),
            ("05-26", (2026, 5)),
            ("5-26", (2026, 5)),
            ("Mayo 2026", (2026, 5)),
            ("Mayo 26", (2026, 5)),
            ("May-26", (2026, 5)),
            ("mayo-2026", (2026, 5)),
            ("2026-05", (2026, 5)),
            ("10/2026", (2026, 10)),
            ("10/26", (2026, 10)),
            ("Oct-26", (2026, 10)),
            ("octubre 2026", (2026, 10)),
        ]
        for inp, expected in test_cases:
            self.assertEqual(parse_period_key(inp), expected, f"Fallo al parsear período '{inp}'")


if __name__ == "__main__":
    unittest.main()
