"""
Lanzador del Dashboard Web Interactivo del Sistema Experto
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (Matrícula: 100001)
Docentes: Prof. Agustín Encina (Titular), Dante Sicardi (Evaluador)

Inicia un servidor HTTP local y abre automáticamente app_dashboard.html
en el navegador predeterminado del sistema (Chrome, Edge, Firefox, etc.)
sin requerir ninguna dependencia externa (usa exclusivamente la biblioteca estándar de Python).
"""

import sys
import os
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path

import json
import base64

BASE_DIR = Path(__file__).resolve().parent
START_PORT = 8085

# Importar GeminiAdvisor si está disponible
try:
    from src.integrations.gemini_advisor import GeminiAdvisor
except Exception:
    GeminiAdvisor = None

# Importar PDFBillExtractor si está disponible
try:
    from src.domain.pdf_extractor import PDFBillExtractor
except Exception:
    PDFBillExtractor = None


class ReusableTCPServer(socketserver.TCPServer):
    # En Windows, SO_REUSEADDR permite colisiones silenciosas entre procesos; solo habilitar en POSIX
    allow_reuse_address = (sys.platform != "win32")


class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador HTTP con soporte de endpoints API y cabeceras CORS."""

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/gemini-advisor":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode("utf-8")) if post_data else {}
                
                if GeminiAdvisor:
                    advisor = GeminiAdvisor()
                    result = advisor.enrich_appliance_diagnostic(payload)
                else:
                    result = {
                        "mode": "LOCAL_HEURISTIC",
                        "status": "SUCCESS",
                        "diagnostic_text": payload.get("diagnostic_summary", "Diagnóstico analítico local."),
                        "recommendations": payload.get("potential_savings_recommendations", [])
                    }

                response_bytes = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
                return
            except Exception as e:
                err_resp = json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_resp)))
                self.end_headers()
                self.wfile.write(err_resp)
                return

        if self.path == "/api/extract-pdf":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)

                pdf_bytes = None
                content_type = self.headers.get("Content-Type", "")

                filename = ""
                if "application/json" in content_type:
                    payload = json.loads(post_data.decode("utf-8")) if post_data else {}
                    b64_data = payload.get("pdf_base64", "")
                    filename = payload.get("filename", "")
                    if b64_data:
                        if "," in b64_data:
                            b64_data = b64_data.split(",", 1)[1]
                        pdf_bytes = base64.b64decode(b64_data)
                elif "application/pdf" in content_type:
                    pdf_bytes = post_data
                elif "multipart/form-data" in content_type:
                    # Búsqueda de cabecera y delimitador PDF
                    start_idx = post_data.find(b"%PDF")
                    if start_idx != -1:
                        end_idx = post_data.rfind(b"%%EOF")
                        if end_idx != -1:
                            pdf_bytes = post_data[start_idx:end_idx + 5]
                        else:
                            pdf_bytes = post_data[start_idx:]

                if not pdf_bytes:
                    err_resp = json.dumps({"status": "ERROR", "message": "No se recibieron datos binarios PDF válidos."}).encode("utf-8")
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(err_resp)))
                    self.end_headers()
                    self.wfile.write(err_resp)
                    return

                if not PDFBillExtractor:
                    err_resp = json.dumps({"status": "ERROR", "message": "El extractor PDFBillExtractor no está disponible."}).encode("utf-8")
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(err_resp)))
                    self.end_headers()
                    self.wfile.write(err_resp)
                    return

                extractor = PDFBillExtractor()
                result = extractor.process_pdf_document(pdf_bytes, strict=False, filename=filename)

                resp_payload = {
                    "status": "SUCCESS",
                    "is_valid": result.is_valid,
                    "data": result.data,
                    "invariants": result.invariants_checked,
                    "errors": result.validation_errors,
                    "warnings": result.validation_warnings
                }
                response_bytes = json.dumps(resp_payload, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
                return

            except Exception as e:
                err_resp = json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_resp)))
                self.end_headers()
                self.wfile.write(err_resp)
                return

        super().do_POST()


def start_local_server():
    """Busca un puerto libre a partir de START_PORT e inicia el servidor en segundo plano."""
    os.chdir(str(BASE_DIR))
    handler = DashboardRequestHandler
    handler.log_message = lambda self, format, *args: None

    for port in range(START_PORT, START_PORT + 10):
        try:
            httpd = ReusableTCPServer(("", port), handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            return port, httpd, thread
        except OSError:
            continue
    return None, None, None


def main():
    print("=" * 80)
    print("SISTEMA EXPERTO DE AUDITORÍA TARIFARIA — SALTA 2026")
    print("Universidad Gastón Dachary (UGD) — Lic. en Gestión de Recursos Tecnológicos")
    print("Estudiante: Estudiante UGD (Matrícula: 100001)")
    print("Cátedra: Prof. Agustín Encina (Titular) | Dante Sicardi (Evaluador)")
    print("=" * 80)

    html_file = BASE_DIR / "app_dashboard.html"
    if not html_file.exists():
        print(f"[ERROR] No se encontró el archivo: {html_file}")
        sys.exit(1)

    file_url = html_file.as_uri()
    port, httpd, server_thread = start_local_server()

    if port:
        url = f"http://localhost:{port}/app_dashboard.html"
        print(f"\n-> Abriendo Dashboard Interactivo en el navegador...")
        print(f"   URL Web Local: {url}")
        print(f"   Ruta Directa:  {file_url}")
        webbrowser.open(url)
    else:
        print(f"\n-> Abriendo archivo local directamente en el navegador...")
        print(f"   Ruta Directa: {file_url}")
        webbrowser.open(file_url)

    print("\n[OK] Dashboard abierto exitosamente. Presione Ctrl+C en esta terminal para finalizar.\n")
    try:
        if server_thread:
            server_thread.join()
        else:
            input("Presione Enter para salir...")
    except KeyboardInterrupt:
        print("\nServidor cerrado correctamente.")


if __name__ == "__main__":
    main()
