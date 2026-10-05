"""
Módulo de Glosario Conceptual y Ontología Normativa de Conceptos Facturados
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Ontología formal de conceptos de la factura unificada de Salta
(EDESA S.A. + Aguas del Norte S.A. + Municipalidad de Salta + ENRESP).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class BillingConcept:
    """Definición ontológica y regulatoria de un concepto de facturación."""
    code: str
    name: str
    issuer: str
    description: str
    legal_basis: str
    billed_amount_ars: float
    percentage_of_total: float
    percentage_of_subtotal: float
    is_split_eligible_enresp: bool
    mitigation_action: str
    category: str


# Monto total consolidado de la factura bajo análisis
TOTAL_INVOICE_ARS = 377559.51
SUBTOTAL_EDESA_ARS = 139850.89
SUBTOTAL_AGUA_ARS = 169262.42
SUBTOTAL_MUNICIPAL_ARS = 48670.80
SUBTOTAL_LUSAL_ARS = 7178.32


BILLING_CONCEPTS_ONTOLOGY: Dict[str, BillingConcept] = {
    "CARGO_FIJO_ELECTRICIDAD": BillingConcept(
        code="CARGO_FIJO_ELECTRICIDAD",
        name="Cargo Fijo Eléctrico Fraccionado (T1-R2)",
        issuer="EDESA S.A.",
        description="Cargo de disponibilidad del servicio independiente del volumen consumido. Prorrateado en dos tramos por actualización de cuadro tarifario.",
        legal_basis="Contrato de Concesión EDESA S.A. y Cuadro Tarifario aprobado por ENRESP",
        billed_amount_ars=9482.73,
        percentage_of_total=round((9482.73 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((9482.73 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="No modificable individualmente; inherente a la categoría T1-R2.",
        category="ELECTRIC"
    ),
    "ENERGIA_ACTIVA_BASE_200KWH": BillingConcept(
        code="ENERGIA_ACTIVA_BASE_200KWH",
        name="Energía Activa Bloque Base Subsidiado (hasta 200 kWh)",
        issuer="EDESA S.A.",
        description="Consumo de energía hasta el límite base subsidiado a tarifa preferencial ($187,0918/kWh).",
        legal_basis="Resolución Secretaría de Energía de la Nación (Esquema RASE N3) y ENRESP",
        billed_amount_ars=37418.36,
        percentage_of_total=round((37418.36 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((37418.36 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="Mantener consumo general por debajo del umbral base de 200 kWh mensuales.",
        category="ELECTRIC"
    ),
    "ENERGIA_ACTIVA_EXCEDENTE": BillingConcept(
        code="ENERGIA_ACTIVA_EXCEDENTE",
        name="Energía Activa Excedente (Tramos 1 y 2 - 228 kWh adicionales)",
        issuer="EDESA S.A.",
        description="Consumo por encima de los 200 kWh base. Facturado a tarifa plena con sobrecosto unitario de hasta +61,3% ($297,57 y $301,88 por kWh).",
        legal_basis="Resolución ENRESP Cuadro Tarifario Vigente y Tope de Subsidio RASE",
        billed_amount_ars=68678.16,
        percentage_of_total=round((68678.16 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((68678.16 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="Implementar gestión de carga y eficiencia energética en calefacción/climatización para no exceder los 200 kWh.",
        category="ELECTRIC"
    ),
    "IVA_ELECTRICIDAD_21": BillingConcept(
        code="IVA_ELECTRICIDAD_21",
        name="IVA Consumidor Final Eléctrico (21%)",
        issuer="ARCA / AFIP vía EDESA S.A.",
        description="Impuesto al Valor Agregado general aplicado sobre los conceptos gravados del suministro eléctrico residencial.",
        legal_basis="Ley Nacional 23.349 de Impuesto al Valor Agregado",
        billed_amount_ars=24271.64,
        percentage_of_total=round((24271.64 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((24271.64 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="Alícuota estándar legal para consumidor final; se reduce proporcionalmente al disminuir el consumo activo.",
        category="ELECTRIC"
    ),
    "INCIDENCIA_ENERGIA_ALUMBRADO_PUB": BillingConcept(
        code="INCIDENCIA_ENERGIA_ALUMBRADO_PUB",
        name="Incidencia Energía Alumbrado Público (27,986 kWh)",
        issuer="EDESA S.A. / Municipalidad de Salta",
        description="Cobro por kilovatios-hora físicos absorbidos por las luminarias públicas zonales ($450,1207/kWh). Integrado a la tarifa eléctrica.",
        legal_basis="Convenio Marco Municipalidad de Salta - EDESA S.A. y Ley Provincial de Electricidad",
        billed_amount_ars=12597.08,
        percentage_of_total=round((12597.08 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((12597.08 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="Concepto de energía física; no desdoblable independientemente del servicio eléctrico.",
        category="ELECTRIC"
    ),
    "SUBSIDIO_ESTATAL_RASE": BillingConcept(
        code="SUBSIDIO_ESTATAL_RASE",
        name="Subsidio Estado Nacional (Segmentación RASE Nivel 3)",
        issuer="Secretaría de Energía de la Nación",
        description="Aporte estatal compensatorio reflejado como bonificación sobre el costo de abastecimiento mayorista (MEM).",
        legal_basis="Decreto PEN 332/2022 y normas complementarias de subsidios energéticos",
        billed_amount_ars=-20185.95,
        percentage_of_total=round((-20185.95 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((-20185.95 / SUBTOTAL_EDESA_ARS) * 100, 2),
        is_split_eligible_enresp=False,
        mitigation_action="Verificar inscripción activa y actualizada en el Registro de Acceso a los Subsidios a la Energía (RASE).",
        category="REGULATORY"
    ),
    "CARGO_FIJO_AGUA": BillingConcept(
        code="CARGO_FIJO_AGUA",
        name="Cargo Fijo Agua y Cloacas (NO RESIDENCIAL 1)",
        issuer="Aguas del Norte S.A. / CoSAySa",
        description="Cargo de infraestructura y servicio básico facturado indebidamente bajo tarifa comercial/no residencial en inmueble catalogado como residencial por EDESA.",
        legal_basis="Régimen Tarifario CoSAySa y Marco Regulatorio Provincial de Aguas",
        billed_amount_ars=69404.04,
        percentage_of_total=round((69404.04 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((69404.04 / SUBTOTAL_AGUA_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Presentar reclamo urgente de recategorización ante Aguas del Norte y ENRESP para pasar a RESIDENCIAL (ahorro estimado superior al 35%).",
        category="WATER"
    ),
    "CONSUMO_VARIABLE_AGUA": BillingConcept(
        code="CONSUMO_VARIABLE_AGUA",
        name="Consumo Variable de Agua Medida (32 m³)",
        issuer="Aguas del Norte S.A. / CoSAySa",
        description="Volumen mensual medido (32,00 m³) liquidado a $1.450,441 por m³.",
        legal_basis="Medición por micromedidor homologado y escala por bloques de CoSAySa",
        billed_amount_ars=46414.10,
        percentage_of_total=round((46414.10 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((46414.10 / SUBTOTAL_AGUA_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Inspeccionar posibles pérdidas internas y solicitar recategorización residencial del metro cúbico.",
        category="WATER"
    ),
    "TASA_FISCALIZACION_ENRESP_AGUA": BillingConcept(
        code="TASA_FISCALIZACION_ENRESP_AGUA",
        name="Tasa de Fiscalización y Control ENRESP (2%)",
        issuer="ENRESP vía Aguas del Norte",
        description="Contribución obligatoria del 2% sobre la facturación de agua para financiamiento del ente de control.",
        legal_basis="Ley Provincial 6835 de Creación del ENRESP",
        billed_amount_ars=2316.36,
        percentage_of_total=round((2316.36 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((2316.36 / SUBTOTAL_AGUA_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Se reduce automáticamente al corregirse la base imponible del servicio sanitario.",
        category="WATER"
    ),
    "IVA_NO_CATEGORIZADO_AGUA_27": BillingConcept(
        code="IVA_NO_CATEGORIZADO_AGUA_27",
        name="IVA Sujeto No Categorizado (27% Agravado)",
        issuer="ARCA / AFIP vía Aguas del Norte",
        description="Penalidad tributaria con alícuota agravada del 27% (en lugar del 21%) por no contar con inscripción o constancia fiscal activa en el padrón de la concesionaria.",
        legal_basis="Resolución General AFIP/ARCA 2126 y Ley 23.349 de IVA",
        billed_amount_ars=31270.90,
        percentage_of_total=round((31270.90 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((31270.90 / SUBTOTAL_AGUA_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Presentar de inmediato constancia de CUIT/DNI ante Aguas del Norte para empadronarse como Consumidor Final (21%).",
        category="WATER"
    ),
    "PERCEPCION_IVA_NO_CATEG_13_5": BillingConcept(
        code="PERCEPCION_IVA_NO_CATEG_13_5",
        name="Percepción IVA Sujeto No Categorizado (13,5% Adicional)",
        issuer="ARCA / AFIP vía Aguas del Norte",
        description="Régimen de percepción fiscal del 13,5% que se suma al 27% de IVA, generando una carga impositiva agregada récord del 40,5% ($51.127,92).",
        legal_basis="Resolución General AFIP/ARCA 2126 (Régimen de Percepción a Sujetos No Categorizados)",
        billed_amount_ars=19857.02,
        percentage_of_total=round((19857.02 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((19857.02 / SUBTOTAL_AGUA_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Eliminación del 100% de esta percepción ($19.857,02 de ahorro mensual directo) acreditando condición de Consumidor Final.",
        category="WATER"
    ),
    "TASA_MUNICIPAL_SALTA": BillingConcept(
        code="TASA_MUNICIPAL_SALTA",
        name="Tasa General de Inmuebles (TGI Municipal)",
        issuer="Municipalidad de la Ciudad de Salta",
        description="Tasa tributaria comunal por servicios de alumbrado, barrido, limpieza y conservación del espacio público comunal.",
        legal_basis="Código Tributario Municipal de la Ciudad de Salta y Ordenanza Tarifaria Anual",
        billed_amount_ars=44614.90,
        percentage_of_total=round((44614.90 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((44614.90 / SUBTOTAL_MUNICIPAL_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Concepto municipal desdoblable conforme a Res. ENRESP 1590/24 si no se puede afrontar el pago global.",
        category="MUNICIPAL"
    ),
    "PROTECCION_BIENES_Y_PERSONAS": BillingConcept(
        code="PROTECCION_BIENES_Y_PERSONAS",
        name="Contribución Protección de Bienes y Personas",
        issuer="Municipalidad de Salta",
        description="Fondo solidario municipal de defensa civil, emergencias y cuerpos de bomberos.",
        legal_basis="Ordenanza Municipal de la Ciudad de Salta",
        billed_amount_ars=1216.77,
        percentage_of_total=round((1216.77 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((1216.77 / SUBTOTAL_MUNICIPAL_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Concepto municipal desdoblable facultativo bajo Res. ENRESP 1590/24.",
        category="MUNICIPAL"
    ),
    "IMPUESTO_INMOBILIARIO_MUNICIPAL": BillingConcept(
        code="IMPUESTO_INMOBILIARIO_MUNICIPAL",
        name="Impuesto Inmobiliario Urbano",
        issuer="Municipalidad de Salta / DGR",
        description="Tributo directo sobre la propiedad inmueble según valuación fiscal catastral.",
        legal_basis="Código Fiscal de la Provincia de Salta y Convenio de Recaudación Municipal",
        billed_amount_ars=2839.13,
        percentage_of_total=round((2839.13 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((2839.13 / SUBTOTAL_MUNICIPAL_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Concepto desdoblable; puede abonarse en sede municipal o solicitar exención si corresponde por condición socioeconómica.",
        category="MUNICIPAL"
    ),
    "MANTENIMIENTO_ALUMBRADO_LUSAL": BillingConcept(
        code="MANTENIMIENTO_ALUMBRADO_LUSAL",
        name="Canon Mantenimiento Alumbrado Público LUSAL UTE (Tarifa C1)",
        issuer="LUSAL UTE (Concesión Municipalidad de Salta)",
        description="Canon mensual privado a la empresa concesionaria por reposición de artefactos y cuadrillas de mantenimiento de luminarias de Salta.",
        legal_basis="Contrato de Concesión Integral del Alumbrado Público y Ordenanza Municipal",
        billed_amount_ars=7178.32,
        percentage_of_total=round((7178.32 / TOTAL_INVOICE_ARS) * 100, 2),
        percentage_of_subtotal=round((7178.32 / SUBTOTAL_LUSAL_ARS) * 100, 2),
        is_split_eligible_enresp=True,
        mitigation_action="Concepto tributario accesorio; desdoblable según Res. ENRESP 1590/24 sin afectar el suministro eléctrico de la vivienda.",
        category="MUNICIPAL"
    )
}


class ConceptGlossary:
    """Módulo de consulta semántica y ontológica de conceptos de facturación."""

    @staticmethod
    def get_concept(code: str) -> Optional[BillingConcept]:
        """Obtiene la ficha conceptual de un ítem facturado."""
        return BILLING_CONCEPTS_ONTOLOGY.get(code)

    @staticmethod
    def get_all_concepts() -> List[BillingConcept]:
        """Retorna todos los conceptos de la base de conocimiento ontológica."""
        return list(BILLING_CONCEPTS_ONTOLOGY.values())

    @staticmethod
    def get_split_eligible_concepts() -> List[BillingConcept]:
        """Retorna aquellos conceptos que son legalmente desdoblables según Res. ENRESP 1590/24."""
        return [c for c in BILLING_CONCEPTS_ONTOLOGY.values() if c.is_split_eligible_enresp]

    @staticmethod
    def calculate_split_totals() -> Dict[str, float]:
        """Calcula el total desdoblable (no eléctrico) vs total eléctrico obligatorio."""
        total_desdoblable = sum(
            c.billed_amount_ars for c in BILLING_CONCEPTS_ONTOLOGY.values() if c.is_split_eligible_enresp
        )
        total_electrico_esencial = TOTAL_INVOICE_ARS - total_desdoblable
        return {
            "total_factura": TOTAL_INVOICE_ARS,
            "total_electrico_esencial": round(total_electrico_esencial, 2),
            "total_desdoblable": round(total_desdoblable, 2),
            "porcentaje_desdoblable": round((total_desdoblable / TOTAL_INVOICE_ARS) * 100, 2),
            "porcentaje_electrico": round((total_electrico_esencial / TOTAL_INVOICE_ARS) * 100, 2)
        }
