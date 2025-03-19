# pdf_generator.py
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape
from datetime import datetime
from config import GREEN, RESET

def limpiar_texto(texto):
    return "".join(c if c.isprintable() else " " for c in texto)


def formatear_linea(linea):
    # Si la línea ya contiene etiquetas HTML (por ejemplo, <b>), se devuelve sin cambios
    if "<b>" in linea or "</b>" in linea:
        return linea

    etiquetas = [
        "Navegador:", "URL:", "Login URL:", "Usuario:", "Contraseña:",
        "ID:", "Current Path:", "Target Path:", "Start Time:", "Total Bytes:", "Tab URL:",
        "Field Name:", "Field Value:", "Date Created:", "Date Last Used:", "Count:",
        "Ext ID:", "Name:", "Version:", "Description:"
    ]
    if re.match(r'^https?://[^\s]+$', linea.strip(), re.IGNORECASE):
        link_escapado = escape(linea.strip())
        return f'<link href="{link_escapado}">{link_escapado}</link>'
    if ":" in linea:
        parte_etiqueta, valor = linea.split(":", 1)
        parte_etiqueta = parte_etiqueta.strip() + ":"
        valor = valor.strip()
        if parte_etiqueta in etiquetas:
            if parte_etiqueta.lower() in ["url:", "login url:", "tab url:"]:
                if not (valor.lower().startswith("http://") or valor.lower().startswith("https://")):
                    enlace = "https://" + valor
                else:
                    enlace = valor
                enlace_escapado = escape(enlace)
                valor_escapado = escape(valor)
                valor_html = f'<link href="{enlace_escapado}">{valor_escapado}</link>'
            else:
                valor_html = escape(valor)
            # Se aplica negrita a la etiqueta
            etiqueta_html = f'<b>{escape(parte_etiqueta)}</b>'
            return f'{etiqueta_html} {valor_html}'
        else:
            return escape(linea)
    else:
        return escape(linea)


def limpiar_lineas_repetidas(content, section_title):
    lines = content.split("\n")
    lines_limpias = []
    for line in lines:
        if line.strip().lower() == section_title.strip().lower():
            continue
        if line.strip().startswith("==="):
            continue
        lines_limpias.append(line)
    return "\n".join(lines_limpias)

fecha_informe = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
def generar_pdf_rl(report_sections, filename=None):
    # Si no se proporciona un nombre, se genera uno con la fecha y hora actuales
    if filename is None:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chromium_report_{fecha}.pdf"
        
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    big_title_style = ParagraphStyle('BigTitle', parent=styles['Title'], fontSize=18, leading=22, alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, leading=18, spaceBefore=12, spaceAfter=6)
    normal_style = styles["BodyText"]
    
    # Se muestra la fecha de creación en el informe
    fecha_informe = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph("Análisis Forense de los navegadores basados en Chromium del dispositivo", big_title_style))
    story.append(Paragraph(f"Fecha de creación del informe: {fecha_informe}", normal_style))
    story.append(Spacer(1, 20))
    
    for section_title, content in report_sections.items():
        story.append(Paragraph(section_title, heading_style))
        content_limpio = limpiar_lineas_repetidas(content, section_title)
        for linea in content_limpio.split("\n"):
            story.append(Paragraph(formatear_linea(linea), normal_style))
        story.append(Spacer(1, 12))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("Herramienta creada por AlejandroCanoMon, 2025", normal_style))
    doc.build(story)
    print(f"{GREEN}Informe PDF generado: {filename}{RESET}")
