# autofill.py
import sqlite3
from datetime import datetime, timedelta
import os
from utils import temporary_copy, timestamp_to_datetime
from config import BROWSER_PATHS

def extract_autofill_chromium(browser, days=0):
    user_dir = os.path.expanduser("~")
    if browser not in BROWSER_PATHS:
        print(f"Navegador '{browser}' no soportado.")
        return []
    webdata_path = os.path.join(user_dir, BROWSER_PATHS[browser]["web_data"])
    if not os.path.exists(webdata_path):
        print(f"No se encontró el archivo Web Data: {webdata_path}")
        return []
    results = []
    cutoff = datetime.now() - timedelta(days=days) if days > 0 else None
    with temporary_copy(webdata_path, suffix="_WebData_Copy.db") as temp_db:
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("Tablas encontradas en Web Data:", tables)
            if ('autofill',) not in tables:
                print("No se encontró la tabla 'autofill' en la base de datos.")
                conn.close()
                return results
            query = "SELECT name, value, date_created, date_last_used, count FROM autofill"
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Número de registros en 'autofill': {len(rows)}")
            for row in rows:
                field_name, field_value, date_created, date_last_used, count_value = row
                dt_created = timestamp_to_datetime(date_created) if date_created else None
                dt_last_used = timestamp_to_datetime(date_last_used) if date_last_used else None
                if cutoff and dt_created and dt_created < cutoff:
                    continue
                results.append({
                    "browser": browser.capitalize(),
                    "field_name": field_name,
                    "field_value": field_value,
                    "date_created": str(dt_created),
                    "date_last_used": str(dt_last_used),
                    "count": count_value
                })
            conn.close()
        except Exception as e:
            print(f"Error al extraer datos de autofill: {e}")
    return results
