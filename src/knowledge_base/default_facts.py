"""
Módulo de Carga y Extracción de Hechos Estructurados (Default Facts)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Extrae y tipifica los hechos iniciales de la factura sanitizada de Salta
para ser inyectados en la Memoria de Trabajo del Sistema Experto.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..domain.fact_model import (
    Fact,
    ElectricFact,
    WaterFact,
    MunicipalFact,
    RegulatoryFact,
    FactCategory
)


def load_default_facts_from_json(json_path: Optional[Path] = None, period: Optional[str] = None) -> List[Fact]:
    """
    Carga el conjunto de hechos iniciales a partir del archivo JSON sanitizado.
    Si se especifica `period` (ej. '06/2026'), busca la boleta correspondiente a ese mes.
    Si no se pasa ruta ni período, busca automáticamente en data/factura_sanitizada.json.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent

    if period:
        sanitized_period = period.replace("/", "_")
        period_path = base_dir / "data" / f"factura_{sanitized_period}.json"
        if period_path.exists():
            json_path = period_path
        else:
            # Buscar en facturas_historico.json
            hist_path = base_dir / "data" / "facturas_historico.json"
            if hist_path.exists():
                with open(hist_path, "r", encoding="utf-8") as f:
                    hist_data = json.load(f)
                period_dict = hist_data.get("facturas_por_periodo", {}).get(period)
                if period_dict:
                    return extract_facts_from_dict(period_dict)

    if json_path is None:
        json_path = base_dir / "data" / "factura_sanitizada.json"

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return extract_facts_from_dict(data)
    else:
        # Fallback autónomo en memoria si el archivo no existe en el disco
        return get_builtin_default_facts()


def load_facts_for_period(period: str) -> List[Fact]:
    """Atajo para cargar los hechos atómicos correspondientes a un período específico."""
    return load_default_facts_from_json(period=period)


