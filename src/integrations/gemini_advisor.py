"""
Módulo de Integración Opcional con Gemini (Gemini Advisor / Neuro-Simbólico)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Proporciona capacidades neuro-simbólicas complementarias:
1. Lee GEMINI_API_KEY desde variables de entorno o archivo .env en el workspace.
2. Si la API Key está configurada:
   - Conecta con Gemini (ej. gemini-2.5-flash / gemini-1.5-flash) para enriquecer
     el análisis de hábitos de uso de electrodomésticos y personalizar cartas de reclamo.
3. Si la API Key NO está configurada o hay fallos de red/cuota:
   - Opera 100% de manera autónoma en modo determinista local sin lanzar excepciones
     ni degradar el funcionamiento del sistema experto.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import warnings

# Intentar cargar variables desde .env si existe python-dotenv
try:
    from dotenv import load_dotenv
    # Buscar .env en el directorio actual, en integrador/ o en la raíz del workspace
    current_file = Path(__file__).resolve()
    potential_paths = [
        current_file.parent.parent.parent / ".env",
        current_file.parent.parent / ".env",
        Path.cwd() / ".env"
    ]
    for env_path in potential_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break
except ImportError:
    pass


class GeminiAdvisor:
    """
    Asesor Neuro-Simbólico con fallback automático a heurísticas locales.
    """

    DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key.strip() if api_key is not None else os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or self.DEFAULT_MODEL
        self._client = None
        if self.api_key:
            self._init_client()

    def _init_client(self) -> None:
        """Inicializa el cliente de Gemini usando google-genai si está disponible."""
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            # Si falla la inicialización, no rompemos: client queda en None
            self._client = None

    def has_api_key(self) -> bool:
        """Indica si se dispone de una clave de API válida configurada."""
        return bool(self.api_key and len(self.api_key) >= 15)

    def get_api_key_status(self) -> Dict[str, Any]:
        """Retorna el estado de configuración de la clave de Gemini e instrucciones claras."""
        if self.has_api_key():
            masked = self.api_key[:6] + "..." + self.api_key[-4:]
            return {
                "configured": True,
                "masked_key": masked,
                "model": self.model_name,
                "mode": "GEMINI_ACTIVE",
                "message": f"Conexión activa con modelo {self.model_name}."
            }
        else:
            return {
                "configured": False,
                "masked_key": "NO_CONFIGURADA",
                "model": "Motor Heurístico Simbólico Local (UGD 2026)",
                "mode": "LOCAL_HEURISTIC",
                "message": "Operando en modo local 100% determinista sin dependencias externas.",
                "setup_instructions": (
                    "Para activar el enriquecimiento neuro-simbólico con Gemini:\n"
                    "1. Crear un archivo .env en la raíz del proyecto (o definir variable de entorno).\n"
                    "2. Agregar la línea: GEMINI_API_KEY=tu_clave_de_google_ai_studio\n"
                    "3. Reiniciar el dashboard o script."
                )
            }

    def enrich_appliance_diagnostic(
        self,
        audit_result_dict: Dict[str, Any],
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enriquece el diagnóstico de artefactos eléctricos.
        Si Gemini no está configurado o falla, devuelve la respuesta heurística determinista.
        """
        base_summary = audit_result_dict.get("diagnostic_summary", "")
        recommendations = list(audit_result_dict.get("potential_savings_recommendations", []))

        if not self.has_api_key() or self._client is None:
            return {
                "mode": "LOCAL_HEURISTIC",
                "ai_model": "Motor Simbólico Heurístico (UGD 2026)",
                "status": "SUCCESS",
                "diagnostic_text": base_summary,
                "recommendations": recommendations,
                "enrichment_notes": "Generado localmente mediante inferencia analítica determinista."
            }

        # Intento de enriquecimiento con Gemini
        try:
            prompt = (
                f"Eres un auditor energético experto en Salta Capital para la cátedra de Principios de IA (UGD).\n"
                f"Analiza estos datos analíticos verificados matemáticamente de un hogar residencial:\n"
                f"- Consumo Facturado Real: {audit_result_dict.get('invoice_real_kwh')} kWh\n"
                f"- Consumo Teórico Declarado: {audit_result_dict.get('total_theoretical_kwh')} kWh\n"
                f"- Cobertura: {audit_result_dict.get('coverage_percentage')}%\n"
                f"- Excedente sobre tope subsidiado RASE N3 (200 kWh): {audit_result_dict.get('excess_over_rase_subsidy_kwh')} kWh\n"
                f"- Artefacto responsable del salto de tarifa: {audit_result_dict.get('culprit_subsidy_loss_appliance')}\n"
                f"Redacta un diagnóstico conciso, empático y riguroso para el usuario final en 2 párrafos:\n"
                f"1. Explica los hábitos de uso del inventario modelado y la correlación directa con las condiciones "
                f"bioclimáticas de Salta Capital (amplitud térmica diaria del Valle de Lerma de 15°C a 20°C y encendido "
                f"nocturno continuo de calefactores resistivos sin inercia térmica).\n"
                f"2. Plantea 3 recomendaciones prácticas y cuantificadas de hábitos y sustitución tecnológica "
                f"para evitar perder el bloque subsidiado RASE N3 (mantener el consumo bajo 200 kWh/mes y limitar el avance a 6,6 kWh/día)."
            )
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if response and response.text:
                return {
                    "mode": "GEMINI_ENRICHED",
                    "ai_model": self.model_name,
                    "status": "SUCCESS",
                    "diagnostic_text": response.text.strip(),
                    "recommendations": recommendations,
                    "enrichment_notes": "Enriquecido con Gemini sobre la base matemática verificada."
                }
        except Exception as e:
            # Fallback seguro en caso de error de conexión / cuota
            warnings.warn(f"Fallo en llamada a Gemini ({e}). Se activa fallback heurístico local.")

        return {
            "mode": "LOCAL_HEURISTIC_FALLBACK",
            "ai_model": "Motor Simbólico Heurístico (UGD 2026)",
            "status": "FALLBACK_TRIGGERED",
            "diagnostic_text": base_summary,
            "recommendations": recommendations,
            "enrichment_notes": "Fallback local activado tras error transitorio en API de Gemini."
        }

    def draft_personalized_claim_letter(
        self,
        working_memory_or_dict: Any,
        claimant_data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Redacta una carta de reclamo personalizada.
        Usa Gemini si está disponible; en caso contrario, delega al generador jurídico formal local.
        """
        from ..engine.explanation_module import ExplanationModule
        from ..engine.working_memory import WorkingMemory

        wm = working_memory_or_dict if isinstance(working_memory_or_dict, WorkingMemory) else WorkingMemory()
        explainer = ExplanationModule()
        local_letter = explainer.generate_enresp_claim_letter(wm, claimant_data)

        if not self.has_api_key() or self._client is None:
            return {
                "mode": "LOCAL_LEGAL_TEMPLATE",
                "ai_model": "Plantilla Pericial Jurídica ENRESP (UGD 2026)",
                "letter_text": local_letter
            }

        try:
            prompt = (
                f"Eres un abogado perito especialista en Derecho de Usuarios y Servicios Públicos en Salta.\n"
                f"Basándote en el siguiente escrito administrativo formal con citas de la Ley 24.240 y Res. ENRESP 1590/24:\n\n"
                f"{local_letter}\n\n"
                f"Por favor, revisa y optimiza el escrito legal manteniendo todo el rigor técnico, "
                f"todas las cifras monetarias exactas ($64.210,15, etc.) y todas las citas normativas, "
                f"asegurando un tono jurídico impecable para presentar ante la mesa de entradas del ENRESP."
            )
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if response and response.text:
                return {
                    "mode": "GEMINI_ENRICHED",
                    "ai_model": self.model_name,
                    "letter_text": response.text.strip()
                }
        except Exception:
            pass

        return {
            "mode": "LOCAL_LEGAL_TEMPLATE_FALLBACK",
            "ai_model": "Plantilla Pericial Jurídica ENRESP (UGD 2026)",
            "letter_text": local_letter
        }
