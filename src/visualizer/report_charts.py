"""
Módulo de Generación de Gráficos Analíticos de Alta Resolución
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Genera los recursos visuales del peritaje tarifario:
1. Gráfico 1: Desglose de la torta de facturación unificada ($377.559,51).
2. Gráfico 2: Serie temporal de 13 meses vs. Umbral base de subsidio RASE (200 kWh).
3. Gráfico 3: Comparador de Factura Actual vs. Optimizada vs. Desdoblamiento (Res. 1590/24).
4. Gráfico 4: Diagrama de flujo del árbol de inferencia deductiva del Sistema Experto.

Implementa un generador dual:
- Matplotlib (PNG alta resolución 300 DPI) si está disponible.
- Generador nativo vectorial SVG (sin dependencias externas) como respaldo garantizado.
"""

import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Intentar importar matplotlib
try:
    import matplotlib
    matplotlib.use("Agg")  # Backend no interactivo sin entorno de ventanas
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ReportChartsGenerator:
    """
    Generador de gráficos analíticos para el dictamen pericial del Parcial.
    Guarda los artefactos visuales en el directorio output_graficos/.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.output_dir = base_dir / "output_graficos"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_charts(self) -> Dict[str, str]:
        """Genera el conjunto completo de 4 gráficos en PNG y SVG."""
        results = {}
        results["chart_1"] = self.generate_chart_1_expenditure_breakdown()
        results["chart_2"] = self.generate_chart_2_historical_consumption()
        results["chart_3"] = self.generate_chart_3_optimization_and_split()
        results["chart_4"] = self.generate_chart_4_inference_tree()
        return results

    # -------------------------------------------------------------------------
    # GRÁFICO 1: Desglose de la Torta de Facturación
    # -------------------------------------------------------------------------
    def generate_chart_1_expenditure_breakdown(self) -> str:
        """Gráfico de torta / dona: Distribución porcentual del gasto total ($377.559,51)."""
        labels = [
            "Aguas del Norte (Saneamiento)",
            "EDESA S.A. (Electricidad Neta)",
            "Tasas Municipales e Inmobiliario",
            "Incidencia Alumbrado (kWh)",
            "Canon LUSAL (Mantenimiento)"
        ]
        values = [169262.42, 139850.89, 48670.80, 12597.08, 7178.32]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

        # Generar SVG nativo garantizado
        svg_path = self.output_dir / "grafico_1_distribucion_gasto.svg"
        self._write_pie_chart_svg(
            svg_path,
            title="Distribución del Gasto Total de la Boleta Unificada ($377.559,51)",
            labels=labels,
            values=values,
            colors=colors
        )

        # Generar PNG con Matplotlib si está disponible
        png_path = self.output_dir / "grafico_1_distribucion_gasto.png"
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(aspect="equal"))
                wedges, texts, autotexts = ax.pie(
                    values,
                    labels=labels,
                    autopct="%1.1f%%",
                    pctdistance=0.76,
                    startangle=140,
                    colors=colors,
                    wedgeprops=dict(width=0.48, edgecolor="white", linewidth=2),
                    textprops=dict(color="#222222", fontsize=8.5)
                )
                plt.setp(autotexts, size=8.5, weight="bold", color="white")
                ax.set_title(
                    "Distribución del Gasto - Boleta Salta (09/2026)\n"
                    "62,95% del total no remunera energía eléctrica pura",
                    fontsize=10.5, fontweight="bold", pad=10
                )
                plt.tight_layout()
                fig.savefig(png_path, dpi=300, bbox_inches="tight")
                plt.close(fig)
            except Exception:
                pass

        return str(png_path if png_path.exists() else svg_path)

    # -------------------------------------------------------------------------
    # GRÁFICO 2: Serie Temporal de Consumo vs. Umbral Subsidio RASE
    # -------------------------------------------------------------------------
    def generate_chart_2_historical_consumption(self) -> str:
        """Serie temporal de 13 meses contrastando contra el umbral base de 200 kWh."""
        meses = ["S-25", "O-25", "N-25", "D-25", "E-26", "F-26", "M-26", "A-26", "M-26", "J-26", "J-26", "A-26", "S-26"]
        consumos = [381, 494, 422, 519, 586, 592, 490, 436, 375, 718, 847, 357, 428]
        threshold = 200

        svg_path = self.output_dir / "grafico_2_historico_consumo_subsidio.svg"
        self._write_bar_chart_svg(
            svg_path,
            title="Evolución Histórica de Consumo Eléctrico (13 Meses) vs. Umbral RASE N3 (200 kWh)",
            categories=meses,
            values=consumos,
            threshold=threshold
        )

        png_path = self.output_dir / "grafico_2_historico_consumo_subsidio.png"
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(7, 4.5))
                bar_colors = ["#d9534f" if v > 600 else "#f0ad4e" if v > 400 else "#5bc0de" for v in consumos]
                bars = ax.bar(meses, consumos, color=bar_colors, edgecolor="#2c3e50", width=0.6)
                
                # Línea de umbral subsidiado
                ax.axhline(y=threshold, color="#27ae60", linestyle="--", linewidth=1.8, label="Umbral Base Subsidiado RASE (200 kWh)")
                
                # Anotación en el pico de julio
                ax.annotate(
                    f"Pico Máximo\n847 kWh (Jul-26)",
                    xy=(10, 847),
                    xytext=(8.2, 880),
                    arrowprops=dict(facecolor="black", shrink=0.05, width=1, headwidth=5),
                    fontweight="bold", color="#c0392b", fontsize=8.5
                )

                ax.set_ylabel("Consumo Mensual (kWh)", fontsize=9.5, fontweight="bold")
                ax.set_xlabel("Mes de Facturación", fontsize=9.5, fontweight="bold")
                ax.set_title(
                    "Curva de Consumo Eléctrico Mensual (Sep-25 a Sep-26)\n"
                    "Excedente Invernal vs. Umbral Subsidiado RASE N3",
                    fontsize=10.5, fontweight="bold", pad=8
                )
                ax.grid(axis="y", linestyle=":", alpha=0.6)
                ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
                plt.tight_layout()
                fig.savefig(png_path, dpi=300, bbox_inches="tight")
                plt.close(fig)
            except Exception:
                pass

        return str(png_path if png_path.exists() else svg_path)

    # -------------------------------------------------------------------------
    # GRÁFICO 3: Comparador de Factura Actual vs. Optimizada vs. Desdoblamiento
    # -------------------------------------------------------------------------
    def generate_chart_3_optimization_and_split(self) -> str:
        """Comparación de montos: Actual vs Optimizada (Saneada) vs Desdoblamiento (Res. 1590/24)."""
        scenarios = ["Monto Actual\n(Sin Saneamiento)", "Monto Optimizado\n(Ahorro -$64.210)", "Pago Prioritario\n(Desdoblamiento Luz)"]
        amounts = [377559.51, 313349.36, 152447.97]
        colors = ["#e74c3c", "#27ae60", "#2980b9"]

        svg_path = self.output_dir / "grafico_3_ahorro_potencial_desdoblamiento.svg"
        self._write_comparison_chart_svg(
            svg_path,
            title="Simulación Económica: Factura Actual vs. Optimizada vs. Desdoblamiento Res. 1590/24",
            labels=scenarios,
            values=amounts,
            colors=colors
        )

        png_path = self.output_dir / "grafico_3_ahorro_potencial_desdoblamiento.png"
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(6.8, 4.4))
                bars = ax.bar(scenarios, amounts, color=colors, width=0.48, edgecolor="#2c3e50")

                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(
                        f"${height:,.2f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha="center", va="bottom",
                        fontweight="bold", fontsize=8.5
                    )

                ax.set_ylabel("Importe a Abonar (ARS)", fontsize=9.5, fontweight="bold")
                ax.set_title(
                    "Auditoría Tarifaria y Protección Regulatoria\n"
                    "Ahorro: $770.521/año | Protección Corte: Res. 1590/24",
                    fontsize=10.5, fontweight="bold", pad=8
                )
                ax.set_ylim(0, 435000)
                ax.tick_params(axis='x', labelsize=8.5)
                ax.grid(axis="y", linestyle=":", alpha=0.6)
                plt.tight_layout()
                fig.savefig(png_path, dpi=300, bbox_inches="tight")
                plt.close(fig)
            except Exception:
                pass

        return str(png_path if png_path.exists() else svg_path)

    # -------------------------------------------------------------------------
    # GRÁFICO 4: Diagrama de Árbol de Inferencia Deductiva
    # -------------------------------------------------------------------------
    def generate_chart_4_inference_tree(self) -> str:
        """Diagrama visual del flujo de derivación lógica del Sistema Experto."""
        svg_path = self.output_dir / "grafico_4_arbol_inferencia_anomalias.svg"
        self._write_inference_tree_svg(svg_path)

        png_path = self.output_dir / "grafico_4_arbol_inferencia_anomalias.png"
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.axis("off")

                # Hechos iniciales
                ax.text(0.15, 0.85, "Hecho 1: EDESA = RESIDENCIAL", bbox=dict(boxstyle="round,pad=0.5", facecolor="#d4edda", edgecolor="#28a745"), ha="center")
                ax.text(0.15, 0.65, "Hecho 2: AGUA = NO RESIDENCIAL", bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8d7da", edgecolor="#dc3545"), ha="center")
                ax.text(0.15, 0.40, "Hecho 3: IVA Sujeto No Categ.", bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffc107"), ha="center")
                ax.text(0.15, 0.15, "Hecho 4: Total > $150k + Res 1590", bbox=dict(boxstyle="round,pad=0.5", facecolor="#cce5ff", edgecolor="#007bff"), ha="center")

                # Reglas
                ax.text(0.50, 0.75, "Regla R02\nInconsistencia Catastral", bbox=dict(boxstyle="square,pad=0.5", facecolor="#e2e3e5", edgecolor="#383d41"), ha="center")
                ax.text(0.50, 0.40, "Regla R01\nCastigo Fiscal IVA 40,5%", bbox=dict(boxstyle="square,pad=0.5", facecolor="#e2e3e5", edgecolor="#383d41"), ha="center")
                ax.text(0.50, 0.15, "Regla R07\nDesdoblamiento ENRESP", bbox=dict(boxstyle="square,pad=0.5", facecolor="#e2e3e5", edgecolor="#383d41"), ha="center")

                # Conclusiones
                ax.text(0.85, 0.60, "Meta R04:\nAhorro Mensual $64.210\n(Anual $770.521)", bbox=dict(boxstyle="round,pad=0.6", facecolor="#d1ecf1", edgecolor="#17a2b8", lw=2), ha="center")
                ax.text(0.85, 0.15, "Meta R12:\nDictamen Reclamo ENRESP\n(Protección contra Corte)", bbox=dict(boxstyle="round,pad=0.6", facecolor="#d4edda", edgecolor="#28a745", lw=2), ha="center")

                # Flechas de conexión
                ax.annotate("", xy=(0.35, 0.75), xytext=(0.28, 0.85), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.35, 0.75), xytext=(0.28, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.35, 0.40), xytext=(0.28, 0.40), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.35, 0.15), xytext=(0.28, 0.15), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.72, 0.60), xytext=(0.63, 0.75), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.72, 0.60), xytext=(0.63, 0.40), arrowprops=dict(arrowstyle="->", lw=1.5))
                ax.annotate("", xy=(0.72, 0.15), xytext=(0.63, 0.15), arrowprops=dict(arrowstyle="->", lw=1.5))

                ax.set_title("Árbol de Derivación Lógica y Reglas de Inferencia (GOFAI)", fontsize=11, fontweight="bold", pad=10)
                plt.tight_layout()
                fig.savefig(png_path, dpi=300, bbox_inches="tight")
                plt.close(fig)
            except Exception:
                pass

        return str(png_path if png_path.exists() else svg_path)

    # -------------------------------------------------------------------------
    # GENERADORES VECTORIALES NATIVOS SVG (100% LIBRES DE DEPENDENCIAS)
    # -------------------------------------------------------------------------
    def _write_pie_chart_svg(
        self,
        filepath: Path,
        title: str,
        labels: List[str],
        values: List[float],
        colors: List[str]
    ) -> None:
        """Crea un gráfico de torta vectorial SVG sin requerir librerías externas."""
        total = sum(values)
        cx, cy, r = 260, 240, 160
        start_angle = 0.0

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 480" width="750" height="480" font-family="Arial, sans-serif">',
            f'<rect width="750" height="480" fill="#ffffff" rx="10"/>',
            f'<text x="375" y="40" text-anchor="middle" font-size="16" font-weight="bold" fill="#2c3e50">{title}</text>',
            f'<g transform="translate(0, 20)">'
        ]

        # Sectores
        legend_y = 120
        for val, col, lab in zip(values, colors, labels):
            angle = (val / total) * 360.0
            rad_start = math.radians(start_angle)
            rad_end = math.radians(start_angle + angle)
            x1 = cx + r * math.cos(rad_start)
            y1 = cy + r * math.sin(rad_start)
            x2 = cx + r * math.cos(rad_end)
            y2 = cy + r * math.sin(rad_end)
            large_arc = 1 if angle > 180 else 0

            path_d = f"M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z"
            svg_parts.append(f'<path d="{path_d}" fill="{col}" stroke="#ffffff" stroke-width="2"/>')

            # Leyenda
            pct = (val / total) * 100.0
            svg_parts.append(f'<rect x="470" y="{legend_y}" width="16" height="16" fill="{col}" rx="3"/>')
            svg_parts.append(f'<text x="495" y="{legend_y + 13}" font-size="12" fill="#333333">{lab}: ${val:,.2f} ({pct:.1f}%)</text>')
            legend_y += 32

            start_angle += angle

        # Centro hueco estilo Donut
        svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="75" fill="#ffffff"/>')
        svg_parts.append(f'<text x="{cx}" y="{cy - 5}" text-anchor="middle" font-size="13" font-weight="bold" fill="#2c3e50">Total Factura</text>')
        svg_parts.append(f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" font-size="12" fill="#7f8c8d">${total:,.2f}</text>')
        svg_parts.append('</g></svg>')

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_parts))

    def _write_bar_chart_svg(
        self,
        filepath: Path,
        title: str,
        categories: List[str],
        values: List[float],
        threshold: float
    ) -> None:
        """Crea un gráfico de barras vectorial SVG sin librerías externas."""
        max_val = max(values) * 1.15
        chart_w, chart_h = 600, 260
        ox, oy = 70, 360

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 460" width="740" height="460" font-family="Arial, sans-serif">',
            f'<rect width="740" height="460" fill="#ffffff" rx="10"/>',
            f'<text x="370" y="38" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">{title}</text>',
            f'<line x1="{ox}" y1="{oy}" x2="{ox + chart_w}" y2="{oy}" stroke="#7f8c8d" stroke-width="2"/>',
            f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - chart_h}" stroke="#7f8c8d" stroke-width="2"/>'
        ]

        # Línea de umbral de 200 kWh
        thresh_y = oy - (threshold / max_val) * chart_h
        svg_parts.append(f'<line x1="{ox}" y1="{thresh_y:.1f}" x2="{ox + chart_w}" y2="{thresh_y:.1f}" stroke="#27ae60" stroke-width="2" stroke-dasharray="6,4"/>')
        svg_parts.append(f'<text x="{ox + chart_w - 5}" y="{thresh_y - 6:.1f}" text-anchor="end" font-size="11" font-weight="bold" fill="#27ae60">Tope Subsidiado RASE (200 kWh)</text>')

        # Barras
        bar_w = chart_w / len(values)
        for i, (cat, val) in enumerate(zip(categories, values)):
            bh = (val / max_val) * chart_h
            bx = ox + i * bar_w + (bar_w * 0.15)
            by = oy - bh
            color = "#c0392b" if val > 700 else "#e67e22" if val > 500 else "#3498db"

            svg_parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w * 0.7:.1f}" height="{bh:.1f}" fill="{color}" rx="3"/>')
            svg_parts.append(f'<text x="{bx + (bar_w * 0.35):.1f}" y="{by - 6:.1f}" text-anchor="middle" font-size="10" font-weight="bold" fill="#2c3e50">{int(val)}</text>')
            svg_parts.append(f'<text x="{bx + (bar_w * 0.35):.1f}" y="{oy + 18}" text-anchor="middle" font-size="10" fill="#333333">{cat}</text>')

        svg_parts.append(f'<text x="{ox - 10}" y="{oy - chart_h + 10}" text-anchor="end" font-size="11" fill="#7f8c8d">kWh</text>')
        svg_parts.append('</svg>')

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_parts))

    def _write_comparison_chart_svg(
        self,
        filepath: Path,
        title: str,
        labels: List[str],
        values: List[float],
        colors: List[str]
    ) -> None:
        """Crea un gráfico de barras comparativo SVG sin dependencias."""
        max_val = max(values) * 1.2
        ox, oy = 80, 360
        chart_w, chart_h = 580, 260

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 440" width="740" height="440" font-family="Arial, sans-serif">',
            f'<rect width="740" height="440" fill="#ffffff" rx="10"/>',
            f'<text x="370" y="38" text-anchor="middle" font-size="15" font-weight="bold" fill="#2c3e50">{title}</text>',
            f'<line x1="{ox}" y1="{oy}" x2="{ox + chart_w}" y2="{oy}" stroke="#7f8c8d" stroke-width="2"/>'
        ]

        bar_slot = chart_w / len(values)
        for i, (lab, val, col) in enumerate(zip(labels, values, colors)):
            bh = (val / max_val) * chart_h
            bx = ox + i * bar_slot + (bar_slot * 0.25)
            by = oy - bh
            w = bar_slot * 0.5

            svg_parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{w:.1f}" height="{bh:.1f}" fill="{col}" rx="4"/>')
            svg_parts.append(f'<text x="{bx + w/2:.1f}" y="{by - 10:.1f}" text-anchor="middle" font-size="12" font-weight="bold" fill="#2c3e50">${val:,.2f}</text>')

            # Etiquetas en múltiples líneas
            lines = lab.split("\n")
            for line_idx, line_text in enumerate(lines):
                svg_parts.append(f'<text x="{bx + w/2:.1f}" y="{oy + 20 + line_idx * 16}" text-anchor="middle" font-size="11" fill="#333333">{line_text}</text>')

        svg_parts.append('</svg>')

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_parts))

    def _write_inference_tree_svg(self, filepath: Path) -> None:
        """Crea el diagrama visual SVG del árbol de inferencia deductiva."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 480" width="860" height="480" font-family="Arial, sans-serif">
  <rect width="860" height="480" fill="#ffffff" rx="10"/>
  <text x="430" y="35" text-anchor="middle" font-size="16" font-weight="bold" fill="#2c3e50">Árbol de Derivación Lógica y Reglas de Inferencia (GOFAI)</text>

  <!-- COLUMNA 1: HECHOS INICIALES (PERCEPCIÓN) -->
  <text x="140" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#7f8c8d">HECHOS PERCIBIDOS (WM)</text>
  
  <rect x="30" y="90" width="220" height="45" fill="#e8f8f5" stroke="#1abc9c" stroke-width="2" rx="6"/>
  <text x="140" y="117" text-anchor="middle" font-size="11" font-weight="bold" fill="#16a085">H1: EDESA = RESIDENCIAL</text>

  <rect x="30" y="160" width="220" height="45" fill="#fdebd0" stroke="#e67e22" stroke-width="2" rx="6"/>
  <text x="140" y="187" text-anchor="middle" font-size="11" font-weight="bold" fill="#d35400">H2: AGUA = NO RESIDENCIAL</text>

  <rect x="30" y="240" width="220" height="45" fill="#fadbd8" stroke="#e74c3c" stroke-width="2" rx="6"/>
  <text x="140" y="267" text-anchor="middle" font-size="11" font-weight="bold" fill="#c0392b">H3: Condición Fiscal = No Categ.</text>

  <rect x="30" y="320" width="220" height="45" fill="#ebf5fb" stroke="#3498db" stroke-width="2" rx="6"/>
  <text x="140" y="347" text-anchor="middle" font-size="11" font-weight="bold" fill="#2980b9">H4: Total > $150k + Res. 1590/24</text>

  <rect x="30" y="390" width="220" height="45" fill="#f4ecf7" stroke="#8e44ad" stroke-width="2" rx="6"/>
  <text x="140" y="417" text-anchor="middle" font-size="11" font-weight="bold" fill="#6c3483">H5: Deuda Vencida = $0 (Al día)</text>

  <!-- COLUMNA 2: REGLAS DISPARADAS (RESOLUCIÓN DE CONFLICTOS) -->
  <text x="440" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#7f8c8d">REGLAS DISPARADAS (INFERENCE)</text>

  <rect x="330" y="125" width="220" height="50" fill="#f2f4f4" stroke="#34495e" stroke-width="2" rx="6"/>
  <text x="440" y="146" text-anchor="middle" font-size="11" font-weight="bold" fill="#2c3e50">Regla R02 [Prioridad 95]</text>
  <text x="440" y="162" text-anchor="middle" font-size="10" fill="#7f8c8d">Inconsistencia Catastral</text>

  <rect x="330" y="235" width="220" height="50" fill="#f2f4f4" stroke="#34495e" stroke-width="2" rx="6"/>
  <text x="440" y="256" text-anchor="middle" font-size="11" font-weight="bold" fill="#2c3e50">Regla R01 [Prioridad 100]</text>
  <text x="440" y="272" text-anchor="middle" font-size="10" fill="#7f8c8d">Castigo Fiscal IVA 40,5%</text>

  <rect x="330" y="335" width="220" height="50" fill="#f2f4f4" stroke="#34495e" stroke-width="2" rx="6"/>
  <text x="440" y="356" text-anchor="middle" font-size="11" font-weight="bold" fill="#2c3e50">Regla R07 [Prioridad 70]</text>
  <text x="440" y="372" text-anchor="middle" font-size="10" fill="#7f8c8d">Desdoblamiento ENRESP 1590</text>

  <!-- COLUMNA 3: METAS Y CONCLUSIONES INFERIDAS -->
  <text x="730" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#7f8c8d">METAS DERIVADAS (XAI)</text>

  <rect x="620" y="160" width="220" height="65" fill="#d4efdf" stroke="#27ae60" stroke-width="2" rx="6"/>
  <text x="730" y="185" text-anchor="middle" font-size="11" font-weight="bold" fill="#1e8449">Meta R04: Ahorro Mensual</text>
  <text x="730" y="202" text-anchor="middle" font-size="11" font-weight="bold" fill="#1e8449">$64.210,15 ARS/mes</text>
  <text x="730" y="218" text-anchor="middle" font-size="9" fill="#27ae60">Anualizado: $770.521,80</text>

  <rect x="620" y="325" width="220" height="65" fill="#d6eaf8" stroke="#2980b9" stroke-width="2" rx="6"/>
  <text x="730" y="350" text-anchor="middle" font-size="11" font-weight="bold" fill="#1f618d">Meta R12: Dictamen ENRESP</text>
  <text x="730" y="367" text-anchor="middle" font-size="10" font-weight="bold" fill="#1f618d">Pagar Luz: $152.447,97</text>
  <text x="730" y="383" text-anchor="middle" font-size="9" fill="#2980b9">Protegido contra Suspensión</text>

  <!-- FLECHAS Y CONEXIONES -->
  <line x1="250" y1="112" x2="330" y2="140" stroke="#7f8c8d" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="250" y1="182" x2="330" y2="160" stroke="#7f8c8d" stroke-width="1.5"/>
  <line x1="250" y1="262" x2="330" y2="260" stroke="#7f8c8d" stroke-width="1.5"/>
  <line x1="250" y1="342" x2="330" y2="350" stroke="#7f8c8d" stroke-width="1.5"/>
  <line x1="250" y1="412" x2="620" y2="365" stroke="#7f8c8d" stroke-width="1.5" stroke-dasharray="4,4"/>

  <line x1="550" y1="150" x2="620" y2="185" stroke="#27ae60" stroke-width="2"/>
  <line x1="550" y1="260" x2="620" y2="195" stroke="#27ae60" stroke-width="2"/>
  <line x1="550" y1="360" x2="620" y2="355" stroke="#2980b9" stroke-width="2"/>
</svg>"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
