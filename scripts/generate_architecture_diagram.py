"""
Generador del Diagrama Formal de Arquitectura de Software del Sistema Experto
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Genera 'grafico_5_arquitectura_sistema_experto.png' y '.svg' a 300 DPI
para inclusión directa en el paper académico en formato IEEE.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def create_architecture_diagram():
    output_dir = Path(r"f:\Universidad Gaston Daechary\Principios de Inteligencia Artificial\04_Desarrollo_TPs\integrador\output_graficos")
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / "grafico_5_arquitectura_sistema_experto.png"
    svg_path = output_dir / "grafico_5_arquitectura_sistema_experto.svg"

    fig, ax = plt.subplots(figsize=(11, 7.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    # Paleta de colores sobria y académica (IEEE style)
    c_l1_bg = "#F0F7FF"
    c_l1_border = "#2563EB"
    c_l1_head = "#1E40AF"

    c_l2_bg = "#F5F3FF"
    c_l2_border = "#6366F1"
    c_l2_head = "#3730A3"

    c_l3_bg = "#ECFDF5"
    c_l3_border = "#059669"
    c_l3_head = "#064E3B"

    box_bg = "#FFFFFF"
    text_dark = "#1F2937"
    text_muted = "#4B5563"

    # ==========================================
    # CAPA 1: INGESTA Y EXTRACCIÓN (Columna Izquierda: x=0.4 a 3.4)
    # ==========================================
    layer1_box = FancyBboxPatch((0.4, 0.4), 3.0, 6.3, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor=c_l1_bg, edgecolor=c_l1_border, linewidth=1.5, zorder=1)
    ax.add_patch(layer1_box)
    ax.text(1.9, 6.35, "CAPA 1: INGESTA Y EXTRACCIÓN", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=c_l1_head)

    # Sub-cajas Capa 1
    # 1. Factura PDF
    b1_1 = FancyBboxPatch((0.6, 4.6), 2.6, 1.35, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#93C5FD", linewidth=1.2, zorder=2)
    ax.add_patch(b1_1)
    ax.text(1.9, 5.65, "Factura Eléctrica EDESA", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(1.9, 5.25, "• PDF Vectorial / Escaneado\n• Régimen Bicuadro Tarifario\n• Servicios Convergentes",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 2. Parser / OCR
    b1_2 = FancyBboxPatch((0.6, 2.65), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#93C5FD", linewidth=1.2, zorder=2)
    ax.add_patch(b1_2)
    ax.text(1.9, 3.8, "Extractor Multi-Estrategia", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(1.9, 3.25, "• PyMuPDF (Estructurado)\n• Expresiones Regulares (Regex)\n• Fallback OCR Tesseract",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 3. Vector de Hechos
    b1_3 = FancyBboxPatch((0.6, 0.7), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#93C5FD", linewidth=1.2, zorder=2)
    ax.add_patch(b1_3)
    ax.text(1.9, 1.85, "Vector de Hechos Iniciales", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(1.9, 1.3, "• 34 Hechos Estructurados (JSON)\n• Segmentación RASE (N1/N2/N3)\n• Mediciones kWh, kVArh, $",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # Flechas internas Capa 1
    a1 = FancyArrowPatch((1.9, 4.6), (1.9, 4.1), arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#2563EB", zorder=4)
    a2 = FancyArrowPatch((1.9, 2.65), (1.9, 2.15), arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#2563EB", zorder=4)
    ax.add_patch(a1)
    ax.add_patch(a2)

    # ==========================================
    # CAPA 2: NÚCLEO SIMBÓLICO DE INFERENCIA (Columna Central: x=4.0 a 7.0)
    # ==========================================
    layer2_box = FancyBboxPatch((4.0, 0.4), 3.0, 6.3, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor=c_l2_bg, edgecolor=c_l2_border, linewidth=1.5, zorder=1)
    ax.add_patch(layer2_box)
    ax.text(5.5, 6.35, "CAPA 2: CORE SIMBÓLICO (IA)", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=c_l2_head)

    # Sub-cajas Capa 2
    # 1. Base de Conocimiento (Desacoplada)
    b2_1 = FancyBboxPatch((4.2, 4.6), 2.6, 1.35, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#A5B4FC", linewidth=1.2, zorder=2)
    ax.add_patch(b2_1)
    ax.text(5.5, 5.65, "Base de Conocimiento (BC)", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(5.5, 5.25, "• 18 Reglas Normativas ENRESP\n• Desacople vía Lambdas (Sicardi)\n• Prioridad / Salience (35 a 100)",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 2. Memoria de Trabajo
    b2_2 = FancyBboxPatch((4.2, 2.65), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#A5B4FC", linewidth=1.2, zorder=2)
    ax.add_patch(b2_2)
    ax.text(5.5, 3.8, "Memoria de Trabajo (WM)", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(5.5, 3.25, "• Estado Activo de Hechos\n• Asersión Dinámica en Sesión\n• Registro Causal de Evidencia",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 3. Motor de Inferencia
    b2_3 = FancyBboxPatch((4.2, 0.7), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#A5B4FC", linewidth=1.2, zorder=2)
    ax.add_patch(b2_3)
    ax.text(5.5, 1.85, "Motor de Inferencia Híbrido", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(5.5, 1.3, "• Forward Chaining (Data-Driven)\n• Backward Chaining (Metas)\n• Detección de Quiescencia",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # Flechas bidireccionales / relaciones Capa 2
    a_bc_wm = FancyArrowPatch((5.5, 4.6), (5.5, 4.1), arrowstyle="<|-|>", mutation_scale=12, lw=1.4, color="#6366F1", zorder=4)
    a_wm_eng = FancyArrowPatch((5.5, 2.65), (5.5, 2.15), arrowstyle="<|-|>", mutation_scale=12, lw=1.4, color="#6366F1", zorder=4)
    ax.add_patch(a_bc_wm)
    ax.add_patch(a_wm_eng)

    # ==========================================
    # CAPA 3: SALIDAS Y EXPLICABILIDAD (Columna Derecha: x=7.6 a 10.6)
    # ==========================================
    layer3_box = FancyBboxPatch((7.6, 0.4), 3.0, 6.3, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor=c_l3_bg, edgecolor=c_l3_border, linewidth=1.5, zorder=1)
    ax.add_patch(layer3_box)
    ax.text(9.1, 6.35, "CAPA 3: EXPLICABILIDAD Y XAI", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=c_l3_head)

    # Sub-cajas Capa 3
    # 1. Motor XAI
    b3_1 = FancyBboxPatch((7.8, 4.6), 2.6, 1.35, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#6EE7B7", linewidth=1.2, zorder=2)
    ax.add_patch(b3_1)
    ax.text(9.1, 5.65, "Motor XAI y Trazabilidad", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(9.1, 5.25, "• Justificación Normativa Ley 6835\n• Res. ENRESP 1590/24 y 216/24\n• Cadena Causal de Auditoría",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 2. Dictamen Pericial
    b3_2 = FancyBboxPatch((7.8, 2.65), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#6EE7B7", linewidth=1.2, zorder=2)
    ax.add_patch(b3_2)
    ax.text(9.1, 3.8, "Dictamen Pericial y Reclamo", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(9.1, 3.25, "• Determinación de Montos ($)\n• Nota Formal de Impugnación\n• Matriz de Responsabilidad",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # 3. Dashboard Web & Neuro-Simbólico
    b3_3 = FancyBboxPatch((7.8, 0.7), 2.6, 1.45, boxstyle="round,pad=0.08,rounding_size=0.1",
                          facecolor=box_bg, edgecolor="#6EE7B7", linewidth=1.2, zorder=2)
    ax.add_patch(b3_3)
    ax.text(9.1, 1.85, "Dashboard SPA & Gemini LLM", ha="center", va="center", fontsize=9.5, fontweight="bold", color=text_dark, zorder=3)
    ax.text(9.1, 1.3, "• Visualizador Web (7 Pestañas)\n• Asesor Gemini 3.8 (Eficiencia)\n• Interfaz Usuario-Sistema",
            ha="center", va="center", fontsize=8, color=text_muted, zorder=3)

    # Flechas internas Capa 3
    a3_1 = FancyArrowPatch((9.1, 4.6), (9.1, 4.1), arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#059669", zorder=4)
    a3_2 = FancyArrowPatch((9.1, 2.65), (9.1, 2.15), arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#059669", zorder=4)
    ax.add_patch(a3_1)
    ax.add_patch(a3_2)

    # ==========================================
    # FLECHAS INTER-CAPAS (Flujo Principal del Sistema)
    # ==========================================
    # De Vector de Hechos a Memoria de Trabajo
    a_l1_l2 = FancyArrowPatch((3.2, 1.42), (4.2, 3.37), connectionstyle="arc3,rad=-0.15",
                              arrowstyle="-|>", mutation_scale=14, lw=2.0, color="#2563EB", zorder=5)
    ax.add_patch(a_l1_l2)
    ax.text(3.7, 2.6, "Carga\nInicial", ha="center", va="center", fontsize=8, fontweight="bold", color="#1D4ED8",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#EFF6FF", edgecolor="#BFDBFE", lw=0.8), zorder=6)

    # De Motor de Inferencia a Motor XAI / Dictamen
    a_l2_l3 = FancyArrowPatch((6.8, 1.42), (7.8, 4.0), connectionstyle="arc3,rad=-0.12",
                              arrowstyle="-|>", mutation_scale=14, lw=2.0, color="#4F46E5", zorder=5)
    ax.add_patch(a_l2_l3)
    ax.text(7.3, 2.8, "Traza de\nReglas", ha="center", va="center", fontsize=8, fontweight="bold", color="#4338CA",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#EEF2FF", edgecolor="#C7D2FE", lw=0.8), zorder=6)

    # Título superior formal
    ax.text(5.5, 6.95, "ARQUITECTURA DE TRES CAPAS DEL SISTEMA EXPERTO (EDESA / ENRESP)",
            ha="center", va="center", fontsize=12, fontweight="bold", color="#111827")

    plt.tight_layout()
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close(fig)

    print(f"[OK] Diagrama de Arquitectura generado exitosamente:")
    print(f"     PNG: {png_path}")
    print(f"     SVG: {svg_path}")

if __name__ == "__main__":
    create_architecture_diagram()