def generar_informe_pdf():
    # Importar las funciones necesarias
    import io
    from history import extract_history_chromium, analyze_urls_virus_total
    from credentials import extract_credentials_chromium, check_leaks_for_credentials
    from downloads import extract_downloads_chromium
    from autofill import extract_autofill_chromium
    from extensions import list_extensions_chromium
    from config import CYAN, RESET

    report_sections = {}

    # Primero se preguntan todas las opciones:
    dias_hist = int(input("Introduce el número de días para analizar el historial: "))
    dias_dl = int(input("Introduce el número de días para descargas: "))
    dias_autofill = int(input("Introduce el número de días para formularios (autofill): "))
    vt_incluir = input(f"{CYAN}¿Desea incluir el análisis de VirusTotal? (s/n): {RESET}").strip().lower() == 's'
    leaks_incluir = input(f"{CYAN}¿Desea incluir el análisis de CheckLeak? (s/n): {RESET}").strip().lower() == 's'
    
    # Sección Historial
    urls = extract_history_chromium(dias_hist)
    seccion_hist = f"=== Historial extraído (últimos {dias_hist} días) ===\n"
    if urls:
        seccion_hist += "\n".join(urls)
    else:
        seccion_hist += "No se extrajeron URLs."
    # Ahora, al final, si se ha solicitado el análisis de VirusTotal, se añade el resumen
    if vt_incluir:
        vt_report = analyze_urls_virus_total(urls)
        seccion_hist += "\n\n=== Análisis VirusTotal ===\n" + vt_report
    report_sections["Historial"] = seccion_hist

    # Sección Credenciales
    credentials = extract_credentials_chromium()
    seccion_creds = "=== Credenciales extraídas ===\n\n"
    if credentials:
        for cred in credentials:
            seccion_creds += f"Navegador: {cred['browser']}\n"
            seccion_creds += f"URL: {cred['main_url']}\n"
            seccion_creds += f"Login URL: {cred['login_url']}\n"
            seccion_creds += f"Usuario: {cred['user']}\n"
            seccion_creds += f"Contraseña: {cred['password']}\n"
            seccion_creds += "-" * 40 + "\n"
    else:
        seccion_creds += "No se encontraron credenciales."
    # Si se solicita el análisis de CheckLeak, se añade el resumen
    if leaks_incluir:
        leaks_report = check_leaks_for_credentials(credentials)
        seccion_creds += "\n=== Análisis de fugas con CheckLeak ===\n" + leaks_report
    report_sections["Credenciales"] = seccion_creds

    # Sección Descargas
    browsers = ["chrome", "edge", "brave", "opera", "vivaldi"]
    seccion_dl = "=== Descargas ===\n\n"
    for browser in browsers:
        downloads = extract_downloads_chromium(browser, dias_dl)
        seccion_dl += f"--- {browser.capitalize()} ---\n"
        if downloads:
            for d in downloads:
                seccion_dl += f"ID: {d['download_id']}\n"
                seccion_dl += f"Current Path: {d['current_path']}\n"
                seccion_dl += f"Target Path: {d['target_path']}\n"
                seccion_dl += f"Start Time: {d['start_time']}\n"
                seccion_dl += f"Total Bytes: {d['total_bytes']}\n"
                seccion_dl += f"Tab URL: {d['tab_url']}\n"
                seccion_dl += "-" * 20 + "\n"
        else:
            seccion_dl += "No se encontraron descargas.\n"
        seccion_dl += "\n"
    report_sections["Descargas"] = seccion_dl

    # Sección Autofill
    seccion_autofill = "=== Datos de Autofill ===\n\n"
    for browser in browsers:
        autofill_data = extract_autofill_chromium(browser, dias_autofill)
        seccion_autofill += f"--- {browser.capitalize()} ---\n"
        if autofill_data:
            for a in autofill_data:
                seccion_autofill += f"Field Name: {a['field_name']}\n"
                seccion_autofill += f"Field Value: {a['field_value']}\n"
                seccion_autofill += f"Date Created: {a['date_created']}\n"
                seccion_autofill += f"Date Last Used: {a['date_last_used']}\n"
                seccion_autofill += f"Count: {a['count']}\n"
                seccion_autofill += "-" * 20 + "\n"
        else:
            seccion_autofill += "No se encontraron datos de autofill.\n"
        seccion_autofill += "\n"
    report_sections["Autofill"] = seccion_autofill

    # Sección Extensiones
    seccion_ext = "=== Extensiones ===\n\n"
    for browser in browsers:
        exts = list_extensions_chromium(browser)
        seccion_ext += f"--- {browser.capitalize()} ---\n"
        if exts:
            for e in exts:
                seccion_ext += f"Ext ID: {e['extension_id']}\n"
                seccion_ext += f"Name: {e['extension_name']}\n"
                seccion_ext += f"Version: {e['version']}\n"
                seccion_ext += f"Description: {e['description']}\n"
                seccion_ext += "-" * 20 + "\n"
        else:
            seccion_ext += "No se encontraron extensiones.\n"
        seccion_ext += "\n"
    report_sections["Extensiones"] = seccion_ext

    # Finalmente, se genera el PDF con todas las secciones
    generar_pdf_rl(report_sections)
