import os
import time
import json
import requests

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def load_local_vault():
    if not os.path.exists(CONFIG_FILE):
        default_map = {
            "is_installed": False, "custom_logo_url": "", "global_check_interval": 30,
            "users": {}, "apps": {
                "Jellyfin": {"url": "http://127.0.0.1:8096", "type": "jellyfin", "enabled": True},
                "Threadfin": {"url": "http://127.0.0.1:34400", "type": "threadfin", "enabled": True},
                "Pihole": {"url": "http://127.0.0.1:80", "type": "pihole", "enabled": False}
            },
            "metrics": {
                "Jellyfin": {"uptime": 0, "downtime": 0, "status": "Offline Data", "log": "Awaiting execution loop..."},
                "Threadfin": {"uptime": 0, "downtime": 0, "status": "Offline Data", "log": "Awaiting execution loop..."},
                "Pihole": {"uptime": 0, "downtime": 0, "status": "Disabled", "log": "Monitoring loop inactive."}
            }
        }
        save_local_vault(default_map)
        return default_map
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_local_vault(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def run_infrastructure_poll():
    vault = load_local_vault()
    if not vault.get("is_installed"):
        return
        
    tick = vault.get("global_check_interval", 30)
    for name, metadata in list(vault["apps"].items()):
        if not metadata["enabled"]:
            vault["metrics"][name]["status"] = "Disabled"
            continue
            
        target = metadata["url"]
        node_type = metadata["type"]
        status = "Healthy"
        log = "Active data responses validated successfully."
        
        try:
            if node_type == "jellyfin":
                r = requests.get(f"{target}/health", timeout=2)
                if r.status_code != 200: raise ValueError(f"HTTP error: {r.status_code}")
            elif node_type == "threadfin":
                r = requests.get(target, timeout=2)
                if r.status_code != 200: raise ValueError("UI frame matrix unreachable.")
            elif node_type == "pihole":
                r = requests.get(f"{target}/admin/api.php?status", timeout=2)
                if r.status_code == 200 and r.json().get("status") == "disabled":
                    status = "Degraded"
                    log = "Pi-hole is active but internal blocking is turned off."
        except Exception as e:
            status = "Unhealthy"
            log = f"Diagnostic Exception: {str(e)}"

        if status == "Healthy":
            vault["metrics"][name]["uptime"] += tick
        else:
            vault["metrics"][name]["downtime"] += tick
            
        vault["metrics"][name]["status"] = status
        vault["metrics"][name]["log"] = log

    save_local_vault(vault)

def start_telemetry_loop():
    while True:
        try: run_infrastructure_poll()
        except: pass
        vault = load_local_vault()
        time.sleep(vault.get("global_check_interval", 30))
