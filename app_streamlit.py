"""
Aplicación Web Interactiva en Streamlit para Auditoría de Facturas de Salta
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Ejecución:
    streamlit run app_streamlit.py
"""

import sys
import copy
from pathlib import Path
import json

# Configurar path base
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    import streamlit as st
except ImportError:
    # Mensaje informativo si se ejecuta directamente con python sin streamlit
    print("Streamlit no se encuentra instalado en este entorno.")
    print("Para usar la versión web sin dependencias, ejecute: python iniciar_dashboard.py")
    print("O abra directamente 'app_dashboard.html' con doble clic en su navegador.")
    sys.exit(0)

from src.knowledge_base.default_facts import load_all_historical_invoices, load_facts_for_period, extract_facts_from_dict
from src.knowledge_base.rules_enresp import get_all_enresp_rules
from src.knowledge_base.concept_glossary import ConceptGlossary
from src.engine.working_memory import WorkingMemory
from src.engine.inference_engine import InferenceEngine
from src.engine.explanation_module import ExplanationModule
from src.engine.comparative_analyzer import ComparativeAnalyzer
from src.persistence.history_store import HistoryStore


def main():
    st.set_page_config(
        page_title="Sistema Experto Tarifario Salta | UGD",
        page_icon="⚡",
        layout="wide"
    )

    st.title("⚡ Sistema Experto de Auditoría Tarifaria Multidominio")
    st.caption("Licenciatura en Gestión de Recursos Tecnológicos — Universidad Gastón Dachary | GT110 PIA 2026")
    st.markdown("**Estudiante:** Estudiante UGD (Matrícula: `100001`) | **Docentes:** Prof. Agustín Encina, Dante Sicardi")

    # Cargar datos
    invoices = load_all_historical_invoices()
    analyzer = ComparativeAnalyzer(invoices)
    history = HistoryStore()
    history.load_historical_invoices(invoices)
    rules = get_all_enresp_rules()
    engine = InferenceEngine(rules)
    xai = ExplanationModule(rules)

    tabs = st.tabs([
        "📋 Auditoría de Factura",
        "🧠 Motor de Inferencia & XAI",
        "📊 Comparación Multi-Período",
        "🛡️ Detección de Duplicación",
        "📖 Glosario Ontológico",
        "⚖️ Dictamen ENRESP"
    ])

    # TAB 1: Auditoría individual
    with tabs[0]:
        st.subheader("Auditoría Individual de Factura de Salta")
        col_sel, col_up = st.columns([2, 2])
        with col_sel:
            periodo = st.selectbox(
                "Seleccionar comprobante emitido a auditar:",
                ["06/2026", "07/2026", "08/2026", "09/2026"],
                index=3
            )
        with col_up:
            uploaded_file = st.file_uploader("O cargar archivo JSON de factura personalizado:", type=["json"])

        if uploaded_file is not None:
            try:
                custom_data = json.load(uploaded_file)
                dup_res = history.check_duplication(custom_data)
                if dup_res["is_duplicate"]:
                    st.error(f"🚫 {dup_res['message']} (Regla R15 disparada)")
                else:
                    st.success("✅ Factura válida y no duplicada en el histórico.")
                facts = extract_facts_from_dict(custom_data)
                periodo = custom_data.get("bloque_a_identificacion", {}).get("periodo_facturado", "CARGADA_JSON")
            except Exception as ex:
                st.error(f"Error procesando archivo JSON: {ex}")
                facts = load_facts_for_period(periodo)
        else:
            facts = load_facts_for_period(periodo)

        wm = WorkingMemory(facts)

        k1, k2, k3, k4 = st.columns(4)
        total = wm.get("factura_monto_total", 0.0)
        edesa = wm.get("electricidad_subtotal_ars", 0.0) + wm.get("electricidad_incidencia_alumbrado_ars", 0.0)
        aguas = wm.get("agua_subtotal_ars", 0.0)
        muni = wm.get("municipal_subtotal_ars", 0.0) + wm.get("alumbrado_canon_lusal_ars", 0.0)

        k1.metric("Total Factura", f"${total:,.2f}")
        k2.metric("Electricidad EDESA", f"${edesa:,.2f}", f"{wm.get('electricidad_consumo_activo_kwh')} kWh")
        k3.metric("Aguas del Norte", f"${aguas:,.2f}", f"{wm.get('agua_consumo_volumen_m3')} m³")
        k4.metric("Tasas Municipales", f"${muni:,.2f}")

        st.progress(edesa / total if total > 0 else 0, text=f"Incidencia Eléctrica: {(edesa/total*100):.1f}%")

    # TAB 2: Motor de Inferencia
    with tabs[1]:
        st.subheader("Ejecución del Motor de Inferencia Simbólico")
        fc_res = engine.forward_chain(wm)
        st.success(f"Quiescencia alcanzada: {fc_res.rules_fired_count} reglas disparadas.")

        st.write("### Anomalías y Dictámenes Derivados")
        anomalies = wm.get_by_category("AUDIT_DERIVED")
        for f in anomalies:
            rule_id = f.metadata.get("rule_id", f.source)
            sev = f.metadata.get("severity", "INFO")
            with st.expander(f"[{sev}] {f.name} — Regla: {rule_id}"):
                st.write(f"**Valor:** {f.value}")
                st.write(f"**Descripción:** {f.description}")
                st.write(f"**Impacto Financiero:** ${getattr(f, 'financial_impact_ars', 0.0):,.2f} ARS")
                st.write(f"**Fundamento Legal:** {f.metadata.get('legal_basis')}")
                st.write(f"**Acción Remedial:** {f.metadata.get('remedy_action')}")

    # TAB 3: Comparación multi-período
    with tabs[2]:
        st.subheader("Análisis Longitudinal y Descomposición de Variaciones")
        trans = st.selectbox(
            "Seleccionar transición intermensual a descomponer:",
            ["06/2026 -> 07/2026 (Pico Invierno)", "07/2026 -> 08/2026 (Fin Pico)", "08/2026 -> 09/2026 (Transición)"]
        )
        p_prev, p_curr = trans.split()[0], trans.split()[2]
        comp = analyzer.compare_periods(p_prev, p_curr)

        c1, c2, c3 = st.columns(3)
        c1.metric("Variación Total", f"${comp.delta_total:,.2f}", f"{comp.pct_change_total:+.1f}%")
        c2.metric("Efecto Volumen", f"${comp.total_volume_effect_ars:,.2f}")
        c3.metric("Efecto Tarifa / Inflación", f"${comp.total_tariff_and_inflation_effect_ars:,.2f}")

        st.info(f"**Driver Principal:** {comp.macro_driver} — {comp.summary_report}")

    # TAB 4: Duplicación e integridad
    with tabs[3]:
        st.subheader("Detector de Duplicación y Validación de Cadena de Pagos")
        chain_res = history.verify_payment_chain()
        if chain_res["is_chain_valid"]:
            st.success("✅ Cadena de pagos 100% íntegra (Art. 25 Ley 24.240). Todos los pagos previos coinciden.")
        for trans in chain_res["verified_transitions"]:
            st.write(f"• {trans['periodo_previo']} ➔ {trans['periodo_actual']}: ${trans['pago_anterior_acreditado']:,.2f} [OK]")

        st.write("---")
        st.write("### Pruebas Interactivas de Detección de Anomalías")
        c_sim1, c_sim2, c_sim3 = st.columns(3)
        with c_sim1:
            if st.button("🚫 Simular Duplicado (09/2026)"):
                dup_sample = {
                    "bloque_a_identificacion": {
                        "periodo_facturado": "09/2026",
                        "nro_liquidacion": "0101-52064404"
                    }
                }
                res = history.check_duplication(dup_sample)
                st.error(f"{res['message']} (R15_DETECCION_FACTURA_DUPLICADA)")

        with c_sim2:
            if st.button("⚠️ Simular Solapamiento"):
                bad_inv = copy.deepcopy(invoices[3])
                bad_inv["bloque_a_identificacion"]["periodo_facturado"] = "10/2026"
                bad_inv["bloque_b_electricidad_edesa"]["periodo_lectura"]["desde"] = "2026-08-01"
                res = history.check_reading_overlap(bad_inv)
                st.warning(f"Solapamiento detectado: {res['details'][0]} (R16)")

        with c_sim3:
            if st.button("❌ Simular Quiebre de Pagos"):
                bad_invs = copy.deepcopy(invoices)
                bad_invs[3]["bloque_a_identificacion"]["pago_anterior_registrado"] = 200000.0
                res = history.verify_payment_chain(bad_invs)
                st.error(f"Inconsistencia: {res['discrepancies'][0]['motivo']} (R17)")

    # TAB 5: Glosario
    with tabs[4]:
        st.subheader("Glosario Conceptual y Ontológico")
        concepts = ConceptGlossary.get_all_concepts()
        for k, c in concepts.items():
            with st.expander(f"{c.name} ({c.issuer})"):
                st.write(f"**Base Legal:** {c.legal_basis}")
                st.write(f"**Descripción:** {c.description}")
                st.write(f"**¿Elegible para desdoblar?:** {'SÍ' if c.is_split_eligible_enresp else 'NO'}")
                st.write(f"**Mitigación:** {c.mitigation_action}")

    # TAB 6: Dictamen
    with tabs[5]:
        st.subheader("Dictamen Pericial Administrativo")
        report_text = xai.generate_audit_report(wm, fc_res)
        st.text_area("Dictamen Formal ENRESP", report_text, height=400)
        st.download_button(
            "Descargar Dictamen (.md)",
            report_text,
            file_name=f"DICTAMEN_PERICIAL_ENRESP_{periodo.replace('/', '_')}.md"
        )


if __name__ == "__main__":
    main()
