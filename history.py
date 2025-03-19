# history.py
import sqlite3, time, base64, io
from datetime import datetime, timedelta
import requests
from utils import temporary_copy, timestamp_to_datetime, get_full_path
from config import VT_API_KEY, VT_ANALYZE_URL, VT_URL_INFO_URL, RED, BLUE, CYAN, RESET, BROWSER_PATHS
import os

def extract_history_chromium(dias):
    """Extrae las URLs del historial de los navegadores definidos."""
    all_urls = []
    fecha_limite = datetime.now() - timedelta(days=dias)
    fecha_unix = int(fecha_limite.timestamp() * 1000000)
    
    for navegador in BROWSER_PATHS:
        history_path = get_full_path(navegador, "history")
        if not os.path.exists(history_path):
            print(f"{RED}[{navegador}] No se encontró el historial: {history_path}{RESET}")
            continue
        with temporary_copy(history_path, suffix=f"_{navegador}_copy.db") as temp_copy:
            try:
                conn = sqlite3.connect(temp_copy)
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM urls WHERE last_visit_time >= ? AND hidden = 0", (fecha_unix,))
                urls = [row[0] for row in cursor.fetchall()]
                conn.close()
                print(f"{BLUE}[{navegador}] Se han extraído {len(urls)} URLs.{RESET}")
                all_urls.extend(urls)
            except Exception as e:
                print(f"{RED}[{navegador}] Error extrayendo historial: {e}{RESET}")
    return all_urls
def analyze_urls_virus_total(urls):
    """
    Analiza una lista de URLs en VirusTotal y retorna un resumen final,
    que muestra únicamente las URLs maliciosas y sospechosas encontradas.
    """
    if not urls:
        return f"{RED}No hay URLs para analizar en VirusTotal.{RESET}\n"

    headers = {"x-apikey": VT_API_KEY}
    maliciosas = []
    sospechosas = []
    
    total_urls = len(urls)
    print(f"{CYAN}\nIniciando análisis de {total_urls} URLs en VirusTotal...{RESET}")

    for i, url in enumerate(urls, start=1):
        # Codifica la URL en base64 para la API
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        
        resp = requests.get(VT_URL_INFO_URL.format(url_id=url_id), headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        elif resp.status_code == 404:
            _ = requests.post(VT_ANALYZE_URL, headers=headers, data={"url": url})
            time.sleep(15)
            resp2 = requests.get(VT_URL_INFO_URL.format(url_id=url_id), headers=headers)
            if resp2.status_code == 200:
                data = resp2.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            else:
                stats = {}
        else:
            stats = {}

        mal = stats.get("malicious", 0)
        susp = stats.get("suspicious", 0)

        if mal > 0:
            maliciosas.append(url)
        if susp > 0:
            sospechosas.append(url)

        porcentaje = (i / total_urls) * 100
        print(f"\rProgreso: {porcentaje:.2f}%  ", end="")

    # Construir el resumen final
    resumen = "Resultado del análisis de las urls:\n\n"
    if maliciosas or sospechosas:
        if maliciosas:
            resumen += f"<b>Maliciosas ({len(maliciosas)}):</b>\n"
            for m in maliciosas:
                resumen += f"  - {m}\n"
        if sospechosas:
            resumen += f"\n<b>Sospechosas ({len(sospechosas)}):</b>\n"
            for s in sospechosas:
                resumen += f"  - {s}\n"
    else:
        resumen += "no se han encontrado urls maliciosas o sospechosas.\n"

    return resumen

