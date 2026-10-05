import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

print("Verificando existencia de graficos:")
g2 = os.path.abspath(r"f:\Universidad Gaston Daechary\Principios de Inteligencia Artificial\04_Desarrollo_TPs\integrador\output_graficos\grafico_2_historico_consumo_subsidio.png")
g3 = os.path.abspath(r"f:\Universidad Gaston Daechary\Principios de Inteligencia Artificial\04_Desarrollo_TPs\integrador\output_graficos\grafico_3_ahorro_potencial_desdoblamiento.png")
print("g2 exists:", os.path.exists(g2))
print("g3 exists:", os.path.exists(g3))
