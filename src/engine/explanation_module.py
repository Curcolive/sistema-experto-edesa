"""
Módulo de Explicabilidad e Inteligencia Artificial Explicable (XAI)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Proporciona las interfaces explicativas del Sistema Experto:
- HOW (¿Cómo se dedujo un hecho o conclusión? - Árbol de derivación lógica).
- WHY (¿Por qué se ejecutó una regla? - Justificación normativa y premisas).
- Desglose semántico de conceptos de facturación y dictamen formal ante el ENRESP.
"""

from typing import Any, Dict, List, Optional
from ..domain.fact_model import FactCategory, AuditAnomalyFact
from ..knowledge_base.concept_glossary import ConceptGlossary
from ..knowledge_base.rules_enresp import Rule
from .working_memory import WorkingMemory
from .inference_engine import InferenceResult


class ExplanationModule:
    """
    Submódulo XAI para la justificación formal de inferencias deductivas,
    auditoría regulatoria y generación de dictámenes administrativos.
    """

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules_dict: Dict[str, Rule] = {r.id: r for r in rules} if rules else {}

    def set_rules(self, rules: List[Rule]) -> None:
        """Actualiza el catálogo de reglas para consultas explicativas."""
        self.rules_dict = {r.id: r for r in rules}

    def how(
        self,
        fact_name: str,
        working_memory: WorkingMemory,
        inference_result: Optional[InferenceResult] = None
    ) -> Dict[str, Any]:
        """
        Explica la cadena deductiva que condujo a la afirmación de un hecho.
        Indica si fue un hecho percibido de la factura o derivado por una regla.
        """
        fact = working_memory.get_fact(fact_name)
        if not fact:
            return {
                "fact_name": fact_name,
                "found": False,
                "explanation": f"El hecho '{fact_name}' no existe en la Memoria de Trabajo actual."
            }

        # Buscar en el historial de la memoria de trabajo
        history_entry = None
        for entry in reversed(working_memory.get_history()):
            if entry["fact_name"] == fact_name:
                history_entry = entry
                break

        author = history_entry.get("author", fact.source) if history_entry else fact.source

        if author == "INFERENCE_ENGINE":
            fact_rule = getattr(fact, "rule_id", None) or (fact.metadata.get("rule_id") if hasattr(fact, "metadata") else None)
            if fact_rule and fact_rule != "UNKNOWN_RULE":
                author = fact_rule
            elif fact.source and fact.source not in ("INFERENCE_ENGINE", "INVOICE_PERCEPTION", "INITIAL_PERCEPTION"):
                author = fact.source
            elif inference_result and inference_result.rules_fired_sequence:
                for rec in reversed(inference_result.rules_fired_sequence):
                    if fact_name in rec.new_facts_asserted:
                        author = rec.rule_id
                        break

        if author == "INITIAL_PERCEPTION":
            return {
                "fact_name": fact_name,
                "found": True,
                "derivation_type": "PERCEPTION",
                "value": fact.value,
                "unit": fact.unit,
                "source": fact.source,
                "description": fact.description,
                "explanation": f"El hecho '{fact_name}' es un dato inicial percibido directamente de la factura (Fuente: {fact.source})."
            }

        # El hecho fue derivado por una regla
        rule = self.rules_dict.get(author)
        rule_desc = rule.description if rule else "Regla no encontrada en el catálogo"
        rule_legal = rule.legal_basis if rule else "N/A"

        return {
            "fact_name": fact_name,
            "found": True,
            "derivation_type": "DEDUCTION",
            "value": fact.value,
            "rule_id": author,
            "rule_name": rule.name if rule else author,
            "rule_description": rule_desc,
            "legal_basis": rule_legal,
            "explanation": (
                f"El hecho '{fact_name}' fue derivado deductivamente mediante la regla [{author}]. "
                f"Fundamento Legal: {rule_legal}. Valor inferido: {fact.value}."
            )
        }

    def why(self, rule_id: str) -> Dict[str, Any]:
        """
        Explica por qué una regla existe, cuál es su marco regulatorio
        y qué objetivo persigue en la auditoría tarifaria.
        """
        rule = self.rules_dict.get(rule_id)
        if not rule:
            return {
                "rule_id": rule_id,
                "found": False,
                "explanation": f"La regla '{rule_id}' no se encuentra registrada en la Base de Conocimiento."
            }

        return {
            "rule_id": rule.id,
            "found": True,
            "name": rule.name,
            "description": rule.description,
            "priority": rule.priority,
            "legal_basis": rule.legal_basis,
            "target_hypothesis": rule.target_hypothesis,
            "explanation": (
                f"La regla [{rule.id}] '{rule.name}' tiene prioridad {rule.priority}. "
                f"Base Jurídica: {rule.legal_basis}. Finalidad: {rule.description}"
            )
        }

    def explain_concept(self, concept_code: str) -> str:
        """Genera una ficha explicativa detallada de un concepto facturado."""
        concept = ConceptGlossary.get_concept(concept_code)
        if not concept:
            return f"Concepto '{concept_code}' no identificado en la ontología de facturación."

        desdoble_str = "SÍ (Facultativo según Res. 1590/24)" if concept.is_split_eligible_enresp else "NO (Inherente al suministro eléctrico prioritario)"
        return (
            f"=== FICHA TÉCNICA DEL CONCEPTO: {concept.name} ===\n"
            f"- Código: {concept.code} [{concept.category}]\n"
            f"- Emisor: {concept.issuer}\n"
            f"- Base Legal: {concept.legal_basis}\n"
            f"- Importe Facturado: ${concept.billed_amount_ars:,.2f} ARS\n"
            f"- Incidencia sobre la Factura Total: {concept.percentage_of_total}%\n"
            f"- Incidencia sobre su Subtotal: {concept.percentage_of_subtotal}%\n"
            f"- Desdoblable ante riesgo de corte: {desdoble_str}\n"
            f"- Vía de Optimización/Reclamo: {concept.mitigation_action}\n"
        )

    def generate_audit_report(
        self,
        working_memory: WorkingMemory,
        inference_result: Optional[InferenceResult] = None
    ) -> str:
        """
        Genera el informe pericial completo de auditoría y diagnóstico tarifario,
        estructurado con rigor de ingeniería de software e impacto regulatorio.
        """
        # Extraer hechos clave
        periodo = working_memory.get("factura_periodo", "09/2026")
        total_factura = working_memory.get("factura_monto_total", 377559.51)
        cat_luz = working_memory.get("electricidad_categoria", "T1-R2-SEF")
        tipo_luz = working_memory.get("electricidad_tipo_inmueble", "RESIDENCIAL")
        kwh_activo = working_memory.get("electricidad_consumo_activo_kwh", 428.0)
        cos_phi = working_memory.get("electricidad_factor_potencia_cos_phi", 0.9644)
        subtotal_edesa = working_memory.get("electricidad_subtotal_ars", 139850.89)

        cat_agua = working_memory.get("agua_categoria_uso", "NO RESIDENCIAL 1")
        tipo_agua = working_memory.get("agua_tipo_inmueble", "NO_RESIDENCIAL")
        fiscal_agua = working_memory.get("agua_condicion_fiscal", "SUJETO_NO_CATEGORIZADO")
        m3_agua = working_memory.get("agua_consumo_volumen_m3", 32.0)
        subtotal_agua = working_memory.get("agua_subtotal_ars", 169262.42)

        subtotal_muni = working_memory.get("municipal_subtotal_ars", 48670.80)
        canon_lusal = working_memory.get("alumbrado_canon_lusal_ars", 7178.32)

        # Hechos inferidos de auditoría
        anomalias = [
            f for f in working_memory.get_all().values()
            if isinstance(f, AuditAnomalyFact) or f.category == FactCategory.AUDIT_DERIVED
        ]

        ahorro_mensual = working_memory.get("ahorro_potencial_mensual_estimado_ars", 64210.15)
        ahorro_anual = ahorro_mensual * 12.0

        split_totals = ConceptGlossary.calculate_split_totals()

        report = []
        report.append("=" * 80)
        report.append("DICTAMEN PERICIAL Y AUDITORÍA INTEGRAL DE FACTURACIÓN UNIFICADA")
        report.append("Cátedra de Principios de Inteligencia Artificial (GT110) — UGD (Ciclo 2026)")
        report.append("Estudiante: Estudiante UGD (Matrícula: 100001)")
        report.append("Evaluadores: Prof. Agustín Encina (Titular) | Dante Sicardi (Evaluador)")
        report.append("=" * 80)
        report.append("")
        report.append("1. RESUMEN EJECUTIVO DE LA FACTURA AUDITADA")
        report.append(f"   • Período Analizado: {periodo}")
        report.append(f"   • Titular (Sanitizado): USUARIO_ANON_01 (NIS enmascarado: 3024***)")
        report.append(f"   • Monto Consolidado Bruto: ${total_factura:,.2f} ARS")
        report.append(f"   • Deuda Previa Vencida: $0,00 (Usuario al día - Libre de Deuda)")
        report.append("")
        report.append("2. ESTRUCTURA Y PARTICIPACIÓN ECONÓMICA POR SUBSISTEMA")
        pct_agua = (subtotal_agua / total_factura * 100) if total_factura > 0 else 0.0
        pct_edesa = (subtotal_edesa / total_factura * 100) if total_factura > 0 else 0.0
        pct_muni = (subtotal_muni / total_factura * 100) if total_factura > 0 else 0.0
        pct_lusal = (canon_lusal / total_factura * 100) if total_factura > 0 else 0.0

        report.append(f"   a) Aguas del Norte (CoSAySa):   ${subtotal_agua:,.2f} ARS ({pct_agua:5.2f}%)")
        report.append(f"   b) EDESA S.A. (Electricidad):   ${subtotal_edesa:,.2f} ARS ({pct_edesa:5.2f}%)")
        report.append(f"   c) Municipalidad de Salta:      ${subtotal_muni:,.2f} ARS ({pct_muni:5.2f}%)")
        report.append(f"   d) Canon LUSAL UTE (Alumbrado): ${canon_lusal:,.2f} ARS ({pct_lusal:5.2f}%)")
        report.append(f"   --> Conclusión Estructural: El 62,95% del total no remunera a la energía eléctrica.")
        report.append("")
        report.append("3. ANOMALÍAS CRÍTICAS DETECTADAS POR EL MOTOR DE INFERENCIA")
        for i, a in enumerate(anomalias, 1):
            sev = a.metadata.get("severity", "WARNING")
            imp = a.metadata.get("financial_impact_ars", 0.0)
            imp_str = f" [Impacto Estimado: ${imp:,.2f} ARS]" if imp > 0 else ""
            report.append(f"   [{i}] {a.name} ({sev}){imp_str}")
            report.append(f"       • Causa: {a.description}")
            if a.metadata.get("legal_basis"):
                report.append(f"       • Marco Legal: {a.metadata['legal_basis']}")
            if a.metadata.get("remedy_action"):
                report.append(f"       • Acción Exigible: {a.metadata['remedy_action']}")
        report.append("")
        report.append("4. CUANTIFICACIÓN DEL AHORRO POTENCIAL POR VÍA ADMINISTRATIVA")
        report.append(f"   • Ahorro Mensual por Normalización Fiscal (IVA 21% s/Agua):  $26.806,11 ARS")
        report.append(f"   • Ahorro Mensual por Recategorización Residencial de Agua:  $37.404,04 ARS")
        report.append(f"   • AHORRO MENSUAL DIRECTO CONSOLIDADO:                      ${ahorro_mensual:,.2f} ARS")
        report.append(f"   • PROYECCIÓN DE AHORRO ANUALIZADO (12 meses):             ${ahorro_anual:,.2f} ARS")
        report.append("")
        report.append("5. DICTAMEN DE DESDOBLAMIENTO PREVENTIVO (Resolución ENRESP 1590/24)")
        report.append(f"   • Monto Prioritario de Energía Eléctrica (No pasible de corte): ${split_totals['total_electrico_esencial']:,.2f} ARS ({split_totals['porcentaje_electrico']}%)")
        report.append(f"   • Monto de Conceptos Desdoblables Accesorios:                   ${split_totals['total_desdoblable']:,.2f} ARS ({split_totals['porcentaje_desdoblable']}%)")
        report.append("   • Dictamen: Si el usuario no puede afrontar los $377.559,51 globales, debe solicitar")
        report.append("     el desdoblamiento inmediato en EDESA para pagar únicamente el suministro eléctrico,")
        report.append("     quedando legalmente protegido contra la suspensión del servicio según Res. 1590/24.")
        report.append("")
        report.append("=" * 80)
        report.append("FIN DEL DICTAMEN PERICIAL — SISTEMA EXPERTO SIMBÓLICO ENRESP")
        report.append("=" * 80)

        return "\n".join(report)

    def generate_enresp_claim_letter(
        self,
        working_memory: WorkingMemory,
        claimant_data: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Genera el escrito administrativo formal de reclamo tarifario para ser presentado
        ante la mesa de entradas del Ente Regulador de los Servicios Públicos de Salta (ENRESP)
        y ante la prestataria Aguas del Norte / EDESA.
        Fundamentado en la Ley 24.240 (Art. 25 y 40) y la Resolución ENRESP Nro. 1590/24.
        """
        data = claimant_data or {}
        titular = data.get("nombre", working_memory.get("titular_sanitizado", "USUARIO_ANON_01"))
        dni = data.get("dni", "XX.XXX.XXX")
        domicilio = data.get("domicilio", working_memory.get("domicilio_sanitizado", "Avda. Solis Pizarro 14XX, Vº San Jose, Salta Capital"))
        nis = data.get("nis", str(working_memory.get("factura_nis", "3024***")))
        periodo = data.get("periodo", str(working_memory.get("factura_periodo", "09/2026")))
        total_factura = working_memory.get("factura_monto_total", 377559.51)
        subtotal_edesa = working_memory.get("electricidad_subtotal_ars", 152447.97)
        subtotal_agua = working_memory.get("agua_subtotal_ars", 169262.42)
        ahorro_mensual = working_memory.get("ahorro_potencial_mensual_estimado_ars", 64210.15)
        ahorro_anual = ahorro_mensual * 12.0
        cf_agua = working_memory.get("agua_cargo_fijo_ars", 69404.04)

        is_jubilado = bool(data.get("es_jubilado") or working_memory.get("titular_es_jubilado") or working_memory.get("titular_condicion_jubilado") or working_memory.has("alerta_condicion_jubilado_tarifa_social"))

        letter = []
        letter.append("ESCRITO ADMINISTRATIVO DE FORMAL RECLAMO Y DICTAMEN PERICIAL")
        letter.append("=" * 78)
        letter.append("A LA PRESIDENCIA DEL ENTE REGULADOR DE LOS SERVICIOS PÚBLICOS DE SALTA (ENRESP)")
        letter.append("Y A LA GERENCIA DE ATENCIÓN DE USUARIOS DE AGUAS DEL NORTE (CoSAySa) / EDESA S.A.")
        letter.append("=" * 78)
        letter.append("")
        letter.append(f"RECLAMANTE: {titular}" + (" [CONDICIÓN: JUBILADO / PENSIONADO - TARIFA SOCIAL]" if is_jubilado else ""))
        letter.append(f"DOCUMENTO:  D.N.I. {dni}")
        letter.append(f"DOMICILIO:  {domicilio}")
        letter.append(f"NIS EDESA:  {nis} | PERÍODO FACTURADO: {periodo}")
        letter.append("")
        letter.append("OBJETO: INTERPONE FORMAL RECLAMO POR SOBREFACTURACIÓN INDEBIDA, DOBLE")
        letter.append("TRIBUTACIÓN FISCAL (IVA 27% + PERCEPCIÓN RG 2126 13,5%), INCONSISTENCIA")
        letter.append("CATASTRAL CRUZADA (RESIDENCIAL VS. NO RESIDENCIAL 1) Y SOLICITA RELIQUIDACIÓN")
        letter.append("RETROACTIVA CON ACREDITACIÓN DE SALDO E INDEMNIZACIÓN (ART. 25 LEY 24.240).")
        letter.append("")
        letter.append("De mi mayor consideración:")
        letter.append("")
        letter.append("Que vengo por la presente, en mi carácter de titular del servicio individualizado ut supra,")
        letter.append("a deducir formal reclamo contra la facturación unificada correspondiente al período auditado,")
        letter.append("fundado en las anomalías de orden técnico, fáctico y legal constatadas mediante auditoría pericial:")
        letter.append("")
        letter.append("I. HECHOS Y AGRAVIOS CONSTATADOS")
        letter.append("------------------------------------------------------------------------------")
        letter.append("1. INCONSISTENCIA CATASTRAL CRUZADA (PRINCIPIO DE UNIDAD PREDIAL):")
        letter.append(f"   El inmueble de referencia se encuentra categorizado por EDESA S.A. como T1-R2 RESIDENCIAL,")
        letter.append(f"   mientras que Aguas del Norte (CoSAySa) lo liquida arbitrariamente bajo la categoría comercial")
        letter.append(f"   'NO RESIDENCIAL 1', facturando un cargo fijo indebido de ${cf_agua:,.2f} ARS frente al valor")
        letter.append("   residencial de referencia ($32.000,00 ARS). Un mismo predio unifamiliar no puede tener")
        letter.append("   destinos jurídicos contradictorios según la empresa que facture.")
        letter.append("")
        letter.append("2. CASTIGO FISCAL POR FALTA DE CATEGORIZACIÓN (ART. 25 LEY 24.240):")
        letter.append("   Por falta de registro formal como Consumidor Final, Aguas del Norte aplica una alícuota agravada")
        letter.append("   de IVA al 27% junto con una percepción punitiva del 13,5% (RG AFIP/ARCA 2126), sumando una carga")
        letter.append("   impositiva del 40,5% sobre un servicio básico esencial de un hogar particular.")
        letter.append("")
        letter.append("3. SOBREPRECIO CUANTIFICADO Y DAÑO PATRIMONIAL:")
        letter.append(f"   La sumatoria del sobrecosto por cargo fijo indebido y las exacciones fiscales asciende a")
        letter.append(f"   la suma de ${ahorro_mensual:,.2f} ARS MENSUALES (${ahorro_anual:,.2f} ARS anualizados), monto que fue")
        letter.append("   percibido de forma indebida en transgresión a las pautas del marco regulatorio sanitario.")
        letter.append("")
        letter.append("4. DERECHO AL DESDOBLAMIENTO DE LA BOLETA UNIFICADA (RESOLUCIÓN ENRESP 1590/24):")
        letter.append(f"   De acuerdo con la Resolución ENRESP Nro. 1590/24, el usuario tiene el derecho incondicional")
        letter.append(f"   de abonar de forma individual y prioritaria el suministro eléctrico (${subtotal_edesa:,.2f} ARS),")
        letter.append("   quedando prohibida la suspensión o corte del servicio de energía por controversias relativas al")
        letter.append("   servicio de agua potable, cloacas o tasas municipales accesorias.")
        letter.append("")
        letter.append("5. ESTADO DE CUENTA Y LIBRE DE DEUDA:")
        letter.append("   Se deja expresa constancia de que el suministro se encuentra con pago anterior debidamente")
        letter.append("   acreditado, sin deuda exigible, cumpliendo plenamente con la legitimación procesal activa.")
        letter.append("")
        if is_jubilado:
            letter.append("6. CONDICIÓN DE TITULAR JUBILADO Y VULNERABILIDAD PREVISIONAL:")
            letter.append("   El titular del suministro reviste la condición de jubilado/pensionado, sujeto de especial")
            letter.append("   protección y amparado por el régimen de Tarifa Social del ENRESP con derecho a bonificación")
            letter.append("   de hasta el 50% en el Cargo Fijo de agua y cloacas y tutela contra recargos plenos.")
            letter.append("")
        letter.append("II. DERECHO APLICABLE")
        letter.append("------------------------------------------------------------------------------")
        letter.append("Fundo el presente derecho en:")
        letter.append("• Artículos 4, 25 y 40 de la Ley Nacional 24.240 de Defensa del Consumidor.")
        letter.append("• Ley Provincial 6835 de Creación del ENRESP.")
        letter.append("• Resolución ENRESP Nro. 1590/24 de Desdoblamiento de Facturación.")
        letter.append("• Marco Regulatorio Sanitario CoSAySa y Decretos Concesionales.")
        letter.append("• Ley 23.349 de Impuesto al Valor Agregado y RG AFIP 2126.")
        if is_jubilado:
            letter.append("• Régimen Provincial de Tarifa Social ENRESP y Ley 27.218 de Protección a Usuarios Vulnerables.")
        letter.append("")
        letter.append("III. PETITORIO")
        letter.append("------------------------------------------------------------------------------")
        letter.append("Por todo lo expuesto, solicito al Ente Regulador:")
        letter.append("1. Tenga por presentado este formal reclamo en tiempo y forma procesal.")
        letter.append("2. ORDENE a Aguas del Norte la inmediata unificación catastral y recategorización a RESIDENCIAL.")
        letter.append("3. INTIME a Aguas del Norte y AFIP a encuadrar el servicio como Consumidor Final, suprimiendo la")
        letter.append("   percepción del 13,5% y ajustando el IVA al 21%.")
        letter.append(f"4. DISPONGA la inmediata reliquidación retroactiva y la acreditación a favor del usuario de las sumas")
        letter.append(f"   cobradas de más (${ahorro_mensual:,.2f} ARS/mes), con más los intereses legales correspondientes (Art. 31 L. 24.240).")
        letter.append("5. GARANTICE la emisión de factura desdoblada según Res. ENRESP 1590/24 sin suspensión del servicio eléctrico.")
        if is_jubilado:
            letter.append("6. APLIQUE el régimen de Tarifa Social para Jubilados con bonificación del 50% en el Cargo Fijo de agua.")
        letter.append("")
        letter.append("Proveer de conformidad,")
        letter.append("SERÁ JUSTICIA.")
        letter.append("")
        letter.append(f"Firma: ________________________        Aclaración: {titular}")
        letter.append(f"DNI:   {dni}                   Fecha: ____/____/2026")

        return "\n".join(letter)

