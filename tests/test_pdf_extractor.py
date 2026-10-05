"""
Batería de Pruebas Unitarias para el Extractor Seguro de PDF e Invariantes Aritméticas
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)
"""

import unittest
from pathlib import Path
from src.domain.pdf_extractor import (
    PDFBillExtractor,
    InvoiceExtractionResult,
    ArithmeticInvariantError
)


class TestPDFBillExtractor(unittest.TestCase):
    """Pruebas de extracción y guardianes de invariantes matemáticas deterministas."""

    def setUp(self):
        self.extractor = PDFBillExtractor(tolerance=0.05)
        # Texto de factura representativo de Salta 2026 con cuadratura exacta
        self.valid_invoice_text = """
        EMPRESA DISTRIBUIDORA DE ELECTRICIDAD DE SALTA S.A. (EDESA)
        AGUAS DEL NORTE (CoSAySa) - MUNICIPALIDAD DE LA CIUDAD DE SALTA
        
        NIS: 3024***
        Liquidación Nro: 0101-52064404
        Período Facturado: 09/2026
        Fecha de Emisión: 2026-09-22
        Fecha de Vencimiento: 2026-10-16
        
        SUMINISTRO ELÉCTRICO (EDESA):
        Lectura Desde: 2026-08-14
        Lectura Hasta: 2026-09-14
        Lectura Anterior: 29796.0
        Lectura Actual: 30224.0
        Consumo Activo: 428.0 kWh
        Subtotal EDESA: $152.447,97
        
        SERVICIO SANITARIO (AGUAS DEL NORTE):
        m3 anterior: 4548.0
        m3 actual: 4580.0
        Consumo Agua: 32.0 m3
        Subtotal Aguas: $169.262,42
        
        TRIBUTOS Y CONCESIONES MUNICIPALES:
        Subtotal Municipal: $48.670,80
        Subtotal LUSAL: $7.178,32
        
        TOTAL A PAGAR: $377.559,51
        """

    def test_valid_invoice_passes_all_invariants(self):
        """Verifica que un comprobante consistente apruebe todas las invariantes matemáticas."""
        res = self.extractor.process_text_content(self.valid_invoice_text, strict=True)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.validation_errors), 0)
        self.assertTrue(res.invariants_checked["electric_meter_reading"])
        self.assertTrue(res.invariants_checked["water_meter_reading"])
        self.assertTrue(res.invariants_checked["total_subtotals_sum"])
        self.assertTrue(res.invariants_checked["reading_dates_order"])
        self.assertTrue(res.invariants_checked["invoice_dates_order"])

        # Verificar datos canónicos
        canon = res.data
        self.assertEqual(canon["bloque_a_identificacion"]["periodo_facturado"], "09/2026")
        self.assertEqual(canon["bloque_a_identificacion"]["nro_liquidacion"], "0101-52064404")
        self.assertEqual(canon["bloque_b_electricidad_edesa"]["energia_activa"]["consumo_kwh"], 428.0)
        self.assertEqual(canon["bloque_c_agua_aguas_del_norte"]["lecturas_volumen"]["consumo_m3"], 32.0)

    def test_tampered_electric_meter_reading_fails_invariant(self):
        """
        Invariante 1: Si Lectura Actual - Anterior != Consumo,
        debe fallar la invariante de medición eléctrica.
        """
        tampered_text = self.valid_invoice_text.replace("Lectura Actual: 30224.0", "Lectura Actual: 30800.0")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["electric_meter_reading"])
        self.assertTrue(any("Medición Eléctrica" in err for err in res.validation_errors))

        # En modo estricto debe lanzar ArithmeticInvariantError
        with self.assertRaises(ArithmeticInvariantError):
            self.extractor.process_text_content(tampered_text, strict=True)

    def test_tampered_water_meter_reading_fails_invariant(self):
        """
        Invariante 2: Si Lectura Actual Agua - Anterior != Consumo m3,
        debe fallar la invariante de medición sanitaria.
        """
        tampered_text = self.valid_invoice_text.replace("m3 actual: 4580.0", "m3 actual: 4620.0")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["water_meter_reading"])
        self.assertTrue(any("Medición de Agua" in err for err in res.validation_errors))

    def test_tampered_totals_subtotals_sum_fails_invariant(self):
        """
        Invariante 3: Si la suma de subtotales no cuadra con el Total Facturado,
        el sistema experto debe bloquear la ingesta.
        """
        tampered_text = self.valid_invoice_text.replace("TOTAL A PAGAR: $377.559,51", "TOTAL A PAGAR: $450.000,00")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["total_subtotals_sum"])
        self.assertTrue(any("Cuadratura de Totales" in err for err in res.validation_errors))

    def test_inverted_reading_dates_fails_invariant(self):
        """
        Invariante 4: Si fecha desde > fecha hasta, viola coherencia temporal.
        """
        tampered_text = self.valid_invoice_text.replace("Lectura Desde: 2026-08-14", "Lectura Desde: 2026-09-20")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["reading_dates_order"])

    def test_in_memory_pdf_creation_and_extraction(self):
        """
        Crea un PDF sintético en memoria con PyMuPDF, lo procesa con PDFBillExtractor
        y verifica que el texto extraído apruebe las invariantes.
        """
        try:
            import pymupdf  # type: ignore
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((50, 50), self.valid_invoice_text)
            pdf_bytes = doc.write()
            doc.close()

            # Procesar el flujo binario
            res = self.extractor.process_pdf_document(pdf_bytes, strict=True)
            self.assertTrue(res.is_valid)
            self.assertEqual(res.data["bloque_a_identificacion"]["periodo_facturado"], "09/2026")
        except ImportError:
            self.skipTest("PyMuPDF no está disponible en este entorno.")


    def test_declared_zero_consumption_with_meter_advance_fails_invariant(self):
        """
        Caso Crítico Anti-Fraude: Si la factura declara 0 kWh de consumo pero el medidor
        avanzó 428 kWh, el extractor NO debe silenciar la discrepancia y debe fallar la invariante.
        """
        tampered_text = self.valid_invoice_text.replace("Consumo Activo: 428.0 kWh", "Consumo Activo: 0.0 kWh")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["electric_meter_reading"])
        self.assertTrue(any("Medición Eléctrica" in err for err in res.validation_errors))

    def test_zero_previous_meter_reading_with_discrepancy_fails_invariant(self):
        """
        Caso de Borde: Lectura anterior 0.0 y lectura actual 100.0 con consumo declarado de 50 kWh
        debe fallar la invariante de medición eléctrica.
        """
        tampered_data = {
            "edesa_lectura_anterior": 0.0,
            "edesa_lectura_actual": 100.0,
            "edesa_consumo_kwh": 50.0
        }
        is_valid, invs, errors = self.extractor.validate_invariants(tampered_data)
        self.assertFalse(is_valid)
        self.assertFalse(invs["electric_meter_reading"])

    def test_backward_meter_roll_fails_invariant(self):
        """
        Invariante Física: Si la lectura actual es menor a la anterior (retroceso físico de medidor),
        el sistema debe rechazar la factura de inmediato.
        """
        tampered_text = self.valid_invoice_text.replace("Lectura Actual: 30224.0", "Lectura Actual: 25000.0")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["electric_meter_reading"])
        self.assertTrue(any("menor a Lectura Anterior" in err for err in res.validation_errors))

    def test_dot_separated_dates_parsed_correctly(self):
        """
        Verifica que fechas argentinas con puntos (ej. 14.08.2026 a 14.09.2026)
        sean parseadas y validadas cronológicamente sin falsos positivos.
        """
        dot_dates_text = self.valid_invoice_text.replace("2026-08-14", "14.08.2026").replace("2026-09-14", "14.09.2026")
        res = self.extractor.process_text_content(dot_dates_text, strict=True)
        self.assertTrue(res.is_valid)
        self.assertTrue(res.invariants_checked["reading_dates_order"])

    def test_zero_total_with_positive_subtotals_fails_invariant(self):
        """
        Invariante de Cuadratura: Si el total facturado es $0,00 pero existen subtotales positivos,
        debe rechazarse por incoherencia de liquidación.
        """
        tampered_text = self.valid_invoice_text.replace("TOTAL A PAGAR: $377.559,51", "TOTAL A PAGAR: $0,00")
        res = self.extractor.process_text_content(tampered_text, strict=False)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.invariants_checked["total_subtotals_sum"])

    def test_two_digit_year_period_normalization_05_26(self):
        """
        Verifica que períodos abreviados con año de 2 dígitos (ej. 05/26)
        se normalicen canónicamente al formato estándar '05/2026'.
        """
        text_05_26 = self.valid_invoice_text.replace("Período Facturado: 09/2026", "Período Facturado: 05/26")
        res = self.extractor.process_text_content(text_05_26, strict=False)
        self.assertEqual(res.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")

    def test_two_digit_year_period_normalization_5_26(self):
        """
        Verifica que períodos con mes de 1 dígito y año de 2 dígitos (ej. 5/26)
        se normalicen canónicamente a '05/2026' con padding de ceros.
        """
        text_5_26 = self.valid_invoice_text.replace("Período Facturado: 09/2026", "Período Facturado: 5/26")
        res = self.extractor.process_text_content(text_5_26, strict=False)
        self.assertEqual(res.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")

    def test_spanish_month_name_period_normalization(self):
        """
        Verifica que comprobantes que expresen el período en texto en español
        (ej. 'Período: Mayo 2026' o 'Mayo 26') se normalicen a '05/2026'.
        """
        text_mayo = self.valid_invoice_text.replace("Período Facturado: 09/2026", "Período Facturado: Mayo 2026")
        res = self.extractor.process_text_content(text_mayo, strict=False)
        self.assertEqual(res.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")

    def test_may_2026_canonical_invoice_passes_all_invariants(self):
        """
        Verifica que una boleta real de Mayo 2026 (05/2026) que antecede a Junio 2026
        apruebe el 100% de las invariantes físicas y de cuadratura contable.
        """
        may_text = """
        EMPRESA DISTRIBUIDORA DE ELECTRICIDAD DE SALTA S.A. (EDESA)
        AGUAS DEL NORTE (CoSAySa) - MUNICIPALIDAD DE LA CIUDAD DE SALTA
        
        NIS: 3024***
        Liquidación Nro: 0101-52060000
        Período Facturado: 05/2026
        Fecha de Emisión: 2026-05-20
        Fecha de Vencimiento: 2026-06-16
        
        SUMINISTRO ELÉCTRICO (EDESA):
        Lectura Desde: 2026-04-15
        Lectura Hasta: 2026-05-14
        Lectura Anterior: 27499.0
        Lectura Actual: 27874.0
        Consumo Activo: 375.0 kWh
        Subtotal EDESA: $165.400,00
        
        SERVICIO SANITARIO (AGUAS DEL NORTE):
        m3 anterior: 4415.0
        m3 actual: 4444.0
        Consumo Agua: 29.0 m3
        Subtotal Aguas: $105.000,00
        
        TRIBUTOS Y CONCESIONES MUNICIPALES:
        Subtotal Municipal: $39.000,00
        Subtotal LUSAL: $6.398,64
        
        TOTAL A PAGAR: $315.798,64
        """
        res = self.extractor.process_text_content(may_text, strict=True)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")
        self.assertEqual(res.data["bloque_a_identificacion"]["total_factura"], 315798.64)
        self.assertEqual(res.data["bloque_b_electricidad_edesa"]["energia_activa"]["consumo_kwh"], 375.0)
        self.assertEqual(res.data["bloque_c_agua_aguas_del_norte"]["lecturas_volumen"]["consumo_m3"], 29.0)

    def test_filename_fallback_when_period_missing_in_text(self):
        """Verifica que si el texto no indica explícitamente el período, se extraiga del nombre de archivo."""
        text_without_period = self.valid_invoice_text.replace("Período Facturado: 09/2026", "")
        # Fallback con archivo factura_05_2026.pdf
        res_05 = self.extractor.process_text_content(text_without_period, strict=False, filename="factura_05_2026.pdf")
        self.assertEqual(res_05.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")

        # Fallback con archivo boleta_05_26.pdf
        res_05_short = self.extractor.process_text_content(text_without_period, strict=False, filename="boleta_05_26.pdf")
        self.assertEqual(res_05_short.data["bloque_a_identificacion"]["periodo_facturado"], "05/2026")

    def test_pago_anterior_and_breakdowns_extraction(self):
        """Verifica la extracción de pago anterior registrado y desgloses de subsidio y alumbrado."""
        text_enriched = self.valid_invoice_text + """
        Pago anterior registrado: $285.400,00
        Subsidio Estado Nacional: $23.500,00
        Alumbrado Público: $10.600,00
        Cargo Fijo Agua: $58.500,00
        Consumo Variable Agua: $32.000,00
        """
        res = self.extractor.process_text_content(text_enriched, strict=False)
        self.assertEqual(res.data["bloque_a_identificacion"]["pago_anterior_registrado"], 285400.00)
        self.assertEqual(res.data["bloque_b_electricidad_edesa"]["desglose_costos"]["subsidio_estatal_declarado"], 23500.00)
        self.assertEqual(res.data["bloque_b_electricidad_edesa"]["desglose_costos"]["incidencia_energia_alumbrado_publico_monto"], 10600.00)
        self.assertEqual(res.data["bloque_c_agua_aguas_del_norte"]["desglose_costos"]["cargo_fijo"], 58500.00)
        self.assertEqual(res.data["bloque_c_agua_aguas_del_norte"]["desglose_costos"]["consumo_variable"], 32000.00)


if __name__ == "__main__":
    unittest.main()
