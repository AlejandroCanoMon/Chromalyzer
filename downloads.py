# downloads.py
import sqlite3
from datetime import datetime, timedelta
from utils import temporary_copy, get_full_path, timestamp_to_datetime
from config import RED
import os

def extract_downloads_chromium(browser: str, days=0):
    history_path = get_full_path(browser, "history")
    if not os.path.exists(history_path):
        print(f"[{browser}] El archivo de historial no se encontró: {history_path}")
        return []
    results = []
    with temporary_copy(history_path, suffix="_copy") as temp_history:
        try:
            conn = sqlite3.connect(temp_history)
            cursor = conn.cursor()
            query = "SELECT id, target_path, start_time, received_bytes, total_bytes FROM downloads"
            cursor.execute(query)
            downloads = cursor.fetchall()
            if downloads:
                for d in downloads:
                    dl_id, target_path, start_time, received_bytes, total_bytes = d
                    dt_start = timestamp_to_datetime(start_time)
                    if days > 0:
                        cutoff = datetime.now() - timedelta(days=days)
                        if dt_start < cutoff:
                            continue
                    result = {
                        "browser": browser.capitalize(),
                        "download_id": dl_id,
                        "current_path": target_path,
                        "target_path": target_path,
                        "start_time": str(dt_start),
                        "total_bytes": total_bytes,
                        "tab_url": ""
                    }
                    results.append(result)
            else:
                print(f"[{browser}] No se encontraron registros de descargas.")
        except sqlite3.Error as e:
            print(f"[{browser}] Error al leer la base de datos SQLite: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    return results
