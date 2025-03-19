# main.py
import io
from config import BLUE, CYAN, RED, RESET
from history import extract_history_chromium, analyze_urls_virus_total
from credentials import extract_credentials_chromium, check_leaks_for_credentials
from cookies import fetch_chromium_cookies
from downloads import extract_downloads_chromium
from autofill import extract_autofill_chromium
from extensions import list_extensions_chromium
from pdf_generator import generar_informe_pdf
from utils import display_and_save

def main():
    while True:
        print(f"\n{BLUE}=== MENÚ PRINCIPAL ==={RESET}")
        print("1. Analizar historial (Chromium)")
        print("2. Extraer credenciales (Chromium)")
        print("3. Extraer cookies (Chromium)")
        print("4. Extraer descargas (Chromium)")
        print("5. Extraer datos de formularios (Autofill) (Chromium)")
        print("6. Listar extensiones (Chromium)")
        print("7. Generar informe completo en PDF")
        print("8. Salir")
        
        opcion = input("Introduce tu elección (1/2/3/4/5/6/7/8): ").strip()
        
        if opcion == "1":
            dias = int(input("Introduce el número de días a analizar: "))
            urls = extract_history_chromium(dias)
            resultado_hist = [f"=== Historial extraído (últimos {dias} días) ===\n"] + urls
            hist_text = "\n".join(resultado_hist)
            display_and_save(hist_text, "historial.txt")
            if input(f"\n{CYAN}¿Desea analizar estas URLs con VirusTotal? (s/n): {RESET}").strip().lower() == 's':
                vt_report = analyze_urls_virus_total(urls)
                display_and_save(vt_report, "historial_virustotal.txt")
                
        elif opcion == "2":
            credentials = extract_credentials_chromium()
            if credentials:
                output = io.StringIO()
                output.write("=== CREDENCIALES EXTRAÍDAS ===\n\n")
                for cred in credentials:
                    output.write(f"Navegador: {cred['browser']}\n")
                    output.write(f"URL: {cred['main_url']}\n")
                    output.write(f"Login URL: {cred['login_url']}\n")
                    output.write(f"Usuario: {cred['user']}\n")
                    output.write(f"Contraseña: {cred['password']}\n")
                    output.write("-" * 40 + "\n")
                cred_text = output.getvalue()
                display_and_save(cred_text, "credenciales.txt")
                if input(f"\n{CYAN}¿Desea verificar fugas con CheckLeak? (s/n): {RESET}").strip().lower() == 's':
                    leaks_report = check_leaks_for_credentials(credentials)
                    display_and_save(leaks_report, "credenciales_leaks.txt")
            else:
                print(f"{RED}No se encontraron credenciales en navegadores Chromium.{RESET}")
                
        elif opcion == "3":
            browser = input("Selecciona el navegador (chrome/edge/brave/opera/vivaldi): ").lower()
            dias = int(input("Introduce el número de días (0 para sin límite): "))
            cookies_grouped = fetch_chromium_cookies(browser)
            if not cookies_grouped:
                print(f"{RED}No se han encontrado cookies o el navegador no existe.{RESET}")
            else:
                output = io.StringIO()
                output.write(f"=== COOKIES EXTRAÍDAS - {browser.capitalize()} ===\n\n")
                for host, cookies in cookies_grouped.items():
                    output.write(f"Host: {host}\n")
                    for ck in cookies:
                        output.write(f"  Name: {ck['name']}\n")
                        output.write(f"  Value: {ck['decrypted_value']}\n")
                        output.write(f"  Last Access: {ck['last_access_utc']}\n")
                        output.write("-" * 40 + "\n")
                cookie_text = output.getvalue()
                display_and_save(cookie_text, f"{browser}_cookies.txt")
                
        elif opcion == "4":
            browser = input("Selecciona el navegador (chrome/edge/brave/opera/vivaldi): ").lower()
            dias = int(input("Introduce el número de días: "))
            downloads = extract_downloads_chromium(browser, dias)
            if not downloads:
                print(f"{RED}No se encontraron registros de descargas o navegador no existe.{RESET}")
            else:
                output = io.StringIO()
                output.write(f"=== DESCARGAS - {browser.capitalize()} ===\n\n")
                for d in downloads:
                    output.write(f"ID: {d['download_id']}\n")
                    output.write(f"Current Path: {d['current_path']}\n")
                    output.write(f"Target Path: {d['target_path']}\n")
                    output.write(f"Start Time: {d['start_time']}\n")
                    output.write(f"Total Bytes: {d['total_bytes']}\n")
                    output.write(f"Tab URL: {d['tab_url']}\n")
                    output.write("-" * 40 + "\n")
                dl_text = output.getvalue()
                display_and_save(dl_text, f"{browser}_descargas.txt")
                
        elif opcion == "5":
            browser = input("Selecciona el navegador (chrome/edge/brave/opera/vivaldi): ").lower()
            dias = int(input("Introduce el número de días: "))
            autofill_data = extract_autofill_chromium(browser, dias)
            if not autofill_data:
                print(f"{RED}No se encontró información de autofill o navegador no existe.{RESET}")
            else:
                output = io.StringIO()
                output.write(f"=== AUTOFILL - {browser.capitalize()} ===\n\n")
                for a in autofill_data:
                    output.write(f"Field Name: {a['field_name']}\n")
                    output.write(f"Field Value: {a['field_value']}\n")
                    output.write(f"Date Created: {a['date_created']}\n")
                    output.write(f"Date Last Used: {a['date_last_used']}\n")
                    output.write(f"Count: {a['count']}\n")
                    output.write("-" * 40 + "\n")
                autofill_text = output.getvalue()
                display_and_save(autofill_text, f"{browser}_autofill.txt")
                
        elif opcion == "6":
            browser = input("Selecciona el navegador (chrome/edge/brave/opera/vivaldi): ").lower()
            exts = list_extensions_chromium(browser)
            if not exts:
                print(f"{RED}No se encontraron extensiones o navegador no existe.{RESET}")
            else:
                output = io.StringIO()
                output.write(f"=== EXTENSIONES - {browser.capitalize()} ===\n\n")
                for e in exts:
                    output.write(f"Ext ID: {e['extension_id']}\n")
                    output.write(f"Name: {e['extension_name']}\n")
                    output.write(f"Version: {e['version']}\n")
                    output.write(f"Description: {e['description']}\n")
                    output.write("-" * 40 + "\n")
                ext_text = output.getvalue()
                display_and_save(ext_text, f"{browser}_extensiones.txt")
                
        elif opcion == "7":
            generar_informe_pdf()
            
        elif opcion == "8":
            print("Saliendo...")
            break
        else:
            print(f"{RED}Opción inválida.{RESET}")

if __name__ == "__main__":
    main()
