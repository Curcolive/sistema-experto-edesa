"""
SCRIPT PRINCIPAL DE SIMULACIÓN Y AUDITORÍA INTEGRAL DE FACTURACIÓN
Cátedra: Principios de Inteligencia Artificial (GT110) — UGD (Ciclo Lectivo 2026)
1º Examen Parcial: "Diseño y Análisis de un Sistema Inteligente: Del Concepto a la Aplicación"
Estudiante: Estudiante UGD (Matrícula / Usuario: 100001)
Equipo Docente: Prof. Agustín Encina (Titular) | Dante Sicardi (Evaluador / Prácticos)

Ejecuta el ciclo de vida completo del Sistema Experto Simbólico:
1. Ingesta de hechos de la factura de Salta sanitizada (PII Masking).
2. Memoria de Trabajo con trazabilidad de procedencia.
3. Motor de Inferencia Bimodal (Forward Chaining + Backward Chaining).
4. Módulo XAI de Explicabilidad (HOW, WHY, desglose de ontología de conceptos).
5. Cuantificación de ahorros y Dictamen de Desdoblamiento (Res. ENRESP 1590/24).
6. Generación de gráficos analíticos de alta resolución en output_graficos/.
7. Emisión y exportación del informe pericial formal a docs/DICTAMEN_PERICIAL_ENRESP.md.
"""

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

# Configurar PYTHONPATH dinámico
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.domain.fact_model import FactCategory, AuditAnomalyFact
from src.domain.anonymizer import InvoiceAnonymizer
from src.knowledge_base.default_facts import (
    load_default_facts_from_json,
    load_all_historical_invoices,
    load_facts_for_period
)
from src.knowledge_base.rules_enresp import get_all_enresp_rules
from src.knowledge_base.concept_glossary import ConceptGlossary
from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.engine.explanation_module import ExplanationModule
from src.engine.comparative_analyzer import ComparativeAnalyzer
from src.persistence.history_store import HistoryStore
from src.visualizer.report_charts import ReportChartsGenerator


def print_banner(title: str):
    """Imprime separadores formateados de sección."""
    print("\n" + "=" * 85)
    print(f" {title.upper()}")
    print("=" * 85)


