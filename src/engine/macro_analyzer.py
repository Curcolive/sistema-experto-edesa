"""
Módulo de Analítica Global Multimes y Descomposición Macroeconómica
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Consolida la serie cuatrimestral de facturas (06/2026 a 09/2026) y descompone:
1. Participación estructural del gasto por servicio (Electricidad, Agua, Tasas comunales).
2. Presión tributaria acumulada integral (IVA 21%, IVA 27%, Percepción 13.5%, Tasas Municipales).
3. Descomposición de la varianza cuatrimestral: Estacionalidad invernal (pico 847 kWh)
   frente a subas tarifarias acumuladas en Aguas del Norte (+11.6%).
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import math
from ..persistence.history_store import parse_period_key


@dataclass
class PeriodShareRecord:
    """Participación económica de cada subsistema en un período particular."""
    period: str
    total_factura: float
    edesa_ars: float
    aguas_ars: float
    muni_ars: float
    lusal_ars: float
    pct_edesa: float
    pct_aguas: float
    pct_muni: float
    pct_lusal: float
    pct_no_electrico: float  # (Aguas + Muni + Lusal) / Total

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CumulativeTaxBreakdown:
    """Consolidado cuatrimestral de presión tributaria y tasas indirectas."""
    iva_21_electrico_ars: float
    iva_27_agua_ars: float
    percepcion_13_5_agua_ars: float
    tasas_municipales_ars: float
    tasa_enresp_agua_ars: float
    total_tributos_acumulados_ars: float
    total_facturado_cuatrimestre_ars: float
    presion_tributaria_efectiva_pct: float
    tributos_castigo_evitables_ars: float  # Percepción 13.5% + diferencial 6% de IVA sobre agua

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MacroVarianceReport:
    """Descomposición macroeconómica de la varianza cuatrimestral."""
    total_cuatrimestre_ars: float
    gasto_promedio_mensual_ars: float
    periodo_minimo: Tuple[str, float]
    periodo_maximo_pico: Tuple[str, float]
    amplitud_variacion_ars: float
    pico_invernal_kwh: float
    pico_invernal_periodo: str
    impacto_estacional_invierno_ars: float
    incremento_acumulado_tarifa_agua_pct: float
    participacion_promedio_aguas_pct: float
    participacion_promedio_edesa_pct: float
    participacion_promedio_tasas_pct: float
    participacion_promedio_no_electrica_pct: float
    diagnostico_macro: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MacroAnalyzer:
    """
    Analizador macroeconómico y de series de auditoría de servicios públicos.
    Consolida las 4 facturas reales del ciclo 2026.
    """

    def __init__(self, invoices: Optional[List[dict]] = None):
        self.invoices_by_period: Dict[str, dict] = {}
        self.ordered_periods: List[str] = []
        if invoices:
            self.load_invoices(invoices)

    def load_invoices(self, invoices: List[dict]) -> None:
        """Carga y ordena cronológicamente la colección de comprobantes."""
        self.invoices_by_period.clear()
        for inv in invoices:
            period = inv.get("bloque_a_identificacion", {}).get("periodo_facturado", "")
            if period:
                self.invoices_by_period[period] = inv

        self.ordered_periods = sorted(self.invoices_by_period.keys(), key=parse_period_key)

    def calculate_service_shares(self) -> List[PeriodShareRecord]:
        """Calcula la participación porcentual de cada servicio para cada mes de la serie."""
        records: List[PeriodShareRecord] = []
        for period in self.ordered_periods:
            inv = self.invoices_by_period[period]
            total = float(inv.get("bloque_a_identificacion", {}).get("total_factura", 0.0))
            edesa = float(inv.get("bloque_b_electricidad_edesa", {}).get("desglose_costos", {}).get("subtotal_con_alumbrado", 0.0))
            if edesa == 0.0:
                edesa = float(inv.get("bloque_b_electricidad_edesa", {}).get("desglose_costos", {}).get("subtotal_edesa_neto", 0.0))

            aguas = float(inv.get("bloque_c_agua_aguas_del_norte", {}).get("desglose_costos", {}).get("subtotal_aguas_del_norte", 0.0))
            muni = float(inv.get("bloque_d_tributos_municipales_y_concesiones", {}).get("municipalidad_de_salta", {}).get("subtotal_municipal", 0.0))
            lusal = float(inv.get("bloque_d_tributos_municipales_y_concesiones", {}).get("lusal_ute", {}).get("subtotal_lusal", 0.0))

            if total > 0:
                p_edesa = (edesa / total) * 100.0
                p_aguas = (aguas / total) * 100.0
                p_muni = (muni / total) * 100.0
                p_lusal = (lusal / total) * 100.0
                p_no_elec = ((aguas + muni + lusal) / total) * 100.0
            else:
                p_edesa = p_aguas = p_muni = p_lusal = p_no_elec = 0.0

            records.append(PeriodShareRecord(
                period=period,
                total_factura=total,
                edesa_ars=edesa,
                aguas_ars=aguas,
                muni_ars=muni,
                lusal_ars=lusal,
                pct_edesa=round(p_edesa, 2),
                pct_aguas=round(p_aguas, 2),
                pct_muni=round(p_muni, 2),
                pct_lusal=round(p_lusal, 2),
                pct_no_electrico=round(p_no_elec, 2)
            ))
        return records

    def calculate_cumulative_tax_breakdown(self) -> CumulativeTaxBreakdown:
        """Calcula el consolidado de carga impositiva acumulada en los meses auditados."""
        total_iva_21 = 0.0
        total_iva_27 = 0.0
        total_perc_13_5 = 0.0
        total_tasas_muni = 0.0
        total_tasa_enresp = 0.0
        total_facturado = 0.0

        for period in self.ordered_periods:
            inv = self.invoices_by_period[period]
            total_facturado += float(inv.get("bloque_a_identificacion", {}).get("total_factura", 0.0))

            # EDESA IVA 21%
            edesa_costos = inv.get("bloque_b_electricidad_edesa", {}).get("desglose_costos", {})
            total_iva_21 += float(edesa_costos.get("iva_consumidor_final_21", 0.0))

            # Aguas del Norte tributos
            agua_costos = inv.get("bloque_c_agua_aguas_del_norte", {}).get("desglose_costos", {})
            total_iva_27 += float(agua_costos.get("iva_no_categorizado_27", 0.0))
            total_perc_13_5 += float(agua_costos.get("percepcion_iva_no_categorizado_13_5", 0.0))
            total_tasa_enresp += float(agua_costos.get("tasa_fiscalizacion_enresp_2", 0.0))

            # Municipalidad
            muni_block = inv.get("bloque_d_tributos_municipales_y_concesiones", {}).get("municipalidad_de_salta", {})
            total_tasas_muni += float(muni_block.get("subtotal_municipal", 0.0))

        total_tributos = (
            total_iva_21 + total_iva_27 + total_perc_13_5 + total_tasas_muni + total_tasa_enresp
        )
        presion_pct = (total_tributos / total_facturado * 100.0) if total_facturado > 0 else 0.0

        # Tributos evitables por saneamiento administrativo:
        # Percepción 13.5% entera + diferencial del 6% de IVA sobre agua (27% cobrado vs 21% legal)
        # diferencial_iva = total_iva_27 * (6.0 / 27.0)
        diferencial_iva_evitable = total_iva_27 * (6.0 / 27.0) if total_iva_27 > 0 else 0.0
        tributos_evitables = total_perc_13_5 + diferencial_iva_evitable

        return CumulativeTaxBreakdown(
            iva_21_electrico_ars=round(total_iva_21, 2),
            iva_27_agua_ars=round(total_iva_27, 2),
            percepcion_13_5_agua_ars=round(total_perc_13_5, 2),
            tasas_municipales_ars=round(total_tasas_muni, 2),
            tasa_enresp_agua_ars=round(total_tasa_enresp, 2),
            total_tributos_acumulados_ars=round(total_tributos, 2),
            total_facturado_cuatrimestre_ars=round(total_facturado, 2),
            presion_tributaria_efectiva_pct=round(presion_pct, 2),
            tributos_castigo_evitables_ars=round(tributos_evitables, 2)
        )

    def analyze_macro_variance(self) -> MacroVarianceReport:
        """
        Ejecuta la descomposición de varianza del cuatrimestre completo.
        Analiza el pico de invierno (Julio 847 kWh) vs la trayectoria tarifaria de Aguas del Norte.
        """
        if not self.ordered_periods:
            return MacroVarianceReport(
                total_cuatrimestre_ars=0.0,
                gasto_promedio_mensual_ars=0.0,
                periodo_minimo=("N/A", 0.0),
                periodo_maximo_pico=("N/A", 0.0),
                amplitud_variacion_ars=0.0,
                pico_invernal_kwh=0.0,
                pico_invernal_periodo="N/A",
                impacto_estacional_invierno_ars=0.0,
                incremento_acumulado_tarifa_agua_pct=0.0,
                participacion_promedio_aguas_pct=0.0,
                participacion_promedio_edesa_pct=0.0,
                participacion_promedio_tasas_pct=0.0,
                participacion_promedio_no_electrica_pct=0.0,
                diagnostico_macro="No hay facturas cargadas en la serie histórica."
            )

        shares = self.calculate_service_shares()
        total_sum = sum(s.total_factura for s in shares)
        avg_monthly = total_sum / len(shares)

        # Período mínimo y máximo de gasto
        min_share = min(shares, key=lambda s: s.total_factura)
        max_share = max(shares, key=lambda s: s.total_factura)
        amplitud = max_share.total_factura - min_share.total_factura

        # Identificar pico de kWh eléctrico
        pico_kwh = 0.0
        pico_kwh_period = ""
        for p in self.ordered_periods:
            kwh = float(self.invoices_by_period[p].get("bloque_b_electricidad_edesa", {}).get("energia_activa", {}).get("consumo_kwh", 0.0))
            if kwh > pico_kwh:
                pico_kwh = kwh
                pico_kwh_period = p

        # Impacto monetario de invierno: salto de 06/2026 a 07/2026 o salto hacia el pico
        inv_06 = self.invoices_by_period.get("06/2026")
        inv_07 = self.invoices_by_period.get("07/2026")
        if inv_06 and inv_07:
            tot_06 = float(inv_06.get("bloque_a_identificacion", {}).get("total_factura", 0.0))
            tot_07 = float(inv_07.get("bloque_a_identificacion", {}).get("total_factura", 0.0))
            impacto_invierno = tot_07 - tot_06
        elif pico_kwh_period in self.ordered_periods:
            idx = self.ordered_periods.index(pico_kwh_period)
            if idx > 0:
                p_prev = self.ordered_periods[idx - 1]
                tot_pico = float(self.invoices_by_period[pico_kwh_period].get("bloque_a_identificacion", {}).get("total_factura", 0.0))
                tot_prev = float(self.invoices_by_period[p_prev].get("bloque_a_identificacion", {}).get("total_factura", 0.0))
                impacto_invierno = tot_pico - tot_prev
            else:
                impacto_invierno = amplitud
        else:
            impacto_invierno = amplitud

        # Variación tarifaria de Aguas del Norte (Cargo Fijo: comparando inicio vs final de la serie)
        p_first = self.ordered_periods[0]
        p_last = self.ordered_periods[-1]
        p_start_agua = "06/2026" if "06/2026" in self.invoices_by_period else p_first
        p_end_agua = "09/2026" if "09/2026" in self.invoices_by_period else p_last

        cf_start = float(self.invoices_by_period[p_start_agua].get("bloque_c_agua_aguas_del_norte", {}).get("desglose_costos", {}).get("cargo_fijo", 0.0))
        cf_end = float(self.invoices_by_period[p_end_agua].get("bloque_c_agua_aguas_del_norte", {}).get("desglose_costos", {}).get("cargo_fijo", 0.0))

        if cf_start > 0 and cf_end > 0:
            pct_aumento_cf_agua = ((cf_end - cf_start) / cf_start) * 100.0
        else:
            pct_aumento_cf_agua = 0.0

        # Participaciones promedio cuatrimestrales
        sum_edesa = sum(s.edesa_ars for s in shares)
        sum_aguas = sum(s.aguas_ars for s in shares)
        sum_tasas = sum((s.muni_ars + s.lusal_ars) for s in shares)

        prom_edesa_pct = (sum_edesa / total_sum * 100.0) if total_sum > 0 else 0.0
        prom_aguas_pct = (sum_aguas / total_sum * 100.0) if total_sum > 0 else 0.0
        prom_tasas_pct = (sum_tasas / total_sum * 100.0) if total_sum > 0 else 0.0
        prom_no_elec_pct = ((sum_aguas + sum_tasas) / total_sum * 100.0) if total_sum > 0 else 0.0

        pico_desc = f"en {pico_kwh_period} ({pico_kwh:.0f} kWh)" if pico_kwh > 0 else "no registrado"
        diagnostico = (
            f"El gasto cuatrimestral consolidado totalizó ${total_sum:,.2f} ARS, con un promedio mensual de "
            f"${avg_monthly:,.2f} ARS. El comportamiento financiero estuvo regido por dos fuerzas asimétricas: "
            f"1) La estacionalidad invernal extrema de calefacción eléctrica {pico_desc}, "
            f"que empujó la factura a su máximo anual de ${max_share.total_factura:,.2f} ARS (+${impacto_invierno:,.2f}); "
            f"2) El crecimiento inelástico y sostenido de la tarifa de Aguas del Norte, cuyo cargo fijo subió un "
            f"+{pct_aumento_cf_agua:.1f}% acumulado entre {p_start_agua} y {p_end_agua}. "
            f"Estructuralmente, los servicios ajenos a la electricidad (Agua y Tasas Municipales) explicaron en promedio "
            f"el {prom_no_elec_pct:.1f}% de la boleta de EDESA."
        )

        return MacroVarianceReport(
            total_cuatrimestre_ars=round(total_sum, 2),
            gasto_promedio_mensual_ars=round(avg_monthly, 2),
            periodo_minimo=(min_share.period, round(min_share.total_factura, 2)),
            periodo_maximo_pico=(max_share.period, round(max_share.total_factura, 2)),
            amplitud_variacion_ars=round(amplitud, 2),
            pico_invernal_kwh=round(pico_kwh, 2),
            pico_invernal_periodo=pico_kwh_period,
            impacto_estacional_invierno_ars=round(impacto_invierno, 2),
            incremento_acumulado_tarifa_agua_pct=round(pct_aumento_cf_agua, 2),
            participacion_promedio_aguas_pct=round(prom_aguas_pct, 2),
            participacion_promedio_edesa_pct=round(prom_edesa_pct, 2),
            participacion_promedio_tasas_pct=round(prom_tasas_pct, 2),
            participacion_promedio_no_electrica_pct=round(prom_no_elec_pct, 2),
            diagnostico_macro=diagnostico
        )

    def generate_stacked_chart_dataset(self) -> List[Dict[str, Any]]:
        """Genera los datos estructurados para renderizar gráficos de barras apiladas multimes."""
        shares = self.calculate_service_shares()
        chart_data = []
        for s in shares:
            chart_data.append({
                "period": s.period,
                "total": s.total_factura,
                "edesa": s.edesa_ars,
                "aguas": s.aguas_ars,
                "muni": s.muni_ars,
                "lusal": s.lusal_ars,
                "pct_edesa": s.pct_edesa,
                "pct_aguas": s.pct_aguas,
                "pct_muni": s.pct_muni,
                "pct_lusal": s.pct_lusal
            })
        return chart_data