def load_all_historical_invoices(data_dir: Optional[Path] = None) -> List[dict]:
    """Carga la lista completa de las 4 facturas históricas estructuradas."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"

    hist_file = data_dir / "facturas_historico.json"
    if hist_file.exists():
        with open(hist_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "facturas" in data:
                return data["facturas"]

    # Fallback a archivos individuales
    invoices = []
    for p in ["06_2026", "07_2026", "08_2026", "09_2026"]:
        p_file = data_dir / f"factura_{p}.json"
        if p_file.exists():
            with open(p_file, "r", encoding="utf-8") as f:
                invoices.append(json.load(f))

    if not invoices:
        single_file = data_dir / "factura_sanitizada.json"
        if single_file.exists():
            with open(single_file, "r", encoding="utf-8") as f:
                invoices.append(json.load(f))

    return invoices


def extract_facts_from_dict(data: dict) -> List[Fact]:
    """Construye la lista tipada de hechos atómicos desde un diccionario."""
    facts: List[Fact] = []

    # Bloque A: Identificación y Estado Administrativo
    b_a = data.get("bloque_a_identificacion", {})
    facts.append(Fact(
        name="factura_periodo",
        value=b_a.get("periodo_facturado", "09/2026"),
        source="INVOICE_HEADER",
        description="Período mensual facturado"
    ))
    facts.append(Fact(
        name="factura_monto_total",
        value=float(b_a.get("total_factura", 377559.51)),
        unit="ARS",
        source="INVOICE_HEADER",
        description="Monto consolidado total de la boleta unificada"
    ))
    facts.append(Fact(
        name="factura_deuda_anterior",
        value=float(b_a.get("deuda_vencida_pendiente", 0.0)),
        unit="ARS",
        source="INVOICE_HEADER",
        description="Saldo adeudado previo exigible"
    ))
    facts.append(Fact(
        name="factura_dias_hasta_corte",
        value=14,  # Entre vto 16/10 y corte 30/10
        unit="dias",
        source="INVOICE_HEADER",
        description="Plazo de gracia hasta aviso de suspensión"
    ))

    # Bloque B: Electricidad (EDESA)
    b_b = data.get("bloque_b_electricidad_edesa", {})
    desg_elec = b_b.get("desglose_costos", {})
    e_activa = b_b.get("energia_activa", {})
    e_reactiva = b_b.get("energia_reactiva", {})
    
    facts.append(ElectricFact(
        name="electricidad_categoria",
        value=b_b.get("categoria_tarifaria", "T1-R2-SEF"),
        description="Categoría tarifaria en EDESA"
    ))
    facts.append(ElectricFact(
        name="electricidad_tipo_inmueble",
        value=b_b.get("tipo_inmueble_declarado", "RESIDENCIAL"),
        description="Tipo de inmueble clasificado por la distribuidora eléctrica"
    ))
    facts.append(ElectricFact(
        name="electricidad_potencia_contratada_kw",
        value=float(b_b.get("potencia_contratada_kw", 2.0)),
        unit="kW",
        description="Potencia monofásica contratada"
    ))
    facts.append(ElectricFact(
        name="electricidad_consumo_activo_kwh",
        value=float(e_activa.get("consumo_kwh", 428.0)),
        unit="kWh",
        description="Consumo de energía activa del mes"
    ))
    facts.append(ElectricFact(
        name="electricidad_consumo_reactivo_kvarh",
        value=float(e_reactiva.get("consumo_kvarh", 117.0)),
        unit="kvarh",
        description="Consumo de energía reactiva del mes"
    ))
    facts.append(ElectricFact(
        name="electricidad_factor_potencia_cos_phi",
        value=float(b_b.get("factor_potencia_cos_phi", 0.9644)),
        description="Factor de potencia medido cos(phi)"
    ))
    facts.append(ElectricFact(
        name="electricidad_cargo_fijo_ars",
        value=float(desg_elec.get("cargo_fijo_total", 9482.73)),
        unit="ARS",
        description="Cargo fijo eléctrico total del período"
    ))
    facts.append(ElectricFact(
        name="electricidad_cargo_fijo_fraccionado",
        value=True,
        description="Indica si hubo prorrateo por dos cuadros tarifarios distintos"
    ))
    facts.append(ElectricFact(
        name="electricidad_consumo_excedente_kwh",
        value=float(e_activa.get("consumo_kwh", 428.0) - 200.0),
        unit="kWh",
        description="Kilovatios-hora consumidos por encima del bloque base subsidiado (200 kWh)"
    ))
    facts.append(ElectricFact(
        name="electricidad_subtotal_ars",
        value=float(desg_elec.get("subtotal_edesa_neto", 139850.89)),
        unit="ARS",
        description="Subtotal de la factura correspondiente a EDESA S.A."
    ))
    facts.append(ElectricFact(
        name="electricidad_incidencia_alumbrado_ars",
        value=float(desg_elec.get("incidencia_energia_alumbrado_publico_monto", 12597.08)),
        unit="ARS",
        description="Consumo físico vial de alumbrado facturado por EDESA"
    ))
    facts.append(ElectricFact(
        name="electricidad_subsidio_estatal_ars",
        value=float(desg_elec.get("subsidio_estatal_declarado", 20185.95)),
        unit="ARS",
        description="Subsidio RASE asignado en la factura"
    ))

    # Bloque C: Agua y Saneamiento (Aguas del Norte)
    b_c = data.get("bloque_c_agua_aguas_del_norte", {})
    desg_agua = b_c.get("desglose_costos", {})
    lect_vol = b_c.get("lecturas_volumen", {})

    facts.append(WaterFact(
        name="agua_categoria_uso",
        value=b_c.get("categoria_uso", "NO RESIDENCIAL 1"),
        description="Categoría de uso asignada por Aguas del Norte"
    ))
    facts.append(WaterFact(
        name="agua_tipo_inmueble",
        value=b_c.get("tipo_inmueble_declarado", "NO_RESIDENCIAL"),
        description="Clasificación de inmueble asignada por Aguas del Norte"
    ))
    facts.append(WaterFact(
        name="agua_condicion_fiscal",
        value="SUJETO_NO_CATEGORIZADO" if "No Categorizado" in b_c.get("condicion_fiscal", "") else "CONSUMIDOR_FINAL",
        description="Condición tributaria registrada ante Aguas del Norte"
    ))
    facts.append(WaterFact(
        name="agua_consumo_volumen_m3",
        value=float(lect_vol.get("consumo_m3", 32.0)),
        unit="m3",
        description="Volumen mensual medido de agua consumida"
    ))
    facts.append(WaterFact(
        name="agua_alicuota_iva_pct",
        value=27.0,
        unit="%",
        description="Alícuota de IVA liquidada en el servicio de agua"
    ))
    facts.append(WaterFact(
        name="agua_alicuota_percepcion_iva_pct",
        value=13.5,
        unit="%",
        description="Alícuota de percepción de IVA RG 2126 aplicada"
    ))
    facts.append(WaterFact(
        name="agua_cargo_fijo_ars",
        value=float(desg_agua.get("cargo_fijo", 69404.04)),
        unit="ARS",
        description="Cargo fijo por servicio de agua y cloacas"
    ))
    facts.append(WaterFact(
        name="agua_consumo_variable_ars",
        value=float(desg_agua.get("consumo_variable", 46414.10)),
        unit="ARS",
        description="Importe por metros cúbicos medidos"
    ))
    facts.append(WaterFact(
        name="agua_tasa_enresp_ars",
        value=float(desg_agua.get("tasa_fiscalizacion_enresp_2", 2316.36)),
        unit="ARS",
        description="Tasa de control ENRESP del 2% sobre agua"
    ))
    facts.append(WaterFact(
        name="agua_subtotal_ars",
        value=float(desg_agua.get("subtotal_aguas_del_norte", 169262.42)),
        unit="ARS",
        description="Subtotal de la factura de Aguas del Norte"
    ))
    facts.append(WaterFact(
        name="agua_iva_no_categorizado_ars",
        value=float(desg_agua.get("iva_no_categorizado_27", 31270.90)),
        unit="ARS",
        description="Monto liquidado por IVA 27% en Aguas del Norte"
    ))
    facts.append(WaterFact(
        name="agua_percepcion_iva_ars",
        value=float(desg_agua.get("percepcion_iva_no_categorizado_13_5", 19857.02)),
        unit="ARS",
        description="Monto liquidado por Percepción IVA RG 2126 13.5% en Aguas del Norte"
    ))

    # Bloque D: Municipalidad y Terceros Concesionarios
    b_d = data.get("bloque_d_tributos_municipales_y_concesiones", {})
    muni = b_d.get("municipalidad_de_salta", {})
    lusal = b_d.get("lusal_ute", {})

    facts.append(MunicipalFact(
        name="municipal_tasa_inmuebles_ars",
        value=float(muni.get("tasa_municipal", 44614.90)),
        unit="ARS",
        description="Tasa General de Inmuebles Municipal de Salta"
    ))
    facts.append(MunicipalFact(
        name="municipal_impuesto_inmobiliario_ars",
        value=float(muni.get("impuesto_inmobiliario", 2839.13)),
        unit="ARS",
        description="Impuesto Inmobiliario descentralizado"
    ))
    facts.append(MunicipalFact(
        name="municipal_subtotal_ars",
        value=float(muni.get("subtotal_municipal", 48670.80)),
        unit="ARS",
        description="Subtotal de tributos de la Municipalidad de Salta"
    ))
    facts.append(MunicipalFact(
        name="alumbrado_canon_lusal_ars",
        value=float(lusal.get("subtotal_lusal", 7178.32)),
        unit="ARS",
        description="Canon privado de mantenimiento a LUSAL UTE"
    ))

    # Bloque E: Regulatorio ENRESP
    facts.append(RegulatoryFact(
        name="enresp_resolucion_desdoblamiento",
        value="1590/24",
        description="Resolución de desdoblamiento facultativo de boleta unificada"
    ))
    facts.append(RegulatoryFact(
        name="enresp_derecho_desdoblamiento_normativo",
        value=True,
        description="Derecho legal vigente del usuario a desdoblar la boleta"
    ))

    return facts


def get_builtin_default_facts() -> List[Fact]:
    """Genera directamente los hechos en memoria con los valores canónicos auditados."""
    # Simula la extracción para cuando se ejecuta de modo independiente
    from ..domain.fact_model import FactCategory
    sample_data = {
        "bloque_a_identificacion": {
            "periodo_facturado": "09/2026",
            "total_factura": 377559.51,
            "deuda_vencida_pendiente": 0.0
        },
        "bloque_b_electricidad_edesa": {
            "categoria_tarifaria": "T1-R2-SEF",
            "tipo_inmueble_declarado": "RESIDENCIAL",
            "potencia_contratada_kw": 2.0,
            "factor_potencia_cos_phi": 0.9644,
            "energia_activa": {"consumo_kwh": 428.0},
            "energia_reactiva": {"consumo_kvarh": 117.0},
            "desglose_costos": {
                "cargo_fijo_total": 9482.73,
                "subtotal_edesa_neto": 139850.89,
                "incidencia_energia_alumbrado_publico_monto": 12597.08,
                "subsidio_estatal_declarado": 20185.95
            }
        },
        "bloque_c_agua_aguas_del_norte": {
            "categoria_uso": "NO RESIDENCIAL 1",
            "tipo_inmueble_declarado": "NO_RESIDENCIAL",
            "condicion_fiscal": "IVA Sujeto No Categorizado",
            "lecturas_volumen": {"consumo_m3": 32.0},
            "desglose_costos": {
                "cargo_fijo": 69404.04,
                "consumo_variable": 46414.10,
                "tasa_fiscalizacion_enresp_2": 2316.36,
                "iva_no_categorizado_27": 31270.90,
                "percepcion_iva_no_categorizado_13_5": 19857.02,
                "subtotal_aguas_del_norte": 169262.42
            }
        },
        "bloque_d_tributos_municipales_y_concesiones": {
            "municipalidad_de_salta": {
                "tasa_municipal": 44614.90,
                "impuesto_inmobiliario": 2839.13,
                "subtotal_municipal": 48670.80
            },
            "lusal_ute": {
                "subtotal_lusal": 7178.32
            }
        }
    }
    return extract_facts_from_dict(sample_data)
