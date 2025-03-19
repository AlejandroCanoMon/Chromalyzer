# extensions.py
import os
import json
from config import BROWSER_PATHS

def list_extensions_chromium(browser):
    user_dir = os.path.expanduser("~")
    if browser not in BROWSER_PATHS:
        return []
    ext_dir = os.path.join(user_dir, BROWSER_PATHS[browser]["extensions"])
    if not os.path.isdir(ext_dir):
        return []
    extensions_info = []
    for ext_id in os.listdir(ext_dir):
        ext_path = os.path.join(ext_dir, ext_id)
        if not os.path.isdir(ext_path):
            continue
        manifest_found = False
        for version in os.listdir(ext_path):
            version_path = os.path.join(ext_path, version)
            if not os.path.isdir(version_path):
                continue
            manifest_file = os.path.join(version_path, "manifest.json")
            if os.path.isfile(manifest_file):
                try:
                    with open(manifest_file, 'r', encoding='utf-8') as mf:
                        data = json.load(mf)
                    name = data.get("name", "Nombre no encontrado")
                    version_val = data.get("version", version)
                    description = data.get("description", "")
                    extensions_info.append({
                        "browser": browser.capitalize(),
                        "extension_id": ext_id,
                        "extension_name": name,
                        "version": version_val,
                        "description": description
                    })
                except Exception as e:
                    extensions_info.append({
                        "browser": browser.capitalize(),
                        "extension_id": ext_id,
                        "extension_name": f"Error leyendo manifest: {e}",
                        "version": version,
                        "description": ""
                    })
                manifest_found = True
                break
        if not manifest_found:
            extensions_info.append({
                "browser": browser.capitalize(),
                "extension_id": ext_id,
                "extension_name": "No se encontró manifest.json",
                "version": "",
                "description": ""
            })
    return extensions_info
