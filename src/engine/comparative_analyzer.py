"""
Módulo de Análisis Comparativo Multimes y Descomposición Económica de Variaciones
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Descompone formalmente la variación del gasto entre períodos consecutivos:
1. Efecto Volumen (ΔQ × P_base): Variación por mayor o menor consumo físico (kWh o m³).
2. Efecto Tarifa / Inflación (Q_actual × ΔP + ΔCargos Fijos): Variación por incrementos en el cuadro tarifario o tributos.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import math
from ..persistence.history_store import parse_period_key


@dataclass
class ServiceVarianceBreakdown:
    """Desglose formal de la variación de un servicio público entre dos períodos."""
    service_name: str
    period_prev: str
    period_curr: str
    amount_prev: float
    amount_curr: float
    delta_amount: float
    pct_change: float
    # Descomposición económica
    volume_prev: float
    volume_curr: float
    delta_volume: float
    pct_volume_change: float
    unit_price_prev: float
    unit_price_curr: float
    delta_unit_price: float
    pct_price_change: float
    volume_effect_ars: float
    tariff_effect_ars: float
    fixed_charge_effect_ars: float
    tax_or_other_effect_ars: float
    primary_driver: str  # "VOLUMEN", "TARIFA_PRECIO", "ESTABLE"
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PeriodComparison:
    """Comparación económica integral entre dos facturas consecutivas."""
    period_prev: str
    period_curr: str
    total_prev: float
    total_curr: float
    delta_total: float
    pct_change_total: float
    # Desgloses por servicio
    edesa: ServiceVarianceBreakdown
    aguas: ServiceVarianceBreakdown
    municipal: Dict[str, Any]
    lusal: Dict[str, Any]
    # Consolidado macro
    total_volume_effect_ars: float
    total_tariff_and_inflation_effect_ars: float
    pct_volume_driver: float
    pct_tariff_driver: float
    macro_driver: str  # "PICO_INVIERNO_VOLUMEN", "CONTRACCION_POST_PICO", "AJUSTE_TARIFARIO", etc.
    summary_report: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ComparativeAnalyzer:
    """
    Analizador econométrico y de auditoría de servicios públicos.
    Compara series temporales de facturas y realiza descomposición de varianzas.
    """

    def __init__(self, invoices: Optional[List[dict]] = None):
        self.invoices_by_period: Dict[str, dict] = {}
        self.ordered_periods: List[str] = []
        if invoices:
            self.load_invoices(invoices)

    def load_invoices(self, invoices: List[dict]) -> None:
        """Carga y ordena cronológicamente la colección de facturas."""
        self.invoices_by_period.clear()
        for inv in invoices:
            period = inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "")
            if period:
                self.invoices_by_period[period] = inv

        self.ordered_periods = sorted(self.invoices_by_period.keys(), key=parse_period_key)

    def decompose_electric_variance(self, prev_inv: dict, curr_inv: dict) -> ServiceVarianceBreakdown:
        """
        Descompone la variación en el servicio eléctrico (EDESA) entre dos períodos.
        Fórmula formal de descomposición:
          ΔCosto_Variable = (Q_t - Q_{t-1}) × P_{t-1} + Q_t × (P_t - P_{t-1})
        """
        p_prev = prev_inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "T-1")
        p_curr = curr_inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "T")

        b_b_prev = prev_inv.get("bloque_b_electricidad_edesa", {})
        b_b_curr = curr_inv.get("bloque_b_electricidad_edesa", {})

        desg_prev = b_b_prev.get("desglose_costos", {})
        desg_curr = b_b_curr.get("desglose_costos", {})

        # Subtotales con alumbrado de EDESA
        tot_prev = float(desg_prev.get("subtotal_con_alumbrado", 
                    desg_prev.get("subtotal_edesa_neto", 0.0) + desg_prev.get("incidencia_energia_alumbrado_publico_monto", 0.0)))
        tot_curr = float(desg_curr.get("subtotal_con_alumbrado", 
                    desg_curr.get("subtotal_edesa_neto", 0.0) + desg_curr.get("incidencia_energia_alumbrado_publico_monto", 0.0)))

        delta_tot = tot_curr - tot_prev
        pct_tot = (delta_tot / tot_prev * 100.0) if tot_prev > 0 else 0.0

        q_prev = float(b_b_prev.get("energia_activa", {}).get("consumo_kwh", 0.0))
        q_curr = float(b_b_curr.get("energia_activa", {}).get("consumo_kwh", 0.0))
        delta_q = q_curr - q_prev
        pct_q = (delta_q / q_prev * 100.0) if q_prev > 0 else 0.0

        cf_prev = float(desg_prev.get("cargo_fijo_total", 0.0))
        cf_curr = float(desg_curr.get("cargo_fijo_total", 0.0))
        delta_cf = cf_curr - cf_prev

        alum_prev = float(desg_prev.get("incidencia_energia_alumbrado_publico_monto", 0.0))
        alum_curr = float(desg_curr.get("incidencia_energia_alumbrado_publico_monto", 0.0))
        delta_alum = alum_curr - alum_prev

        # Costo variable puro = neto sin cargo fijo
        var_cost_prev = max(0.0, float(desg_prev.get("subtotal_edesa_neto", 0.0)) - cf_prev)
        var_cost_curr = max(0.0, float(desg_curr.get("subtotal_edesa_neto", 0.0)) - cf_curr)

        p_unit_prev = (var_cost_prev / q_prev) if q_prev > 0 else 0.0
        p_unit_curr = (var_cost_curr / q_curr) if q_curr > 0 else 0.0
        delta_p = p_unit_curr - p_unit_prev
        pct_p = (delta_p / p_unit_prev * 100.0) if p_unit_prev > 0 else 0.0

        # Descomposición exacta
        if q_prev > 0:
            volume_effect = delta_q * p_unit_prev
            tariff_effect = q_curr * delta_p
        else:
            volume_effect = delta_q * p_unit_curr
            tariff_effect = 0.0
        fixed_charge_effect = delta_cf
        tax_other_effect = delta_alum

        if abs(volume_effect) > abs(tariff_effect + fixed_charge_effect):
            driver = "VOLUMEN"
            expl = f"Variación impulsada principalmente por consumo físico (Δ {delta_q:+.0f} kWh, {pct_q:+.1f}%)."
        else:
            driver = "TARIFA_PRECIO"
            expl = f"Variación explicada predominantemente por actualización tarifaria y cargos fijos (Δ $/kWh: {delta_p:+.2f})."

        return ServiceVarianceBreakdown(
            service_name="Electricidad (EDESA)",
            period_prev=p_prev,
            period_curr=p_curr,
            amount_prev=round(tot_prev, 2),
            amount_curr=round(tot_curr, 2),
            delta_amount=round(delta_tot, 2),
            pct_change=round(pct_tot, 2),
            volume_prev=round(q_prev, 1),
            volume_curr=round(q_curr, 1),
            delta_volume=round(delta_q, 1),
            pct_volume_change=round(pct_q, 2),
            unit_price_prev=round(p_unit_prev, 3),
            unit_price_curr=round(p_unit_curr, 3),
            delta_unit_price=round(delta_p, 3),
            pct_price_change=round(pct_p, 2),
            volume_effect_ars=round(volume_effect, 2),
            tariff_effect_ars=round(tariff_effect, 2),
            fixed_charge_effect_ars=round(fixed_charge_effect, 2),
            tax_or_other_effect_ars=round(tax_other_effect, 2),
            primary_driver=driver,
            explanation=expl
        )

    def decompose_water_variance(self, prev_inv: dict, curr_inv: dict) -> ServiceVarianceBreakdown:
        """
        Descompone la variación en el servicio sanitario (Aguas del Norte) entre dos períodos.
        """
        p_prev = prev_inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "T-1")
        p_curr = curr_inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "T")

        b_c_prev = prev_inv.get("bloque_c_agua_aguas_del_norte", {})
        b_c_curr = curr_inv.get("bloque_c_agua_aguas_del_norte", {})

        desg_prev = b_c_prev.get("desglose_costos", {})
        desg_curr = b_c_curr.get("desglose_costos", {})

        tot_prev = float(desg_prev.get("subtotal_aguas_del_norte", 0.0))
        tot_curr = float(desg_curr.get("subtotal_aguas_del_norte", 0.0))
        delta_tot = tot_curr - tot_prev
        pct_tot = (delta_tot / tot_prev * 100.0) if tot_prev > 0 else 0.0

        q_prev = float(b_c_prev.get("lecturas_volumen", {}).get("consumo_m3", 0.0))
        q_curr = float(b_c_curr.get("lecturas_volumen", {}).get("consumo_m3", 0.0))
        delta_q = q_curr - q_prev
        pct_q = (delta_q / q_prev * 100.0) if q_prev > 0 else 0.0

        cf_prev = float(desg_prev.get("cargo_fijo", 0.0))
        cf_curr = float(desg_curr.get("cargo_fijo", 0.0))
        delta_cf = cf_curr - cf_prev

        var_prev = float(desg_prev.get("consumo_variable", 0.0))
        var_curr = float(desg_curr.get("consumo_variable", 0.0))

        p_unit_prev = (var_prev / q_prev) if q_prev > 0 else 0.0
        p_unit_curr = (var_curr / q_curr) if q_curr > 0 else 0.0
        delta_p = p_unit_curr - p_unit_prev
        pct_p = (delta_p / p_unit_prev * 100.0) if p_unit_prev > 0 else 0.0

        taxes_prev = tot_prev - cf_prev - var_prev
        taxes_curr = tot_curr - cf_curr - var_curr
        delta_taxes = taxes_curr - taxes_prev

        if q_prev > 0:
            volume_effect = delta_q * p_unit_prev
            tariff_effect = q_curr * delta_p
        else:
            volume_effect = delta_q * p_unit_curr
            tariff_effect = 0.0
        fixed_charge_effect = delta_cf
        tax_other_effect = delta_taxes

        if abs(volume_effect) > abs(tariff_effect + fixed_charge_effect):
            driver = "VOLUMEN"
            expl = f"Variación impulsada por metros cúbicos medidos (Δ {delta_q:+.1f} m³, {pct_q:+.1f}%)."
        else:
            driver = "TARIFA_PRECIO"
            expl = f"Variación explicada por aumentos en cargo fijo tarifario (+${delta_cf:,.2f}) e impuestos asociados."

        return ServiceVarianceBreakdown(
            service_name="Agua y Saneamiento (Aguas del Norte)",
            period_prev=p_prev,
            period_curr=p_curr,
            amount_prev=round(tot_prev, 2),
            amount_curr=round(tot_curr, 2),
            delta_amount=round(delta_tot, 2),
            pct_change=round(pct_tot, 2),
            volume_prev=round(q_prev, 1),
            volume_curr=round(q_curr, 1),
            delta_volume=round(delta_q, 1),
            pct_volume_change=round(pct_q, 2),
            unit_price_prev=round(p_unit_prev, 3),
            unit_price_curr=round(p_unit_curr, 3),
            delta_unit_price=round(delta_p, 3),
            pct_price_change=round(pct_p, 2),
            volume_effect_ars=round(volume_effect, 2),
            tariff_effect_ars=round(tariff_effect, 2),
            fixed_charge_effect_ars=round(fixed_charge_effect, 2),
            tax_or_other_effect_ars=round(tax_other_effect, 2),
            primary_driver=driver,
            explanation=expl
        )

    def compare_periods(self, period_prev: str, period_curr: str) -> PeriodComparison:
        """Compara exhaustivamente dos períodos arbitrarios."""
        if period_prev not in self.invoices_by_period:
            raise KeyError(f"Período anterior '{period_prev}' no encontrado en el dataset.")
        if period_curr not in self.invoices_by_period:
            raise KeyError(f"Período actual '{period_curr}' no encontrado en el dataset.")

        inv_prev = self.invoices_by_period[period_prev]
        inv_curr = self.invoices_by_period[period_curr]

        tot_prev = float(inv_prev.get("bloque_a_identificacion", {}).get("total_factura", 0.0))
        tot_curr = float(inv_curr.get("bloque_a_identificacion", {}).get("total_factura", 0.0))
        delta_tot = tot_curr - tot_prev
        pct_tot = (delta_tot / tot_prev * 100.0) if tot_prev > 0 else 0.0

        # Desgloses
        edesa_bd = self.decompose_electric_variance(inv_prev, inv_curr)
        aguas_bd = self.decompose_water_variance(inv_prev, inv_curr)

        # Municipal y Lusal
        muni_prev = float(inv_prev.get("bloque_d_tributos_municipales_y_concesiones", {}).get("municipalidad_de_salta", {}).get("subtotal_municipal", 0.0))
        muni_curr = float(inv_curr.get("bloque_d_tributos_municipales_y_concesiones", {}).get("municipalidad_de_salta", {}).get("subtotal_municipal", 0.0))
        delta_muni = muni_curr - muni_prev

        lusal_prev = float(inv_prev.get("bloque_d_tributos_municipales_y_concesiones", {}).get("lusal_ute", {}).get("subtotal_lusal", 0.0))
        lusal_curr = float(inv_curr.get("bloque_d_tributos_municipales_y_concesiones", {}).get("lusal_ute", {}).get("subtotal_lusal", 0.0))
        delta_lusal = lusal_curr - lusal_prev

        municipal_info = {
            "amount_prev": round(muni_prev, 2),
            "amount_curr": round(muni_curr, 2),
            "delta_amount": round(delta_muni, 2),
            "pct_change": round((delta_muni / muni_prev * 100.0) if muni_prev > 0 else 0.0, 2)
        }

        lusal_info = {
            "amount_prev": round(lusal_prev, 2),
            "amount_curr": round(lusal_curr, 2),
            "delta_amount": round(delta_lusal, 2),
            "pct_change": round((delta_lusal / lusal_prev * 100.0) if lusal_prev > 0 else 0.0, 2)
        }

        # Consolidación macro de efectos
        total_vol_effect = edesa_bd.volume_effect_ars + aguas_bd.volume_effect_ars
        total_tariff_inflation_effect = delta_tot - total_vol_effect

        total_denom = abs(total_vol_effect) + abs(total_tariff_inflation_effect)
        if total_denom > 0.001:
            pct_vol_driver = round((abs(total_vol_effect) / total_denom) * 100.0, 1)
            pct_tariff_driver = round(100.0 - pct_vol_driver, 1)
        else:
            pct_vol_driver = 50.0
            pct_tariff_driver = 50.0

        # Clasificación macro de driver
        if edesa_bd.delta_volume > 100:
            macro = "PICO_INVERNAL_VOLUMEN"
            summary = f"Fuerte salto por pico invernal de calefacción (+{edesa_bd.delta_volume:.0f} kWh). El efecto volumen explica el mayor componente del aumento."
        elif edesa_bd.delta_volume < -200:
            macro = "CONTRACCION_POST_PICO"
            summary = f"Marcada reducción de factura (-${abs(delta_tot):,.2f}) explicada por el fin de la demanda invernal (-{abs(edesa_bd.delta_volume):.0f} kWh en luz)."
        elif delta_tot > 0 and edesa_bd.delta_volume <= 0:
            macro = "AUMENTO_TARIFA_INFLACION"
            summary = "Aumento nominal traccionado por incrementos tarifarios de cargos fijos y precios unitarios a pesar de consumo constante o menor."
        else:
            macro = "MODERADO_MIXTO"
            summary = f"Variación moderada mixta: Consumo luz {edesa_bd.delta_volume:+.0f} kWh, agua {aguas_bd.delta_volume:+.1f} m³."

        return PeriodComparison(
            period_prev=period_prev,
            period_curr=period_curr,
            total_prev=round(tot_prev, 2),
            total_curr=round(tot_curr, 2),
            delta_total=round(delta_tot, 2),
            pct_change_total=round(pct_tot, 2),
            edesa=edesa_bd,
            aguas=aguas_bd,
            municipal=municipal_info,
            lusal=lusal_info,
            total_volume_effect_ars=round(total_vol_effect, 2),
            total_tariff_and_inflation_effect_ars=round(total_tariff_inflation_effect, 2),
            pct_volume_driver=pct_vol_driver,
            pct_tariff_driver=pct_tariff_driver,
            macro_driver=macro,
            summary_report=summary
        )

    def analyze_all_consecutive(self) -> List[PeriodComparison]:
        """Compara sucesivamente cada par de períodos consecutivos (06->07, 07->08, 08->09)."""
        comparisons: List[PeriodComparison] = []
        for i in range(len(self.ordered_periods) - 1):
            p_prev = self.ordered_periods[i]
            p_curr = self.ordered_periods[i + 1]
            comparisons.append(self.compare_periods(p_prev, p_curr))
        return comparisons

    def get_multimonth_evolution_table(self) -> List[Dict[str, Any]]:
        """Genera una tabla tabular de las 4 facturas para dashboards y reportes."""
        table = []
        for p in self.ordered_periods:
            inv = self.invoices_by_period[p]
            b_a = inv.get("bloque_a_identificacion", {})
            b_b = inv.get("bloque_b_electricidad_edesa", {})
            b_c = inv.get("bloque_c_agua_aguas_del_norte", {})
            b_d = inv.get("bloque_d_tributos_municipales_y_concesiones", {})

            desg_b = b_b.get("desglose_costos", {})
            desg_c = b_c.get("desglose_costos", {})
            muni = b_d.get("municipalidad_de_salta", {})
            lusal = b_d.get("lusal_ute", {})

            tot_edesa = float(desg_b.get("subtotal_con_alumbrado", 
                          desg_b.get("subtotal_edesa_neto", 0.0) + desg_b.get("incidencia_energia_alumbrado_publico_monto", 0.0)))

            table.append({
                "periodo": p,
                "emision": b_a.get("fecha_emision"),
                "vencimiento": b_a.get("fecha_vencimiento"),
                "total_factura": float(b_a.get("total_factura", 0.0)),
                "pago_anterior": float(b_a.get("pago_anterior_registrado", 0.0)),
                # Electricidad
                "edesa_total": round(tot_edesa, 2),
                "edesa_consumo_kwh": float(b_b.get("energia_activa", {}).get("consumo_kwh", 0.0)),
                "edesa_cos_phi": float(b_b.get("factor_potencia_cos_phi", 0.0)),
                "edesa_subsidio": float(desg_b.get("subsidio_estatal_declarado", 0.0)),
                # Agua
                "aguas_total": float(desg_c.get("subtotal_aguas_del_norte", 0.0)),
                "aguas_consumo_m3": float(b_c.get("lecturas_volumen", {}).get("consumo_m3", 0.0)),
                "aguas_cargo_fijo": float(desg_c.get("cargo_fijo", 0.0)),
                "aguas_iva_percepcion": float(desg_c.get("iva_no_categorizado_27", 0.0)) + float(desg_c.get("percepcion_iva_no_categorizado_13_5", 0.0)),
                # Tasas
                "municipal_total": float(muni.get("subtotal_municipal", 0.0)),
                "lusal_total": float(lusal.get("subtotal_lusal", 0.0))
            })
        return table
