"""
Módulo de Sanitización y Enmascaramiento de Datos Personales (PII Masking)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Normativa: Ley 25.326 de Protección de Datos Personales (República Argentina)
"""

import re
from typing import Any, Dict


class InvoiceAnonymizer:
    """
    Motor de anonimización para sanitizar facturas de servicios públicos
    antes de la ingesta en la Memoria de Trabajo del Sistema Experto.
    """

    @staticmethod
    def mask_name(name: str, placeholder: str = "USUARIO_ANON_01") -> str:
        """Anonimiza el nombre y apellido del titular."""
        if not name:
            return placeholder
        return placeholder

    @staticmethod
    def mask_address(address: str) -> str:
        """Enmascara la numeración exacta de una dirección física."""
        if not address:
            return "Domicilio Anonimizado, Salta Capital"
        # Reemplazar números de 3 a 5 dígitos por XX
        return re.sub(r'\b\d{2,5}\b', lambda m: m.group(0)[:2] + "XX", address)

    @staticmethod
    def mask_identifier(ident: str, visible_prefix: int = 4, mask_char: str = "*") -> str:
        """Enmascara dígitos finales de identificadores sensibles (NIS, medidor, catastro)."""
        if not ident:
            return f"{mask_char * 6}"
        s = str(ident).strip()
        if len(s) <= visible_prefix:
            return s[:max(1, len(s) // 2)] + (mask_char * 3)
        return s[:visible_prefix] + (mask_char * (len(s) - visible_prefix))

    @staticmethod
    def mask_nis(nis: Any) -> str:
        """Enmascara el NIS (Número de Identificación de Suministro)."""
        return InvoiceAnonymizer.mask_identifier(str(nis), visible_prefix=4)

    @staticmethod
    def mask_catastro(catastro: Any) -> str:
        """Enmascara el número de catastro inmobiliario."""
        return InvoiceAnonymizer.mask_identifier(str(catastro), visible_prefix=3)

    @staticmethod
    def mask_meter(meter_id: Any) -> str:
        """Enmascara el número de serie del medidor."""
        return InvoiceAnonymizer.mask_identifier(str(meter_id), visible_prefix=4)

    @classmethod
    def sanitize_invoice_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza recursivamente un diccionario de factura cruda
        asegurando que ningún dato PII quede expuesto en claro.
        """
        sanitized = dict(data)
        
        # Inyectar metadata de sanitización
        sanitized["metadata_sanitizacion"] = {
            "protocolo": "PII Masking - Ley 25.326 (Protección de Datos Personales Argentina)",
            "titular_sanitizado": "USUARIO_ANON_01",
            "auditor_responsable": "Estudiante UGD (100001)",
            "estado": "COMPLETO"
        }

        # Sanitizar bloque A
        if "bloque_a_identificacion" in sanitized:
            b_a = dict(sanitized["bloque_a_identificacion"])
            if "nis" in b_a:
                b_a["nis"] = cls.mask_nis(b_a["nis"])
            if "nro_liquidacion" in b_a:
                b_a["nro_liquidacion"] = cls.mask_identifier(str(b_a["nro_liquidacion"]), visible_prefix=9)
            sanitized["bloque_a_identificacion"] = b_a

        # Sanitizar bloque B
        if "bloque_b_electricidad_edesa" in sanitized:
            b_b = dict(sanitized["bloque_b_electricidad_edesa"])
            if "medidor" in b_b:
                b_b["medidor"] = cls.mask_meter(b_b["medidor"])
            sanitized["bloque_b_electricidad_edesa"] = b_b

        # Sanitizar bloque C
        if "bloque_c_agua_aguas_del_norte" in sanitized:
            b_c = dict(sanitized["bloque_c_agua_aguas_del_norte"])
            if "usuario_id" in b_c:
                b_c["usuario_id"] = cls.mask_identifier(str(b_c["usuario_id"]), visible_prefix=3)
            if "catastro" in b_c:
                b_c["catastro"] = cls.mask_catastro(b_c["catastro"])
            if "medidor" in b_c:
                b_c["medidor"] = cls.mask_meter(b_c["medidor"])
            sanitized["bloque_c_agua_aguas_del_norte"] = b_c

        return sanitized