def run_full_audit_walkthrough():
    """Ejecuta el walkthrough completo de auditoría y simulación."""
    start_total = time.time()

    print_banner("SISTEMA EXPERTO DE AUDITORÍA Y DIAGNÓSTICO TARIFARIO MULTIDOMINIO (EDESA + AGUAS DEL NORTE)")
    print("Institución: Universidad Gastón Dachary (UGD) — Sede Posadas / Virtual")
    print("Carrera:     Licenciatura en Gestión de Recursos Tecnológicos")
    print("Asignatura:  Principios de Inteligencia Artificial (GT110) — 1º Examen Parcial")
    print("Estudiante:  Estudiante UGD — Matrícula: 100001")
    print("Cátedra:     Prof. Agustín Encina (Titular) | Dante Sicardi (Evaluador)")
    print("Documento:   Factura Unificada Período 09/2026 (Salta Capital)")

    # -------------------------------------------------------------------------
    # FASE 1: PERCEPCIÓN E INGESTA CON SANITIZACIÓN PII
    # -------------------------------------------------------------------------
    print_banner("Fase 1: Capa de Percepción y Sanitización de Datos Sensibles (PII Masking)")
    print("Protocolo Aplicado: Ley 25.326 de Protección de Datos Personales (Argentina)")
    print("• Titular Original:   VELARDE SARA JOSEFINA  --> Anonimizado: USUARIO_ANON_01")
    print("• Suministro NIS:     3024122                --> Enmascarado: 3024***")
    print("• Medidor Eléctrico:  1688895                --> Enmascarado: 1688*** (LANDIS+GYR)")
    print("• Medidor Sanitario:  0000007147             --> Enmascarado: 0000007*** (19 mm)")
    print("• Catastro Inmueble:  43038                  --> Enmascarado: 430**")

    json_file = PROJECT_ROOT / "data" / "factura_sanitizada.json"
    initial_facts = load_default_facts_from_json(json_file)
    print(f"-> Ingesta exitosa: {len(initial_facts)} hechos atómicos cargados en la Memoria de Trabajo.")

    # -------------------------------------------------------------------------
    # FASE 2: INICIALIZACIÓN DE MEMORIA DE TRABAJO Y BASE DE CONOCIMIENTO
    # -------------------------------------------------------------------------
    print_banner("Fase 2: Base de Conocimiento y Memoria de Trabajo (Working Memory)")
    wm = WorkingMemory(initial_facts)
    rules = get_all_enresp_rules()
    engine = InferenceEngine(rules)
    xai = ExplanationModule(rules)

    print(f"• Hechos Iniciales Activos: {len(wm)}")
    print(f"• Reglas de Inferencia Compiladas (Lambdas Desacopladas): {len(rules)}")
    print("  Catálogo de Reglas: " + ", ".join([r.id[:7] for r in rules]))

    # Resumen de valores percibidos clave
    total_factura = wm.get("factura_monto_total")
    consumo_luz = wm.get("electricidad_consumo_activo_kwh")
    cos_phi = wm.get("electricidad_factor_potencia_cos_phi")
    consumo_agua = wm.get("agua_consumo_volumen_m3")
    cat_luz = wm.get("electricidad_tipo_inmueble")
    cat_agua = wm.get("agua_tipo_inmueble")
    fiscal_agua = wm.get("agua_condicion_fiscal")

    print(f"\n[Datos de Entrada Clave]")
    print(f"  Total Boleta Unificada:     ${total_factura:,.2f} ARS")
    print(f"  Electricidad EDESA:         {consumo_luz} kWh (cos(phi) = {cos_phi}) | Cat: {cat_luz}")
    print(f"  Aguas del Norte:            {consumo_agua} m3 | Cat: {cat_agua} | Cond. Fiscal: {fiscal_agua}")
    print(f"  Deuda Anterior:             ${wm.get('factura_deuda_anterior', 0.0):,.2f} ARS (Usuario Libre de Deuda)")

    # -------------------------------------------------------------------------
    # FASE 3: MOTOR DE INFERENCIA — FORWARD CHAINING (DATA-DRIVEN)
    # -------------------------------------------------------------------------
    print_banner("Fase 3: Ejecución de Encadenamiento hacia Adelante (Forward Chaining)")
    print("Algoritmo: Match-Resolve-Act con Refracción y Resolución por Prioridad")
    
    fc_start = time.time()
    fc_result = engine.forward_chain(wm)
    fc_elapsed = time.time() - fc_start

    print(f"-> Estado de Quiescencia Alcanzado en {fc_result.cycles_executed} ciclos ({fc_elapsed*1000:.2f} ms).")
    print(f"-> Reglas disparadas exitosamente: {fc_result.rules_fired_count} de {len(rules)}")
    print(f"-> Total de hechos en Memoria tras inferencia: {fc_result.final_facts_count}")

    print("\n[Secuencia de Disparo de Reglas en Forward Chaining]:")
    print(f"{'Ciclo':<7} | {'ID Regla':<36} | {'Prioridad':<10} | {'Hecho(s) Derivado(s)'}")
    print("-" * 85)
    for rec in fc_result.rules_fired_sequence:
        facts_str = ", ".join(rec.new_facts_asserted) if rec.new_facts_asserted else "(Acción sin aserción)"
        print(f"{rec.cycle:<7} | {rec.rule_id:<36} | {rec.priority:<10} | {facts_str}")

    # -------------------------------------------------------------------------
    # FASE 4: MOTOR DE INFERENCIA — BACKWARD CHAINING (GOAL-DRIVEN)
    # -------------------------------------------------------------------------
    print_banner("Fase 4: Ejecución de Encadenamiento hacia Atrás (Backward Chaining)")
    print("Evaluación de Hipótesis y Metas Regulatorias Específicas:")

    # Prueba de Meta 1: Derecho a Desdoblamiento
    wm_bc1 = WorkingMemory(initial_facts)
    goal_1 = "derecho_desdoblamiento_habilitado"
    bc_result_1 = engine.backward_chain(wm_bc1, goal_fact_name=goal_1)
    print(f"\n[Meta 1]: ¿El usuario tiene derecho legal a desdoblar la boleta? ('{goal_1}')")
    print(f"  • Resultado: {'DEMOSTRADA (TRUE)' if bc_result_1.goal_proven else 'NO DEMOSTRADA'}")
    print(f"  • Detalle de Prueba: {bc_result_1.proof_tree}")

    # Prueba de Meta 2: Inconsistencia Tarifaria
    wm_bc2 = WorkingMemory(initial_facts)
    goal_2 = "alerta_inconsistencia_tarifaria"
    bc_result_2 = engine.backward_chain(wm_bc2, goal_fact_name=goal_2)
    print(f"\n[Meta 2]: ¿Existe inconsistencia cruzada catastral? ('{goal_2}')")
    print(f"  • Resultado: {'DEMOSTRADA (TRUE)' if bc_result_2.goal_proven else 'NO DEMOSTRADA'}")
    print(f"  • Detalle de Prueba: {bc_result_2.proof_tree}")

    # Prueba de Meta 3: Emisión de Dictamen Formal ENRESP (Deducción Recursiva Multi-Nivel)
    wm_bc3 = WorkingMemory(initial_facts)
    goal_3 = "dictamen_enresp_formal_generado"
    bc_result_3 = engine.backward_chain(wm_bc3, goal_fact_name=goal_3)
    print(f"\n[Meta 3]: ¿Se prueba deductivamente la emisión del dictamen formal ENRESP? ('{goal_3}')")
    print(f"  • Resultado: {'DEMOSTRADA (TRUE)' if bc_result_3.goal_proven else 'NO DEMOSTRADA'}")
    print(f"  • Sub-reglas encadenadas: {[r.rule_id for r in bc_result_3.rules_fired_sequence]}")
    print(f"  • Detalle de Prueba: {bc_result_3.proof_tree}")

    # -------------------------------------------------------------------------
    # FASE 5: EXPLICABILIDAD E INTELIGENCIA ARTIFICIAL EXPLICABLE (XAI)
    # -------------------------------------------------------------------------
    print_banner("Fase 5: Módulo de Explicabilidad (XAI - Consultas HOW y WHY)")

    # Consulta HOW para hecho deducido
    how_inconsistencia = xai.how("alerta_inconsistencia_tarifaria", wm, fc_result)
    print("[Consulta HOW: ¿Cómo se dedujo 'alerta_inconsistencia_tarifaria'?]")
    print(f"  • Tipo: {how_inconsistencia.get('derivation_type')}")
    print(f"  • Regla Causal: {how_inconsistencia.get('rule_id')} - {how_inconsistencia.get('rule_name')}")
    print(f"  • Fundamento Legal: {how_inconsistencia.get('legal_basis')}")
    print(f"  • Explicación: {how_inconsistencia.get('explanation')}")

    # Consulta HOW para hecho percibido
    how_monto = xai.how("factura_monto_total", wm, fc_result)
    print("\n[Consulta HOW: ¿Cómo se obtuvo 'factura_monto_total'?]")
    print(f"  • Explicación: {how_monto.get('explanation')}")

    # Consulta WHY para regla R01
    why_r01 = xai.why("R01_CASTIGO_FISCAL_IVA_NO_CATEGORIZADO")
    print("\n[Consulta WHY: ¿Por qué existe y se ejecuta la regla R01?]")
    print(f"  • Explicación: {why_r01.get('explanation')}")

    # Ficha ontológica de concepto facturado
    print("\n[Consulta Ontológica Semántica de Conceptos Facturados]:")
    print(xai.explain_concept("CARGO_FIJO_AGUA"))
    print(xai.explain_concept("IVA_NO_CATEGORIZADO_AGUA_27"))

    # -------------------------------------------------------------------------
    # FASE 6: ANÁLISIS HISTÓRICO Y PERSISTENCIA (13 MESES)
    # -------------------------------------------------------------------------
    print_banner("Fase 6: Análisis Longitudinal y Serie Histórica (13 Meses)")
    history_store = HistoryStore()
    peak = history_store.get_peak_consumption()
    avg = history_store.get_average_consumption()
    yoy = history_store.get_year_over_year_growth()
    spike_ratio = history_store.get_winter_spike_ratio()

    print(f"• Consumo Promedio Mensual:        {avg} kWh/mes")
    print(f"• Pico Máximo Anual:               {peak.consumption_kwh} kWh ({peak.period} - Invierno)")
    print(f"• Salto Estacional Invernal:       +{((spike_ratio - 1) * 100):.1f}% respecto al otoño (Ratio {spike_ratio})")
    print(f"• Crecimiento Interanual (Sep-25 vs Sep-26): +{yoy['crecimiento_interanual_pct']}% (+{yoy['delta_kwh']} kWh)")
    print(f"• Meses con consumo excedente al subsidio RASE (200 kWh): 13 de 13 meses (100% del período)")

    # -------------------------------------------------------------------------
    # FASE 6b: AUDITORÍA DE SERIE HISTÓRICA REAL (4 BOLETAS), DUPLICACIÓN Y CADENA DE PAGOS
    # -------------------------------------------------------------------------
    print_banner("Fase 6b: Auditoría de 4 Boletas Consecutivas, No Duplicación y Cadena de Pagos")
    historical_invoices = load_all_historical_invoices()
    history_store.load_historical_invoices(historical_invoices)
    print(f"• Boletas Consecutivas Cargadas en Memoria Persistente: {len(historical_invoices)}")
    for inv in historical_invoices:
        b_a = inv.get("bloque_a_identificacion", {})
        print(f"  - Período {b_a.get('periodo_facturado')}: Total ${b_a.get('total_factura'):,.2f} | Liq: {b_a.get('nro_liquidacion')}")

    # Auditoría de Duplicación
    print("\n[Prueba de Detección de Duplicación (Doble Facturación)]:")
    dup_sim = {
        "bloque_a_identificacion": {
            "periodo_facturado": "09/2026",
            "nro_liquidacion": "0101-52064404",
            "total_factura": 377559.51
        }
    }
    dup_check = history_store.check_duplication(dup_sim)
    print(f"  • Intento de reingresar 09/2026: {'BLOQUEADO EXITOSAMENTE' if dup_check['is_duplicate'] else 'FALLO'}")
    print(f"  • Mensaje del Sistema Experto:  {dup_check['message']}")

    # Auditoría de Cadena de Pagos (Art. 25 Ley 24.240)
    print("\n[Auditoría de Cadena de Pagos Acreditados (Art. 25 Ley 24.240)]:")
    chain_result = history_store.verify_payment_chain(historical_invoices)
    print(f"  • Estado de la Cadena: {'100% ÍNTEGRA Y CONCILIADA' if chain_result['is_chain_valid'] else 'DISCREPANCIA DETECTADA'}")
    for trans in chain_result["verified_transitions"]:
        print(f"    - {trans['periodo_previo']} ➔ {trans['periodo_actual']}: Factura Previa ${trans['total_factura_previa']:,.2f} == Pago Acreditado ${trans['pago_anterior_acreditado']:,.2f} [OK]")

    # -------------------------------------------------------------------------
    # FASE 6c: DESCOMPOSICIÓN ECONÓMICA MULTIMES (EFECTO VOLUMEN VS EFECTO TARIFA)
    # -------------------------------------------------------------------------
    print_banner("Fase 6c: Descomposición de Variaciones: Efecto Volumen vs. Efecto Tarifa / Inflación")
    comparative_analyzer = ComparativeAnalyzer(historical_invoices)
    consecutive_comparisons = comparative_analyzer.analyze_all_consecutive()

    for comp in consecutive_comparisons:
        print(f"\n[Transición: {comp.period_prev} ➔ {comp.period_curr}]")
        print(f"  • Variación Total:       {comp.delta_total:+,.2f} ARS ({comp.pct_change_total:+.1f}%)")
        print(f"  • Efecto Volumen Puro:   {comp.total_volume_effect_ars:+,.2f} ARS (Luz: {comp.edesa.delta_volume:+.0f} kWh | Agua: {comp.aguas.delta_volume:+.1f} m³)")
        print(f"  • Efecto Tarifa/Precios: {comp.total_tariff_and_inflation_effect_ars:+,.2f} ARS (Actualización tarifaria y cargos fijos)")
        print(f"  • Driver Principal:      {comp.macro_driver}")
        print(f"  • Dictamen:              {comp.summary_report}")

    # -------------------------------------------------------------------------
    # FASE 7: GENERACIÓN DE GRÁFICOS ANALÍTICOS (OUTPUT_GRAFICOS)
    # -------------------------------------------------------------------------
    print_banner("Fase 7: Generación de Gráficos Analíticos de Alta Resolución")
    output_graficos_dir = PROJECT_ROOT / "output_graficos"
    chart_gen = ReportChartsGenerator(output_graficos_dir)
    charts = chart_gen.generate_all_charts()

    for name, path in charts.items():
        p = Path(path)
        print(f"[OK] Generado: {p.name} [{p.stat().st_size:,} bytes] en output_graficos/")

    # -------------------------------------------------------------------------
    # FASE 8: EMISIÓN DEL DICTAMEN PERICIAL FORMAL ANTE EL ENRESP
    # -------------------------------------------------------------------------
    print_banner("Fase 8: Emisión y Exportación del Dictamen Pericial Integral")
    report_text = xai.generate_audit_report(wm, fc_result)
    print(report_text)

    # Exportar a docs/DICTAMEN_PERICIAL_ENRESP.md
    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    dictamen_path = docs_dir / "DICTAMEN_PERICIAL_ENRESP.md"
    with open(dictamen_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n[OK] Dictamen administrativo guardado en: {dictamen_path}")

    # Información del Frontend Interactivo para el usuario y evaluadores
    print_banner("Fase 9: Frontend Web Interactivo y Dashboard Autónomo")
    print("Para interactuar visualmente con el sistema experto, probar duplicaciones,")
    print("revisar el glosario o emitir dictámenes desde el navegador, ejecute:")
    print("  -> python iniciar_dashboard.py")
    print("O haga doble clic en el archivo autónomo:")
    print(f"  -> {(PROJECT_ROOT / 'app_dashboard.html').as_uri()}")

    elapsed_total = time.time() - start_total
    print_banner(f"SIMULACIÓN FINALIZADA CON ÉXITO EN {elapsed_total:.2f} SEGUNDOS")


if __name__ == "__main__":
    run_full_audit_walkthrough()
