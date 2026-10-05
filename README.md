# Sistema Experto de Auditoría Tarifaria y Diagnóstico Energético (EDESA / Aguas del Norte)

**Cátedra:** Principios de Inteligencia Artificial (GT110)  
**Carrera:** Licenciatura en Gestión de Recursos Tecnológicos  
**Institución:** Universidad Gastón Dachary (UGD) — Ciclo Lectivo 2026  

---

## 📌 Descripción del Proyecto

Aplicación web y motor de inferencia analítico diseñado bajo arquitectura de **Sistemas Expertos Basados en Reglas con Explicabilidad (XAI)** y **Razonamiento Energético**. Realiza la auditoría fiscal, técnica y tarifaria de comprobantes de servicios públicos unificados (EDESA y Aguas del Norte) en la provincia de Salta, evaluando 17 reglas regulatorias (ENRESP, RG AFIP/ARCA 2126, Ley 23.349 y Ley 24.240).

### Características Principales:
1. **Extracción y Validación de Comprobantes:** Ingesta de boletas en formato PDF y JSON con validación de invariantes físicas de medidor y cuadratura contable.
2. **Motor de Inferencia de 17 Reglas:** Detección de distorsiones tarifarias, castigo fiscal por IVA no categorizado, cobro ilegítimo de tributos municipales sin consentimiento y anomalías en subsidios.
3. **Módulo de Explicabilidad XAI (Why / How):** Desglose detallado del sustento normativo, causalidad y recomendación de remediación para cada regla disparada.
4. **Auditoría de Artefactos Residenciales:** Estimación termodinámica y desagregación de consumos eléctricos por electrodoméstico correlacionados con la factura.
5. **Panel de Control Web Interactivo:** Dashboard en tiempo real con series temporales multi-mes (05/2026 a 09/2026), comparativas y asistente pericial integrado con Gemini.

---

## 🚀 Puesta en Marcha

### Prerrequisitos
- Python 3.10 o superior.
- Navegador web moderno.

### Instalación
1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd integrador
   ```
2. Instalar dependencias requeridas (opcional si se utiliza entorno virtual):
   ```bash
   pip install PyMuPDF google-genai python-dotenv
   ```
3. (Opcional) Configurar clave de Gemini:
   - Copiar `.env.example` a `.env`:
     ```bash
     cp .env.example .env
     ```
   - Asignar la API Key correspondiente a `GEMINI_API_KEY`. *(Si no se configura, el sistema opera en modo heurístico local sin interrupción)*.

### Ejecución
Iniciar el servidor local:
```bash
python iniciar_dashboard.py
```
Abrir en el navegador:
```
http://localhost:8000/app_dashboard.html
```

---

## 🧪 Pruebas Automatizadas

Para ejecutar la batería completa de 110 pruebas unitarias:
```bash
python tests/run_all_tests.py
```

---

## 📂 Estructura del Repositorio

```
integrador/
├── app_dashboard.html          # Interfaz web principal y dashboard interactivo
├── iniciar_dashboard.py        # Servidor HTTP local con endpoints API
├── app_streamlit.py            # Interfaz alternativa en Streamlit
├── .env.example                # Plantilla de variables de entorno seguras
├── .gitignore                  # Exclusiones de Git (evita filtración de .env y caché)
├── src/                        # Código fuente modular
│   ├── domain/                 # Entidades y extractor de comprobantes PDF
│   ├── engine/                 # Motor de inferencia y analizador de artefactos
│   ├── integrations/           # Integración con Gemini Advisor
│   ├── knowledge_base/         # Base de conocimiento (17 reglas ENRESP)
│   ├── persistence/            # Almacenamiento histórico y control de duplicados
│   └── visualizer/             # Generador de gráficos y reportes
├── data/                       # Facturas canónicas de prueba (JSON)
├── scripts/                    # Scripts utilitarios y de verificación
├── tests/                      # Suite de 110 pruebas automatizadas
└── output_graficos/            # Visualizaciones generadas
```
