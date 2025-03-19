# config.py
VT_API_KEY = '<INSERT VIRUSTOTAL API KEY HERE>'
VT_ANALYZE_URL = "https://www.virustotal.com/api/v3/urls"
VT_URL_INFO_URL = "https://www.virustotal.com/api/v3/urls/{url_id}"

# Códigos de colores ANSI
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"

# Rutas para cada navegador (relativas al directorio de usuario)
BROWSER_PATHS = {
    "chrome": {
        "history":    r"AppData\Local\Google\Chrome\User Data\Default\History",
        "logins":     r"AppData\Local\Google\Chrome\User Data\Default\Login Data",
        "cookies":    r"AppData\Local\Google\Chrome\User Data\Default\Network\Cookies",
        "web_data":   r"AppData\Local\Google\Chrome\User Data\Default\Web Data",
        "extensions": r"AppData\Local\Google\Chrome\User Data\Default\Extensions",
        "local_state": r"AppData\Local\Google\Chrome\User Data\Local State"
    },
    "edge": {
        "history":    r"AppData\Local\Microsoft\Edge\User Data\Default\History",
        "logins":     r"AppData\Local\Microsoft\Edge\User Data\Default\Login Data",
        "cookies":    r"AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies",
        "web_data":   r"AppData\Local\Microsoft\Edge\User Data\Default\Web Data",
        "extensions": r"AppData\Local\Microsoft\Edge\User Data\Default\Extensions",
        "local_state": r"AppData\Local\Microsoft\Edge\User Data\Local State"
    },
    "brave": {
        "history":    r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History",
        "logins":     r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Login Data",
        "cookies":    r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Cookies",
        "web_data":   r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Web Data",
        "extensions": r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Extensions",
        "local_state": r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State"
    },
    "opera": {
        "history":    r"AppData\Roaming\Opera Software\Opera Stable\History",
        "logins":     r"AppData\Roaming\Opera Software\Opera Stable\Login Data",
        "cookies":    r"AppData\Roaming\Opera Software\Opera Stable\Cookies",
        "web_data":   r"AppData\Roaming\Opera Software\Opera Stable\Web Data",
        "extensions": r"AppData\Roaming\Opera Software\Opera Stable\Extensions",
        "local_state": r"AppData\Roaming\Opera Software\Opera Stable\Local State"
    },
    "vivaldi": {
        "history":    r"AppData\Local\Vivaldi\User Data\Default\History",
        "logins":     r"AppData\Local\Vivaldi\User Data\Default\Login Data",
        "cookies":    r"AppData\Local\Vivaldi\User Data\Default\Cookies",
        "web_data":   r"AppData\Local\Vivaldi\User Data\Default\Web Data",
        "extensions": r"AppData\Local\Vivaldi\User Data\Default\Extensions",
        "local_state": r"AppData\Local\Vivaldi\User Data\Local State"
    }
}
