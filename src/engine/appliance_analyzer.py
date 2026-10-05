"""
Módulo de Analizador de Dispositivos Eléctricos y Desagregación de Cargas (NILM Heurístico)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Modela el parque de artefactos residenciales típicos en Salta Capital,
calcula analíticamente su demanda mensual teórica en kWh:
    Consumo_i = (Potencia_i × HorasUso_i × DutyCycle_i × Días_i) / 1000
y correlaciona con la factura auditada para identificar:
1. Grado de explicación del consumo real de la boleta (Coverage Ratio).
2. Artefacto de mayor demanda (consumo predominante).
3. Artefacto culpable del salto por encima del tope subsidiado RASE N3 (200 kWh/mes).
4. Recomendaciones operativas de ahorro y optimización de uso horario.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class ApplianceModel:
    """Modelo formal de un artefacto eléctrico del catálogo residencial."""
    id: str
    name: str
    nominal_watts: float
    default_hours_per_day: float
    duty_cycle: float = 1.0  # Factor de marcha / ciclado del compresor (ej. 0.35 heladera)
    days_per_month: int = 30
    category: str = "BASE"  # "BASE", "CLIMATIZACION", "AGUA_CALIENTE", "COCINA", "OTROS"
    is_thermal: bool = False
    description: str = ""

    def calculate_monthly_kwh(self, hours_per_day: Optional[float] = None, quantity: int = 1) -> float:
        """Calcula el consumo mensual teórico en kWh."""
        h = self.default_hours_per_day if hours_per_day is None else max(0.0, float(hours_per_day))
        q = max(0, int(quantity))
        kwh = (self.nominal_watts * h * self.duty_cycle * self.days_per_month * q) / 1000.0
        return round(kwh, 2)


@dataclass
class ApplianceUsageItem:
    """Consumo desglosado de un electrodoméstico específico configurado por el usuario."""
    appliance_id: str
    name: str
    category: str
    quantity: int
    hours_per_day: float
    nominal_watts: float
    monthly_kwh: float
    monthly_cost_ars: float
    pct_of_total_consumption: float
    is_thermal: bool
    duty_cycle: float = 1.0
    is_culprit_for_subsidy_loss: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApplianceAuditResult:
    """Resultado de la correlación analítica entre el inventario de artefactos y la boleta."""
    total_theoretical_kwh: float
    invoice_real_kwh: float
    discrepancy_kwh: float
    coverage_percentage: float
    items: List[ApplianceUsageItem]
    base_load_kwh: float
    thermal_load_kwh: float
    highest_consumption_appliance: str
    culprit_subsidy_loss_appliance: Optional[str]
    excess_over_rase_subsidy_kwh: float
    excess_financial_impact_ars: float
    potential_savings_recommendations: List[str]
    diagnostic_summary: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["items"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in self.items]
        return d


class ApplianceAnalyzer:
    """
    Analizador determinista y heurístico de desagregación de cargas eléctricas (NILM).
    Permite validar y auditar picos estacionales de consumo.
    """

    CATALOG: List[ApplianceModel] = [
        # Cargas Base Continuas
        ApplianceModel(
            id="heladera_freezer",
            name="Heladera con Freezer (Clase A)",
            nominal_watts=200.0,
            default_hours_per_day=24.0,
            duty_cycle=0.35,  # Ciclado termostático ~8.4h de compresor activo al día
            category="BASE",
            is_thermal=False,
            description="Refrigerador estándar clase A en funcionamiento continuo."
        ),
        ApplianceModel(
            id="iluminacion_led",
            name="Lámpara LED individual (9W c/u)",
            nominal_watts=9.0,
            default_hours_per_day=5.0,
            duty_cycle=1.0,
            category="BASE",
            is_thermal=False,
            description="Lámpara LED individual de alta eficiencia (9W)."
        ),
        ApplianceModel(
            id="smart_tv_wifi",
            name="Smart TV 50'' + Router Wi-Fi",
            nominal_watts=110.0,
            default_hours_per_day=6.0,
            duty_cycle=1.0,
            category="BASE",
            is_thermal=False,
            description="Smart TV en uso residencial más router de enlace permanente."
        ),
        ApplianceModel(
            id="lavarropas_auto",
            name="Lavarropas Automático (5 kg)",
            nominal_watts=500.0,
            default_hours_per_day=1.0,
            duty_cycle=1.0,
            category="BASE",
            is_thermal=False,
            description="Lavado estándar con agua fría 4 a 5 veces por semana."
        ),
        ApplianceModel(
            id="computadora_laptop",
            name="Computadora / Laptop de Trabajo",
            nominal_watts=90.0,
            default_hours_per_day=6.0,
            duty_cycle=1.0,
            category="BASE",
            is_thermal=False,
            description="PC de escritorio o laptop en jornada de estudio/trabajo."
        ),

        # Cargas Térmicas Críticas (Picos de Invierno / Pérdida de Subsidios)
        ApplianceModel(
            id="caloventor_electrico",
            name="Caloventor Eléctrico",
            nominal_watts=2000.0,
            default_hours_per_day=4.0,
            duty_cycle=1.0,
            category="CLIMATIZACION",
            is_thermal=True,
            description="Calefactor por convección resistiva forzada de alta potencia."
        ),
        ApplianceModel(
            id="estufa_cuarzo",
            name="Estufa Eléctrica de Cuarzo / Halógena",
            nominal_watts=1200.0,
            default_hours_per_day=6.0,
            duty_cycle=1.0,
            category="CLIMATIZACION",
            is_thermal=True,
            description="Radiador infrarrojo de 2 o 3 velas."
        ),
        ApplianceModel(
            id="aire_acondicionado_fc",
            name="Aire Acondicionado Frío/Calor (3000 Fg)",
            nominal_watts=1400.0,
            default_hours_per_day=5.0,
            duty_cycle=0.60,  # Termostato inverter/on-off
            category="CLIMATIZACION",
            is_thermal=True,
            description="Equipo Split en modo calor para climatización de invierno."
        ),
        ApplianceModel(
            id="termotanque_electrico",
            name="Termotanque Eléctrico (80 Litros)",
            nominal_watts=1500.0,
            default_hours_per_day=4.0,
            duty_cycle=1.0,
            category="AGUA_CALIENTE",
            is_thermal=True,
            description="Calentamiento acumulativo de agua sanitaria."
        ),
        ApplianceModel(
            id="pava_electrica",
            name="Pava Eléctrica",
            nominal_watts=1800.0,
            default_hours_per_day=0.5,
            duty_cycle=1.0,
            category="COCINA",
            is_thermal=True,
            description="Calentamiento rápido de agua para infusiones."
        ),
        ApplianceModel(
            id="microondas",
            name="Horno Microondas",
            nominal_watts=1200.0,
            default_hours_per_day=0.3,
            duty_cycle=1.0,
            category="COCINA",
            is_thermal=False,
            description="Calentamiento y cocción breve de alimentos."
        )
    ]

    def __init__(self, catalog: Optional[List[ApplianceModel]] = None):
        self.catalog = list(catalog) if catalog is not None else list(self.CATALOG)
        self.catalog_map: Dict[str, ApplianceModel] = {app.id: app for app in self.catalog}

    def get_catalog(self) -> List[ApplianceModel]:
        """Retorna el catálogo predeterminado de artefactos residenciales."""
        return list(self.catalog)

    def correlate_with_invoice(
        self,
        invoice_kwh: float,
        custom_inputs: Optional[List[Dict[str, Any]]] = None,
        unit_price_base: float = 187.09,
        unit_price_excess: float = 301.88,
        rase_subsidy_threshold_kwh: float = 200.0
    ) -> ApplianceAuditResult:
        """
        Calcula la correlación analítica entre el inventario de electrodomésticos
        y el consumo real medido de la factura auditada.
        """
        invoice_kwh = max(0.0, float(invoice_kwh))
        items: List[ApplianceUsageItem] = []

        # Usar custom_inputs si se proporcionan, sino usar catálogo con defaults
        configured_appliances: List[Tuple[ApplianceModel, int, float]] = []

        # Diccionario de alias entre IDs de frontend y del catálogo analítico
        id_aliases = {
            "heladera": "heladera_freezer",
            "iluminacion": "iluminacion_led",
            "tv_wifi": "smart_tv_wifi",
            "lavarropas": "lavarropas_auto",
            "pc": "computadora_laptop",
            "caloventor": "caloventor_electrico",
            "estufa_cuarzo": "estufa_cuarzo",
            "aire_fc": "aire_acondicionado_fc",
            "termotanque": "termotanque_electrico",
            "pava": "pava_electrica",
            "microondas": "microondas"
        }

        if custom_inputs is not None:
            for inp in custom_inputs:
                app_id = inp.get("id", "")
                resolved_id = id_aliases.get(app_id, app_id)
                qty = max(0, int(inp.get("quantity", inp.get("qty", 1))))
                hours = max(0.0, float(inp.get("hours_per_day", inp.get("hours", 0.0))))
                enabled = bool(inp.get("enabled", True))
                if not enabled or qty == 0 or hours == 0.0:
                    continue

                if resolved_id in self.catalog_map:
                    base_app = self.catalog_map[resolved_id]
                    watts = float(inp.get("nominal_watts", inp.get("watts", base_app.nominal_watts)))
                    duty = float(inp.get("duty_cycle", inp.get("dutyCycle", base_app.duty_cycle)))
                    is_th = bool(inp.get("is_thermal", inp.get("isThermal", base_app.is_thermal)))
                    app = ApplianceModel(
                        id=base_app.id,
                        name=base_app.name,
                        nominal_watts=watts,
                        default_hours_per_day=hours,
                        duty_cycle=duty,
                        days_per_month=base_app.days_per_month,
                        category=base_app.category,
                        is_thermal=is_th,
                        description=base_app.description
                    )
                    configured_appliances.append((app, qty, hours))
                else:
                    # Artefacto personalizado ad-hoc
                    watts = float(inp.get("nominal_watts", inp.get("watts", 500.0)))
                    duty = float(inp.get("duty_cycle", inp.get("dutyCycle", 1.0)))
                    is_th = bool(inp.get("is_thermal", inp.get("isThermal", False)))
                    custom_app = ApplianceModel(
                        id=app_id or "custom",
                        name=inp.get("name", "Artefacto Personalizado"),
                        nominal_watts=watts,
                        default_hours_per_day=hours,
                        duty_cycle=duty,
                        category=inp.get("category", "OTROS"),
                        is_thermal=is_th
                    )
                    configured_appliances.append((custom_app, qty, hours))
        else:
            # Caso por defecto: artefactos base más calefactor moderado
            for app in self.catalog:
                # Activar por defecto artefactos base y caloventor/termotanque si es factura de invierno
                is_winter_peak = (invoice_kwh >= 600.0)
                if app.category == "BASE" or app.id in ("pava_electrica", "microondas"):
                    qty = 8 if app.id == "iluminacion_led" else 1
                    configured_appliances.append((app, qty, app.default_hours_per_day))
                elif is_winter_peak and app.id in ("caloventor_electrico", "termotanque_electrico"):
                    configured_appliances.append((app, 1, app.default_hours_per_day))

        # Calcular consumo de cada electrodoméstico
        total_kwh = 0.0
        base_kwh = 0.0
        thermal_kwh = 0.0

        for app, qty, hours in configured_appliances:
            kwh = app.calculate_monthly_kwh(hours_per_day=hours, quantity=qty)
            total_kwh += kwh
            if app.is_thermal or app.category in ("CLIMATIZACION", "AGUA_CALIENTE"):
                thermal_kwh += kwh
            else:
                base_kwh += kwh

        # Segunda pasada: calcular porcentajes de participación y costos
        for app, qty, hours in configured_appliances:
            kwh = app.calculate_monthly_kwh(hours_per_day=hours, quantity=qty)
            pct = (kwh / total_kwh * 100.0) if total_kwh > 0 else 0.0

            # Costo aproximado (ponderado entre base y tarifa plena según umbral)
            if invoice_kwh > rase_subsidy_threshold_kwh and (app.is_thermal or app.category in ("CLIMATIZACION", "AGUA_CALIENTE")):
                cost = kwh * unit_price_excess
            else:
                cost = kwh * unit_price_base

            items.append(ApplianceUsageItem(
                appliance_id=app.id,
                name=app.name,
                category=app.category,
                quantity=qty,
                hours_per_day=hours,
                nominal_watts=app.nominal_watts,
                monthly_kwh=kwh,
                monthly_cost_ars=round(cost, 2),
                pct_of_total_consumption=round(pct, 2),
                is_thermal=app.is_thermal,
                duty_cycle=app.duty_cycle
            ))

        # Ordenar por consumo descendente
        items.sort(key=lambda x: x.monthly_kwh, reverse=True)

        # Cobertura y discrepancia con la boleta real
        discrepancy = round(invoice_kwh - total_kwh, 2)
        coverage_pct = round((total_kwh / invoice_kwh * 100.0) if invoice_kwh > 0 else 100.0, 2)

        # Artefacto con mayor consumo
        highest_app = items[0].name if items else "Ninguno declarado"

        # Exceso RASE N3
        excess_kwh = max(0.0, round(invoice_kwh - rase_subsidy_threshold_kwh, 2))
        excess_cost = round(excess_kwh * unit_price_excess, 2)

        # Identificar al principal causante de la pérdida del subsidio
        culprit: Optional[str] = None
        if excess_kwh > 0 and items:
            # Buscar el artefacto térmico o de mayor consumo que explique el desborde
            thermal_candidates = [it for it in items if it.is_thermal]
            if thermal_candidates:
                culprit_item = max(thermal_candidates, key=lambda x: x.monthly_kwh)
                culprit_item.is_culprit_for_subsidy_loss = True
                culprit = culprit_item.name
            else:
                items[0].is_culprit_for_subsidy_loss = True
                culprit = items[0].name

        # Recomendaciones operativas de ahorro
        recommendations: List[str] = []
        for it in items:
            if it.is_thermal and it.hours_per_day >= 2.0:
                hours_saving = min(2.0, it.hours_per_day)
                kwh_saved = (it.nominal_watts * hours_saving * it.duty_cycle * it.quantity * 30.0) / 1000.0
                money_saved = kwh_saved * unit_price_excess
                recommendations.append(
                    f"Reducir {hours_saving:.0f} horas diarias de '{it.name}' ahorra aprox. {kwh_saved:.1f} kWh/mes "
                    f"y evita ${money_saved:,.2f} ARS de consumo a tarifa plena sin subsidio."
                )

        if not recommendations and excess_kwh > 0:
            recommendations.append(
                f"El consumo excede el tope subsidiado en {excess_kwh:.1f} kWh. Apagar artefactos térmicos "
                f"en horas pico permite reingresar al bloque protegido de $187/kWh."
            )
        elif not recommendations:
            recommendations.append(
                "La instalación se encuentra dentro del bloque subsidiado de 200 kWh. Mantener los hábitos actuales."
            )

        # Resumen diagnóstico pericial
        if culprit:
            diag = (
                f"El inventario de artefactos explica el {coverage_pct:.1f}% de la energía consumida en el período "
                f"({total_kwh:.1f} kWh declarados vs. {invoice_kwh:.1f} kWh facturados). "
                f"El artefacto de mayor impacto es '{highest_app}'. "
                f"El principal responsable de haber superado el tope subsidiado RASE N3 (200 kWh) es '{culprit}', "
                f"lo cual generó un excedente de {excess_kwh:.1f} kWh liquidado a tarifa plena ($301/kWh) "
                f"por un costo adicional de ${excess_cost:,.2f} ARS."
            )
        elif excess_kwh > 0:
            diag = (
                f"La boleta auditada registra un consumo de {invoice_kwh:.1f} kWh, excediendo el tope subsidiado "
                f"RASE N3 (200 kWh) en {excess_kwh:.1f} kWh (${excess_cost:,.2f} ARS a tarifa plena). "
                f"El inventario configurado declara {total_kwh:.1f} kWh (cobertura: {coverage_pct:.1f}%). "
                f"Se recomienda declarar el uso de artefactos térmicos (caloventores, termotanques) para identificar la causa del excedente."
            )
        else:
            diag = (
                f"El consumo declarado ({total_kwh:.1f} kWh) explica el {coverage_pct:.1f}% del total de la boleta. "
                f"La demanda permanece encuadrada dentro de los parámetros de alta eficiencia."
            )

        return ApplianceAuditResult(
            total_theoretical_kwh=round(total_kwh, 2),
            invoice_real_kwh=round(invoice_kwh, 2),
            discrepancy_kwh=discrepancy,
            coverage_percentage=coverage_pct,
            items=items,
            base_load_kwh=round(base_kwh, 2),
            thermal_load_kwh=round(thermal_kwh, 2),
            highest_consumption_appliance=highest_app,
            culprit_subsidy_loss_appliance=culprit,
            excess_over_rase_subsidy_kwh=excess_kwh,
            excess_financial_impact_ars=excess_cost,
            potential_savings_recommendations=recommendations,
            diagnostic_summary=diag
        )
